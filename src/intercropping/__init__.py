"""
Helios Intercropping Pipeline

A modular pipeline for generating photorealistic RGB/multispectral camera images
with semantic segmentation masks for faba bean and wheat intercropping research
using PyHelios.
"""

__version__ = "1.0.0"
__author__ = "Nelson"

from intercropping.config.constants import (
    BEAN_EMERGENCE_RATE,
    WHEAT_EMERGENCE_RATE,
    SPECIES_GROUND,
    SPECIES_BEAN,
    SPECIES_WHEAT,
)

__all__ = [
    "BEAN_EMERGENCE_RATE",
    "WHEAT_EMERGENCE_RATE",
    "SPECIES_GROUND",
    "SPECIES_BEAN",
    "SPECIES_WHEAT",
]
