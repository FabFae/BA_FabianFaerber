import RPi.GPIO as GPIO
import time
import board
import neopixel
from datetime import datetime
import subprocess
from PIL import Image
import os
import numpy as np
from picamera2 import Picamera2
import csv

class cam_test():
	
	def __init__(self):
		self.path_images = "/home/pi/images"
		self.exposure_time = 80000
		self.img_height = 480
		self.img_width = 480 			
		self.picam2 = self.cam_setup()
		

	def cam_setup(self):
		# Kamera konfigurieren und starten
		
		# Create the folder if it does not exist
		# If the folder exists, do nothing
		os.makedirs(self.path_images, exist_ok=True)
		
		
		camera = Picamera2()
		camera.configure(camera.create_still_configuration(main={"size": (self.img_height, self.img_width)}))
		camera.set_controls({'ExposureTime': self.exposure_time})
		camera.start()
		time.sleep(2)  # Wartezeit für das Bereitsein der Kamera	
		return camera	
	
	def take_picture(self):
		# Bild aufnehmen und Kamera stoppen
		image = self.picam2.capture_array()
		

		# Holen Sie sich den aktuellen Zeitstempel mit Millisekundengenauigkeit
		timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')[:-3]  # Millisekunden auf 3 Stellen gekürzt
		file_name = os.path.join(self.path_images, f"img_{timestamp}.jpg")
		
		# Bild spiegeln und speichern
		Image.fromarray(image).transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM).save(file_name)

		return file_name
		
test = cam_test()
test.take_picture()
test.take_picture()



