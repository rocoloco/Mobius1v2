"""
Pytest configuration and fixtures.

Provides common fixtures for testing.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime
from mobius.models.brand import Brand, BrandGuidelines, BrandColors, BrandTypography, BrandLogo


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
    """Sample brand entity for testing."""
    return Brand(
        brand_id="test-brand-123",
        organization_id="test-org-456",
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=BrandColors(primary=["#FF0000", "#00FF00"], secondary=["#0000FF"]),
            typography=BrandTypography(font_families=["Arial"]),
            logo=BrandLogo(),
            tone_of_voice=["Professional", "Friendly"],
            visual_rules=["Use bold colors"],
            dos_and_donts={},
        ),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
