"""
Unit tests for configuration management.

Tests Settings validation including pooler URL warning.
"""

import pytest
import warnings
import os
from mobius.config import Settings


def test_settings_loads_from_env():
    """Test that Settings loads values from environment variables."""
    # Set test environment variables
    os.environ["FAL_API_KEY"] = "test_fal_key"
    os.environ["GEMINI_API_KEY"] = "test_gemini_key"
    os.environ["SUPABASE_URL"] = "https://test.supabase.co"
    os.environ["SUPABASE_KEY"] = "test_key"

    settings = Settings()

    assert settings.fal_api_key == "test_fal_key"
    assert settings.gemini_api_key == "test_gemini_key"
    assert settings.supabase_url == "https://test.supabase.co"
    assert settings.supabase_key == "test_key"

    # Clean up
    del os.environ["FAL_API_KEY"]
    del os.environ["GEMINI_API_KEY"]
    del os.environ["SUPABASE_URL"]
    del os.environ["SUPABASE_KEY"]


def test_settings_default_values():
    """Test that Settings has correct default values."""
    settings = Settings()

    assert settings.max_generation_attempts == 3
    assert settings.compliance_threshold == 0.80
    assert settings.template_threshold == 0.95
    assert settings.job_expiry_hours == 24
    assert settings.webhook_retry_max == 5
    assert settings.brands_bucket == "brands"
    assert settings.assets_bucket == "assets"


def test_pooler_url_validation_warns_on_direct_connection():
    """Test that Settings warns when not using pooler URL."""
    # Direct connection URL (port 5432)
    direct_url = "postgresql://postgres.test:password@aws-0-us-east-1.supabase.com:5432/postgres"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        settings = Settings(supabase_url=direct_url, supabase_key="test")

        # Should have issued a warning
        assert len(w) == 1
        assert "pooler" in str(w[0].message).lower()
        assert "6543" in str(w[0].message)


def test_pooler_url_validation_no_warning_with_pooler():
    """Test that Settings does not warn when using pooler URL."""
    # Pooler URL (port 6543)
    pooler_url = (
        "postgresql://postgres.test:password@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    )

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        settings = Settings(supabase_url=pooler_url, supabase_key="test")

        # Should not have issued a warning
        assert len(w) == 0


def test_pooler_url_validation_no_warning_with_port_6543():
    """Test that Settings does not warn when URL contains port 6543."""
    # URL with port 6543 (even without 'pooler' in domain)
    url_with_6543 = "postgresql://postgres.test:password@aws-0-us-east-1.supabase.com:6543/postgres"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        settings = Settings(supabase_url=url_with_6543, supabase_key="test")

        # Should not have issued a warning
        assert len(w) == 0


def test_settings_case_insensitive():
    """Test that Settings accepts case-insensitive environment variables."""
    os.environ["fal_api_key"] = "test_key_lowercase"

    settings = Settings()

    assert settings.fal_api_key == "test_key_lowercase"

    # Clean up
    del os.environ["fal_api_key"]
