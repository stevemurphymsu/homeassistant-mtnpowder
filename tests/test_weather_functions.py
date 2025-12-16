"""Test MtnPowder weather utility functions."""

import pytest

from custom_components.mtnpowder.weather import _direction_to_bearing, _map_condition


def test_direction_to_bearing():
    """Test wind direction to bearing conversion."""
    assert _direction_to_bearing("N") == 0
    assert _direction_to_bearing("E") == 90
    assert _direction_to_bearing("S") == 180
    assert _direction_to_bearing("W") == 270
    assert _direction_to_bearing("NE") == 45
    assert _direction_to_bearing("SW") == 225
    assert _direction_to_bearing("invalid") is None


def test_map_condition():
    """Test weather condition mapping."""
    assert _map_condition("Clear") == "sunny"
    assert _map_condition("Cloudy") == "cloudy"
    assert _map_condition("Rainy") == "rainy"
    assert _map_condition("Snowy") == "snowy"
    assert _map_condition("Unknown") == "sunny"  # default