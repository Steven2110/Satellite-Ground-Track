import numpy as np
from typing import List

GM = 398600.4418  # Earth's gravitational parameter [km^3/s^2]
W = 7.292115e-5 # Earth's rotation rate [rad/s]
R = 6378 # Earth's radius [km]
TIME_STEPS = [0.01, 0.001, 0.0001]

class SatelliteConfig:
    def __init__(
        self,
        name: str,
        num_satellite: int,
        inclination: float, # degrees
        longitude_of_ascending_node: List[float], #degrees
        argument_pericenter: List[float], #degrees
        semi_major_axis: float, #km
        eccentricity: float
    ):
        self.satellite_name = name
        self.num_satellite = num_satellite
        self.inclination = inclination
        self.longitude_of_ascending_node = longitude_of_ascending_node
        self.argument_pericenter = argument_pericenter
        self.semi_major_axis = semi_major_axis
        self.eccentricity = eccentricity
        # Вычисляем период орбиты спутника и среднюю аномалию
        self.T = 2 * np.pi * np.sqrt(semi_major_axis**3/GM)
        self.mean_anomaly = 360 / self.T
        
    # Для представления в виде строки (в UI)
    def info(self):
        T_hours = int(self.T // 3600)
        T_minutes = int((self.T % 3600) // 60)
        T_seconds = self.T % 60
        return (f"Satellite system name: {self.satellite_name}\n"
                f"Number of satellites in system: {self.num_satellite} satellites\n"
                f"Semi-Major Axis (a): {self.semi_major_axis} km\n"
                f"Eccentricity (e): {self.eccentricity}\n"
                f"Inclination (i): {self.inclination}°\n"
                f"Longitude of Ascending Node (Ω): {', '.join(f'{Omega}°' for Omega in self.longitude_of_ascending_node)}\n"
                f"Argument of Pericenter (ω): {', '.join(f'{omega}°' for omega in self.argument_pericenter)}\n"
                f"Mean Anomaly (M0): {self.mean_anomaly}°\n"
                f"Orbital Period (T): {T_hours} hours {T_minutes} minutes {T_seconds:.2f} seconds\n\n")
    
     
        
# SATELLITES CONFIGURATION CONSTANTS        
"""
Galileo
- 27 satellites
"""
GALILEO = SatelliteConfig(
    name="Galileo",
    num_satellite=27,
    inclination=56,
    longitude_of_ascending_node=[0, 120, 240],
    argument_pericenter=[0, 40, 80, 120, 160, 200, 240, 280, 320],
    semi_major_axis=R + 23222,
    eccentricity=0
)


"""
TSIKADA
- 4 satellites
"""
TSIKADA = SatelliteConfig(
    name="Tsikada",
    num_satellite=4,
    inclination=83,
    longitude_of_ascending_node=[0, 180],
    argument_pericenter=[0],
    semi_major_axis=R + 1000,
    eccentricity=0
)


"""
NAVSAT
- 6 satellites
"""
NAVSAT = SatelliteConfig(
    name="NAVSAT",
    num_satellite=6,
    inclination=64.8,
    longitude_of_ascending_node=[0, 60, 120, 180, 240, 300],
    argument_pericenter=[0],
    semi_major_axis=R + 1000,
    eccentricity=0
)


"""
IRNSS
- 7 satellites in total
- 3 geostationary satellites
- 4 geosynchronous satellites
"""
IRNSS_GEOSTAT = SatelliteConfig(
    name="IRNSS Geostationary",
    num_satellite=3,
    inclination=0,
    longitude_of_ascending_node=[32.5, 83, 131.5],
    argument_pericenter=[0],
    semi_major_axis=42000,
    eccentricity=0
)

IRNSS_GEOSYNC = SatelliteConfig(
    name="IRNSS Geosynchronous",
    num_satellite=6,
    inclination=29,
    longitude_of_ascending_node=[55, 111.75],
    argument_pericenter=[0, 180],
    semi_major_axis=18753.1,
    eccentricity=0.63323
)


"""
BeiDou
- 35 satellites in total
- 5 geostationary satellites
- 3 inclined satellites
- 27 MEO satellites
"""
BEIDOU_GEO = SatelliteConfig(
    name="BeiDou Geostationary",
    num_satellite=5,
    inclination=0,
    longitude_of_ascending_node=[0, 72, 144, 216, 288],
    argument_pericenter=[0],
    semi_major_axis=42000,
    eccentricity=0
)

BEIDOU_INCLINED = SatelliteConfig(
    name="BeiDou Inclined",
    num_satellite=3,
    inclination=29,
    longitude_of_ascending_node=[0, 120, 240],
    argument_pericenter=[0],
    semi_major_axis=R + 35786,
    eccentricity=0
)

BEIDOU_MEDIUM = SatelliteConfig(
    name="BeiDou MEO",
    num_satellite=27,
    inclination=55,
    longitude_of_ascending_node=[0, 120, 240],
    argument_pericenter=[0],
    semi_major_axis=R + 21500,
    eccentricity=0
)


"""
GPS
- 24 satellites
"""
GPS = SatelliteConfig(
    name="GPS",
    num_satellite=24,
    inclination=55,
    longitude_of_ascending_node=[0, 60, 120, 180, 240, 300],
    argument_pericenter=[0, 90, 180, 270],
    semi_major_axis=R + 20200,
    eccentricity=0
)


"""
GLONASS
- 24 satellites
"""
GLONASS = SatelliteConfig(
    name="GLONASS",
    num_satellite=24,
    inclination=64.8,
    longitude_of_ascending_node=[0, 120, 240],
    argument_pericenter=[0, 45, 90, 135, 180, 225, 270, 315],
    semi_major_axis=R + 19100,
    eccentricity=0
)

"""
All satellite systems
"""
SATELLITES = {
    "Galileo": [GALILEO],
    "GPS": [GPS],
    "TSIKADA": [TSIKADA],
    "IRNSS": [IRNSS_GEOSTAT, IRNSS_GEOSYNC],
    "NAVSAT": [NAVSAT],
    "BeiDou": [BEIDOU_GEO, BEIDOU_INCLINED, BEIDOU_MEDIUM],
    "Glonass": [GLONASS]
}
