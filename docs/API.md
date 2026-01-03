# API Reference

Complete API documentation for the Helios Intercropping Pipeline modules.

## Table of Contents

- [Configuration](#configuration)
- [Core](#core)
- [Geometry](#geometry)
- [Radiation](#radiation)
- [Segmentation](#segmentation)
- [I/O](#io)
- [Visualization](#visualization)
- [Utilities](#utilities)

---

## Configuration

### `intercropping.config.constants`

Global constants including emergence rates, species IDs, and physical parameters.

**Constants:**
- `BEAN_EMERGENCE_RATE` (float): 0.875 (87.5%)
- `WHEAT_EMERGENCE_RATE` (float): 0.80 (80%)
- `SPECIES_GROUND` (int): 0
- `SPECIES_BEAN` (int): 1
- `SPECIES_WHEAT` (int): 2
- `BAND_WAVELENGTHS` (dict): Wavelength ranges for radiation bands
- `SOLAR_IRRADIANCE` (dict): Solar flux values (W/m²)
- `SOIL_REFLECTANCE` (dict): Soil reflectance by band
- `LEAF_REFLECTANCE` (dict): Leaf reflectance by band

### `intercropping.config.defaults`

Default parameter values for scene generation.

**Parameters:**
- `DEFAULT_PLOT_WIDTH`: 1.0m
- `DEFAULT_BEAN_DENSITY`: 36 seeds/m²
- `DEFAULT_GROWTH_DAYS`: 40 days
- `DEFAULT_COLLISION_PARAMS`: Collision avoidance settings
- `DEFAULT_CAMERA_PARAMS`: Camera configuration
- `DEFAULT_SOLAR_PARAMS`: Solar position defaults

---

## Core

### `intercropping.core.context`

Helios context creation and datetime configuration.

#### `setup_helios_context(year, month, day, hour, minute)`

Create configured PyHelios Context.

**Parameters:**
- `year` (int): Year (e.g., 2022)
- `month` (int): Month (1-12)
- `day` (int): Day (1-31)
- `hour` (int): Hour (0-23)
- `minute` (int): Minute (0-59)

**Returns:**
- `Context`: Configured Helios Context

**Example:**
```python
context = setup_helios_context(2022, 6, 14, 12, 0)
```

#### `parse_date_time(date_str, time_str)`

Parse date/time strings.

**Parameters:**
- `date_str` (str): "YYYY-MM-DD"
- `time_str` (str): "HH:MM"

**Returns:**
- `tuple`: (year, month, day, hour, minute)

### `intercropping.core.collision`

Collision avoidance configuration.

#### `setup_collision_avoidance(plant_architecture, view_half_angle_deg=70.0, ...)`

Configure soft collision avoidance.

**Parameters:**
- `plant_architecture` (PlantArchitecture): PA instance
- `view_half_angle_deg` (float): Perception cone half-angle
- `look_ahead_distance` (float): Ray sampling distance (m)
- `sample_count` (int): Ray samples
- `inertia_weight` (float): Growth inertia (0-1)

#### `setup_ground_obstacle(plant_architecture, ground_uuid, avoidance_distance=0.1)`

Enable ground obstacle avoidance.

**Parameters:**
- `plant_architecture` (PlantArchitecture): PA instance
- `ground_uuid` (int): Ground primitive UUID
- `avoidance_distance` (float): Minimum distance (m)

---

## Geometry

### `intercropping.geometry.soil`

Soil plane creation.

#### `create_soil_plane(context, width, length, soil_texture="dirt.jpg", ...)`

Create textured soil with ground clipping prevention.

**Parameters:**
- `context` (Context): Helios Context
- `width` (float): Plot width (m)
- `length` (float): Plot length (m)
- `soil_texture` (str): Texture filename
- `subdivisions` (int): Mesh subdivisions
- `margin` (float): Extra margin (m)

**Returns:**
- `tuple`: (ground_uuid, margin)

### `intercropping.geometry.plants`

Plant positioning and growth.

#### `generate_intercrop_positions(plot_width, plot_length, n_rows, ...)`

Generate realistic intercrop positions with row-based planting.

**Parameters:**
- `plot_width` (float): Plot width (m)
- `plot_length` (float): Plot length (m)
- `n_rows` (int): Number of rows
- `row_spacing` (float): Row spacing (m)
- `bean_density` (float): Bean sowing density (seeds/m²)
- `wheat_density` (float): Wheat sowing density (seeds/m²)
- `bean_emergence` (float): Bean emergence rate (0-1)
- `wheat_emergence` (float): Wheat emergence rate (0-1)
- `seed` (int): Random seed

**Returns:**
- `list`: [(species, x, y), ...]

#### `build_plants(context, plant_architecture, positions, initial_age=5.0, margin=0.3)`

Build plant instances.

**Parameters:**
- `context` (Context): Helios Context
- `plant_architecture` (PlantArchitecture): PA instance
- `positions` (list): Position tuples
- `initial_age` (float): Initial age (days)
- `margin` (float): Soil margin (m)

**Returns:**
- `dict`: {plant_id: species_id}

### `intercropping.geometry.camera`

Camera geometry calculations.

#### `calculate_nadir_camera_height(plot_width, plot_length, fov_degrees=60.0)`

Calculate camera height for nadir view.

**Parameters:**
- `plot_width` (float): Plot width (m)
- `plot_length` (float): Plot length (m)
- `fov_degrees` (float): Field of view

**Returns:**
- `float`: Camera height (m)

---

## Radiation

### `intercropping.radiation.properties`

Radiative properties configuration.

#### `apply_radiative_properties(context, ground_uuid, bands=None)`

Set reflectance/transmissivity for all primitives.

**Parameters:**
- `context` (Context): Helios Context
- `ground_uuid` (int): Ground primitive UUID
- `bands` (list): Radiation bands

**Returns:**
- `int`: Number of primitives configured

### `intercropping.radiation.imaging`

Camera imaging using RadiationModel.

#### `setup_radiation_camera(radiation, bands, plot_width, plot_length, ...)`

Add nadir camera.

**Parameters:**
- `radiation` (RadiationModel): Radiation instance
- `bands` (list): Radiation bands
- `plot_width` (float): Plot width (m)
- `plot_length` (float): Plot length (m)
- `camera_resolution` (tuple): (width, height) pixels
- `fov` (float): Field of view (degrees)

**Returns:**
- `tuple`: (camera_position, lookat_point)

#### `save_camera_images(radiation, camera_label, bands, output_folder, ...)`

Export camera images.

**Parameters:**
- `radiation` (RadiationModel): Radiation instance
- `camera_label` (str): Camera ID
- `bands` (list): Radiation bands
- `output_folder` (Path): Output directory
- `camera_type` (str): "rgb" or "multispectral"

**Returns:**
- `str`: Primary image filename

---

## Segmentation

### `intercropping.segmentation.labels`

Species/organ labeling.

#### `apply_species_labels(context, ground_uuid, plant_species_map)`

Apply labels for segmentation.

**Parameters:**
- `context` (Context): Helios Context
- `ground_uuid` (int): Ground UUID
- `plant_species_map` (dict): Plant ID -> species ID

**Returns:**
- `tuple`: (total_labeled, bean_count, wheat_count)

---

## I/O

### `intercropping.io.export`

Scene export.

#### `export_scene(context, output_folder, export_ply=True, export_obj=True)`

Export to PLY/OBJ.

**Parameters:**
- `context` (Context): Helios Context
- `output_folder` (Path): Output directory
- `export_ply` (bool): Export PLY
- `export_obj` (bool): Export OBJ

**Returns:**
- `tuple`: (ply_path, obj_path)

### `intercropping.io.metadata`

Metadata generation.

#### `save_scene_metadata(output_folder, scene_info, args)`

Save metadata markdown.

**Parameters:**
- `output_folder` (Path): Output directory
- `scene_info` (dict): Scene statistics
- `args`: Argument namespace

**Returns:**
- `Path`: Metadata file path

---

## Visualization

### `intercropping.visualization.renderer`

Interactive visualization.

#### `render_interactive(context, sun_direction, plot_width, plot_length, ...)`

Render scene interactively.

**Parameters:**
- `context` (Context): Helios Context
- `sun_direction` (tuple): (x, y, z) sun vector
- `plot_width` (float): Plot width (m)
- `plot_length` (float): Plot length (m)
- Various rendering options...

---

## Utilities

### `intercropping.utils.file_utils`

File management.

#### `get_next_output_folder(base_dir)`

Get auto-numbered output folder.

**Parameters:**
- `base_dir` (str|Path): Base directory

**Returns:**
- `Path`: Next available folder (1/, 2/, 3/, ...)

### `intercropping.utils.texture_utils`

Texture management.

#### `get_builtin_texture_path(texture_name)`

Get PyHelios built-in texture path.

**Parameters:**
- `texture_name` (str): Texture filename

**Returns:**
- `str`: Absolute path or None
