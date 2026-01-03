"""
Species and organ labeling for segmentation masks.

Applies primitive labels used by RadiationModel's writeImageSegmentationMasks()
to generate COCO JSON annotations.
"""

from pyhelios import Context
from typing import Dict, Tuple

from intercropping.config.constants import PLANT_PART_GROUND, PLANT_PART_BEAN


def apply_species_labels(
    context: Context,
    ground_uuid: int,
    plant_species_map: Dict[int, int]
) -> Tuple[int, int, int]:
    """
    Apply species labels to all primitives for segmentation.
    
    Simplified approach matching official PyHelios docs pattern:
    - Ground primitive labeled as "ground"
    - ALL other primitives labeled as "bean" (for monoculture)
    - For mixed crops, would need plant-specific UUID tracking
    
    Args:
        context: Helios Context
        ground_uuid: UUID of ground primitive
        plant_species_map: Dict mapping plant_id -> species_id (for future use)
        
    Returns:
        Tuple of (total_labeled, bean_count, wheat_count)
        
    Example:
        >>> plant_map = build_plants(context, pa, positions)
        >>> labeled, bean, wheat = apply_species_labels(context, ground_uuid, plant_map)
        
    Note:
        Labels must be strings via setPrimitiveDataString(), not integers.
        The field name "plant_part" is used by RadiationModel segmentation.
    """
    labeled_count = 0
    bean_primitives = 0
    wheat_primitives = 0
    
    # Get all UUIDs
    all_uuids = context.getAllUUIDs()
    
    # Label ground using "plant_part" field (matching official docs)
    context.setPrimitiveDataString(ground_uuid, "plant_part", PLANT_PART_GROUND)
    labeled_count += 1
    
    # Label ALL other primitives as bean
    # (For monoculture; intercrop would need per-plant UUID tracking)
    for uuid in all_uuids:
        if uuid != ground_uuid:
            context.setPrimitiveDataString(uuid, "plant_part", PLANT_PART_BEAN)
            bean_primitives += 1
            labeled_count += 1
    
    print(f"    Labeled {labeled_count:,} total primitives")
    print(f"      - 1 ground primitive")
    print(f"      - {bean_primitives:,} bean primitives")
    
    return labeled_count, bean_primitives, wheat_primitives
