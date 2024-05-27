import json
from datetime import datetime
from picamera2 import Picamera2
from PIL import Image

import board
import csv
import neopixel
import os
import random
import serial
import time
import sys

from StepperMotor import StepperMotor
from utils import spherical_to_stereographic, get_angles

STEPS_PER_DEGREE_VERTICAL = 91
STEPS_PER_DEGREE_HORIZONTAL = 100

# Befehle zur Steuerung der SgateOnAir
OVR_STOP = b'OVR_STOP\r\n'
OVR_LOADPREF = b'OVR_LOADPREF\r\n'
OVR_SAVEPREF = b'OVR_SAVEPREF\r\n'
OVR_SETSTEPS_002 = b"OVR_SETSTEPS_002\r\n"
OVR_SETSTEPS_003 = b"OVR_SETSTEPS_003\r\n"
OVR_SETSTEPS_004 = b"OVR_SETSTEPS_004\r\n"
OVR_SETSTEPS_005 = b"OVR_SETSTEPS_005\r\n"
OVR_SETSTEPS_006 = b"OVR_SETSTEPS_006\r\n"
OVR_SETSTEPS_008 = b"OVR_SETSTEPS_008\r\n"
OVR_SETSTEPS_009 = b"OVR_SETSTEPS_009\r\n"
OVR_SETSTEPS_010 = b"OVR_SETSTEPS_010\r\n"
OVR_SETSTEPS_012 = b"OVR_SETSTEPS_012\r\n"
OVR_SETSTEPS_015 = b"OVR_SETSTEPS_015\r\n"
OVR_SETSTEPS_018 = b"OVR_SETSTEPS_018\r\n"
OVR_SETSTEPS_020 = b"OVR_SETSTEPS_020\r\n"
OVR_SETSTEPS_024 = b"OVR_SETSTEPS_024\r\n"
OVR_SETSTEPS_030 = b"OVR_SETSTEPS_030\r\n"
OVR_SETSTEPS_036 = b"OVR_SETSTEPS_036\r\n"
OVR_SETSTEPS_040 = b"OVR_SETSTEPS_040\r\n"
OVR_SETSTEPS_045 = b"OVR_SETSTEPS_045\r\n"
OVR_SETSTEPS_060 = b"OVR_SETSTEPS_060\r\n"
OVR_SETSTEPS_072 = b"OVR_SETSTEPS_072\r\n"
OVR_SETSTEPS_090 = b"OVR_SETSTEPS_090\r\n"
OVR_SETSTEPS_120 = b"OVR_SETSTEPS_120\r\n"
OVR_SETSTEPS_180 = b"OVR_SETSTEPS_180\r\n"
OVR_SETSTEPS_360 = b"OVR_SETSTEPS_360\r\n"
OVR_SHOOTTURN_000 = b'OVR_SHOOTTURN_000\r\n'
OVR_STEPSHOOT_002 = b'OVR_STEPSHOOT_002\r\n'
OVR_START_001 = b'OVR_START_001\r\n'
OVR_GOON = b'OVR_GOON\r\n'


def rotate_motor(horizontal=False, invert_direction=False):
    if not horizontal:
        step_pin = 6,
        dir_pin = 5,
        enable_pin = 23
    else:
        step_pin = 11,
        dir_pin = 9,
        enable_pin = 22

    current_motor = StepperMotor(
        step_pin=step_pin,
        dir_pin=dir_pin,
        enable_pin=enable_pin,
        steps_per_rev=40000,
        step_time=0.0001,
        step_delay=0.00005,
    )
    current_motor.initialize()

    start_angle = 0
    end_angle = 1
    angle_steps = 1

    for next_angle in range(start_angle, end_angle + 1, angle_steps):
        current_motor.step(1, invert_direction=invert_direction)

    current_motor.cleanup()


def move_clockwise(degrees: int):
    for i in range(degrees * STEPS_PER_DEGREE_VERTICAL):
        rotate_motor(horizontal=True, invert_direction=True)


