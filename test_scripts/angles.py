import numpy as np
import matplotlib.pyplot as plt
import random

PYSICAL_LED_ANGLES = [90.0, 89.07, 87.94, 86.8, 85.67, 84.54, 83.41, 82.27, 81.14, 80.01, 78.88, 77.75, 76.61, 75.48,
                      74.35, 73.22, 72.08, 70.95, 69.82, 68.69, 67.55, 66.42, 65.29, 64.16, 63.03, 61.89, 60.76, 59.63,
                      58.5, 57.36, 56.23, 55.1, 53.97, 52.84, 51.7, 50.57, 49.44, 48.31, 47.17, 46.04, 44.91, 43.78,
                      42.65, 41.51, 40.38, 39.25, 38.12, 36.98, 35.85, 34.72, 33.59, 32.45, 31.32, 30.19, 29.06, 27.93,
                      26.79, 25.66, 24.53, 23.4, 22.26, 21.13, 20.0, 18.87, 17.74, 16.6, 15.47, 14.34, 13.21,
                      12.07]  # Liste, die jedem LED-Index einen Winkel zuordnet


def create_sphere_points(num_lats, num_lons):
    # Berechne den Abstand zwischen den Breiten- und Längengraden
    lat_step = 180.0 / (num_lats)
    lon_step = 360.0 / num_lons

    # Initialisiere eine Liste, um die Punkte zu speichern
    points = []

    for i in range(0, num_lats + 1):
        lat = i * lat_step

        # Erstelle die Längengrade, startend mit 0 bis (360 - lon_step)
        for j in range(num_lons):
            lon = j * lon_step
            points.append((lat, lon))
    print(points)
    return points


def fibonacci_sphere(pts: int):
    # Berechnung der goldenen Winkel
    phi = np.pi * (3. - np.sqrt(5.))  # ~2.39996322972865332

    # Erstellen der Punkte
    points_to_return = []
    for i in range(pts):
        # y = 1 - (i / float(pts - 1)) * 2  # y geht von 1 bis -1 # das wäre der Ansatz für eine ganze Kugel
        y = i / float(pts - 1)  # y geht von 0 bis 1 für halbe Kugel

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
            if 0 <= elevation_deg < 89:
                # Hinzufügen des Punktes zur Liste
                points_to_return.append((round(azimuth_deg), round(elevation_deg)))

    return sorted(points_to_return)


# Diese Funktion nimmt einen Winkel als Argument und gibt den Index des nächstliegenden Lichtwinkels zurück.
def get_closest_light(angle):
    index_of_min = 0
    # Initialisiere die Variable 'distance' mit einem großen Wert als Startpunkt für den minimalen Abstand.
    distance = 1000

    # Initialisiere einen Zähler, um den aktuellen Index in der Schleife zu verfolgen.
    current_index = 0
    for light in PYSICAL_LED_ANGLES:
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
    #cartesian_points =  [point for point in cartesian_points if point[1] >= 0]
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


def get_angles(num_angles):
    angles_list = fibonacci_sphere(num_angles * 5)
    random_selection = random.sample(angles_list, num_angles)
    return_list = []
    for pair in random_selection:
        closest_light_index = get_closest_light(pair[1])
        return_list.append([pair[0], PYSICAL_LED_ANGLES[closest_light_index], closest_light_index])
    return sorted(return_list)




WRONG_ANGLES = [0.0, 1.3, 2.8, 4.3, 5.8, 7.3, 8.8, 10.3, 11.8, 13.3, 14.8, 16.3, 17.8, 19.4, 20.9, 22.4, 23.9,
                25.4, 26.9, 28.4, 29.9, 31.4, 32.9, 34.4, 35.9, 37.4, 38.9, 40.4, 41.9, 43.4, 44.9, 46.4, 47.9,
                49.4, 50.9, 52.4, 53.9, 55.4, 57.0, 58.5, 60.0, 61.5, 63.0, 64.5, 66.0, 67.5, 69.0, 70.5, 72.0,
                73.5, 75.0, 76.5, 78.0, 79.5, 81.0, 82.5, 84.0, 85.5, 87.0, 88.5, 90.0, 91.5, 93.0, 94.6, 96.1,
                97.6, 99.1, 100.6, 102.1, 103.6]  # Liste, die jedem LED-Index einen Winkel zuordnet


# all_points = fibonacci_sphere(100)
#
# visualize_3d(all_points)

vor = ((0.6 +0.3)/2 + 0.2)
nach = ((0.5+0.2)/2 + 0.2)
gesamt = (vor+nach)/2
delta = 0.3
ww= 0.5

print(vor)
print(nach)
print (ww+delta+gesamt)
