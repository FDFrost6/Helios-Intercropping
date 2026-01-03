# Helios Intercropping Pipeline

A modular, production-ready pipeline for generating photorealistic RGB and multispectral camera images with semantic segmentation masks for faba bean and wheat intercropping research using PyHelios.

## Features

- 🌱 **Realistic Plant Growth** - Soft collision avoidance for natural canopy structure
- 📸 **GPU-Accelerated Camera Imaging** - RGB and multispectral (R, G, B, NIR) imaging
- 🎯 **Instance Segmentation** - COCO JSON format masks for ML training
- 🌍 **Accurate Solar Modeling** - Date/time/location-based sun positioning
- 🔬 **Literature-Based Parameters** - Emergence rates, reflectance values from research
- 🎨 **Photorealistic Rendering** - Textured soil, sky domes, realistic lighting
- 🧩 **Modular Architecture** - Clean separation of concerns for easy extension

## Installation

### Prerequisites

- **Python 3.8+**
- **NVIDIA GPU with CUDA 12.x** (for camera imaging)
- **OptiX 7.x** (for GPU ray tracing)
- **PyHelios** (see installation below)

### Quick Start

```bash
# 1. Clone PyHelios
git clone https://github.com/PlantSimulationLab/PyHelios.git
cd PyHelios

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install PyHelios
pip install -e .

# 4. Clone this project
cd /path/to/your/workspace
git clone https://github.com/yourusername/helios-intercropping.git
cd helios-intercropping

# 5. Install dependencies
pip install -r requirements.txt

# 6. Install package (optional, for development)
pip install -e .

# 7. Verify installation
python scripts/generate_scene.py --help
```

### Verify GPU Acceleration

```bash
# Check CUDA availability
nvidia-smi

# Test GPU with RadiationModel
python -c "from pyhelios import Context, RadiationModel; ctx = Context(); rad = RadiationModel(ctx); print(f'GPU: {rad.hasGPUAcceleration()}')"
```

## Usage

### Basic Scene Generation

```bash
# Generate scene with interactive visualization
python scripts/generate_scene.py

# Generate and save scene with RGB camera
python scripts/generate_scene.py --save --camera

# Multispectral camera with segmentation
python scripts/generate_scene.py --save --camera --camera-type multispectral --segmentation
```

### Common Options

```bash
# Custom plot dimensions
python scripts/generate_scene.py --plot-width 2.0 --plot-length 1.5

# Higher plant density
python scripts/generate_scene.py --bean-density 50 --wheat-density 25

# Older plants
python scripts/generate_scene.py --growth-days 60

# High-resolution camera
python scripts/generate_scene.py --camera --camera-resolution 2048 2048

# Intercropping (bean + wheat)
python scripts/generate_scene.py --bean-density 36 --wheat-density 18 --save --camera
```

### Full Example

```bash
# Generate 1.5m × 1.5m plot with 50 bean/m², 60-day old plants,
# 2K multispectral camera, and segmentation masks
python scripts/generate_scene.py \
    --plot-width 1.5 --plot-length 1.5 \
    --bean-density 50 --growth-days 60 \
    --camera --camera-type multispectral \
    --camera-resolution 2048 2048 \
    --segmentation --save
```

## Project Structure

```
helios-intercropping/
├── src/
│   └── intercropping/
│       ├── config/          # Constants and default parameters
│       ├── core/            # Helios context and collision management
│       ├── geometry/        # Soil, plants, camera positioning
│       ├── radiation/       # Optical properties and imaging
│       ├── segmentation/    # Species/organ labeling
│       ├── io/              # Export and metadata
│       ├── visualization/   # Interactive rendering
│       └── utils/           # File and texture utilities
├── scripts/
│   └── generate_scene.py    # Main entry point
├── params/
│   └── faba_bean.xml        # Plant architecture parameters
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── requirements.txt
├── setup.py
├── pyproject.toml
└── README.md
```

## Output Structure