def move_counter_clockwise(degrees: int):
    for i in range(degrees * STEPS_PER_DEGREE_VERTICAL):
        rotate_motor(horizontal=True)


def move_up(degrees: int):
    for i in range(degrees * STEPS_PER_DEGREE_HORIZONTAL):
        rotate_motor(horizontal=False)


def move_down(degrees: int):
    for i in range(degrees * STEPS_PER_DEGREE_HORIZONTAL):
        rotate_motor(horizontal=False, invert_direction=True)


def time_passed(start_time):
    # Verstrichene Zeit berechnen
    elapsed_time = time.time() - start_time

    # Stunden, Minuten und Sekunden aus der Gesamtzeit berechnen
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)

    # Ausgabe der verstrichenen Zeit in Stunden, Minuten und Sekunden
    print("--- %d Stunde(n) %d Minute(n) %d Sekunde(n) ---" % (hours, minutes, seconds))


class ImageMaker:
    def __init__(self,
                 folder_path: str = None,
                 num_samples: int = 3,
                 start_index: int = 0,
                 exposure_time: int = 8000000,
                 img_size: int = 1920,
                 table_rotations: int = 2,
                 height_levels: int = 2,
                 starting_height: int = 0,
                 positions=None
                 ):

        self.folder_path = folder_path
        if self.folder_path is None:
            time_stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            self.folder_path = os.path.join("/home/pi/images", time_stamp)
        self.relative_path = "/home/pi"

        self.num_samples = num_samples

        self.labels_file_name = "labels.csv"
        self.detail_file_name = "details.csv"
        self.metadata_file_name = "metadata.json"

        self.position_index = start_index

        self.exposure_time = exposure_time
        self.img_height = img_size
        self.img_width = img_size
        self.camera = None

        self.table_rotations = table_rotations
        print(f"self.table_rotations = {self.table_rotations}")

        self.num_leds = 90  # Anzahl LEDs am LED-Streifen
        self.leds_used = 67  # Anzahl der verwendeten LEDs

        self.height_levels = height_levels
        self.current_horizontal = -153
        self.current_vertical = 0
        self.current_height_level = 0

        self.pixels = neopixel.NeoPixel(board.D18, self.num_leds, brightness=1)  # setup des LED-Streifens

        if positions:
            self.light_positions = positions
        else:
            self.light_positions = get_angles(num_samples)  # liste aus [Azimutwinkel, Elevationswinkel, LED-Index]

        # Erstelle die serielle Verbindung mit den angegebenen Parametern
        self.ser = serial.Serial(port='/dev/ttyUSB0',
                                 baudrate=57600,
                                 bytesize=8,
                                 parity='N',
                                 stopbits=1,
                                 timeout=1)
        if self.table_rotations > 0:
            print(f"run setup_stage() for {self.table_rotations} rotations")
            self.setup_stage()
        self.go_to_starting_height(starting_height)

        # self.light_positions = [[-140, 30.19, 53]]
        print("Light Positions:")
        print(self.light_positions)

    def setup_stage(self):
        # Laden der aktuell gespeicherten Einstellungen
        self.send_command_to_stage_on_air(OVR_LOADPREF)

        # Einstellen der Rotationswinkel
        if self.table_rotations == 2:
            self.send_command_to_stage_on_air(OVR_SETSTEPS_002)
        if self.table_rotations == 3:
            self.send_command_to_stage_on_air(OVR_SETSTEPS_003)
        if self.table_rotations == 4:
            self.send_command_to_stage_on_air(OVR_SETSTEPS_004)
        if self.table_rotations == 5:
            self.send_command_to_stage_on_air(OVR_SETSTEPS_005)
        # if self.table_rotations == 6:
        #     OVR_SETSTEPS_006 = b"OVR_SETSTEPS_006\r\n"
        # if self.table_rotations == 8:
        #     OVR_SETSTEPS_008 = b"OVR_SETSTEPS_008\r\n"
        # if self.table_rotations == 9:
        #     OVR_SETSTEPS_009 = b"OVR_SETSTEPS_009\r\n"
        # if self.table_rotations == 10:
        #     OVR_SETSTEPS_010 = b"OVR_SETSTEPS_010\r\n"
        # if self.table_rotations == 12:
        #     OVR_SETSTEPS_012 = b"OVR_SETSTEPS_012\r\n"
        # if self.table_rotations == 15:
        #     OVR_SETSTEPS_015 = b"OVR_SETSTEPS_015\r\n"
        # if self.table_rotations == 18:
        #     OVR_SETSTEPS_018 = b"OVR_SETSTEPS_018\r\n"
        # if self.table_rotations == 20:
        #     OVR_SETSTEPS_020 = b"OVR_SETSTEPS_020\r\n"
        # if self.table_rotations == 24:
        #     OVR_SETSTEPS_024 = b"OVR_SETSTEPS_024\r\n"
        # if self.table_rotations == 30:
        #     OVR_SETSTEPS_030 = b"OVR_SETSTEPS_030\r\n"
        # if self.table_rotations == 36:
        #     OVR_SETSTEPS_036 = b"OVR_SETSTEPS_036\r\n"
        # if self.table_rotations == 40:
        #     OVR_SETSTEPS_040 = b"OVR_SETSTEPS_040\r\n"
        # if self.table_rotations == 45:
        #     OVR_SETSTEPS_045 = b"OVR_SETSTEPS_045\r\n"
        # if self.table_rotations == 60:
        #     OVR_SETSTEPS_060 = b"OVR_SETSTEPS_060\r\n"
        # if self.table_rotations == 72:
        #     OVR_SETSTEPS_072 = b"OVR_SETSTEPS_072\r\n"
        # if self.table_rotations == 90:
        #     OVR_SETSTEPS_090 = b"OVR_SETSTEPS_090\r\n"
        # if self.table_rotations == 120:
        #     OVR_SETSTEPS_120 = b"OVR_SETSTEPS_120\r\n"
        # if self.table_rotations == 180:
        #     OVR_SETSTEPS_180 = b"OVR_SETSTEPS_180\r\n"
        # if self.table_rotations == 360:
        #     OVR_SETSTEPS_360 = b"OVR_SETSTEPS_360\r\n"

        # Rotationssinn festlegen (im Uhrzeigersinn)
        self.send_command_to_stage_on_air(OVR_SHOOTTURN_000)
        # Betriebsmodus auf STOPSHOOT setzen
        self.send_command_to_stage_on_air(OVR_STEPSHOOT_002)
        # Speichere die Einstellungen auf der Vorrichtung
        self.send_command_to_stage_on_air(OVR_SAVEPREF)
        # Starte die automatische Positionierung
        self.send_command_to_stage_on_air(OVR_START_001)

        print("stage-setup complete")

    def send_command_to_stage_on_air(self, command):
        self.ser.write(command)
        response = self.ser.readline()
        print(response)

    def go_to_starting_height(self, steps_up):
        if self.height_levels - 1 > 0:
            dist_per_height_lvl = int(140 / (self.height_levels - 1))
        else:
            dist_per_height_lvl = 0
        print(f"going up to height level {steps_up}")
        print(f"distance per height level: {dist_per_height_lvl}")

        for i in range(steps_up):
            move_up(dist_per_height_lvl)
            print("one lvl up")
        self.current_height_level = steps_up
        print(f"current height level: {self.current_height_level}")

    def save_metadata(self):
        file_path = os.path.join(self.folder_path, "metadata.json")
        print(f"save metadate to {file_path}")
        metadata = {"num_samples": len(self.light_positions),
                    "start_index": self.position_index,
                    "exposure": self.exposure_time,
                    "img_size": self.img_width,
                    "table_rotations": self.table_rotations,
                    "height_levels": self.current_height_level,
                    "starting_height": self.current_height_level,
                    "positions": self.light_positions
                    }

        with open(file_path, 'w', encoding='utf-8') as f:  # überschreibt sie date, wenn sie bereits existiert
            json.dump(metadata, f, ensure_ascii=False, indent=4)

    def rotate_stage_on_air(self):
        print("----------> rotate stage")
        # Öffne die serielle Verbindung, wenn sie nicht bereits offen ist
        if not self.ser.is_open:
            self.ser.open()

        try:
            # Befehle senden: Rotation um definierten Winkel durchführen
            self.send_command_to_stage_on_air(OVR_GOON)
            time.sleep(.5)  # Wartezeit abhängig von der Rotationsgeschwindigkeit

        finally:
            # Schließe die serielle Verbindung, wenn du fertig bist
            # self.ser.close()
            pass

    # Funktion, um Befehle an die Stage zu senden

    def cam_setup(self):
        # Kamera konfigurieren und starten
        camera = Picamera2()
        camera.configure(camera.create_still_configuration(main={"size": (self.img_height, self.img_width)}))
        camera.set_controls({'ExposureTime': self.exposure_time})
        camera.start()
        time.sleep(2)  # Wartezeit bis Kamera einstellungen übernommen hat
        return camera

    def take_picture(self):
        time.sleep(.5)  # um Wackeln der Kamera zu vermeiden

        # Bild aufnehmen und Kamera stoppen
        image = self.camera.capture_array()

        # Holen Sie sich den aktuellen Zeitstempel mit Millisekundengenauigkeit
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')[:-3]  # Millisekunden auf 3 Stellen gekürzt

        file_name_big = f"big/img_{timestamp}.png"
        big_path = os.path.join(self.folder_path, file_name_big)

        file_name_small = f"img_{timestamp}.png"
        small_path = os.path.join(self.folder_path, file_name_small)

        # Bild spiegeln und speichern
        flipped_image = Image.fromarray(image).transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
        flipped_image.save(big_path)

        # Verkleinern und speichern
        small_image = flipped_image.resize((224, 224))
        small_image.save(small_path)

        return file_name_small

    def add_labels(self, img_name: str):
        labels_path = os.path.join(self.folder_path, self.labels_file_name)
        azimut = self.current_horizontal + 180
        print(f"current index: {self.position_index}")
        elevation = self.light_positions[self.position_index][1]
        converted = spherical_to_stereographic(azimut, elevation)
        path_to_image = os.path.join(self.folder_path, img_name)
        relative_path = os.path.relpath(path_to_image, self.relative_path)
        data_to_add = [relative_path,
                       converted[0],  # Azimutwinkel
                       converted[1],  # Elevationswinkel
                       ]

        with open(labels_path, 'a', newline='') as file:
            writer = csv.writer(file)
            # Fügt der Datei eine neue Zeile hinzu
            writer.writerow(data_to_add)

    def create_labels_file(self):
        file_path = os.path.join(self.folder_path, self.labels_file_name)
        # Überprüfen Sie, ob die Datei bereits existiert
        if not os.path.exists(file_path):
            # Die Datei existiert nicht, also erstellen Sie sie
            with open(file_path, 'w') as file:
                # Optional: Schreiben Sie den Header der CSV-Datei
                file.write('FileName,S_x,S_y\n')
            print(f'Die Datei {file_path} wurde erstellt.')
        else:
            print(f'Die Datei {file_path} existiert bereits.')

    def create_details_file(self):
        file_path = os.path.join(self.folder_path, self.detail_file_name)
        # Überprüfen Sie, ob die Datei bereits existiert
        if not os.path.exists(file_path):
            # Die Datei existiert nicht, also erstellen Sie sie
            with open(file_path, 'w') as file:
                # Optional: Schreiben Sie den Header der CSV-Datei
                file.write('FileName,NumLED,Index,KameraHeight\n')
            print(f'Die Datei {file_path} wurde erstellt.')
        else:
            print(f'Die Datei {file_path} existiert bereits.')

    def save_details(self, img_name: str):
        details_path = os.path.join(self.folder_path, self.detail_file_name)
        path_to_image = os.path.join(self.folder_path, img_name)
        relative_path = os.path.relpath(path_to_image, self.relative_path)
        data_to_add = [relative_path,
                       self.light_positions[self.position_index][2],
                       self.position_index,
                       self.current_height_level
                       ]

        with open(details_path, 'a', newline='') as file:
            writer = csv.writer(file)
            # Fügt der Datei eine neue Zeile hinzu
            writer.writerow(data_to_add)

    def create_folder(self):
        full_path = os.path.join(self.folder_path, "big")

        access_rights = 0o755  # Zugriffsrechte für Nutzer

        # Überprüfe, ob der Unterordner bereits existiert, und erstelle ihn ggf.
        if not os.path.exists(full_path):
            os.makedirs(full_path, access_rights)

    def set_led(self, number):
        self.pixels.fill((0, 0, 0))
        self.pixels[number] = (255, 255, 255)

    def go_to_horizontal(self, destination_deg: int):
        self.pixels.fill((0, 0, 0))
        print(f"going form {self.current_horizontal} to {destination_deg}. ")
        self.pixels.fill((0, 0, 0))
        if self.current_horizontal < destination_deg:
            dist = abs(self.current_horizontal - destination_deg)
            move_clockwise(dist)
            print(f"move_clockwise {dist}")
        else:
            dist = (destination_deg - self.current_horizontal)
            move_counter_clockwise(dist)
            print(f"move_counter_clockwise {dist}")
        self.current_horizontal = destination_deg

    def select_random_elements(self, positons):
        if self.num_samples >= len(positons):
            print("Liste der Lichtpinkte wurde nicht verändert")
            return sorted(positons)
        else:
            return random.sample(positons, self.num_samples)

    def start(self):
        start_time = time.time()
        self.create_folder()
        self.create_labels_file()
        self.create_details_file()
        self.camera = self.cam_setup()

        # einmal LEDs aufleuchten lassen
        for i in range(self.leds_used):
            self.set_led(i)
        one_level_up = int(140 / (self.height_levels - 1))
        self.horizontal_pass()
        # schrittweise rauf
        for i in range(self.height_levels - 1 - self.current_height_level):
            # Starte die automatische Positionierung
            self.send_command_to_stage_on_air(OVR_START_001)
            move_up(one_level_up)
            self.current_height_level += 1
            self.horizontal_pass()

        # schrittweise runter
        for i in range(self.height_levels - 1):
            move_down(one_level_up)

        time_passed(start_time)

    def horizontal_pass(self):
        if self.table_rotations == 0:
            self.take_images()
        else:
            for j in range(self.table_rotations - 1):
                print(f"rotation {j}")
                # abfahren aller positionen
                self.take_images()

                # zurück zur Startposition und stage drehen
                self.position_index = 0
                self.pixels.fill((0, 0, 0))
                move_counter_clockwise(self.current_horizontal + 155)
                self.current_horizontal = -153
                if self.table_rotations > 0:
                    self.rotate_stage_on_air()
    def take_images(self):
        for i in range(self.position_index, len(self.light_positions)):
            # wenn self.position_index von json Datei geladen wurde, dann ist der Wert =! 0
            pos = self.light_positions[i]
            self.go_to_horizontal(pos[0])
            time.sleep(.075)
            self.set_led(self.light_positions[self.position_index][2])
            img_name = self.take_picture()
            self.add_labels(img_name)
            self.save_details(img_name)
            self.save_metadata()
            self.position_index += 1


im = ImageMaker(positions=[[-140, 30.19, 53]])
im.start()