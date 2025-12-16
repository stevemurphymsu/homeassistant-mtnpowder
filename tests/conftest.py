"""Test configuration for MtnPowder integration."""

import json
from unittest.mock import Mock

import pytest


@pytest.fixture
def sample_feed():
    """Load sample feed data."""
    with open("tests/sample_feed.json", "r") as f:
        return json.load(f)


@pytest.fixture
def mock_api_response(sample_feed):
    """Mock API response."""
    return Mock(json=Mock(return_value=sample_feed))