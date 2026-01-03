"""
Scene export utilities for PLY and OBJ files.

Exports Helios scenes to standard 3D formats compatible with Blender, MeshLab,
and other 3D software.
"""

from pathlib import Path
from pyhelios import Context
from typing import Tuple


def export_scene(
    context: Context,
    output_folder: Path,
    export_ply: bool = True,
    export_obj: bool = True
) -> Tuple[Path, Path]:
    """
    Export scene to PLY and/or OBJ files.
    
    PLY: Geometry only (Blender/MeshLab compatible)
    OBJ: Geometry + material groups (Helios/Blender compatible, preserves organ info)
    
    Args:
        context: Helios Context with scene geometry
        output_folder: Output directory
        export_ply: Export PLY file
        export_obj: Export OBJ file
        
    Returns:
        Tuple of (ply_path, obj_path) or (None, None) if skipped
        
    Example:
        >>> ply_file, obj_file = export_scene(context, output_folder)
    """
    ply_file = None
    obj_file = None
    
    if export_ply:
        ply_file = output_folder / "scene.ply"
        context.writePLY(str(ply_file))
        print(f"  ✓ Saved PLY: {ply_file}")
    
    if export_obj:
        obj_file = output_folder / "scene.obj"
        context.writeOBJ(str(obj_file))
        print(f"  ✓ Saved OBJ: {obj_file} (preserves material groups)")
    
    return ply_file, obj_file
