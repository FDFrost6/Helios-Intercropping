"""
Default parameter values for the intercropping pipeline.

These can be overridden via command-line arguments or programmatic configuration.
"""

# Plot dimensions
DEFAULT_PLOT_WIDTH = 1.0  # meters
DEFAULT_PLOT_LENGTH = 1.0  # meters
DEFAULT_N_ROWS = 4
DEFAULT_ROW_SPACING = 0.21  # meters

# Sowing densities
DEFAULT_BEAN_DENSITY = 36  # seeds/m²
DEFAULT_WHEAT_DENSITY = 0  # seeds/m²

# Plant age parameters
DEFAULT_INITIAL_AGE = 5.0  # days (plants start young)
DEFAULT_GROWTH_DAYS = 40  # days

# Collision avoidance parameters (soft collision mode)
DEFAULT_COLLISION_PARAMS = {
    "view_half_angle_deg": 70.0,  # Perception cone half-angle
    "look_ahead_distance": 0.08,   # meters
    "sample_count": 256,           # Ray samples for collision detection
    "inertia_weight": 0.3,         # Growth inertia (0-1)
    "ground_avoidance_distance": 0.1,  # meters
    "enable_obstacle_pruning": True,
    "enable_fruit_adjustment": True,
    "include_internodes": True,
    "include_leaves": True,
    "include_petioles": False,  # Exclude for performance
    "include_flowers": False,
    "include_fruit": False,
}

# Camera parameters
DEFAULT_CAMERA_PARAMS = {
    "type": "rgb",  # "rgb" or "multispectral"
    "resolution": (1024, 1024),  # width, height in pixels
    "fov": 60.0,  # Field of view in degrees
    "lens_diameter": 0.0,  # Pinhole camera (infinite depth of field)
    "antialiasing_samples": 100,  # High AA for sharp edges
}

# Radiation simulation parameters
DEFAULT_RADIATION_PARAMS = {
    "scattering_depth": 4,  # Multiple bounces through canopy
    "direct_ray_count": 2000,
    "diffuse_ray_count": 5000,
}

# Solar position parameters (PhenoRoam reference: June 14, 2022, Campus Klein-Altendorf)
DEFAULT_SOLAR_PARAMS = {
    "date": "2022-06-14",
    "time": "12:00",
    "latitude": 50.865,  # Campus Klein-Altendorf, Germany
    "longitude": 7.134,
    "utc_offset": 2,
}

# Rendering parameters
DEFAULT_RENDERING_PARAMS = {
    "width": 1920,
    "height": 1080,
    "aa_samples": 8,
    "light_intensity": 1.5,
    "lighting_model": "phong_shadowed",
}

# Soil parameters
DEFAULT_SOIL_PARAMS = {
    "texture": "dirt.jpg",
    "subdivisions": 30,
    "margin": 0.3,  # meters (extra margin around plot)
}

# Sky parameters
DEFAULT_SKY_PARAMS = {
    "use_dome": False,
    "texture": "SkyDome_clouds.jpg",
}

# Export parameters
DEFAULT_EXPORT_PARAMS = {
    "save": False,
    "output_dir": "output",
    "export_ply": True,
    "export_obj": True,
    "save_metadata": True,
}

# Segmentation parameters
DEFAULT_SEGMENTATION_PARAMS = {
    "enabled": False,
    "object_class_id": 1,
    "primitive_data_field": "plant_part",
}

# Random seed
DEFAULT_SEED = 42
