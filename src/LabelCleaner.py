import os
from pathlib import Path
import csv
import pandas as pd
import argparse


def check_if_file_exists(directory_path):
    num_missing = 0
    directory_path = Path(directory_path)
    # Der Pfad zur CSV-Datei
    csv_file_path = os.path.join(directory_path, "labels.csv")
    if not os.path.exists(csv_file_path):
        print(f"Die Datei 'labels.csv' wurde im Verzeichnis {directory_path} nicht gefunden.")
        return

    missing = []

    # Öffnen und Lesen der CSV-Datei
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)  # Ueberspringen des Headers

        for row_number, row in enumerate(csv_reader, start=2):  # Mit Zeile 2 anfangen
            if len(row) == 0:  # Überspringen leerer Zeilen
                continue

            file_name = os.path.basename(Path(row[0]))

            # Der volle Pfad zur Datei innerhalb des Ordners
            full_file_path = Path(os.path.join(directory_path, file_name))

            # Prüfe, ob die Datei existiert
            if not os.path.isfile(full_file_path):
                print(f"Datei nicht gefunden: {file_name} (in Zeile {row_number})")
                missing.insert(0, row_number - 1)  # -1, da die erste zeile übersprungen wurde
                num_missing += 1
    print(f"number of missing labels: {num_missing}")
    print(missing)
    return csv_file_path, missing


def delete_rows(csv_file_path, row_to_delete):
    # Eine temporäre Datei erstellen
    temp_file_path = csv_file_path + '.tmp'

    with open(csv_file_path, 'r') as csvfile, open(temp_file_path, 'w', newline='') as tempfile:
        reader = csv.reader(csvfile)
        writer = csv.writer(tempfile)

        # Kopieren von Zeilen in temporäre Datei, ausgenommen die zu löschenden Zeilen
        line_num = 0
        skipped_rows = 0
        for row in reader:
            if line_num not in row_to_delete:
                writer.writerow(row)
                pass
            else:
                skipped_rows += 1
            line_num += 1

    # Vorherige CSV-Datei entfernen
    os.remove(csv_file_path)

    # Temporäre Datei umbenennen, um die originale Datei zu ersetzen
    os.rename(temp_file_path, csv_file_path)


def update_file_paths(directory):
    # Überprüfen, ob das angegebene Verzeichnis existiert
    if not os.path.exists(directory):
        raise ValueError(f"Das Verzeichnis {directory} existiert nicht.")

    # Pfad zur CSV-Datei
    csv_file_path = os.path.join(directory, "labels.csv")

    # Überprüfen, ob die labels.csv Datei existiert
    if not os.path.isfile(csv_file_path):
        raise ValueError(f"Die Datei labels.csv wurde im Verzeichnis {directory} nicht gefunden.")

    # Einlesen der CSV-Datei
    df = pd.read_csv(csv_file_path)

    # Überprüfen, ob die erste Spalte existiert
    if df.columns.size < 1:
        raise ValueError("Die CSV-Datei enthält keine Spalten.")

    # Name der ersten Spalte
    first_column_name = df.columns[0]

    # Aktualisieren der Dateipfade in der ersten Spalte beginnend mit dem zweiten Element
    for i in range(len(df)):
        # Extrahieren des Dateinamens aus dem ursprünglichen Pfad
        _, filename = os.path.split(df[first_column_name][i])

        # Neuen Pfad zusammensetzen
        new_path = os.path.join(os.path.basename(directory), filename)

        # Neuen Pfad in der DataFrame aktualisieren
        df.at[i, first_column_name] = new_path

    # Zurück in CSV schreiben
    df.to_csv(csv_file_path, index=False)
    print(f"Die Pfade in der Datei {csv_file_path} wurden erfolgreich aktualisiert.")


def rename_first_column(csv_path):
    # Versuch, die CSV-Datei zu lesen
    try:
        df = pd.read_csv(csv_path)

        # Namen der vorhandenen Spalten
        columns = df.columns

        # Prüfe, ob die erste Spalte 'Filename' heißt
        if not columns[0] == 'Filename':
            # Umbenennen der ersten Spalte in 'Filename'
            df.rename(columns={columns[0]: 'Filename'}, inplace=True)

            # Speichere die geänderte Datei zurück
            df.to_csv(csv_path, index=False)
            print(f"Die erste Spalte wurde in 'Filename' umbenannt und gespeichert in {csv_path}")
        else:
            print(f"Die erste Spalte heißt bereits 'Filename'. Es wurden keine Änderungen vorgenommen.")

    except Exception as e:
        # Falls es einen Fehler gibt, drucke die Fehlermeldung
        print(f"Es gab einen Fehler beim Öffnen oder Bearbeiten der Datei: {e}")


def verify_csv(path):
    # Prüfen, ob der Pfad zu einer CSV-Datei führt
    if not path.endswith('.csv'):
        return False, "Der angegebene Pfad ist keine .csv Datei."

    # Prüfen, ob die Datei existiert
    if not os.path.isfile(path):
        return False, "Die Datei wurde nicht gefunden."

    try:
        # Laden der CSV-Datei
        data = pd.read_csv(path)
    except Exception as e:
        return False, f"Ein Fehler beim Laden der Datei ist aufgetreten: {e}"

    # Prüfen auf die korrekte Anzahl an Spalten
    expected_columns = ["Filename", "S_x", "S_y"]
    if data.shape[1] != len(expected_columns):
        return False, f"Die CSV-Datei sollte genau {len(expected_columns)} Spalten haben."

    # Prüfen auf die korrekte Benennung der Spalten
    if not all(column in data.columns for column in expected_columns):
        return False, "Nicht alle erforderlichen Spalten sind vorhanden oder korrekt benannt."

    return True,  # Die CSV-Datei ist korrekt formatiert und alle Spalten sind vorhanden.


def full_clean(directory_path):
    fiel_path, missing = check_if_file_exists(directory_path)
    delete_rows(fiel_path, missing)
    update_file_paths(directory_path)


# Haupt-Teil, um den Code über die Konsole aufrufen zu können.
# if __name__ == "__main__":
#     # Initialisieren des Argument-Parsers
#     parser = argparse.ArgumentParser(description='Cleans up labels in the specified directory.')
#
#     # Hinzufügen des 'directory_path'-Arguments
#     parser.add_argument('directory_path', type=str, help='The path to the directory containing label files to clean.')
#
#     # Parsen der Argumente
#     args = parser.parse_args()
#
#     # Aufrufen der 'full_clean'-Methode mit dem übergebenen Pfad
#     if verify_csv(args.directory_path):
#         full_clean(args.directory_path)

full_clean("C:\\Users\\Homebase\\Desktop\\training_data\\teapot_back_brown")
