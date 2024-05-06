import os
import time
from datetime import datetime
import subprocess
import numpy as np
from PIL import Image

STEPS_PER_DEGREE_VERTICAL = 92
STEPS_PER_DEGREE_HORIZONTAL = 100


class ImageSession:
    def __init__(self):
        self.points_on_sphere = 15
        self.path_images = "/home/pi/images"
        self.shutter_speed = 10000
        self.num_leds = 90

        # self.pixels = neopixel.NeoPixel(board.D18, self.num_leds, brightness=1)  # des LED-Streifens
        self.current_horizontal = -153
        self.current_vertical = 0
        self.angles = [0.0, 1.3, 2.8, 4.3, 5.8, 7.3, 8.8, 10.3, 11.8, 13.3, 14.8, 16.3, 17.8, 19.4, 20.9, 22.4, 23.9,
                       25.4, 26.9, 28.4, 29.9, 31.4, 32.9, 34.4, 35.9, 37.4, 38.9, 40.4, 41.9, 43.4, 44.9, 46.4, 47.9,
                       49.4, 50.9, 52.4, 53.9, 55.4, 57.0, 58.5, 60.0, 61.5, 63.0, 64.5, 66.0, 67.5, 69.0, 70.5, 72.0,
                       73.5, 75.0, 76.5, 78.0, 79.5, 81.0, 82.5, 84.0, 85.5, 87.0, 88.5, 90.0, 91.5, 93.0, 94.6, 96.1,
                       97.6, 99.1, 100.6, 102.1, 103.6]  # Liste, die jedem LED-Index einen Winkel zuordnet
        self.light_positions = []  # liste aus [Azimutwinkel, Elevationswinkel, LED-Index]

    def set_led(self, number):
        # self.pixels.fill((0, 0, 0))
        # self.pixels[number] = (255, 255, 255)
        # self.current_led = number
        print(f"led {number} ON!")

    def take_picture(self):
        # Create the folder if it does not exist
        # If the folder exists, do nothing
        os.makedirs(self.path_images, exist_ok=True)

        # Holen Sie sich den aktuellen Zeitstempel mit Millisekundengenauigkeit
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')[:-3]  # Millisekunden auf 3 Stellen gekürzt
        file_name = os.path.join(self.path_images, f"img_{timestamp}.jpg")

        command = [
            "libcamera-still",  # Das Programm (bitte durch den tatsächlichen Namen ersetzen)
            "-o", file_name,  # Option für das Ausgabeformat
            "--shutter", str(self.shutter_speed),  # Shutter-Speed in Mikrosekunden
            "--width", "480",  # Breite des Bildes
            "--height", "480"  # Höhe des Bildes

        ]

        # Ausführen des Befehls
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Prüfen, ob der Befehl erfolgreich war
        if result.returncode == 0:
            flip_image_horizontal(file_name)
            print(f"Bild gespeichert unter: {file_name}")
        else:
            print("Ein Fehler ist aufgetreten! Der Fehlercode:", result.returncode)

    def go_to_horizontal(self, destination_deg: int):
        # self.pixels.fill((0, 0, 0))
        if self.current_horizontal < destination_deg:
            self.move_clockwise(abs(self.current_horizontal - destination_deg))
        else:
            self.move_counter_clockwise(abs(destination_deg - self.current_horizontal))
        self.current_horizontal = destination_deg
        print(f"new pos: {self.current_horizontal}, horizontal")
        # self.pixels.fill((0, 0, 0))

    # Diese Funktion nimmt einen Winkel als Argument und gibt den Index des nächstliegenden Lichtwinkels zurück.
    def get_closest_light(self, angle: int):
        index_of_min = 0
        # Initialisiere die Variable 'distance' mit einem großen Wert als Startpunkt für den minimalen Abstand.
        distance = 1000

        # Initialisiere einen Zähler, um den aktuellen Index in der Schleife zu verfolgen.
        current_index = 0
        for light in self.angles:

            # Prüfe, ob der Betrag der Differenz zwischen dem gegebenen Winkel und dem aktuellen 'light'
            # kleiner ist als die bisher gespeicherte 'distance'.
            if abs(angle - light) < distance:
                # Update 'distance' auf den neuen kleineren Abstand.
                distance = abs(angle - light)
                # Aktualisiere 'index_of_min' auf den Index des Lichtwinkels, der aktuell der nächste ist.
                index_of_min = current_index
            current_index += 1

        # Gebe den Index des Lichtwinkels zurück, der dem gegebenen Winkel am nächsten ist.
        return index_of_min

    def fibonacci_sphere(self):
        pts = self.points_on_sphere
        # Berechnung der goldenen Winkel
        phi = np.pi * (3. - np.sqrt(5.))  # ~2.39996322972865332

        # Erstellen der Punkte
        points_to_return = []
        for i in range(pts):
            y = 1 - (i / float(pts - 1)) * 2  # y geht von 1 bis -1
            radius = np.sqrt(1 - y * y)  # radius im Zylinder

            theta = phi * i  # goldenes Winkelinkrement

            x = np.cos(theta) * radius
            z = np.sin(theta) * radius

            # Umrechnung von kartesischen Koordinaten in sphärische Koordinaten
            azimuth = np.arctan2(z, x)
            elevation = np.arcsin(y)

            # Umwandlung von radian zu Grad
            azimuth_deg = np.degrees(azimuth)
            elevation_deg = np.degrees(elevation)
            if -163 < azimuth_deg < 163:
                if 0 <= elevation_deg < 80:
                    # Hinzufügen des Punktes zur Liste
                    points_to_return.append((round(azimuth_deg), round(elevation_deg)))

        return sorted(points_to_return)

    def get_angles(self):
        angles_list = self.fibonacci_sphere()
        return_list = []
        for pair in angles_list:
            closest_light_index = self.get_closest_light(pair[1])
            return_list.append([pair[0], self.angles[closest_light_index], closest_light_index])
        return return_list

    def move_clockwise(self, degrees: int):
        # for i in range(degrees * STEPS_PER_DEGREE_VERTICAL):
        #     rotate_motor(horizontal=True, invert_direction=True)
        print(f"move_clockwise {degrees}, brrrr")

    def move_counter_clockwise(self, degrees: int):
        # for i in range(degrees * STEPS_PER_DEGREE_VERTICAL):
        #     rotate_motor(horizontal=True)
        print(f"move_counter_clockwise {degrees}, brrrr")

    def start(self):
        print("lets_go")
        self.light_positions = self.get_angles()
        print(self.light_positions)
        for pos in self.light_positions:
            print(pos[0])
            self.go_to_horizontal(pos[0])
            self.set_led(pos[2])
            # self.take_picture()
        self.move_counter_clockwise(self.current_horizontal + 158)


def move_up(degrees: int):
    # for i in range(degrees * STEPS_PER_DEGREE_HORIZONTAL):
    #     rotate_motor(horizontal=False)
    print(f"move_up {degrees}, brrrr")


def move_down(degrees: int):
    # for i in range(degrees * STEPS_PER_DEGREE_HORIZONTAL):
    #     rotate_motor(horizontal=False, invert_direction=True)
    print(f"move_down {degrees}, brrrr")


def flip_image_horizontal(file_path):
    try:
        # Bild öffnen
        with Image.open(file_path) as img:
            # Bild horizontal spiegeln
            flipped_img = img.transpose(Image.FLIP_TOP_BOTTOM)
            # Das gespiegelte Bild speichern
            flipped_img.save(file_path)
            print("Das Bild wurde erfolgreich gespiegelt!")
    except Exception as e:
        print("Ein Fehler ist aufgetreten beim Spiegeln des Bildes:", e)


photo_session = ImageSession()
photo_session.start()
