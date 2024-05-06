import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def fibonacci_sphere(samples: int):
    # Berechnung der goldenen Winkel
    phi = np.pi * (3. - np.sqrt(5.))  # ~2.39996322972865332

    # Erstellen der Punkte
    points_to_return = []
    for i in range(samples):
        y = 1 - (i / float(samples - 1)) * 2  # y geht von 1 bis -1
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

    return points_to_return


def spherical_to_cartesian(azimuth_deg, elevation_deg):
    azimuth_rad = np.radians(azimuth_deg)
    elevation_rad = np.radians(elevation_deg)
    x = np.cos(azimuth_rad) * np.cos(elevation_rad)
    y = np.sin(azimuth_rad) * np.cos(elevation_rad)
    z = np.sin(elevation_rad)
    return x, y, z


def visualize_distribution(pts):
    # Daten extrahieren
    azimuths, elevations = zip(*pts)

    # Bins für das Histogramm
    azimuth_bins = np.arange(-170, 170, 1)
    elevation_bins = np.arange(0, 85, 1)

    # Histogramm der Daten erstellen
    azimuth_hist, _ = np.histogram(azimuths, bins=azimuth_bins)
    elevation_hist, _ = np.histogram(elevations, bins=elevation_bins)

    # Plots erstellen
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))

    # Azimut Plot
    axs[0].bar(azimuth_bins[:-1], azimuth_hist, width=5, align='edge')
    axs[0].set_title("Verteilung der Azimutwinkel")
    axs[0].set_xlabel("Azimutwinkel (Grad)")
    axs[0].set_ylabel("Anzahl der Punkte")

    # Elevation Plot
    axs[1].bar(elevation_bins[:-1], elevation_hist, width=5, align='edge')
    axs[1].set_title("Verteilung der Elevationswinkel")
    axs[1].set_xlabel("Elevationswinkel (Grad)")
    axs[1].set_ylabel("Anzahl der Punkte")

    # Layout anpassen und anzeigen
    plt.tight_layout()
    plt.show()


def visualize_3d(pts):
    # Konvertieren Sie die Punkte in kartesische Koordinaten
    cartesian_points = [spherical_to_cartesian(azim, elev) for azim, elev in pts]

    # Entpacken der kartesischen Koordinaten
    x_vals, y_vals, z_vals = zip(*cartesian_points)

    # 3D Plot erstellen
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Punkte zu dem Plot hinzufügen
    ax.scatter(x_vals, y_vals, z_vals)

    # Setzen der Aspekte, sodass die Skalierung aller Achsen gleich bleibt
    ax.set_box_aspect([np.ptp(x_vals), np.ptp(y_vals), np.ptp(z_vals)])

    # Titel hinzufügen
    ax.set_title('Verteilung der Punkte')

    # Anzeigen des Plots
    plt.show()


# Anzahl der Punkte, die erzeugt werden sollen
num_points = 300
points = fibonacci_sphere(num_points)
print(f"Anzahl Punkte auf der Kugel: {len(points)}")
#visualize_distribution(points)
visualize_3d(points)
for az, ele in points:
    if ele > 80:
        print(f"{az}, {ele}")
