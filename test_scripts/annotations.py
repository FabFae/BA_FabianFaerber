import os
import csv


# Pfad zur Datei
file_path = '/home/pi/images/labels.csv'

def create_file():
	# Überprüfen Sie, ob die Datei bereits existiert
	if not os.path.exists(file_path):
		# Die Datei existiert nicht, also erstellen Sie sie
		with open(file_path, 'w') as file:
			# Optional: Schreiben Sie den Header der CSV-Datei
			file.write('FileName, Azimuth,elevation,KameraPos,Drehteller\n')
			file.write('')
		print(f'Die Datei {file_path} wurde erstellt.')
	else:
		print(f'Die Datei {file_path} existiert bereits.')


def add_data(name:str, azi:int, elev:int, cam:int, table:int):
	# Daten, die hinzugefügt werden sollen
	data_to_add = [azi,elev,cam,table]
	with open(file_path, 'a', newline='') as file:
		writer = csv.writer(file)
		
		# Fügen Sie der Datei eine neue Zeile hinzu
		writer.writerow(data_to_add)

print(f'Eine neue Zeile wurde zur Datei {file_path} hinzugefügt.')


create_file()
add_data("Test", 20, 30, 10 ,5)
add_data("Test2", 20, 30, 10 ,5)
