"""
Scene metadata generation for documentation.

Creates human-readable markdown files documenting scene parameters,
configuration, and usage instructions.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def save_scene_metadata(
    output_folder: Path,
    scene_info: Dict[str, Any],
    args: Any
) -> Path:
    """
    Save scene metadata and settings to markdown file.
    
    Creates comprehensive documentation of scene parameters including:
    - Plot dimensions and plant counts
    - Collision avoidance settings
    - Environmental parameters (solar position, date/time)
    - Rendering settings
    - Usage instructions for Blender/Helios
    
    Args:
        output_folder: Output directory
        scene_info: Dictionary with scene statistics:
            - n_bean: Number of bean plants
            - n_wheat: Number of wheat plants
            - bean_density: Actual bean density (plants/m²)
            - wheat_density: Actual wheat density (plants/m²)
            - total_primitives: Total primitive count
            - bean_age: Bean age in days
            - wheat_age: Wheat age in days
            - sun_elevation: Sun elevation angle (degrees)
            - solar_flux: Solar flux (W/m²)
        args: Argument namespace from argparse
        
    Returns:
        Path to created metadata file
        
    Example:
        >>> metadata_file = save_scene_metadata(output_folder, scene_info, args)
    """
    metadata_file = output_folder / "scene_info.md"
    
    with open(metadata_file, 'w') as f:
        f.write(f"# Scene Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Scene Contents\n\n")
        f.write(f"- **Plot Size**: {args.plot_width}m × {args.plot_length}m ")
        f.write(f"({args.plot_width * args.plot_length:.2f} m²)\n")
        f.write(f"- **Bean Plants**: {scene_info['n_bean']} plants ")
        f.write(f"({scene_info['bean_density']:.1f}/m²)\n")
        f.write(f"- **Wheat Plants**: {scene_info['n_wheat']} plants ")
        f.write(f"({scene_info['wheat_density']:.1f}/m²)\n")
        f.write(f"- **Total Primitives**: {scene_info['total_primitives']:,}\n")
        f.write(f"- **Plant Age**: {scene_info['bean_age']} days (bean), ")
        f.write(f"{scene_info['wheat_age']} days (wheat)\n\n")
        
        f.write("## Plot Configuration\n\n")
        f.write(f"- **Rows**: {args.n_rows}\n")
        f.write(f"- **Row Spacing**: {args.row_spacing}m\n")
        f.write(f"- **Bean Sowing Density**: {args.bean_density} seeds/m²\n")
        f.write(f"- **Wheat Sowing Density**: {args.wheat_density} seeds/m²\n")
        f.write(f"- **Bean Emergence Rate**: {args.bean_emergence * 100:.1f}%\n")
        f.write(f"- **Wheat Emergence Rate**: {args.wheat_emergence * 100:.1f}%\n")
        f.write(f"- **Random Seed**: {args.seed}\n\n")
        
        f.write("## Collision Avoidance\n\n")
        f.write(f"- **Mode**: Soft collision + Ground obstacle pruning\n")
        f.write(f"- **View Half-Angle**: {args.view_angle}°\n")
        f.write(f"- **Look-Ahead Distance**: {args.lookahead}m\n")
        f.write(f"- **Ray Samples**: {args.samples}\n")
        f.write(f"- **Inertia Weight**: {args.inertia}\n")
        f.write(f"- **Ground Avoidance**: 0.1m with obstacle pruning\n")
        f.write(f"- **Collision Organs**: Internodes + Leaves\n\n")
        
        f.write("## Environmental Settings\n\n")
        f.write(f"- **Date/Time**: {args.date} {args.time}\n")
        f.write(f"- **Location**: {args.latitude}°N, {args.longitude}°E (UTC+{args.utc_offset})\n")
        f.write(f"- **Sun Elevation**: {scene_info['sun_elevation']:.1f}°\n")
        f.write(f"- **Solar Flux**: {scene_info['solar_flux']:.0f} W/m²\n\n")
        
        f.write("## Files\n\n")
        f.write(f"- `scene.ply` - 3D geometry (Blender/MeshLab compatible)\n")
        f.write(f"- `scene.obj` - Wavefront OBJ with material groups\n")
        f.write(f"- `scene_info.md` - This metadata file\n")
        if hasattr(args, 'camera') and args.camera:
            f.write(f"- `images/` - Camera images and segmentation masks\n")
        f.write("\n")
        
        f.write("## Usage\n\n")
        f.write("### Import to Blender:\n")
        f.write("```\n")
        f.write("File → Import → Stanford (.ply) or Wavefront (.obj)\n")
        f.write("OBJ import preserves material groups for easy selection\n")
        f.write("```\n\n")
        
        f.write("### Helios OBJ Loading (preserves materials):\n")
        f.write("```python\n")
        f.write("from pyhelios import Context\n")
        f.write("with Context() as context:\n")
        f.write(f"    context.loadOBJ('{output_folder.name}/scene.obj')\n")
        f.write("```\n")
    
    return metadata_file
