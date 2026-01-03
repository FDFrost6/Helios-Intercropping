# Usage Guide

Comprehensive guide to using the Helios Intercropping Pipeline.

## Quick Start

### 1. Basic Scene Generation

Generate a simple intercropping scene with default parameters:

```bash
python scripts/generate_scene.py
```

This creates a 1m × 1m plot with 36 bean plants/m² and opens an interactive 3D view.

### 2. Save Scene Files

Export scene geometry to PLY and OBJ files:

```bash
python scripts/generate_scene.py --save
```

Output location: `output/1/scene.{ply,obj,mtl,scene_info.md}`

### 3. Generate Camera Images

Create RGB camera images with RadiationModel:

```bash
python scripts/generate_scene.py --save --camera
```

Output: `output/1/images/nadir_camera_rgb.jpeg`

### 4. Add Segmentation Masks

Generate COCO JSON segmentation masks:

```bash
python scripts/generate_scene.py --save --camera --segmentation
```

Output: `output/1/images/segmentation.json`

---

## Common Workflows

### Workflow 1: ML Training Dataset

Generate synthetic dataset for machine learning:

```bash
# High-resolution RGB with segmentation
python scripts/generate_scene.py \
    --save --camera --segmentation \
    --camera-resolution 2048 2048 \
    --bean-density 50 --growth-days 45 \
    --seed 1001

# Repeat with different seeds for dataset variety
for seed in {1001..1100}; do
    python scripts/generate_scene.py --save --camera --segmentation --seed $seed --no-interactive
done
```

### Workflow 2: Multispectral Analysis

Generate multispectral images (RGB + NIR):

```bash
python scripts/generate_scene.py \
    --save --camera \
    --camera-type multispectral \
    --camera-resolution 1024 1024 \
    --bean-density 40 --wheat-density 20
```

### Workflow 3: Time Series

Simulate plant growth over time:

```bash
# Day 10
python scripts/generate_scene.py --save --camera --growth-days 10 --output-dir timeseries

# Day 20
python scripts/generate_scene.py --save --camera --growth-days 20 --output-dir timeseries

# Day 30
python scripts/generate_scene.py --save --camera --growth-days 30 --output-dir timeseries

# ... continue to day 60
```

### Workflow 4: Density Comparison

Compare different planting densities:

```bash
# Low density (30 plants/m²)
python scripts/generate_scene.py --save --camera --bean-density 30 --output-dir density_study

# Medium density (40 plants/m²)
python scripts/generate_scene.py --save --camera --bean-density 40 --output-dir density_study

# High density (50 plants/m²)
python scripts/generate_scene.py --save --camera --bean-density 50 --output-dir density_study
```

---

## Parameter Guide

### Plot Configuration

**Plot dimensions:**
```bash
# Small plot
--plot-width 0.5 --plot-length 0.5

# Standard plot (default)
--plot-width 1.0 --plot-length 1.0

# Large plot
--plot-width 2.0 --plot-length 2.0
```

**Row configuration:**
```bash
# Default (4 rows @ 21cm spacing)
--n-rows 4 --row-spacing 0.21

# Wider rows (typical wheat)
--n-rows 6 --row-spacing 0.15

# Custom spacing
--n-rows 8 --row-spacing 0.125
```

### Plant Densities

**Monoculture bean:**
```bash
--bean-density 40 --wheat-density 0
```

**Intercropping:**
```bash
--bean-density 30 --wheat-density 15
```

**High density:**
```bash
--bean-density 60 --wheat-density 30
```

### Plant Age

**Young plants (seedling stage):**
```bash
--growth-days 15
```

**Medium age (vegetative):**
```bash
--growth-days 40
```

**Mature plants (flowering):**
```bash
--growth-days 60
```

**Species-specific ages:**
```bash
--bean-age 45 --wheat-age 50
```

### Camera Settings

**Resolution:**
```bash
# Low (fast)
--camera-resolution 512 512

# Medium (default)
--camera-resolution 1024 1024

# High (slow but detailed)
--camera-resolution 2048 2048

# 4K
--camera-resolution 3840 2160
```

**Camera type:**
```bash
# RGB only
--camera-type rgb

# Multispectral (RGB + NIR)
--camera-type multispectral
```

### Solar Position

**Validation against PhenoRoam (June 14, 2022, noon):**
```bash
--date 2022-06-14 --time 12:00 --latitude 50.865 --longitude 7.134 --utc-offset 2
```

