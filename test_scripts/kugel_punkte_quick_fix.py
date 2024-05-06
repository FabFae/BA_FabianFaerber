import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_points_on_sphere(num_azimuthal, elevation_angle):
    # Konvertieren der Elevation in Radianten
    elevation_radians = np.deg2rad(elevation_angle)

    # Berechnen der Winkel zwischen den Punkten basierend auf der Anzahl der Azimut-Winkel
    azimuth_increment = 360 / num_azimuthal
    azimuth_angles = np.arange(0, 360, azimuth_increment)

    # Erstellen einer Figure und einer 3D-Achse
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Berechnen der Positionen der Punkte
    for azimuth_deg in azimuth_angles:
        azimuth_rad = np.deg2rad(azimuth_deg)
        x = np.cos(elevation_radians) * np.cos(azimuth_rad)
        y = np.cos(elevation_radians) * np.sin(azimuth_rad)
        z = np.sin(elevation_radians)
        ax.scatter(x, y, z)  # Hinzufügen des Punktes zur Visualisierung

    # Setzen der Achsengleichheit
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1, 1])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Anzeigen der Visualisierung
    plt.show()

# Beispielaufruf der Funktion
plot_points_on_sphere(10, 45)