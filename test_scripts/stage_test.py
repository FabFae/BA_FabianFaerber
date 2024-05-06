import serial
import time

# Paramter für die serielle Verbindung
PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
TIMEOUT = 1  # Timeout in Sekunden

# Kommandos
OVR_STOP = b'OVR_STOP\r\n'
OVR_LOADPREF = b'OVR_LOADPREF\r\n'
OVR_SAVEPREF = b'OVR_SAVEPREF\r\n'
OVR_SETSTEPS_005 = b'OVR_SETSTEPS_005\r\n'  # Annahme: Dieser Befehl setzt 72° Schritte
OVR_SHOOTTURN_000 = b'OVR_SHOOTTURN_000\r\n'
OVR_STEPSHOOT_002 = b'OVR_STEPSHOOT_002\r\n'
OVR_START_001 = b'OVR_START_001\r\n'
OVR_GOON = b'OVR_GOON\r\n'

# Hinzufügen von Geschwindigkeitskommandos
OVR_SPEED_001 = b'OVR_SPEED_001\r\n'  # erhöht die Rotationsgeschwindigkeit
OVR_SPEED_000 = b'OVR_SPEED_000\r\n'  # verringert die Rotationsgeschwindigkeit

# Funktion zur Erhöhung der Geschwindigkeit
def set_speed_increase(steps):
    for _ in range(steps):
        send_command(OVR_SPEED_001)
        time.sleep(0.5)  # Pausieren, um dem Gerät Zeit zur Verarbeitung des Befehls zu geben


# Erstelle eine serielle Verbindung
ser = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)

def send_command(command):
    ser.write(command)
    response = ser.readline()
    print(response)
    
    
# set_speed_increase(10)
def setup_stage():
    # Laden der aktuell gespeicherten Einstellungen
    send_command(OVR_LOADPREF)

    # Festlegen der Schritte (72° pro Schritt)
    send_command(OVR_SETSTEPS_005)

    # Rotationssinn festlegen (im Uhrzeigersinn)
    send_command(OVR_SHOOTTURN_000)

    # Betriebsmodus auf STOPSHOOT setzen
    send_command(OVR_STEPSHOOT_002)

    # Speichere die Einstellungen auf der Vorrichtung
    send_command(OVR_SAVEPREF)

    # Starte die automatische Positionierung
    send_command(OVR_START_001)

    time.sleep(1)  # Warte einen Moment auf die Antwort


setup_stage()

# Rotation viermal um 72° durchführen 
for i in range(1):
    print(f"turn {i}")
    send_command(OVR_GOON)
    time.sleep(.5)  # Wartezeit abhängig von der Rotationsgeschwindigkeit


# Stoppe die Drehung
# send_command(OVR_STOP)

# Schließe die serielle Verbindung
# ser.close()