**Morning light:**
```bash
--date 2022-06-14 --time 08:00
```

**Afternoon light:**
```bash
--date 2022-06-14 --time 16:00
```

**Different season:**
```bash
--date 2022-09-15 --time 12:00
```

---

## Advanced Usage

### Batch Processing

Create multiple scenes without interactive view:

```bash
#!/bin/bash
for density in 30 40 50 60; do
    for age in 20 30 40 50 60; do
        python scripts/generate_scene.py \
            --save --camera --segmentation \
            --bean-density $density \
            --growth-days $age \
            --seed $((density * 100 + age)) \
            --no-interactive \
            --output-dir batch_output
    done
done
```

### Programmatic API

Use modules directly in Python:

```python
from pathlib import Path
from intercropping.core.context import setup_helios_context
from intercropping.geometry.soil import create_soil_plane
from intercropping.geometry.plants import generate_intercrop_positions, build_plants
from intercropping.core.collision import setup_full_collision_system
from intercropping.io.export import export_scene
from pyhelios import PlantArchitecture

# Setup
context = setup_helios_context(2022, 6, 14, 12, 0)
ground_uuid, margin = create_soil_plane(context, 1.5, 1.5)

# Generate positions
positions = generate_intercrop_positions(
    plot_width=1.5, plot_length=1.5,
    n_rows=6, row_spacing=0.21,
    bean_density=40, wheat_density=20,
    seed=42
)

# Build and grow plants
with PlantArchitecture(context) as pa:
    setup_full_collision_system(pa, ground_uuid)
    plant_map = build_plants(context, pa, positions, initial_age=5.0, margin=margin)
    pa.advanceTime(40.0)

# Export
output = Path("output/custom")
output.mkdir(parents=True, exist_ok=True)
export_scene(context, output)

print(f"Scene saved to {output}")
```

---

## Troubleshooting

### GPU Issues

**Problem:** "CUDA device not available"

**Solution:**
```bash
# Check GPU
nvidia-smi

# Verify CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Check PyHelios GPU support
python -c "from pyhelios import Context, RadiationModel; ctx = Context(); print(RadiationModel(ctx).hasGPUAcceleration())"
```

### Import Errors

**Problem:** "ModuleNotFoundError: No module named 'intercropping'"

**Solution:**
```bash
# Ensure you're in project directory
cd /path/to/helios-intercropping

# Install in development mode
pip install -e .

# OR add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/helios-intercropping/src"
```

### Segmentation Masks Empty

**Problem:** Segmentation JSON contains no annotations

**Solution:**
- Ensure `--segmentation` flag is used
- Verify labels are applied before camera imaging
- Check that primitives have `plant_part` field set

### Slow Performance

**Problem:** Camera imaging is very slow

**Solution:**
- Verify GPU acceleration is enabled
- Reduce ray counts: `direct_rays=1000, diffuse_rays=2000`
- Lower camera resolution
- Reduce scattering depth to 2-3

---

## Tips & Best Practices

### 1. Use Auto-Numbered Output Folders

The pipeline automatically creates numbered folders (1/, 2/, 3/...) to prevent overwrites:

```bash
# Safe to run multiple times
python scripts/generate_scene.py --save --camera
# Output: output/1/
python scripts/generate_scene.py --save --camera
# Output: output/2/
```

### 2. Set Random Seeds for Reproducibility

```bash
# Same seed = identical plant positions
python scripts/generate_scene.py --seed 42 --save
python scripts/generate_scene.py --seed 42 --save  # Identical scene
```

### 3. Skip Interactive View for Batch Processing

```bash
python scripts/generate_scene.py --save --camera --no-interactive
```

### 4. Check Metadata Files

Every output folder contains `scene_info.md` with complete parameters:

```bash
cat output/1/scene_info.md
```

### 5. Import to Blender

```python
# In Blender Python console
import bpy
bpy.ops.import_scene.obj(filepath="/path/to/output/1/scene.obj")
```

---

## Next Steps

- Explore [API Reference](API.md) for programmatic usage
- Check [PyHelios Documentation](https://plantsimulationlab.github.io/PyHelios/) for advanced features
- Modify plant parameters in `params/faba_bean.xml`
- Create custom textures for soil/sky
- Extend modules for new plant species
