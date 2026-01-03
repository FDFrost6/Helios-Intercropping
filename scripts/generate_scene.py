#!/usr/bin/env python3
"""
Intercropping Scene Generator

Main entry point for generating photorealistic RGB/multispectral camera images
with semantic segmentation masks for faba bean and wheat intercropping research.

Usage:
    python scripts/generate_scene.py --save --camera --segmentation
    python scripts/generate_scene.py --camera-type multispectral --camera-resolution 2048 2048
    python scripts/generate_scene.py --bean-density 50 --wheat-density 25 --growth-days 60

For help:
    python scripts/generate_scene.py --help
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyhelios import Context, PlantArchitecture, RadiationModel
from pyhelios.exceptions import HeliosError

from intercropping.config.constants import BEAN_EMERGENCE_RATE, WHEAT_EMERGENCE_RATE
from intercropping.config.defaults import (
    DEFAULT_PLOT_WIDTH,
    DEFAULT_PLOT_LENGTH,
    DEFAULT_BEAN_DENSITY,
    DEFAULT_INITIAL_AGE,
    DEFAULT_GROWTH_DAYS,
)
from intercropping.core.context import setup_helios_context, parse_date_time
from intercropping.core.scene import check_required_plugins
from intercropping.core.collision import setup_full_collision_system
from intercropping.geometry.soil import create_soil_plane
from intercropping.geometry.plants import generate_intercrop_positions, build_plants, grow_plants
from intercropping.radiation.solar import calculate_solar_position
from intercropping.radiation.properties import apply_radiative_properties
from intercropping.radiation.imaging import (
    setup_radiation_bands,
    setup_sun_source,
    configure_band_rendering,
    setup_radiation_camera,
    run_camera_simulation,
    save_camera_images,
    save_segmentation_masks,
)
from intercropping.segmentation.labels import apply_species_labels
from intercropping.io.export import export_scene
from intercropping.io.metadata import save_scene_metadata
from intercropping.visualization.renderer import render_interactive
from intercropping.utils.file_utils import get_next_output_folder


def create_argument_parser():
    """Create and configure command-line argument parser."""
    parser = argparse.ArgumentParser(
        description='Generate intercropping scenes with camera imaging and segmentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic scene with visualization
  %(prog)s
  
  # Save scene with camera imaging
  %(prog)s --save --camera --segmentation
  
  # Multispectral camera with high resolution
  %(prog)s --camera --camera-type multispectral --camera-resolution 2048 2048
  
  # Custom plot and densities
  %(prog)s --plot-width 2.0 --plot-length 1.5 --bean-density 50 --wheat-density 25
  
  # Older plants
  %(prog)s --growth-days 60 --save --camera
        """
    )
    
    # Plot parameters
    plot_group = parser.add_argument_group('Plot Configuration')
    plot_group.add_argument('--plot-width', type=float, default=DEFAULT_PLOT_WIDTH,
                           help=f'Plot width (m) [default: {DEFAULT_PLOT_WIDTH}]')
    plot_group.add_argument('--plot-length', type=float, default=DEFAULT_PLOT_LENGTH,
                           help=f'Plot length (m) [default: {DEFAULT_PLOT_LENGTH}]')
    plot_group.add_argument('--n-rows', type=int, default=4,
                           help='Number of planting rows [default: 4]')
    plot_group.add_argument('--row-spacing', type=float, default=0.21,
                           help='Row spacing (m) [default: 0.21]')
    
    # Sowing densities
    density_group = parser.add_argument_group('Sowing Densities')
    density_group.add_argument('--bean-density', type=float, default=DEFAULT_BEAN_DENSITY,
                              help=f'Bean sowing density (seeds/m²) [default: {DEFAULT_BEAN_DENSITY}]')
    density_group.add_argument('--wheat-density', type=float, default=0,
                              help='Wheat sowing density (seeds/m²) [default: 0]')
    density_group.add_argument('--bean-emergence', type=float, default=BEAN_EMERGENCE_RATE,
                              help=f'Bean emergence rate (0.0-1.0) [default: {BEAN_EMERGENCE_RATE}]')
    density_group.add_argument('--wheat-emergence', type=float, default=WHEAT_EMERGENCE_RATE,
                              help=f'Wheat emergence rate (0.0-1.0) [default: {WHEAT_EMERGENCE_RATE}]')
    
    # Plant growth
    growth_group = parser.add_argument_group('Plant Growth')
    growth_group.add_argument('--growth-days', type=int, default=DEFAULT_GROWTH_DAYS,
                             help=f'Plant age in days [default: {DEFAULT_GROWTH_DAYS}]')
    growth_group.add_argument('--bean-age', type=int, default=None,
                             help='Bean age (days) - overrides --growth-days')
    growth_group.add_argument('--wheat-age', type=int, default=None,
                             help='Wheat age (days) - overrides --growth-days')
    
    # Collision avoidance
    collision_group = parser.add_argument_group('Collision Avoidance')
    collision_group.add_argument('--view-angle', type=float, default=70.0,
                                help='Perception cone half-angle (degrees) [default: 70.0]')
    collision_group.add_argument('--lookahead', type=float, default=0.08,
                                help='Look-ahead distance (m) [default: 0.08]')
    collision_group.add_argument('--samples', type=int, default=256,
                                help='Ray samples for collision detection [default: 256]')
    collision_group.add_argument('--inertia', type=float, default=0.3,
                                help='Growth inertia weight (0-1) [default: 0.3]')
    
    # Camera options
    camera_group = parser.add_argument_group('Camera Imaging')
    camera_group.add_argument('--camera', action='store_true',
                             help='Generate camera images using RadiationModel')
    camera_group.add_argument('--camera-type', type=str, default='rgb',
                             choices=['rgb', 'multispectral'],
                             help='Camera type [default: rgb]')
    camera_group.add_argument('--camera-resolution', type=int, nargs=2,
                             default=[1024, 1024], metavar=('WIDTH', 'HEIGHT'),
                             help='Camera resolution in pixels [default: 1024 1024]')
    camera_group.add_argument('--segmentation', action='store_true',
                             help='Generate instance segmentation masks (COCO JSON)')
    
    # Solar position
    solar_group = parser.add_argument_group('Solar Position')
    solar_group.add_argument('--date', type=str, default='2022-06-14',
                            help='Date (YYYY-MM-DD) [default: 2022-06-14]')
    solar_group.add_argument('--time', type=str, default='12:00',
                            help='Time (HH:MM) [default: 12:00]')
    solar_group.add_argument('--latitude', type=float, default=50.865,
                            help='Latitude (degrees) [default: 50.865]')
    solar_group.add_argument('--longitude', type=float, default=7.134,
                            help='Longitude (degrees) [default: 7.134]')
    solar_group.add_argument('--utc-offset', type=int, default=2,
                            help='UTC offset (hours) [default: 2]')
    
    # Rendering
    render_group = parser.add_argument_group('Visualization')
    render_group.add_argument('--width', type=int, default=1920,
                             help='Window width [default: 1920]')
    render_group.add_argument('--height', type=int, default=1080,
                             help='Window height [default: 1080]')
    render_group.add_argument('--aa-samples', type=int, default=8,
                             help='Anti-aliasing samples [default: 8]')
    render_group.add_argument('--soil-subdivisions', type=int, default=30,
                             help='Soil mesh subdivisions [default: 30]')
    render_group.add_argument('--use-sky-dome', action='store_true',
                             help='Use sky dome texture background')
    render_group.add_argument('--sky-texture', type=str, default='SkyDome_clouds.jpg',
                             help='Sky dome texture [default: SkyDome_clouds.jpg]')
    render_group.add_argument('--light-intensity', type=float, default=1.5,
                             help='Light intensity factor [default: 1.5]')
    render_group.add_argument('--show-grid', action='store_true',
                             help='Display reference grid')
    
    # Export options
    export_group = parser.add_argument_group('Export')
    export_group.add_argument('--save', action='store_true',
                             help='Save scene to PLY/OBJ files with metadata')
    export_group.add_argument('--output-dir', type=str, default='output',
                             help='Base directory for saved scenes [default: output]')
    export_group.add_argument('--no-interactive', action='store_true',
                             help='Skip interactive visualization (useful for batch processing)')
    
    # Other
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility [default: 42]')
    
    return parser


