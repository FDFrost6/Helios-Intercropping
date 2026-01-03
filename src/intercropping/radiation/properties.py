"""
Radiative properties configuration for camera imaging.

Sets reflectance and transmissivity values for all primitives based on
literature values (PROSPECT model for leaves, soil reflectance studies).
"""

from pyhelios import Context
from typing import List

from intercropping.config.constants import (
    SOIL_REFLECTANCE,
    LEAF_REFLECTANCE,
    LEAF_TRANSMISSIVITY,
)


def set_soil_properties(context: Context, uuid: int, bands: List[str]) -> None:
    """
    Set radiative properties for soil primitives.
    
    Uses literature values for dry brown agricultural soil:
    - Red: highest reflectance (brown color)
    - Green: middle reflectance
    - Blue: lowest reflectance
    - NIR: moderate reflectance
    
    Args:
        context: Helios Context
        uuid: UUID of soil primitive
        bands: List of radiation bands to configure
        
    Example:
        >>> set_soil_properties(context, ground_uuid, ["Red", "Green", "Blue"])
    """
    for band in bands:
        if band in SOIL_REFLECTANCE:
            context.setPrimitiveDataFloat(
                uuid, f"reflectivity_{band}", SOIL_REFLECTANCE[band]
            )
            context.setPrimitiveDataFloat(
                uuid, f"transmissivity_{band}", 0.0
            )


def set_leaf_properties(context: Context, uuid: int, bands: List[str]) -> None:
    """
    Set radiative properties for plant leaf primitives.
    
    Uses PROSPECT model typical values for healthy green vegetation:
    - Red: low reflectance (strong chlorophyll absorption)
    - Green: high reflectance (peak green reflection)
    - Blue: middle-low reflectance (some chlorophyll absorption)
    - NIR: very high reflectance AND transmissivity (leaf structure scattering)
    
    Args:
        context: Helios Context
        uuid: UUID of leaf primitive
        bands: List of radiation bands to configure
        
    Example:
        >>> set_leaf_properties(context, leaf_uuid, ["Red", "Green", "Blue", "NIR"])
    """
    for band in bands:
        if band in LEAF_REFLECTANCE:
            context.setPrimitiveDataFloat(
                uuid, f"reflectivity_{band}", LEAF_REFLECTANCE[band]
            )
        if band in LEAF_TRANSMISSIVITY:
            context.setPrimitiveDataFloat(
                uuid, f"transmissivity_{band}", LEAF_TRANSMISSIVITY[band]
            )


def apply_radiative_properties(
    context: Context,
    ground_uuid: int,
    bands: List[str] = None
) -> int:
    """
    Set realistic radiative properties for all primitives based on literature.
    
    For camera imaging with emission disabled:
    - reflectivity + transmissivity ≈ 1.0 (absorption ignored for reflectance-only mode)
    - Leaf properties from PROSPECT model typical values
    - Soil properties from literature (dry agricultural soil)
    
    Args:
        context: Helios Context
        ground_uuid: UUID of ground primitive
        bands: List of radiation bands (default: ["Red", "Green", "Blue", "NIR"])
        
    Returns:
        Number of primitives configured
        
    Example:
        >>> count = apply_radiative_properties(context, ground_uuid)
        >>> print(f"Configured {count} primitives")
    """
    if bands is None:
        bands = ["Red", "Green", "Blue", "NIR"]
    
    all_uuids = context.getAllUUIDs()
    
    for uuid in all_uuids:
        if uuid == ground_uuid:
            set_soil_properties(context, uuid, bands)
        else:
            set_leaf_properties(context, uuid, bands)
    
    return len(all_uuids)
