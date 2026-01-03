"""
Soil plane geometry creation with texture support.

Creates textured soil with ground clipping prevention for realistic plant growth.
"""

import numpy as np
from pyhelios import Context
from pyhelios.types import vec3, vec2, RGBcolor, SphericalCoord, int2
from typing import Tuple

from intercropping.utils.texture_utils import get_builtin_texture_path


def create_soil_plane(
    context: Context,
    width: float,
    length: float,
    soil_texture: str = "dirt.jpg",
    subdivisions: int = 30,
    margin: float = 0.3
) -> Tuple[int, float]:
    """
    Create textured soil with ground clipping prevention.
    
    Creates a ground obstacle at Z=0.0 to prevent plants growing below ground,
    following PyHelios Pattern 3 (obstacle at Z=0, avoidance_distance prevents
    downward growth).
    
    Args:
        context: Helios Context instance
        width: Plot width in meters
        length: Plot length in meters
        soil_texture: Name of built-in texture file (default: "dirt.jpg")
        subdivisions: Number of subdivisions for tiled soil
        margin: Extra margin around plot in meters
        
    Returns:
        Tuple of (ground_uuid, margin) where ground_uuid is the obstacle UUID
        
    Example:
        >>> with Context() as ctx:
        ...     ground_uuid, margin = create_soil_plane(ctx, 1.0, 1.0)
        ...     print(f"Ground UUID: {ground_uuid}")
    """
    soil_color = RGBcolor(0.35, 0.25, 0.18)  # Brown soil color
    
    soil_width = width + 2 * margin
    soil_length = length + 2 * margin
    
    # Create ground obstacle at Z=0.0 to prevent plants growing below ground
    # Per Pattern 3: obstacle at Z=0, avoidance_distance prevents downward growth
    ground_uuid = context.addPatch(
        center=vec3(soil_width / 2, soil_length / 2, 0.0),
        size=vec2(soil_width, soil_length),
        rotation=SphericalCoord(1, 0, 0),
        color=soil_color
    )
    
    # Get built-in texture path
    texture_path = get_builtin_texture_path(soil_texture)
    
    if texture_path:
        # Create textured ground using triangles slightly above obstacle to avoid z-fighting
        # Counter-clockwise winding for upward-facing normals
        vertices = np.array([
            [0, 0, 0.001],
            [soil_width, 0, 0.001],
            [soil_width, soil_length, 0.001],
            [0, soil_length, 0.001]
        ], dtype=np.float32)
        
        # Counter-clockwise triangles facing up
        faces = np.array([
            [0, 2, 1],
            [0, 3, 2]
        ], dtype=np.int32)
        
        # UV coordinates (tile texture)
        texture_repeat = 2.0  # Number of times to repeat texture
        uv_coords = np.array([
            [0, 0],
            [texture_repeat, 0],
            [texture_repeat, texture_repeat],
            [0, texture_repeat]
        ], dtype=np.float32)
        
        try:
            context.addTrianglesFromArraysTextured(vertices, faces, uv_coords, texture_path)
            print(f"  ✓ Textured soil created: {soil_texture}")
        except Exception as e:
            print(f"  ⚠ Could not create textured soil: {e}")
            print(f"  ⚠ Using plain color fallback")
            context.addTile(
                center=vec3(soil_width / 2, soil_length / 2, 0.0),
                size=vec2(soil_width, soil_length),
                rotation=SphericalCoord(1, 0, 0),
                subdiv=int2(subdivisions, subdivisions),
                color=soil_color
            )
    else:
        # Fallback to plain tile
        context.addTile(
            center=vec3(soil_width / 2, soil_length / 2, 0.0),
            size=vec2(soil_width, soil_length),
            rotation=SphericalCoord(1, 0, 0),
            subdiv=int2(subdivisions, subdivisions),
            color=soil_color
        )
        print(f"  ✓ Plain soil created")
    
    return ground_uuid, margin
