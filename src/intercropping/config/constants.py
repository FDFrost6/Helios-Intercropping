"""
Global constants for the intercropping pipeline.

Includes:
- Realistic germination/establishment rates (field emergence)
- Species labels for segmentation
- Physical constants
"""

# Realistic germination/establishment rates (field emergence)
# Based on literature (Cook & Veseth 1991, Lafond et al. 2008)
BEAN_EMERGENCE_RATE = 0.875  # 87.5% (85-90% literature range)
WHEAT_EMERGENCE_RATE = 0.80  # 80% (75-85% literature range)

# Species labels for segmentation
SPECIES_GROUND = 0
SPECIES_BEAN = 1
SPECIES_WHEAT = 2

# Species names mapping
SPECIES_NAMES = {
    SPECIES_GROUND: "ground",
    SPECIES_BEAN: "bean",
    SPECIES_WHEAT: "wheat",
}

# Plant part labels for segmentation masks
PLANT_PART_GROUND = "ground"
PLANT_PART_BEAN = "bean"
PLANT_PART_WHEAT = "wheat"

# Radiation band wavelength ranges (nm)
BAND_WAVELENGTHS = {
    "Red": (620, 750),
    "Green": (495, 570),
    "Blue": (450, 495),
    "NIR": (750, 1400),
}

# Solar irradiance values (W/m²) for balanced color rendering
SOLAR_IRRADIANCE = {
    "Red": 900.0,
    "Green": 900.0,
    "Blue": 800.0,
    "NIR": 1000.0,
}

# Diffuse skylight values (W/m²)
DIFFUSE_IRRADIANCE = {
    "Red": 180.0,
    "Green": 180.0,
    "Blue": 160.0,
    "NIR": 200.0,
}

# Soil reflectance properties (dry brown agricultural soil)
SOIL_REFLECTANCE = {
    "Red": 0.35,
    "Green": 0.25,
    "Blue": 0.18,
    "NIR": 0.38,
}

# Leaf reflectance properties (healthy green vegetation)
# Based on PROSPECT model typical values
LEAF_REFLECTANCE = {
    "Red": 0.10,    # Low (strong chlorophyll absorption)
    "Green": 0.35,  # High (strong green reflection)
    "Blue": 0.15,   # Middle-low (some chlorophyll absorption)
    "NIR": 0.50,    # Very high (leaf structure scattering)
}

# Leaf transmissivity properties
LEAF_TRANSMISSIVITY = {
    "Red": 0.05,
    "Green": 0.15,
    "Blue": 0.08,
    "NIR": 0.40,  # Very high transmission in NIR
}
