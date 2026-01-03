"""
Collision avoidance configuration for realistic plant growth.

Configures soft collision avoidance and ground obstacle avoidance to prevent
plants from growing through each other or below ground level.
"""

from pyhelios import PlantArchitecture
from typing import List, Optional


def setup_collision_avoidance(
    plant_architecture: PlantArchitecture,
    view_half_angle_deg: float = 70.0,
    look_ahead_distance: float = 0.08,
    sample_count: int = 256,
    inertia_weight: float = 0.3
) -> None:
    """
    Enable and configure soft collision avoidance.
    
    Soft collision avoidance allows plants to detect and avoid growing into
    each other using a perception cone system. Plants sample rays within
    a cone to detect obstacles and adjust growth direction accordingly.
    
    Args:
        plant_architecture: PlantArchitecture instance
        view_half_angle_deg: Perception cone half-angle in degrees (default: 70°)
        look_ahead_distance: Ray sampling distance in meters (default: 0.08m = 8cm)
        sample_count: Number of ray samples for collision detection (default: 256)
        inertia_weight: Growth inertia weight 0-1, higher = more persistent direction
        
    Example:
        >>> with PlantArchitecture(context) as pa:
        ...     setup_collision_avoidance(pa)
        ...     # ... build plants and grow ...
        
    Reference:
        PyHelios Pattern 3: Soft collision with ground obstacle avoidance
    """
    # Configure soft collision parameters
    plant_architecture.setSoftCollisionAvoidanceParameters(
        view_half_angle_deg=view_half_angle_deg,
        look_ahead_distance=look_ahead_distance,
        sample_count=sample_count,
        inertia_weight=inertia_weight
    )
    
    # Set collision-relevant organs (leaves + internodes for realism)
    plant_architecture.setCollisionRelevantOrgans(
        include_internodes=True,
        include_leaves=True,
        include_petioles=False,  # Exclude for performance (recommended)
        include_flowers=False,
        include_fruit=False
    )
    
    # Enable soft collision avoidance
    plant_architecture.enableSoftCollisionAvoidance()
    
    print(f"    ✓ Soft collision enabled (view={view_half_angle_deg}°, lookahead={look_ahead_distance}m)")


def setup_ground_obstacle(
    plant_architecture: PlantArchitecture,
    ground_uuid: int,
    avoidance_distance: float = 0.1,
    enable_pruning: bool = True,
    enable_fruit_adjustment: bool = True
) -> None:
    """
    Enable ground obstacle avoidance to prevent plants growing below ground.
    
    Creates a solid obstacle at ground level (Z=0) that plants cannot penetrate.
    The avoidance_distance prevents organs from getting too close to the ground.
    
    Args:
        plant_architecture: PlantArchitecture instance
        ground_uuid: UUID of ground primitive (obstacle)
        avoidance_distance: Minimum distance from ground in meters (default: 0.1m)
        enable_pruning: Remove organs that penetrate obstacle (default: True)
        enable_fruit_adjustment: Adjust fruit positions to avoid ground (default: True)
        
    Example:
        >>> ground_uuid, margin = create_soil_plane(context, 1.0, 1.0)
        >>> with PlantArchitecture(context) as pa:
        ...     setup_ground_obstacle(pa, ground_uuid)
        
    Reference:
        PyHelios Pattern 3: Ground obstacle at Z=0 with avoidance_distance
    """
    plant_architecture.enableSolidObstacleAvoidance(
        obstacle_UUIDs=[ground_uuid],
        avoidance_distance=avoidance_distance,
        enable_fruit_adjustment=enable_fruit_adjustment,
        enable_obstacle_pruning=enable_pruning
    )
    
    print(f"    ✓ Ground clipping prevention enabled (distance={avoidance_distance}m)")


def setup_full_collision_system(
    plant_architecture: PlantArchitecture,
    ground_uuid: int,
    collision_params: Optional[dict] = None
) -> None:
    """
    Set up complete collision avoidance system (soft + ground obstacle).
    
    Convenience function that configures both soft collision avoidance
    and ground obstacle avoidance in one call.
    
    Args:
        plant_architecture: PlantArchitecture instance
        ground_uuid: UUID of ground primitive
        collision_params: Optional dict with collision parameters:
            - view_half_angle_deg (float)
            - look_ahead_distance (float)
            - sample_count (int)
            - inertia_weight (float)
            - ground_avoidance_distance (float)
            - enable_obstacle_pruning (bool)
            
    Example:
        >>> params = {"view_half_angle_deg": 80.0, "look_ahead_distance": 0.1}
        >>> setup_full_collision_system(pa, ground_uuid, params)
    """
    if collision_params is None:
        collision_params = {}
    
    # Soft collision parameters
    setup_collision_avoidance(
        plant_architecture,
        view_half_angle_deg=collision_params.get("view_half_angle_deg", 70.0),
        look_ahead_distance=collision_params.get("look_ahead_distance", 0.08),
        sample_count=collision_params.get("sample_count", 256),
        inertia_weight=collision_params.get("inertia_weight", 0.3)
    )
    
    # Ground obstacle
    setup_ground_obstacle(
        plant_architecture,
        ground_uuid,
        avoidance_distance=collision_params.get("ground_avoidance_distance", 0.1),
        enable_pruning=collision_params.get("enable_obstacle_pruning", True),
        enable_fruit_adjustment=collision_params.get("enable_fruit_adjustment", True)
    )