def main():
    """Main entry point for scene generation."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Calculate plant ages
    bean_age = args.bean_age if args.bean_age is not None else args.growth_days
    wheat_age = args.wheat_age if args.wheat_age is not None else args.growth_days
    bean_growth_time = max(0.0, bean_age - DEFAULT_INITIAL_AGE)
    wheat_growth_time = max(0.0, wheat_age - DEFAULT_INITIAL_AGE)
    max_growth_time = max(bean_growth_time, wheat_growth_time)
    
    # Parse date/time
    year, month, day, hour, minute = parse_date_time(args.date, args.time)
    
    # Print header
    plot_area = args.plot_width * args.plot_length
    print("=" * 70)
    print("HELIOS INTERCROPPING SCENE GENERATOR")
    print("=" * 70)
    print(f"Plot: {args.plot_width}m × {args.plot_length}m ({plot_area:.2f} m²)")
    print(f"Rows: {args.n_rows} @ {args.row_spacing}m spacing")
    print(f"Sowing: {args.bean_density} bean/m² + {args.wheat_density} wheat/m²")
    print(f"Emergence: {args.bean_emergence*100:.1f}% bean, {args.wheat_emergence*100:.1f}% wheat")
    print(f"Age: {bean_age} days (bean), {wheat_age} days (wheat)")
    print(f"Camera: {'Yes (' + args.camera_type + ')' if args.camera else 'No'}")
    print(f"Segmentation: {'Yes' if args.segmentation else 'No'}")
    print()
    
    # Check plugins
    if not check_required_plugins():
        return 1
    
    # Create scene
    print("[SCENE CREATION]")
    print("-" * 70)
    
    context = setup_helios_context(year, month, day, hour, minute)
    
    # Soil
    print("  Creating ground with clipping prevention...")
    ground_uuid, margin = create_soil_plane(
        context, args.plot_width, args.plot_length,
        soil_texture="dirt.jpg",
        subdivisions=args.soil_subdivisions
    )
    print(f"  ✓ Ground obstacle created")
    
    # Generate positions
    print(f"  Generating intercrop pattern...")
    positions = generate_intercrop_positions(
        args.plot_width, args.plot_length, args.n_rows, args.row_spacing,
        args.bean_density, args.wheat_density,
        args.bean_emergence, args.wheat_emergence, args.seed
    )
    
    # Build and grow plants
    print(f"\n  Growing plants with collision avoidance...")
    
    plant_species_map = {}
    
    with PlantArchitecture(context) as pa:
        # Setup collision system
        collision_params = {
            "view_half_angle_deg": args.view_angle,
            "look_ahead_distance": args.lookahead,
            "sample_count": args.samples,
            "inertia_weight": args.inertia,
        }
        setup_full_collision_system(pa, ground_uuid, collision_params)
        
        # Build plants
        plant_species_map = build_plants(context, pa, positions, DEFAULT_INITIAL_AGE, margin)
        
        # Grow plants
        if max_growth_time > 0:
            grow_plants(pa, max_growth_time)
            print(f"    ✓ Plants now at age {bean_age} days (bean) / {wheat_age} days (wheat)")
    
    total_prims = context.getPrimitiveCount()
    n_bean = sum(1 for s, _, _ in positions if s == 'bean')
    n_wheat = sum(1 for s, _, _ in positions if s == 'wheat')
    print(f"  ✓ Scene: {total_prims:,} primitives ({n_bean} bean + {n_wheat} wheat plants)")
    
    # Apply segmentation labels if needed
    if args.segmentation:
        print("\n[LABELING FOR SEGMENTATION]")
        print("-" * 70)
        print("  Applying species labels to primitives...")
        apply_species_labels(context, ground_uuid, plant_species_map)
    
    # Solar position
    print("\n[SOLAR POSITION]")
    print("-" * 70)
    
    solar_info = calculate_solar_position(context, args.utc_offset, args.latitude, args.longitude)
    sun_direction = solar_info['direction']
    print(f"  ✓ Sun: {solar_info['elevation_deg']:.1f}° elevation, {solar_info['azimuth_deg']:.1f}° azimuth")
    print(f"  ✓ Solar flux: {solar_info['flux']:.0f} W/m²")
    
    # Prepare output folder if saving
    output_folder = None
    if args.save:
        output_folder = get_next_output_folder(args.output_dir)
    
    # Camera imaging
    if args.camera:
        print("\n[CAMERA IMAGING]")
        print("-" * 70)
        
        # Set radiative properties
        bands_for_props = ["Red", "Green", "Blue", "NIR"] if args.camera_type == 'multispectral' else ["Red", "Green", "Blue"]
        props_count = apply_radiative_properties(context, ground_uuid, bands_for_props)
        print(f"  ✓ Set reflectance properties for {props_count:,} primitives")
        
        try:
            with RadiationModel(context) as radiation:
                # Setup bands
                bands = setup_radiation_bands(radiation, args.camera_type)
                
                # Add sun source
                setup_sun_source(radiation, bands, solar_info['elevation_deg'], solar_info['azimuth_deg'])
                
                # Configure rendering
                configure_band_rendering(radiation, bands)
                
                # Add camera
                setup_radiation_camera(
                    radiation, bands, args.plot_width, args.plot_length, margin,
                    tuple(args.camera_resolution), camera_label="nadir_camera"
                )
                
                # Run simulation
                run_camera_simulation(radiation, bands)
                
                # Save images
                if args.save and output_folder:
                    primary_image = save_camera_images(
                        radiation, "nadir_camera", bands, output_folder, args.camera_type
                    )
                    
                    # Save segmentation if requested
                    if args.segmentation and primary_image:
                        save_segmentation_masks(radiation, "nadir_camera", primary_image, output_folder)
                else:
                    print(f"  ⚠ Use --save to export camera images")
                    
        except HeliosError as e:
            print(f"  ✗ Camera imaging failed: {e}")
            print(f"  Continuing with visualization...")
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            print(f"  Continuing with visualization...")
    
    # Export scene if requested
    if args.save and output_folder:
        print("\n[EXPORT]")
        print("-" * 70)
        
        export_scene(context, output_folder)
        
        scene_info = {
            'n_bean': n_bean,
            'n_wheat': n_wheat,
            'bean_density': n_bean / plot_area,
            'wheat_density': n_wheat / plot_area,
            'total_primitives': total_prims,
            'bean_age': bean_age,
            'wheat_age': wheat_age,
            'sun_elevation': solar_info['elevation_deg'],
            'solar_flux': solar_info['flux'],
        }
        
        metadata_file = save_scene_metadata(output_folder, scene_info, args)
        print(f"  ✓ Saved metadata: {metadata_file}")
        print(f"  ✓ Output folder: {output_folder.absolute()}")
    
    # Interactive visualization
    if not args.no_interactive:
        print("\n[VISUALIZATION]")
        print("-" * 70)
        
        render_interactive(
            context, sun_direction, args.plot_width, args.plot_length, margin,
            args.light_intensity, args.use_sky_dome, args.sky_texture,
            args.show_grid, args.width, args.height, args.aa_samples
        )
    
    print("\n" + "=" * 70)
    print("✓ COMPLETE")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
