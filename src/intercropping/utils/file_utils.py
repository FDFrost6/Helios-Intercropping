"""
File management utilities for the intercropping pipeline.

Handles output folder creation with auto-incrementing numbering to prevent overwrites.
"""

from pathlib import Path
from typing import Union


def get_next_output_folder(base_dir: Union[str, Path]) -> Path:
    """
    Get next available numbered folder (1, 2, 3, ...).
    
    Creates auto-incrementing output folders to prevent accidental overwrites
    during batch processing. This is the standard pattern used throughout
    the intercropping pipeline.
    
    Args:
        base_dir: Base directory for output folders
        
    Returns:
        Path to the next available numbered folder
        
    Example:
        >>> output = get_next_output_folder("output")
        >>> print(output)
        output/1/
        >>> output = get_next_output_folder("output")
        >>> print(output)
        output/2/
    """
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Find existing numbered folders
    existing = [
        int(d.name) for d in base_path.iterdir()
        if d.is_dir() and d.name.isdigit()
    ]
    
    next_num = max(existing, default=0) + 1
    output_folder = base_path / str(next_num)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    return output_folder


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_output_subdirectories(output_folder: Path) -> dict:
    """
    Create standard subdirectories for output data.
    
    Args:
        output_folder: Base output folder
        
    Returns:
        Dictionary with paths to subdirectories:
        - images: Camera images
        - annotations: Segmentation masks
        - meta: Metadata files
    """
    subdirs = {
        "images": output_folder / "images",
        "annotations": output_folder / "annotations",
        "meta": output_folder / "meta",
    }
    
    for subdir in subdirs.values():
        subdir.mkdir(exist_ok=True)
    
    return subdirs
