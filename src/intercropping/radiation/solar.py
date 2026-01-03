"""
Solar position calculation utilities.

Wraps PyHelios SolarPosition plugin for sun ephemeris calculations.
"""

import numpy as np
from pyhelios import Context, SolarPosition
from typing import Tuple, Dict


def calculate_solar_position(
    context: Context,
    utc_offset: int,
    latitude: float,
    longitude: float
) -> Dict[str, float]:
    """
    Calculate solar position and irradiance for current scene date/time.
    
    Uses PyHelios SolarPosition plugin to compute:
    - Sun direction vector
    - Sun elevation angle (degrees)
    - Sun azimuth angle (degrees)
    - Solar flux (W/m²)
    
    Args:
        context: Helios Context (must have date/time set)
        utc_offset: UTC offset in hours (e.g., 2 for UTC+2)
        latitude: Latitude in degrees north
        longitude: Longitude in degrees east
        
    Returns:
        Dictionary with solar parameters:
        - 'direction': Sun direction vector (tuple)
        - 'elevation_deg': Sun elevation in degrees
        - 'azimuth_deg': Sun azimuth in degrees
        - 'flux': Solar flux in W/m²
        - 'zenith_deg': Sun zenith angle in degrees (90 - elevation)
        
    Example:
        >>> context.setDate(2022, 6, 14)
        >>> context.setTime(12, 0)
        >>> solar_info = calculate_solar_position(context, 2, 50.865, 7.134)
        >>> print(f"Sun elevation: {solar_info['elevation_deg']:.1f}°")
    """
    with SolarPosition(context, utc_offset, latitude, longitude) as sun:
        sun_direction = sun.getSunDirectionVector()
        sun_elevation_deg = np.degrees(sun.getSunElevation())
        sun_azimuth_deg = np.degrees(sun.getSunAzimuth())
        
        # Calculate solar flux (atmospheric parameters for clear day)
        pressure_Pa = 101325  # Sea level pressure
        temperature_K = 293.15  # 20°C
        humidity = 0.6  # 60% relative humidity
        turbidity = 0.05  # Clear atmosphere
        
        solar_flux = sun.getSolarFlux(pressure_Pa, temperature_K, humidity, turbidity)
        
        return {
            'direction': (sun_direction.x, sun_direction.y, sun_direction.z),
            'elevation_deg': sun_elevation_deg,
            'azimuth_deg': sun_azimuth_deg,
            'zenith_deg': 90.0 - sun_elevation_deg,
            'flux': solar_flux,
        }
