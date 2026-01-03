"""Radiation simulation modules for camera imaging and optical properties."""

from intercropping.radiation.properties import (
    apply_radiative_properties,
    set_soil_properties,
    set_leaf_properties,
)
from intercropping.radiation.solar import calculate_solar_position
from intercropping.radiation.imaging import (
    setup_radiation_camera,
    run_camera_simulation,
    save_camera_images,
)

__all__ = [
    "apply_radiative_properties",
    "set_soil_properties",
    "set_leaf_properties",
    "calculate_solar_position",
    "setup_radiation_camera",
    "run_camera_simulation",
    "save_camera_images",
]
