"""
Pytest configuration and fixtures.

Provides common fixtures for testing.
"""

import os
import pytest
from unittest.mock import Mock
from datetime import datetime, timezone
from hypothesis import settings, Verbosity
from mobius.models.brand import Brand, BrandGuidelines, Color, Typography, LogoRule


# Configure Hypothesis profiles for different test environments
settings.register_profile(
    "ci",
    max_examples=10,
    deadline=None,
    verbosity=Verbosity.normal
)

settings.register_profile(
    "dev",
    max_examples=100,
    deadline=None,
    verbosity=Verbosity.normal
)

# Load profile based on environment variable
if os.getenv("CI") or os.getenv("QUICK_TESTS"):
    settings.load_profile("ci")
else:
    settings.load_profile("dev")


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for unit tests."""
    return Mock()


@pytest.fixture
def mock_gemini():
    """Mock Gemini API client."""
    mock = Mock()
    mock.analyze_image.return_value = {
        "overall_score": 85,
        "approved": True,
        "categories": [],
    }
    return mock


@pytest.fixture
def sample_brand():
    """Sample brand entity for testing with Digital Twin schema."""
    return Brand(
        brand_id="test-brand-123",
        organization_id="test-org-456",
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=[
                Color(name="Primary Red", hex="#FF0000", usage="primary"),
                Color(name="Primary Green", hex="#00FF00", usage="primary"),
                Color(name="Secondary Blue", hex="#0000FF", usage="secondary"),
            ],
            typography=[
                Typography(family="Arial", weights=["400", "700"], usage="Body text")
            ],
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
