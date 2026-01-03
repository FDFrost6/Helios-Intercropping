"""
Texture management utilities for PyHelios built-in textures.

Handles resolution of built-in texture paths from the PyHelios installation.
"""

from pathlib import Path
from typing import Optional
import pyhelios


def get_builtin_texture_path(texture_name: str) -> Optional[str]:
    """
    Get path to PyHelios built-in texture.
    
    PyHelios includes several built-in textures in its assets directory:
    - dirt.jpg: Brown soil texture
    - SkyDome_clouds.jpg: Sky dome with clouds
    - grass.jpg: Grass texture
    - And others
    
    Args:
        texture_name: Name of the texture file (e.g., "dirt.jpg")
        
    Returns:
        Absolute path to texture file if found, None otherwise
        
    Example:
        >>> path = get_builtin_texture_path("dirt.jpg")
        >>> print(path)
        /path/to/pyhelios/assets/build/plugins/visualizer/textures/dirt.jpg
    """
    texture_dir = Path(pyhelios.__file__).parent / "assets/build/plugins/visualizer/textures"
    texture_path = texture_dir / texture_name
    
    if texture_path.exists():
        return str(texture_path)
    else:
        print(f"  ⚠ Built-in texture not found: {texture_name}")
        print(f"     Searched in: {texture_dir}")
        return None


def list_builtin_textures() -> list[str]:
    """
    List all available PyHelios built-in textures.
    
    Returns:
        List of texture filenames
    """
    texture_dir = Path(pyhelios.__file__).parent / "assets/build/plugins/visualizer/textures"
    
    if not texture_dir.exists():
        return []
    
    textures = [
        f.name for f in texture_dir.iterdir()
        if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tga']
    ]
    
    return sorted(textures)


def validate_texture_file(texture_path: str) -> bool:
    """
    Validate that a texture file exists and has a supported format.
    
    Args:
        texture_path: Path to texture file
        
    Returns:
        True if valid, False otherwise
    """
    path = Path(texture_path)
    
    if not path.exists():
        return False
    
    supported_formats = ['.jpg', '.jpeg', '.png', '.tga', '.bmp']
    return path.suffix.lower() in supported_formats
