"""
Plugin availability checking.

Validates that required PyHelios plugins are available before scene creation.
"""

from pyhelios.plugins.registry import get_plugin_registry
from typing import List


def check_required_plugins(required: List[str] = None) -> bool:
    """
    Check that required PyHelios plugins are available.
    
    Args:
        required: List of required plugin names. If None, checks default set:
                 ['plantarchitecture', 'visualizer', 'solarposition']
                 
    Returns:
        True if all plugins available, False otherwise
        
    Example:
        >>> if check_required_plugins():
        ...     print("All plugins ready")
        ... else:
        ...     print("Missing plugins")
    """
    if required is None:
        required = ['plantarchitecture', 'visualizer', 'solarposition']
    
    registry = get_plugin_registry()
    all_available = True
    
    for plugin in required:
        if not registry.is_plugin_available(plugin):
            print(f"ERROR: {plugin} plugin not available")
            all_available = False
    
    if all_available:
        print("✓ All plugins available\n")
    
    return all_available
