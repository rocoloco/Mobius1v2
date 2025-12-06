"""
Tests for learning storage module.

Tests CRUD operations for learning settings, patterns, and audit logs.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from mobius.storage.learning import LearningStorage
from mobius.models.learning import (
    LearningSettings,
    BrandPattern,
    IndustryPattern,
    LearningAuditLog,
    PrivacyTier
)


# Fixtures

@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client."""
    client = Mock()
    client.table = Mock(return_value=client)
    client.select = Mock(return_value=client)
    client.insert = Mock(return_value=client)
    client.update = Mock(return_value=client)
    client.delete = Mock(return_value=client)
    client.eq = Mock(return_value=client)
    client.order = Mock(return_value=client)
    client.limit = Mock(return_value=client)
    client.execute = Mock()
    return client


@pytest.fixture
def sample_learning_settings():
    """Sample learning settings for testing."""
    return LearningSettings(
        brand_id="brand-123",
        privacy_tier=PrivacyTier.PRIVATE,
        consent_given=False,
        consent_timestamp=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_brand_pattern():
    """Sample brand pattern for testing."""
    return BrandPattern(
        pattern_id="pattern-123",
        brand_id="brand-123",
        pattern_type="color_preference",
        pattern_data={"primary": "#FF0000"},
        confidence_score=0.85,
        sample_count=10,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_industry_pattern():
    """Sample industry pattern for testing."""
    return IndustryPattern(
        pattern_id="industry-pattern-123",
        cohort="fashion",
        pattern_type="color_preference",
        pattern_data={"primary": "#FF0000"},
        contributor_count=5,
        noise_level=0.1,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_audit_log():
    """Sample audit log for testing."""
    return LearningAuditLog(
        log_id="log-123",
        brand_id="brand-123",
        action="privacy_tier_changed",
        details={"from": "OFF", "to": "PRIVATE"},
        timestamp=datetime.now(timezone.utc),
    )


# LearningStorage Tests

@pytest.mark.asyncio
@patch("mobius.storage.learning.get_supabase_client")
async def test_learning_storage_get_settings(
    mock_get_client, mock_supabase_client, sample_learning_settings
):
    """Test getting learning settings."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(
        data=[sample_learning_settings.model_dump()]
    )
    
    storage = LearningStorage()
    result = await storage.get_settings("brand-123")
    
    assert result is not None
    assert result.brand_id == "brand-123"
    assert result.privacy_tier == PrivacyTier.PRIVATE
    mock_supabase_client.table.assert_called_with("learning_settings")


@pytest.mark.asyncio
@patch("mobius.storage.learning.get_supabase_client")
async def test_learning_storage_get_settings_not_found(
    mock_get_client, mock_supabase_client
):
    """Test getting non-existent learning settings."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[])
    
    storage = LearningStorage()
    result = await storage.get_settings("nonexistent")
    
    assert result is None


@pytest.mark.asyncio
@patch("mobius.storage.learning.get_supabase_client")
async def test_learning_storage_create_settings(
    mock_get_client, mock_supabase_client, sample_learning_settings
):
    """Test creating learning settings."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(
        data=[sample_learning_settings.model_dump()]
    )
    
    storage = LearningStorage()
    result = await storage.create_settings(sample_learning_settings)
    
    assert result.brand_id == "brand-123"
    mock_supabase_client.insert.assert_called_once()


@pytest.mark.asyncio
@patch("mobius.storage.learning.get_supabase_client")
async def test_learning_storage_update_settings(
    mock_get_client, mock_supabase_client, sample_learning_settings
):
    """Test updating learning settings."""
    mock_get_client.return_value = mock_supabase_client
    updated_settings = sample_learning_settings.model_copy()
    updated_settings.privacy_tier = PrivacyTier.SHARED
    mock_supabase_client.execute.return_value = Mock(
        data=[updated_settings.model_dump()]
    )
    
    storage = LearningStorage()
    result = await storage.update_settings(
        "brand-123", {"privacy_tier": PrivacyTier.SHARED}
    )
    
    assert result.privacy_tier == PrivacyTier.SHARED
    mock_supabase_client.update.assert_called_once()


@pytest.mark.asyncio
@patch("mobius.storage.learning.get_supabase_client")
async def test_learning_storage_get_brand_patterns(
    mock_get_client, mock_supabase_client, sample_brand_pattern
):
    """Test getting brand patterns."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(
        data=[sample_brand_pattern.model_dump()]
    )
    
    storage = LearningStorage()
    result = await storage.get_brand_patterns("brand-123")
    
    assert len(result) == 1
    assert result[0].pattern_id == "pattern-123"
    mock_supabase_client.table.assert_called_with("brand_patterns")


@pytest.mark.asyncio
@patch("mobius.storage.learning.get_supabase_client")
async def test_learning_storage_get_brand_patterns_with_type(
    mock_get_client, mock_supabase_client, sample_brand_pattern
):
    """Test getting brand patterns with type filter."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(
        data=[sample_brand_pattern.model_dump()]
    )
    
    storage = LearningStorage()
    result = await storage.get_brand_patterns("brand-123", pattern_type="color_preference")
    
    assert len(result) == 1
    # Verify eq was called twice: once for brand_id, once for pattern_type
    assert mock_supabase_client.eq.call_count == 2


@pytest.mark.asyncio
@patch("mobius.storage.learning.get_supabase_client")
async def test_learning_storage_create_brand_pattern(
    mock_get_client, mock_supabase_client, sample_brand_pattern
):
    """Test creating a brand pattern."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(
        data=[sample_brand_pattern.model_dump()]
    )
    
    storage = LearningStorage()
    result = await storage.create_brand_pattern(sample_brand_pattern)
    
    assert result.pattern_id == "pattern-123"
    mock_supabase_client.insert.assert_called_once()


@pytest.mark.asyncio
@patch("mobius.storage.learning.get_supabase_client")
async def test_learning_storage_delete_brand_patterns(
    mock_get_client, mock_supabase_client, sample_brand_pattern
):
    """Test deleting brand patterns."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(
        data=[sample_brand_pattern.model_dump()]
    )
    
    storage = LearningStorage()
    result = await storage.delete_brand_patterns("brand-123")
    
    assert result == 1
    mock_supabase_client.delete.assert_called_once()


@pytest.mark.asyncio
@patch("mobius.storage.learning.get_supabase_client")
async def test_learning_storage_get_industry_patterns(
    mock_get_client, mock_supabase_client, sample_industry_pattern
):
    """Test getting industry patterns."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(
        data=[sample_industry_pattern.model_dump()]
    )
    
    storage = LearningStorage()
    result = await storage.get_industry_patterns("fashion")
    
    assert len(result) == 1
    assert result[0].cohort == "fashion"
    mock_supabase_client.table.assert_called_with("industry_patterns")


