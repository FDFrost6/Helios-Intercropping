"""
Camera imaging using RadiationModel plugin.

Handles setup and execution of GPU-accelerated radiation simulation for
photorealistic RGB and multispectral camera images.
"""

from pathlib import Path
from pyhelios import Context, RadiationModel, CameraProperties
from pyhelios.types import vec3
from typing import List, Tuple, Optional, Dict

from intercropping.config.constants import (
    BAND_WAVELENGTHS,
    SOLAR_IRRADIANCE,
    DIFFUSE_IRRADIANCE,
)
from intercropping.geometry.camera import calculate_nadir_camera_height


def setup_radiation_bands(
    radiation: RadiationModel,
    camera_type: str = "rgb"
) -> List[str]:
    """
    Add radiation bands with proper wavelength ranges.
    
    Args:
        radiation: RadiationModel instance
        camera_type: "rgb" or "multispectral"
        
    Returns:
        List of band names
    """
    if camera_type == 'multispectral':
        bands = ["Red", "Green", "Blue", "NIR"]
        print(f"  Setting up multispectral camera (R, G, B, NIR)")
    else:
        bands = ["Red", "Green", "Blue"]
        print(f"  Setting up RGB camera")
    
    # Add bands with wavelength ranges
    for band in bands:
        if band in BAND_WAVELENGTHS:
            wl_min, wl_max = BAND_WAVELENGTHS[band]
            radiation.addRadiationBand(band, wl_min, wl_max)
    
    return bands


def setup_sun_source(
    radiation: RadiationModel,
    bands: List[str],
    sun_elevation_deg: float,
    sun_azimuth_deg: float
) -> int:
    """
    Add sun radiation source with balanced irradiance.
    
    Args:
        radiation: RadiationModel instance
        bands: List of radiation bands
        sun_elevation_deg: Sun elevation angle in degrees
        sun_azimuth_deg: Sun azimuth angle in degrees
        
    Returns:
        Sun source ID
    """
    # Convert elevation to zenith
    sun_zenith_deg = 90.0 - sun_elevation_deg
    
    # Add sun sphere source
    sun_id = radiation.addSunSphereRadiationSource(
        radius=0.5,
        zenith=sun_zenith_deg,
        azimuth=sun_azimuth_deg
    )
    
    # Set solar irradiance for each band
    irradiance_str = []
    for band in bands:
        if band in SOLAR_IRRADIANCE:
            radiation.setSourceFlux(sun_id, band, SOLAR_IRRADIANCE[band])
            irradiance_str.append(f"{band[0]}={int(SOLAR_IRRADIANCE[band])}")
    
    print(f"  Solar irradiance: {' '.join(irradiance_str)} W/m²")
    
    return sun_id


def configure_band_rendering(
    radiation: RadiationModel,
    bands: List[str],
    direct_rays: int = 2000,
    diffuse_rays: int = 5000,
    scattering_depth: int = 4
) -> None:
    """
    Configure ray counts and scattering for each band.
    
    Args:
        radiation: RadiationModel instance
        bands: List of radiation bands
        direct_rays: Number of direct rays per band
        diffuse_rays: Number of diffuse rays per band
        scattering_depth: Scattering depth (3-5 good for vegetation)
    """
    for band in bands:
        # Ray counts
        radiation.setDirectRayCount(band, direct_rays)
        radiation.setDiffuseRayCount(band, diffuse_rays)
        
        # Diffuse skylight
        if band in DIFFUSE_IRRADIANCE:
            radiation.setDiffuseRadiationFlux(band, DIFFUSE_IRRADIANCE[band])
        
        # CRITICAL: Enable scattering to use reflectance/transmissivity!
        radiation.setScatteringDepth(band, scattering_depth)
        
        # Disable thermal emission (reflected light only)
        radiation.disableEmission(band)
    
    print(f"  Scattering: depth={scattering_depth} (multiple bounces through canopy)")
    print(f"  Ray counts: direct={direct_rays}, diffuse={diffuse_rays} per band")


