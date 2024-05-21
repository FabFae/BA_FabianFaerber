import json
import os
from ImageMaker import ImageMaker, move_counter_clockwise, move_down
from PyQt5 import QtWidgets, uic


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.positions = None
        uic.loadUi('/home/pi/BA/src/UiPhotoSession.ui', self)

        # setup UI
        self.update_info()

        # Verbindung herstellen
        self.browser_button.clicked.connect(self.open_file_dialog)
        self.load_settings_button.clicked.connect(self.read_json_file)
        self.height_levels_spin.valueChanged.connect(self.update_info)
        self.number_of_images_spin.valueChanged.connect(self.update_info)
        self.table_rotations_spin.valueChanged.connect(self.update_info)
        self.start_button.clicked.connect(self.start)
        self.counter_clockwise_button.clicked.connect(self.move_counter_clockwise)
        self.down_button.clicked.connect(self.move_down)
        self.table_rotations_spin.valueChanged.connect(self.validate_table_rotations)

    def validate_table_rotations(self):
        # Die gültigen Werte, die table_rotations annehmen darf
        valid_values = {2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36, 40, 45, 60, 72, 90, 120, 180, 360}

        # Der aktuelle Wert von table_rotations_spin
        current_value = self.table_rotations_spin.value()

        # Wenn der aktuelle Wert ungültig ist, zeigen Sie ein Popup an und setzen Sie den Wert zurück auf 1
        if current_value not in valid_values:
            # Erstellen des Pop-up-Fensters mit Warnung
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText(f"Ungültiger Wert: {current_value}.")
            msg.setInformativeText("Der Wert muss\n2, 3, 4, 5, 6, 8, 9, 10, 12,\n15, 18, 20, 24, 30, 36, 40, 45,\n"
                                   "60, 72, 90, 120, 180 oder 360 sein.")
            msg.setWindowTitle("Ungültiger Wert")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()  # Das Pop-up-Fenster wird hier angezeigt

            # Zurücksetzen des Werts von table_rotations_spin auf 1
            self.table_rotations_spin.blockSignals(True)  # Verhindere Signal beim Setzen des Werts
            self.table_rotations_spin.setValue(1)
            self.table_rotations_spin.blockSignals(False)  # Erlaube Signale wieder

    def move_counter_clockwise(self):
        # im = ImageMaker()
        move_counter_clockwise(self.counter_clockwise_spin.value())

    def move_down(self):
        # im = ImageMaker()
        move_down(self.down_spin.value())

    def open_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                             "Open File", "",
                                                             "All Files (*);;Text Files (*.txt);;Python Files (*.py)",
                                                             options=options)
        if file_name:
            self.file_path_text.setText(file_name)

    def update_info(self):
        self.update_total_images()
        self.update_time_estimation()

    def update_total_images(self):
        height_levels = self.height_levels_spin.value()
        number_of_images = self.number_of_images_spin.value()
        table_rotations = self.table_rotations_spin.value()
        total = height_levels * number_of_images * table_rotations
        self.total_images_text.setText(str(total))

    def update_time_estimation(self):
        sec_img = 2.2
        sec_rotation = 10
        sec_roll_back = 20
        sec_back_to_zero = sec_rotation + sec_roll_back
        sec_go_up = 10
        num_images = self.number_of_images_spin.value() * self.table_rotations_spin.value() * self.height_levels_spin.value()
        sec_total = (num_images * sec_img * self.table_rotations_spin.value() + sec_back_to_zero + sec_go_up)

        m, s = divmod(sec_total, 60)
        h, m = divmod(m, 60)
        self.time_estimation_text.setText(f"{int(h)}h, {int(m)}min, {int(s)}sec")

    def read_json_file(self):
        # Get the file path from QLineEdit
        file_to_load_path = self.file_path_text.text()
        try:
            with open(file_to_load_path, 'r',
                      encoding='utf-8') as f:  # Sicherstellen, dass die Datei korrekt geöffnet und geschlossen wird
                file_data = (json.load(f))  # JSON-Daten in ein Python-Dict umwandeln

                self.folder_path_text.setText(os.path.dirname(file_to_load_path))

                self.number_of_images_spin.setValue(file_data["num_samples"])
                self.start_image_spin.setValue(file_data["start_index"])
                self.exposure_spin.setValue(file_data["exposure"])
                self.img_size_spin.setValue(file_data["img_size"])
                self.table_rotations_spin.setValue(file_data["table_rotations"])
                self.height_levels_spin.setValue(file_data["height_levels"])
                self.starting_height_spin.setValue(file_data["starting_height"])
                self.positions = file_data["positions"]

                # prüfen ob start_index das letzte Bild in der horizontalen war
                if file_data["start_index"] == file_data["num_samples"]:
                    self.start_image_spin.setValue(0)
                    if file_data["starting_height"] < self.height_levels_spin.setValue(file_data["height_levels"]):
                        self.starting_height_spin.setValue(file_data["starting_height"])
                    else:
                        self.starting_height_spin.setValue(file_data["starting_height"])
            self.update_info()

        except FileNotFoundError:
            print("Die Datei wurde nicht gefunden: ", file_to_load_path)
            return None
        except json.JSONDecodeError:
            print("Fehler beim Parsen der JSON-Datei: ", file_to_load_path)
            return None
        except Exception as e:
            print(f"Ein unbekannter Fehler ist aufgetreten: {e}")
            return None

    def start(self):
        if self.file_path_text.text():
            folder_path = os.path.dirname(self.file_path_text.text())
            ps = ImageMaker(folder_path=folder_path,
                            num_samples=self.number_of_images_spin.value(),
                            start_index=self.start_image_spin.value(),
                            exposure_time=self.exposure_spin.value(),
                            img_size=self.img_size_spin.value(),
                            table_rotations=self.table_rotations_spin.value(),
                            height_levels=self.height_levels_spin.value(),
                            starting_height=self.starting_height_spin.value(),
                            positions=self.positions)
        else:
            ps = ImageMaker(num_samples=self.number_of_images_spin.value(),
                            start_index=self.start_image_spin.value(),
                            exposure_time=self.exposure_spin.value(),
                            img_size=self.img_size_spin.value(),
                            table_rotations=self.table_rotations_spin.value(),
                            height_levels=self.height_levels_spin.value(),
                            starting_height=self.starting_height_spin.value(),
                            positions=self.positions)

        ps.start()


def main():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
