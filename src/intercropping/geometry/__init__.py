"""Geometry modules for scene construction."""

from intercropping.geometry.soil import create_soil_plane
from intercropping.geometry.plants import generate_intercrop_positions, build_plants
from intercropping.geometry.camera import calculate_nadir_camera_height

__all__ = [
    "create_soil_plane",
    "generate_intercrop_positions",
    "build_plants",
    "calculate_nadir_camera_height",
]
