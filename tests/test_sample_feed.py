"""Test sample feed data."""

import pytest


def test_sample_feed_loading(sample_feed):
    """Test that sample feed can be loaded and has expected structure."""
    assert sample_feed is not None
    assert "Resorts" in sample_feed
    assert isinstance(sample_feed["Resorts"], list)
    assert len(sample_feed["Resorts"]) > 0

    # Check first resort
    resort = sample_feed["Resorts"][0]
    assert "Name" in resort
    assert "OperatingStatus" in resort
    assert "SnowReport" in resort
    assert "MountainAreas" in resort
    assert "CurrentConditions" in resort