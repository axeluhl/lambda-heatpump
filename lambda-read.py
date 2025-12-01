#!/usr/bin/python3
from pymodbus.client.sync import ModbusTcpClient
import struct

# Modbus-Verbindung aufbauen
client = ModbusTcpClient('192.168.101.11', port=502)
client.connect()

# Vorlauftemperatur (flowline temperature) auslesen: Register 1104
# Modbus-Register-Adresse: 1104, diese entspricht der Adresse für "T-flow"
register_address = 1004

# Versuche, die Vorlauftemperatur (Flow Line Temperature) zu lesen
result = client.read_holding_registers(register_address, 1, unit=1)

# Prüfe, ob der Wert erfolgreich gelesen wurde
if result.isError():
     # Gib die Fehlerbeschreibung aus
    print("Fehler beim Auslesen der Vorlauftemperatur: "+str(result))
else:
    # Temperaturwert aus den 2 Registern extrahieren
    # Die Vorlauftemperatur wird in 0.01°C gemessen, daher teilen wir den Wert durch 100
    # flowline_temperature = struct.unpack('>h', struct.pack('>HH', result.registers[0], result.registers[1]))[0] / 100.0
    # print("Vorlauftemperatur: "+flowline_temperature+"°C")
    print(str(result.registers))
    print(result.registers[0])

# Verbindung schließen
client.close()