@pytest.mark.asyncio
@patch("mobius.storage.learning.get_supabase_client")
async def test_learning_storage_create_industry_pattern(
    mock_get_client, mock_supabase_client, sample_industry_pattern
):
    """Test creating an industry pattern."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(
        data=[sample_industry_pattern.model_dump()]
    )
    
    storage = LearningStorage()
    result = await storage.create_industry_pattern(sample_industry_pattern)
    
    assert result.pattern_id == "industry-pattern-123"
    mock_supabase_client.insert.assert_called_once()


@pytest.mark.asyncio
@patch("mobius.storage.learning.get_supabase_client")
async def test_learning_storage_get_audit_log(
    mock_get_client, mock_supabase_client, sample_audit_log
):
    """Test getting audit log."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(
        data=[sample_audit_log.model_dump()]
    )
    
    storage = LearningStorage()
    result = await storage.get_audit_log("brand-123")
    
    assert len(result) == 1
    assert result[0].log_id == "log-123"
    mock_supabase_client.table.assert_called_with("learning_audit_log")


@pytest.mark.asyncio
@patch("mobius.storage.learning.get_supabase_client")
async def test_learning_storage_create_audit_log(
    mock_get_client, mock_supabase_client, sample_audit_log
):
    """Test creating an audit log entry."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(
        data=[sample_audit_log.model_dump()]
    )
    
    storage = LearningStorage()
    result = await storage.create_audit_log(sample_audit_log)
    
    assert result.log_id == "log-123"
    mock_supabase_client.insert.assert_called_once()
