"""
Helios context creation and configuration.

Manages PyHelios Context lifecycle and datetime setup.
"""

import os
from pathlib import Path
from pyhelios import Context
import pyhelios
from typing import Tuple


def setup_helios_environment() -> None:
    """
    Set up Helios environment variables.
    
    PyHelios requires the HELIOS_BUILD environment variable to be set
    to access spectral libraries and other assets.
    """
    pyhelios_assets = Path(pyhelios.__file__).parent / "assets/build"
    os.environ['HELIOS_BUILD'] = str(pyhelios_assets)


def setup_helios_context(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int
) -> Context:
    """
    Create and configure a PyHelios Context with date/time.
    
    Args:
        year: Year (e.g., 2022)
        month: Month (1-12)
        day: Day of month (1-31)
        hour: Hour (0-23)
        minute: Minute (0-59)
        
    Returns:
        Configured PyHelios Context instance
        
    Example:
        >>> context = setup_helios_context(2022, 6, 14, 12, 0)
        >>> print(f"Context created for 2022-06-14 12:00")
        
    Note:
        The Context should be used in a context manager or manually closed
        when done to free resources.
    """
    # Ensure environment is set up
    setup_helios_environment()
    
    # Create context
    context = Context()
    context.setDate(year, month, day)
    context.setTime(hour, minute)
    
    print(f"  ✓ Date/Time: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}")
    
    return context


def parse_date_time(date_str: str, time_str: str) -> Tuple[int, int, int, int, int]:
    """
    Parse date and time strings into components.
    
    Args:
        date_str: Date string in format "YYYY-MM-DD"
        time_str: Time string in format "HH:MM"
        
    Returns:
        Tuple of (year, month, day, hour, minute)
        
    Example:
        >>> year, month, day, hour, minute = parse_date_time("2022-06-14", "12:00")
        >>> print(f"{year}-{month}-{day} {hour}:{minute}")
        2022-6-14 12:0
    """
    date_parts = date_str.split('-')
    year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
    
    hour, minute = map(int, time_str.split(':'))
    
    return year, month, day, hour, minute
