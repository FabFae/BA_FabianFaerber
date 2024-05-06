import random

import numpy as np
import heapq

PHYSICAL_LED_ANGLES = [90.0, 89.07, 87.94, 86.8, 85.67, 84.54, 83.41, 82.27, 81.14, 80.01, 78.88, 77.75, 76.61, 75.48,
                       74.35, 73.22, 72.08, 70.95, 69.82, 68.69, 67.55, 66.42, 65.29, 64.16, 63.03, 61.89, 60.76, 59.63,
                       58.5, 57.36, 56.23, 55.1, 53.97, 52.84, 51.7, 50.57, 49.44, 48.31, 47.17, 46.04, 44.91, 43.78,
                       42.65, 41.51, 40.38, 39.25, 38.12, 36.98, 35.85, 34.72, 33.59, 32.45, 31.32, 30.19, 29.06, 27.93,
                       26.79, 25.66, 24.53, 23.4, 22.26, 21.13, 20.0, 18.87, 17.74, 16.6, 15.47, 14.34, 13.21,
                       12.07]  # Liste, die jedem LED-Index einen Winkel zuordnet


def fibonacci_sphere(num_points: int):
    pts = int(num_points * 1.5)

    # Berechnung des Goldenen Winkels
    phi = np.pi * (3. - np.sqrt(5.))  # Golden Ratio etwa 137.507764 Grad

    points_to_return = []
    for i in range(pts):
        y = i / float(pts - 1)  # y geht von 0 bis 1 für halbe Kugel
        radius = np.sqrt(1 - y ** 2)  # radius im Zylinder

        theta = phi * i  # Goldenes Winkelinkrement

        x = np.cos(theta) * radius
        z = np.sin(theta) * radius

        # Umrechnung von kartesischen Koordinaten in sphärische Koordinaten
        azimuth = np.arctan2(z, x)
        elevation = np.arcsin(y)

        points_to_return.append((np.degrees(azimuth), np.degrees(elevation)))
        print(f"points on sphere: {len(points_to_return)}")
    return points_to_return


def spherical_cosine_law_distance(p1, p2):
    # Umrechnung von Grad in Radianten
    lat1, lon1 = np.radians(p1)
    lat2, lon2 = np.radians(p2)

    # Sphärischer Kosinussatz
    return np.arccos(np.sin(lat1) * np.sin(lat2) +
                     np.cos(lat1) * np.cos(lat2) * np.cos(lon1 - lon2))


def find_smallest_angle(num_points: int):
    points = fibonacci_sphere(num_points)
    smallest_angles = []

    for i, point in enumerate(points):
        distances_heap = []
        for j, other_point in enumerate(points):
            if i != j:
                distance = spherical_cosine_law_distance(point, other_point)
                if len(distances_heap) < 10:
                    heapq.heappush(distances_heap,
                                   -distance)  # Negative, weil wir maximale Werte aus der Heapspeicher entfernen möchten
                else:
                    heapq.heappushpop(distances_heap, -distance)

        # Heapspeicher enthält die größten Abstände also negieren wir den Wert und konvertieren zu Grad
        smallest_angles.append(np.degrees(-distances_heap[0]))

    return smallest_angles


# Konvertiert sphärische Koordinaten (Phi: Azimutwinkel, Theta = Elevationswinkel) in stereografische Koordinaten
def spherical_to_stereographic(phi, theta, r=1):
    m = 2 * r * np.tan(np.radians((90 - theta) / 2))
    sy = m * np.sin(np.radians(phi))
    sx = m * np.cos(np.radians(phi))
    return sx, sy


def get_angles(num_pts):
    points = fibonacci_sphere(num_pts)
    # points = random.sample(angles_list, num_angles)
    return_list = []
    for pair in points:
        closest_light_index = get_closest_light(pair[1])
        return_list.append([pair[0], PHYSICAL_LED_ANGLES[closest_light_index], closest_light_index])
    return sorted(return_list)


def get_closest_light(angle: int):
    index_of_min = 0
    # Initialisiere die Variable 'distance' mit einem großen Wert als Startpunkt für den minimalen Abstand.
    distance = 1000

    # Initialisiere einen Zähler, um den aktuellen Index in der Schleife zu verfolgen.
    current_index = 0
    for light in PHYSICAL_LED_ANGLES:
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


num_points = 935
# Liste der kleinsten Winkel zu den nächsten 10 Nachbarn für alle Punkte finden
smallest_angles = find_smallest_angle(num_points)
print(min(smallest_angles))
