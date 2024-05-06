from PIL import Image
import subprocess

def take_picture():
    # Ersetzen Sie "jpeg" durch den tatsächlichen Namen des Programms und fügen Sie die korrekten Argumente hinzu
    command = [
        "rpicam-jpeg",  # Das Programm (bitte durch den tatsächlichen Namen ersetzen)
        "-o", "test.jpg",  # Optionen für das Ausgabeformat
        "-t", "50",  # Eine andere Option (vielleicht Zeit oder Qualität oder was auch immer -t ist)
        "--width", "480",  # Breite des Bildes
        "--height", "480"  # Höhe des Bildes
    ]

    # Ausführen des Befehls
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Prüfen, ob der Befehl erfolgreich war
    if result.returncode == 0:
        flip_image_horizontal("test.jpg")
        print("Der Befehl wurde erfolgreich ausgeführt!")
    else:
        print("Ein Fehler ist aufgetreten! Der Fehlercode:", result.returncode)


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

take_picture()