```
output/
├── 1/                       # Auto-numbered folders prevent overwrites
│   ├── scene.ply            # 3D geometry (Blender/MeshLab)
│   ├── scene.obj            # 3D geometry with materials
│   ├── scene.mtl            # Material definitions
│   ├── scene_info.md        # Metadata and parameters
│   └── images/
│       ├── nadir_camera_rgb.jpeg           # RGB image
│       ├── nadir_camera_rgb_normalized.jpeg # Auto-scaled
│       ├── nadir_camera_multispectral.jpeg  # MS image (if requested)
│       └── segmentation.json               # COCO format masks
├── 2/
│   └── ...
```

## Key Features Explained

### Realistic Emergence Rates

Uses literature-based germination rates:
- **Bean**: 87.5% (85-90% range from Cook & Veseth 1991)
- **Wheat**: 80% (75-85% range from Lafond et al. 2008)

### Soft Collision Avoidance

Plants detect and avoid growing into each other using perception cones:
- **View angle**: 70° half-angle cone
- **Look-ahead distance**: 8cm ray sampling
- **Ground obstacle**: Prevents growth below Z=0

### Camera Imaging

- **RGB**: Red (620-750nm), Green (495-570nm), Blue (450-495nm)
- **Multispectral**: RGB + NIR (750-1400nm)
- **Ray tracing**: 2000 direct + 5000 diffuse rays per band
- **Scattering**: 4-depth multiple bounces through canopy
- **Output**: JPEG images with optional normalization

### Segmentation Masks

- **Format**: COCO JSON with polygon annotations
- **Labels**: `ground`, `bean`, `wheat` (from `plant_part` field)
- **Class IDs**: Configurable object class assignment

## Programmatic Usage

```python
from pathlib import Path
from intercropping.core.context import setup_helios_context
from intercropping.geometry.soil import create_soil_plane
from intercropping.geometry.plants import generate_intercrop_positions, build_plants
from pyhelios import Context, PlantArchitecture

# Setup
year, month, day = 2022, 6, 14
hour, minute = 12, 0
context = setup_helios_context(year, month, day, hour, minute)

# Create scene
ground_uuid, margin = create_soil_plane(context, 1.0, 1.0)

# Generate plant positions
positions = generate_intercrop_positions(
    plot_width=1.0, plot_length=1.0,
    n_rows=4, row_spacing=0.21,
    bean_density=36, wheat_density=0
)

# Build plants
with PlantArchitecture(context) as pa:
    plant_map = build_plants(context, pa, positions, initial_age=5.0, margin=margin)
    pa.advanceTime(35.0)  # Grow for 35 days

# Export
context.writePLY("scene.ply")
```

## Documentation

- **[API Reference](docs/API.md)** - Detailed module and function documentation
- **[Usage Guide](docs/USAGE.md)** - Examples and workflows
- **[PyHelios Docs](https://plantsimulationlab.github.io/PyHelios/)** - Official PyHelios documentation

## Development

```bash
# Install in development mode
pip install -e .[dev]

# Run tests
pytest tests/

# Format code
black src/ scripts/

# Type checking
mypy src/
```

## Citation

If you use this pipeline in your research, please cite:

```bibtex
@software{helios_intercropping_2026,
  author = {Your Name},
  title = {Helios Intercropping Pipeline},
  year = {2026},
  url = {https://github.com/yourusername/helios-intercropping}
}
```

And the PyHelios framework:

```bibtex
@article{bailey2023helios,
  title={Helios: A scalable 3D plant and environmental biophysical modeling framework},
  author={Bailey, Brian N},
  journal={Frontiers in Plant Science},
  volume={14},
  year={2023}
}
```

## License

MIT License - see LICENSE file for details

## Acknowledgments

- **PyHelios** - Plant Simulation Lab, UC Davis
- **PhenoRoam Dataset** - Reference validation data (Campus Klein-Altendorf)
- Literature sources for emergence rates and reflectance values

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/helios-intercropping/issues)
- **PyHelios Forum**: [Discussions](https://github.com/PlantSimulationLab/PyHelios/discussions)
- **Email**: your.email@example.com

---

**Status**: Production-ready ✅  
**Version**: 1.0.0  
**Last Updated**: January 2026
