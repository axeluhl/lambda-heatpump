#!/usr/bin/env python3

# Read all relevant parameters from a Lambda Heatpump and record them in an InfluxDB
# Please change the IP address of your Heat Pump (e.g. 192.168.178.41 and Port (default 502) to suite your environment - see below)
#
import pymodbus
import argparse
import time
import sys
import datetime
from time import sleep
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

from influxdb import InfluxDBClient

class lambda_modbusquery:
    def __init__(self, heatpump, port):
        # Change the IP address and port to suite your environment:
        self.heatpump_ip=heatpump
        self.heatpump_port=port
        # No more changes required beyond this point
        self.LambdaRegister = []
        self.Adr = []
        # --------------- General Ambient ----------------
        self.Adr.append([0, "General Ambient Error number", "U16_1", 0])
        self.Adr.append([1, "General Ambient Operating state", "U16_1", 0])
        self.Adr.append([2, "General Ambient Actual ambient temperature", "S16", 0])
        self.Adr.append([3, "General Ambient Actual ambient temperature 1h", "S16", 0])
        self.Adr.append([4, "General Ambient Calculated ambient temperature", "S16", 0])
        # --------------- General E-Manager --------------
        self.Adr.append([100, "General E-Manager Error number", "S16", 0])
        self.Adr.append([101, "General E-Manager Operating state", "U16_1", 0])
        self.Adr.append([102, "General E-Manager Actual power", "S16", 0])
        self.Adr.append([103, "General E-Manager Actual power consumption", "S16", 0])
        self.Adr.append([104, "General E-Manager Power consumption setpoint", "S16", 0])
        # ------------------- Heat Pump ------------------
        self.Adr.append([1000, "Heat Pump Error state", "S16", 0])
        self.Adr.append([1001, "Heat Pump Error number", "S16", 0])
        self.Adr.append([1004, "Heat Pump T-flow", "S16", 0])
        self.Adr.append([1005, "Heat Pump T-return", "S16", 0])
        self.Adr.append([1006, "Heat Pump Volume sink", "S16", 0])
        self.Adr.append([1007, "Heat Pump EQin", "S16", 0])
        self.Adr.append([1008, "Heat Pump EQout", "S16", 0])
        self.Adr.append([1009, "Heat Pump Volume source", "S16", 0])
        self.Adr.append([1010, "Heat Pump Compressor rating", "U16_1", 0])
        self.Adr.append([1011, "Heat Pump Qp heating", "S16", 0])
        self.Adr.append([1012, "Heat Pump FI power consumption", "S16", 0])
        self.Adr.append([1013, "Heat Pump COP", "S16", 0])
        #self.Adr.append([1014, "Heat Pump Modbus request release password", "U16_1", 0])
        #self.Adr.append([1015, "Heat Pump Request type", "S16", 0])
        self.Adr.append([1016, "Heat Pump Request flow line temperature", "S16", 0])
        self.Adr.append([1017, "Heat Pump Request return line temperature", "S16", 0])
        self.Adr.append([1018, "Heat Pump Request heat sink temperature difference", "S16", 0])
        self.Adr.append([1019, "Heat Pump Request Relais state for 2nd heating stage", "S16", 0])
        self.Adr.append([1020, "Heat Pump Statistic VdA E since last reset", "S32", 0])
        self.Adr.append([1022, "Heat Pump Statistic VdA Q since last reset", "S32", 0])
        # --------------------- Boiler -------------------
        self.Adr.append([2000, "Boiler Error number", "S16", 0])
        self.Adr.append([2001, "Boiler Operating state", "U16_1", 0])
        self.Adr.append([2002, "Boiler Actual high temperature", "S16", 0])
        self.Adr.append([2003, "Boiler Actual low temperature", "S16", 0])
        self.Adr.append([2050, "Boiler Actual Maximum boiler temperature", "S16", 0])
        # --------------------- Buffer -------------------
        self.Adr.append([3000, "Buffer Error number", "S16", 0])
        self.Adr.append([3001, "Buffer Operating state", "U16_1", 0])
        self.Adr.append([3002, "Buffer Actual high temperature", "S16", 0])
        self.Adr.append([3003, "Buffer Actual low temperature", "S16", 0])
        self.Adr.append([3050, "Buffer Maximum boiler temperature", "S16", 0])
        # --------------------- Solar --------------------
        #self.Adr.append([4000, "Solar Error number", "S16", 0])
        #self.Adr.append([4001, "Solar Operating state", "U16_1", 0])
        # --------------- Heating Circuit ----------------
        self.Adr.append([5000, "Heating curcuit Error number", "S16", 0])
        self.Adr.append([5001, "Heating curcuit Operating state", "U16_1", 0])
        self.Adr.append([5002, "Heating curcuit Flow line temperature", "S16", 0])
        self.Adr.append([5004, "Heating curcuit Return line temperature", "S16", 0])
        self.Adr.append([5005, "Heating curcuit Setpoint flow line temperature", "S16", 0])
        self.Adr.append([5006, "Heating curcuit Operating mode", "S16", 0])
        self.Adr.append([5050, "Heating curcuit Offset flow line temperature setpoint", "S16", 0])
        self.Adr.append([5051, "Heating curcuit Setpoint room heating temperature", "S16", 0])
        self.Adr.append([5052, "Heating curcuit Setpoint room cooling temperature", "S16", 0])
      
    #-----------------------------------------
    # Routine to read a string from one address with n registers 
    def ReadStr(self,myadr_dec,n):
        r1=self.client.read_holding_registers(myadr_dec,n,unit=1)
        STRGRegister = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big)
        result_STRGRegister =STRGRegister.decode_string(n)      
        return(result_STRGRegister) 
    #-----------------------------------------
    # Routine to read a string from one address with 8 registers 
    def ReadStr8(self,myadr_dec):
        return self.ReadStr(myadr_dec,8)
    #-----------------------------------------
    # Routine to read a string from one address with 16 registers 
    def ReadStr16(self,myadr_dec):
        return self.ReadStr(myadr_dec,16)
    #-----------------------------------------
    # Routine to read a string from one address with 8 registers 
    def ReadStr32(self,myadr_dec):
        return self.ReadStr(myadr_dec,32)
    #-----------------------------------------
    # Routine to read a Float from one address with 2 registers     
    def ReadFloat(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,2,unit=1)
        FloatRegister = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_FloatRegister =round(FloatRegister.decode_32bit_float(),2)
        return(result_FloatRegister)   
    #-----------------------------------------
    # Routine to read a U16 from one address with 1 register 
    def ReadU16_1(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,1,unit=1)
        U16register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_U16register = U16register.decode_16bit_uint()
        return(result_U16register)
    #-----------------------------------------
    # Routine to read a U16 from one address with 2 registers 
    def ReadU16_2(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,2,unit=1)
        U16register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_U16register = U16register.decode_16bit_uint()
        return(result_U16register)
    #-----------------------------------------
    # Routine to read an R32 from one address with 2 registers 
    def ReadR32(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,2,unit=1)
        R32register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_R32register = R32register.decode_32bit_float()
        return(result_R32register)
    #-----------------------------------------
    # Routine to read a U32 from one address with 2 registers 
    def ReadU32(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,2,unit=1)
        U32register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        result_U32register = U32register.decode_32bit_uint()
        return(result_U32register)
    #-----------------------------------------
    # Routine to read a S16 from one address with 2 registers 
    def ReadS16(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,1,unit=1)
        S16register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_S16register = S16register.decode_16bit_int()
        return(result_S16register)
    #-----------------------------------------
    # Routine to read a S32 from one address with 2 registers 
    def ReadS32(self,myadr_dec):
        r1=self.client.read_holding_registers(myadr_dec,2,unit=1)
        S32register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_S32register = S32register.decode_32bit_int()
        return(result_S32register)
        
    try:
        def run(self):
            self.client = ModbusTcpClient(self.heatpump_ip,port=self.heatpump_port)            
            self.client.connect()
            self.LambdaRegister=[]
            for adr in self.Adr:
                print ("Handling "+str(adr))
                if adr[2] == "Strg8":
                    adr[3] = self.ReadStr8(adr[0])
                elif adr[2] == "Strg16":
                    adr[3] = self.ReadStr16(adr[0])
                elif adr[2] == "Strg32":
                    adr[3] = self.ReadStr32(adr[0])
                elif adr[2] == "Float":
                    adr[3] = self.ReadFloat(adr[0])
                elif adr[2] == "U16_1":
                    adr[3] = self.ReadU16_1(adr[0])
                elif adr[2] == "U16_2":
                    adr[3] = self.ReadU16_2(adr[0])
                elif adr[2] == "U32":
                    adr[3] = self.ReadU32(adr[0])
                elif adr[2] == "R32":
                    adr[3] = self.ReadR32(adr[0])
                elif adr[2] == "S16":
                    adr[3] = self.ReadS16(adr[0])
                elif adr[2] == "S32":
                    adr[3] = self.ReadS32(adr[0])
                else:
                  print ("Format "+adr[2]+" unknown")
                self.LambdaRegister.append(adr)
            self.client.close()

    except Exception as ex:
            print ("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            print ("XXX- Hit the following error :From subroutine lambda_modbusquery :", ex)
            print ("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
#-----------------------------


if __name__ == "__main__":  
  my_parser = argparse.ArgumentParser()
  my_parser.add_argument('--heatpump', default='lambda',
                      help='The host name or IP address of your heat pump; defaults to "lambda"')
  my_parser.add_argument('--modbusport', default='502',
                      help='The Modbus port of your heat pump; defaults to 502')
  my_parser.add_argument('--influx', default='klo.axeluhl.de',
                      help='The host name or IP address where your InfluxDB database for storing your heat pump values is running; defaults to "klo.axeluhl.de"')
  my_parser.add_argument('--db', default='lambda',
                      help='The InfluxDB database name for storing your heat pump values; defaults to "lambda"')
  my_parser.add_argument('repetitions', nargs='?', default='1',
                      help='The number of times to poll the Modbus values; defaults to 1')
  my_parser.add_argument('intervalInSeconds', nargs='?', default='0',
                      help='The time between polling the Modbus values; defaults to 0')
  args = vars(my_parser.parse_args())
  repetitions=int(args['repetitions'])
  intervalInSeconds=int(args['intervalInSeconds'])
  for i in range(0, repetitions):
    start=time.time()
    print ("Starting QUERY #"+str(i+1)+"...")
    try:
        Lambdavalues =[]
        Lambdaquery = lambda_modbusquery(args['heatpump'], int(args['modbusport']))
        Lambdaquery.run()
    except Exception as ex:
        print (traceback.format_exc())
        print ("Issues querying Lambda Heatpump -ERROR :", ex)
    influx_json_body = [
            {
                "measurement": "heatpump",
                "tags": {"heatpump": Lambdaquery.heatpump_ip},
                "time": int(time.time()),
                "fields": {
                }
            }
            ]
    for elements in Lambdaquery.LambdaRegister:
        print ( elements[1], ":", elements[3], "Type:", elements[2])
        if elements[2].startswith("Strg"):
            influx_json_body[0]["fields"][elements[1]] = "\""+str(elements[3])[2:len(elements[3])-1]+"\""
        else:
            influx_json_body[0]["fields"][elements[1]] = elements[3]
    print ("Done...")
    ##########################################
    print ("----------------------------------")
    print ("Doing some Calculations of the received information:")
    LambdaVal ={}
    for elements in Lambdaquery.LambdaRegister:
        LambdaVal.update({elements[1]: elements[3]})
    #LeftSidePowerGeneration= round((LambdaVal['Power DC1']+ LambdaVal['Power DC2']),1)
    #print ("Left Side Raw Power Generation of Panles :", LeftSidePowerGeneration)
    #BatteryCharge = round(LambdaVal['Battery voltage']* LambdaVal['Actual battery charge -minus or discharge -plus current'],1)
    #print ("BatteryCharge (-) / Discharge(+) is      :", BatteryCharge)
    #TotalHomeconsumption =round((LambdaVal['Home own consumption from battery'] + LambdaVal['Home own consumption from grid'] + LambdaVal['Home own consumption from PV']),1)
    #PowertoGrid = round(LambdaVal['Heatpump Generation Power (actual)'] - TotalHomeconsumption,1)
    #print ("Powerfromgrid (-) /To Grid (+) is        :", PowertoGrid)
    #print ("Total current Home consumption is        :", TotalHomeconsumption)
    ####### InfluxDB Stuff ######
    print ("Adding to InfluxDB...")
    #influx_json_body[0]["fields"]['Home own consumption'] = TotalHomeconsumption
    #influx_json_body[0]["fields"]['PV production'] = LeftSidePowerGeneration
    #influx_json_body[0]["fields"]['Battery Charge'] = BatteryCharge
    print ("The data is: ", influx_json_body)
    influx_client = InfluxDBClient(host=args['influx'], database=args['db'])
    influx_client.create_database(args['db'])
    try:
        if not influx_client.write_points(influx_json_body, time_precision='s'):
            print ("Some problem (but no exception) inserting data into InfluxDB")
    except Exception as ex:
        print ("Problem inserting into InfluxDB:", ex)
    waitTimeInSeconds=start+intervalInSeconds-time.time()
    if waitTimeInSeconds > 0:
        sleep(waitTimeInSeconds)