def setup_radiation_camera(
    radiation: RadiationModel,
    bands: List[str],
    plot_width: float,
    plot_length: float,
    margin: float = 0.0,
    camera_resolution: Tuple[int, int] = (1024, 1024),
    fov: float = 60.0,
    aa_samples: int = 100,
    camera_label: str = "nadir_camera"
) -> Tuple[vec3, vec3]:
    """
    Add nadir (overhead) camera for plot imaging.
    
    Args:
        radiation: RadiationModel instance
        bands: List of radiation bands
        plot_width: Plot width in meters
        plot_length: Plot length in meters
        margin: Extra margin around plot
        camera_resolution: (width, height) in pixels
        fov: Field of view in degrees
        aa_samples: Anti-aliasing samples (100+ for sharp edges)
        camera_label: Camera identifier
        
    Returns:
        Tuple of (camera_position, lookat_point)
    """
    soil_width = plot_width + 2 * margin
    soil_length = plot_length + 2 * margin
    
    # Calculate nadir camera height
    camera_height = calculate_nadir_camera_height(soil_width, soil_length, fov)
    
    # Camera directly above center, looking down
    camera_center = vec3(soil_width / 2, soil_length / 2, 0.0)
    camera_position = vec3(soil_width / 2, soil_length / 2, camera_height)
    
    print(f"  Camera position: ({camera_position.x:.2f}, {camera_position.y:.2f}, {camera_position.z:.2f})")
    print(f"  Camera height: {camera_height:.2f}m (nadir view)")
    
    # Create camera properties
    # CRITICAL: lens_diameter=0 for pinhole camera (infinite depth of field)
    camera_props = CameraProperties(
        camera_resolution=camera_resolution,
        focal_plane_distance=camera_height,
        lens_diameter=0.0,  # Pinhole = sharp focus everywhere
        HFOV=fov
    )
    
    # Add camera to radiation model
    radiation.addRadiationCamera(
        camera_label=camera_label,
        band_labels=bands,
        position=camera_position,
        lookat_or_direction=camera_center,
        camera_properties=camera_props,
        antialiasing_samples=aa_samples
    )
    
    return camera_position, camera_center


def run_camera_simulation(
    radiation: RadiationModel,
    bands: List[str]
) -> None:
    """
    Run radiation simulation for all bands.
    
    CRITICAL: Run all bands in ONE call for 2-5x speedup (GPU setup overhead).
    
    Args:
        radiation: RadiationModel instance
        bands: List of radiation bands to simulate
    """
    print(f"  Running radiation simulation...")
    radiation.updateGeometry()
    
    # CRITICAL: Single call for efficiency
    radiation.runBand(bands)
    
    print(f"    ✓ Radiation simulation complete")


def save_camera_images(
    radiation: RadiationModel,
    camera_label: str,
    bands: List[str],
    output_folder: Path,
    camera_type: str = "rgb",
    save_normalized: bool = True
) -> Optional[str]:
    """
    Save camera images to disk.
    
    Args:
        radiation: RadiationModel instance
        camera_label: Camera identifier
        bands: List of radiation bands
        output_folder: Output directory path
        camera_type: "rgb" or "multispectral"
        save_normalized: Save auto-scaled normalized image
        
    Returns:
        Primary image filename (for segmentation), or None if failed
    """
    images_folder = output_folder / "images"
    images_folder.mkdir(exist_ok=True)
    
    primary_image_filename = None
    
    try:
        if camera_type == 'multispectral':
            # Multispectral: save raw band data
            image_file = radiation.writeCameraImage(
                camera=camera_label,
                bands=bands,
                imagefile_base="multispectral",
                image_path=str(images_folder)
            )
            primary_image_filename = Path(image_file).name
            print(f"    ✓ Multispectral image saved: {primary_image_filename}")
        else:
            # RGB camera - save standard image
            image_file = radiation.writeCameraImage(
                camera=camera_label,
                bands=bands,
                imagefile_base="rgb",
                image_path=str(images_folder)
            )
            primary_image_filename = Path(image_file).name
            print(f"    ✓ RGB image saved: {primary_image_filename}")
        
        # Save normalized image (auto-scaled brightness)
        if save_normalized:
            try:
                norm_file = radiation.writeNormCameraImage(
                    camera=camera_label,
                    bands=bands,
                    imagefile_base="rgb_normalized",
                    image_path=str(images_folder)
                )
                print(f"    ✓ Normalized image saved: {Path(norm_file).name}")
            except Exception as e:
                print(f"    ⚠ Normalized image failed: {e}")
        
        return primary_image_filename
        
    except Exception as e:
        print(f"  ✗ Camera image export failed: {e}")
        return None


def save_segmentation_masks(
    radiation: RadiationModel,
    camera_label: str,
    primary_image_filename: str,
    output_folder: Path,
    primitive_data_field: str = "plant_part",
    object_class_id: int = 1
) -> bool:
    """
    Generate and save instance segmentation masks (COCO JSON format).
    
    Args:
        radiation: RadiationModel instance
        camera_label: Camera identifier
        primary_image_filename: Name of primary RGB/multispectral image
        output_folder: Output directory path
        primitive_data_field: Primitive data field containing labels
        object_class_id: Object class ID for labeled primitives
        
    Returns:
        True if successful, False otherwise
    """
    images_folder = output_folder / "images"
    
    print(f"  Generating segmentation masks...")
    try:
        radiation.writeImageSegmentationMasks(
            camera_label=camera_label,
            primitive_data_labels=primitive_data_field,
            object_class_ids=object_class_id,
            json_filename=str(images_folder / "segmentation.json"),
            image_file=primary_image_filename,
            append_file=False
        )
        print(f"    ✓ Segmentation masks saved: segmentation.json")
        print(f"    Field: {primitive_data_field} (values: ground, bean, wheat)")
        return True
    except Exception as e:
        print(f"    ⚠ Segmentation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
