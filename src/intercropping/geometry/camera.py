"""
Camera geometry calculations for scene imaging.

Provides utilities for calculating camera positions and parameters for
overhead (nadir) imaging of intercropping plots.
"""

import numpy as np
from typing import Tuple


def calculate_nadir_camera_height(
    plot_width: float,
    plot_length: float,
    fov_degrees: float = 60.0,
    margin_factor: float = 1.1
) -> float:
    """
    Calculate camera height for nadir view to capture entire plot.
    
    Computes the height needed for a camera to capture the entire plot in a
    nadir (overhead) view, given the field of view. Uses plot diagonal to
    ensure full coverage with a safety margin.
    
    Args:
        plot_width: Plot width in meters
        plot_length: Plot length in meters
        fov_degrees: Camera field of view in degrees (default: 60°)
        margin_factor: Safety margin multiplier (default: 1.1 = 10% margin)
        
    Returns:
        Camera height in meters above ground (Z=0)
        
    Example:
        >>> height = calculate_nadir_camera_height(1.0, 1.0)
        >>> print(f"Camera height: {height:.2f}m")
        Camera height: 1.60m
        
    Mathematical Derivation:
        For a camera to capture a rectangular plot, we need to ensure the
        diagonal fits within the field of view:
        
        diagonal = sqrt(width² + length²)
        height = (diagonal / 2) / tan(fov / 2)
        
        A margin factor is applied for safety.
    """
    # Use diagonal of plot to ensure full coverage
    diagonal = np.sqrt(plot_width**2 + plot_length**2)
    
    # Calculate height needed to capture diagonal with given FOV
    # h = (diagonal / 2) / tan(fov/2)
    fov_rad = np.radians(fov_degrees)
    height = (diagonal / 2.0) / np.tan(fov_rad / 2.0)
    
    # Add margin for safety
    height *= margin_factor
    
    return height


def calculate_camera_position(
    plot_width: float,
    plot_length: float,
    margin: float = 0.0,
    fov_degrees: float = 60.0
) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    """
    Calculate nadir camera position and lookat point.
    
    Args:
        plot_width: Plot width in meters
        plot_length: Plot length in meters
        margin: Extra margin around plot in meters
        fov_degrees: Camera field of view in degrees
        
    Returns:
        Tuple of ((camera_x, camera_y, camera_z), (lookat_x, lookat_y, lookat_z))
        
    Example:
        >>> position, lookat = calculate_camera_position(1.0, 1.0, margin=0.3)
        >>> print(f"Camera at {position}, looking at {lookat}")
    """
    soil_width = plot_width + 2 * margin
    soil_length = plot_length + 2 * margin
    
    # Camera height above plot
    camera_height = calculate_nadir_camera_height(soil_width, soil_length, fov_degrees)
    
    # Center of plot (also the lookat point)
    center_x = soil_width / 2
    center_y = soil_length / 2
    center_z = 0.0
    
    # Camera directly above center
    camera_position = (center_x, center_y, camera_height)
    lookat_point = (center_x, center_y, center_z)
    
    return camera_position, lookat_point


def calculate_oblique_camera_position(
    plot_width: float,
    plot_length: float,
    margin: float = 0.0,
    angle_multiplier: float = 1.2,
    height_multiplier: float = 1.0
) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    """
    Calculate oblique (angled) camera position for artistic/visualization views.
    
    Args:
        plot_width: Plot width in meters
        plot_length: Plot length in meters
        margin: Extra margin around plot in meters
        angle_multiplier: Horizontal distance multiplier (larger = more distant)
        height_multiplier: Vertical distance multiplier (larger = higher view)
        
    Returns:
        Tuple of ((camera_x, camera_y, camera_z), (lookat_x, lookat_y, lookat_z))
    """
    soil_width = plot_width + 2 * margin
    soil_length = plot_length + 2 * margin
    max_dim = max(plot_width, plot_length)
    
    # Lookat point (center of plot, slightly above ground)
    lookat_x = soil_width / 2
    lookat_y = soil_length / 2
    lookat_z = 0.4  # Slightly above ground
    
    # Camera position (offset diagonally)
    camera_x = lookat_x + max_dim * angle_multiplier
    camera_y = lookat_y + max_dim * angle_multiplier
    camera_z = max_dim * height_multiplier
    
    camera_position = (camera_x, camera_y, camera_z)
    lookat_point = (lookat_x, lookat_y, lookat_z)
    
    return camera_position, lookat_point
