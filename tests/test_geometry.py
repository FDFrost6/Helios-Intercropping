"""Tests for geometry modules."""

import pytest
import numpy as np
from intercropping.geometry.plants import generate_intercrop_positions
from intercropping.geometry.camera import calculate_nadir_camera_height


def test_generate_intercrop_positions():
    """Test intercrop position generation."""
    positions = generate_intercrop_positions(
        plot_width=1.0,
        plot_length=1.0,
        n_rows=4,
        row_spacing=0.21,
        bean_density=36,
        wheat_density=0,
        seed=42
    )
    
    # Check we got reasonable number of plants
    assert len(positions) > 0
    assert len(positions) < 40  # Should be ~31-32 with emergence rate
    
    # Check position format
    for species, x, y in positions:
        assert species in ['bean', 'wheat']
        assert 0 <= x <= 1.0
        assert 0 <= y <= 1.0


def test_calculate_nadir_camera_height():
    """Test camera height calculation."""
    height = calculate_nadir_camera_height(1.0, 1.0, fov_degrees=60.0)
    
    # For 1m x 1m plot with 60° FOV, height should be ~1.5-1.6m
    assert 1.4 < height < 1.8
    
    # Larger plot should need higher camera
    height_large = calculate_nadir_camera_height(2.0, 2.0, fov_degrees=60.0)
    assert height_large > height


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
