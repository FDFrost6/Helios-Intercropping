"""
Interactive visualization using PyHelios Visualizer.

Provides 3D OpenGL rendering with realistic lighting and camera controls.
"""

from pyhelios import Context, Visualizer
from pyhelios.types import vec3, RGBcolor
from typing import Tuple, Optional

from intercropping.utils.texture_utils import get_builtin_texture_path


def setup_visualizer(
    context: Context,
    width: int = 1920,
    height: int = 1080,
    aa_samples: int = 8,
    headless: bool = False
) -> Visualizer:
    """
    Create and configure Visualizer instance.
    
    Args:
        context: Helios Context with scene geometry
        width: Window width in pixels
        height: Window height in pixels
        aa_samples: Anti-aliasing samples
        headless: Run without display (for batch processing)
        
    Returns:
        Configured Visualizer instance
    """
    vis = Visualizer(
        width=width,
        height=height,
        antialiasing_samples=aa_samples,
        headless=headless
    )
    
    return vis


def render_interactive(
    context: Context,
    sun_direction: Tuple[float, float, float],
    plot_width: float,
    plot_length: float,
    margin: float = 0.3,
    light_intensity: float = 1.5,
    use_sky_dome: bool = False,
    sky_texture: str = "SkyDome_clouds.jpg",
    show_grid: bool = False,
    width: int = 1920,
    height: int = 1080,
    aa_samples: int = 8
) -> None:
    """
    Render scene interactively with realistic lighting.
    
    Args:
        context: Helios Context with scene geometry
        sun_direction: Sun direction vector (x, y, z)
        plot_width: Plot width in meters
        plot_length: Plot length in meters
        margin: Soil margin in meters
        light_intensity: Light intensity factor
        use_sky_dome: Use sky dome texture background
        sky_texture: Sky dome texture filename
        show_grid: Display reference grid
        width: Window width
        height: Window height
        aa_samples: Anti-aliasing samples
    """
    total_prims = context.getPrimitiveCount()
    
    with Visualizer(
        width=width,
        height=height,
        antialiasing_samples=aa_samples,
        headless=False
    ) as vis:
        
        vis.buildContextGeometry(context)
        print(f"  ✓ Loaded {total_prims:,} primitives")
        
        # Set sky background
        if use_sky_dome:
            sky_texture_path = get_builtin_texture_path(sky_texture)
            if sky_texture_path:
                print(f"  Using sky dome texture: {sky_texture}")
                vis.setBackgroundSkyTexture(sky_texture_path)
            else:
                print(f"  Sky texture not found, using plain blue")
                vis.setBackgroundColor(RGBcolor(0.5, 0.7, 1.0))
        else:
            vis.setBackgroundColor(RGBcolor(0.5, 0.7, 1.0))
        
        # Lighting
        sun_vec = vec3(*sun_direction)
        vis.setLightDirection(sun_vec)
        vis.setLightIntensityFactor(light_intensity)
        vis.setLightingModel("phong_shadowed")
        print(f"  ✓ Realistic outdoor lighting with shadows")
        
        # Optional grid
        if show_grid:
            soil_width = plot_width + 2 * margin
            soil_length = plot_length + 2 * margin
            vis.addGridWireFrame(
                center=vec3(soil_width / 2, soil_length / 2, 0),
                size=vec3(soil_width, soil_length, 0),
                subdivisions=[10, 10, 1]
            )
        
        # Camera position (oblique view)
        soil_width = plot_width + 2 * margin
        soil_length = plot_length + 2 * margin
        max_dim = max(plot_width, plot_length)
        
        vis.setCameraPosition(
            position=vec3(
                soil_width / 2 + max_dim * 1.2,
                soil_length / 2 + max_dim * 1.2,
                max_dim * 1.0
            ),
            lookAt=vec3(soil_width / 2, soil_length / 2, 0.4)
        )
        vis.hideWatermark()
        
        # Interactive rendering
        print("\n[INTERACTIVE VIEW]")
        print("-" * 70)
        print(f"  Controls: Mouse to rotate, scroll to zoom, arrow keys to pan")
        print()
        
        vis.plotInteractive()
