"""
Plant positioning and growth management.

Handles realistic intercrop positioning with row-based patterns and random mixing,
plus plant building with collision avoidance.
"""

import numpy as np
from pyhelios import Context, PlantArchitecture
from pyhelios.types import vec3
from typing import List, Tuple, Dict, Optional

from intercropping.config.constants import (
    BEAN_EMERGENCE_RATE,
    WHEAT_EMERGENCE_RATE,
    SPECIES_BEAN,
    SPECIES_WHEAT,
)


def generate_intercrop_positions(
    plot_width: float,
    plot_length: float,
    n_rows: int,
    row_spacing: float,
    bean_density: float,
    wheat_density: float,
    bean_emergence: float = BEAN_EMERGENCE_RATE,
    wheat_emergence: float = WHEAT_EMERGENCE_RATE,
    seed: int = 42
) -> List[Tuple[str, float, float]]:
    """
    Generate realistic intercrop positions with random mixing within rows.
    
    Uses row-based planting pattern with random mixing within each row, matching
    real experimental designs. Includes realistic emergence rates based on
    literature (Cook & Veseth 1991, Lafond et al. 2008).
    
    Args:
        plot_width: Plot width in meters
        plot_length: Plot length in meters
        n_rows: Number of planting rows
        row_spacing: Distance between rows in meters
        bean_density: Bean sowing density (seeds/m²)
        wheat_density: Wheat sowing density (seeds/m²)
        bean_emergence: Bean emergence rate (0.0-1.0)
        wheat_emergence: Wheat emergence rate (0.0-1.0)
        seed: Random seed for reproducibility
        
    Returns:
        List of (species, x, y) tuples where species is 'bean' or 'wheat'
        
    Example:
        >>> positions = generate_intercrop_positions(1.0, 1.0, 4, 0.21, 36, 18)
        >>> print(f"Generated {len(positions)} plants")
    """
    np.random.seed(seed)
    
    plot_area = plot_width * plot_length
    
    # Calculate seeds sown → emerged plants
    bean_seeds = int(bean_density * plot_area)
    wheat_seeds = int(wheat_density * plot_area)
    bean_emerged = int(bean_seeds * bean_emergence)
    wheat_emerged = int(wheat_seeds * wheat_emergence)
    
    total_plants = bean_emerged + wheat_emerged
    
    print(f"  Sowing simulation:")
    print(f"    Bean: {bean_seeds} seeds → {bean_emerged} emerged ({bean_emergence*100:.1f}%)")
    print(f"    Wheat: {wheat_seeds} seeds → {wheat_emerged} emerged ({wheat_emergence*100:.1f}%)")
    print(f"    Total: {total_plants} plants")
    
    # Create randomly mixed plant list
    plant_types = ['bean'] * bean_emerged + ['wheat'] * wheat_emerged
    np.random.shuffle(plant_types)
    
    # Calculate row positions
    row_y_positions = np.linspace(row_spacing, plot_length - row_spacing, n_rows)
    
    # Distribute plants across rows
    plants_per_row = total_plants // n_rows
    remainder = total_plants % n_rows
    
    positions = []
    plant_idx = 0
    
    for row_idx, row_y in enumerate(row_y_positions):
        n_plants_this_row = plants_per_row + (1 if row_idx < remainder else 0)
        
        if n_plants_this_row > 0:
            base_spacing = plot_width / (n_plants_this_row + 1)
            
            for i in range(n_plants_this_row):
                if plant_idx >= total_plants:
                    break
                    
                species = plant_types[plant_idx]
                
                # Add jitter to prevent perfect grid alignment
                x = base_spacing * (i + 1) + np.random.uniform(-0.02, 0.02)  # ±2cm along-row
                y = row_y + np.random.uniform(-0.015, 0.015)  # ±1.5cm cross-row
                
                # Clip to plot boundaries
                x = np.clip(x, 0.05, plot_width - 0.05)
                y = np.clip(y, 0.05, plot_length - 0.05)
                
                positions.append((species, x, y))
                plant_idx += 1
    
    n_bean = sum(1 for s, _, _ in positions if s == 'bean')
    n_wheat = sum(1 for s, _, _ in positions if s == 'wheat')
    
    print(f"  Final: {n_bean} bean + {n_wheat} wheat = {len(positions)} plants")
    print(f"  Densities: {n_bean/plot_area:.1f} bean/m², {n_wheat/plot_area:.1f} wheat/m²")
    
    return positions


def build_plants(
    context: Context,
    plant_architecture: PlantArchitecture,
    positions: List[Tuple[str, float, float]],
    initial_age: float = 5.0,
    margin: float = 0.3
) -> Dict[int, int]:
    """
    Build plants at specified positions and age.
    
    Creates plant instances using PlantArchitecture, starting at a young age
    (typically 5 days) before collision-aware growth is applied.
    
    Args:
        context: Helios Context
        plant_architecture: PlantArchitecture instance
        positions: List of (species, x, y) tuples
        initial_age: Initial plant age in days
        margin: Soil margin offset to apply to positions
        
    Returns:
        Dictionary mapping plant_id -> species_id for segmentation
        
    Example:
        >>> with Context() as ctx, PlantArchitecture(ctx) as pa:
        ...     positions = generate_intercrop_positions(1.0, 1.0, 4, 0.21, 36, 0)
        ...     plant_map = build_plants(ctx, pa, positions)
    """
    plant_species_map = {}
    
    n_bean = sum(1 for s, _, _ in positions if s == 'bean')
    n_wheat = sum(1 for s, _, _ in positions if s == 'wheat')
    
    # Build bean plants
    if n_bean > 0:
        plant_architecture.loadPlantModelFromLibrary("bean")
        print(f"    ✓ Loaded bean model")
        
        bean_count = 0
        for species, x, y in positions:
            if species == 'bean':
                plant_id = plant_architecture.buildPlantInstanceFromLibrary(
                    vec3(float(x + margin), float(y + margin), 0.0),
                    float(initial_age)
                )
                plant_species_map[plant_id] = SPECIES_BEAN
                bean_count += 1
        print(f"    ✓ Built {bean_count} bean plants at age {initial_age} days")
    
    # Build wheat plants
    if n_wheat > 0:
        plant_architecture.loadPlantModelFromLibrary("wheat")
        print(f"    ✓ Loaded wheat model")
        
        wheat_count = 0
        for species, x, y in positions:
            if species == 'wheat':
                plant_id = plant_architecture.buildPlantInstanceFromLibrary(
                    vec3(float(x + margin), float(y + margin), 0.0),
                    float(initial_age)
                )
                plant_species_map[plant_id] = SPECIES_WHEAT
                wheat_count += 1
        print(f"    ✓ Built {wheat_count} wheat plants at age {initial_age} days")
    
    return plant_species_map


def grow_plants(
    plant_architecture: PlantArchitecture,
    growth_time: float
) -> None:
    """
    Advance plant growth by specified time period.
    
    Growth happens with collision avoidance active if it has been enabled.
    
    Args:
        plant_architecture: PlantArchitecture instance
        growth_time: Time to advance in days
        
    Example:
        >>> with PlantArchitecture(context) as pa:
        ...     # ... setup collision avoidance ...
        ...     grow_plants(pa, 35.0)  # Grow for 35 days
    """
    if growth_time > 0:
        print(f"\n  Growing plants for {growth_time} days with collision avoidance...")
        plant_architecture.advanceTime(growth_time)
        print(f"    ✓ Growth complete")
