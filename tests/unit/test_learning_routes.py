"""
Tests for learning routes.

Tests API endpoints for learning system management.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
from mobius.api.learning_routes import (
    update_learning_settings_handler,
    get_learning_settings_handler,
    get_learning_dashboard_handler,
    get_learning_patterns_handler,
    export_learning_data_handler,
    delete_learning_data_handler,
    get_learning_audit_log_handler,
)
from mobius.models.learning import (
    LearningSettings,
    BrandPattern,
    LearningAuditLog,
    PrivacyTier,
)
from mobius.api.schemas import UpdateLearningSettingsRequest


# Fixtures

@pytest.fixture
def sample_learning_settings():
    """Sample learning settings."""
    return LearningSettings(
        brand_id="brand-123",
        privacy_tier=PrivacyTier.PRIVATE,
        consent_date=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_brand_pattern():
    """Sample brand pattern."""
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
def sample_audit_log():
    """Sample audit log."""
    return LearningAuditLog(
        log_id="log-123",
        brand_id="brand-123",
        action="privacy_tier_changed",
        details={"from": "OFF", "to": "PRIVATE"},
        timestamp=datetime.now(timezone.utc),
    )


# Update Learning Settings Tests

@pytest.mark.asyncio
@patch("mobius.api.learning_routes.BrandStorage")
@patch("mobius.api.learning_routes.LearningStorage")
@patch("mobius.api.learning_routes.generate_request_id")
async def test_update_learning_settings_handler(
    mock_gen_id, mock_learning_storage_class, mock_brand_storage_class, sample_learning_settings
):
    """Test updating learning settings."""
    mock_gen_id.return_value = "req-123"
    
    # Mock BrandStorage
    mock_brand_storage = Mock()
    mock_brand_storage_class.return_value = mock_brand_storage
    mock_brand_storage.get_brand = AsyncMock(return_value=Mock(brand_id="brand-123"))
    
    # Mock LearningStorage
    mock_learning_storage = Mock()
    mock_learning_storage_class.return_value = mock_learning_storage
    
    # Mock get_settings to return existing settings
    mock_learning_storage.get_settings = AsyncMock(return_value=sample_learning_settings)
    
    # Mock update_settings
    updated_settings = sample_learning_settings.model_copy()
    updated_settings.privacy_tier = PrivacyTier.SHARED
    mock_learning_storage.update_settings = AsyncMock(return_value=updated_settings)
    
    request = UpdateLearningSettingsRequest(
        privacy_tier=PrivacyTier.SHARED,
        consent_given=True
    )
    
    response = await update_learning_settings_handler("brand-123", request)
    
    assert response.privacy_tier == "shared"
    assert response.request_id == "req-123"
    mock_learning_storage.update_settings.assert_called_once()


@pytest.mark.asyncio
@patch("mobius.api.learning_routes.BrandStorage")
@patch("mobius.api.learning_routes.LearningStorage")
@patch("mobius.api.learning_routes.generate_request_id")
async def test_update_learning_settings_creates_if_not_exists(
    mock_gen_id, mock_learning_storage_class, mock_brand_storage_class, sample_learning_settings
):
    """Test creating learning settings if they don't exist."""
    mock_gen_id.return_value = "req-123"
    
    # Mock BrandStorage
    mock_brand_storage = Mock()
    mock_brand_storage_class.return_value = mock_brand_storage
    mock_brand_storage.get_brand = AsyncMock(return_value=Mock(brand_id="brand-123"))
    
    # Mock LearningStorage
    mock_learning_storage = Mock()
    mock_learning_storage_class.return_value = mock_learning_storage
    
    # Mock get_settings to return None (doesn't exist)
    mock_learning_storage.get_settings = AsyncMock(return_value=None)
    
    # Mock create_settings
    mock_learning_storage.create_settings = AsyncMock(return_value=sample_learning_settings)
    
    request = UpdateLearningSettingsRequest(
        privacy_tier=PrivacyTier.PRIVATE,
        consent_given=False
    )
    
    response = await update_learning_settings_handler("brand-123", request)
    
    assert response.brand_id == "brand-123"
    mock_learning_storage.create_settings.assert_called_once()


# Get Learning Settings Tests

@pytest.mark.asyncio
@patch("mobius.api.learning_routes.BrandStorage")
@patch("mobius.api.learning_routes.LearningStorage")
@patch("mobius.api.learning_routes.generate_request_id")
async def test_get_learning_settings_handler(
    mock_gen_id, mock_learning_storage_class, mock_brand_storage_class, sample_learning_settings
):
    """Test getting learning settings."""
    mock_gen_id.return_value = "req-123"
    
    # Mock BrandStorage
    mock_brand_storage = Mock()
    mock_brand_storage_class.return_value = mock_brand_storage
    mock_brand_storage.get_brand = AsyncMock(return_value=Mock(brand_id="brand-123"))
    
    # Mock LearningStorage
    mock_learning_storage = Mock()
    mock_learning_storage_class.return_value = mock_learning_storage
    mock_learning_storage.get_settings = AsyncMock(return_value=sample_learning_settings)
    
    response = await get_learning_settings_handler("brand-123")
    
    assert response.brand_id == "brand-123"
    assert response.privacy_tier == "private"
    assert response.request_id == "req-123"


@pytest.mark.asyncio
@patch("mobius.api.learning_routes.BrandStorage")
@patch("mobius.api.learning_routes.LearningStorage")
@patch("mobius.api.learning_routes.generate_request_id")
async def test_get_learning_settings_not_found(
    mock_gen_id, mock_learning_storage_class, mock_brand_storage_class
):
    """Test getting non-existent learning settings."""
    mock_gen_id.return_value = "req-123"
    
    # Mock BrandStorage to return None (brand not found)
    mock_brand_storage = Mock()
    mock_brand_storage_class.return_value = mock_brand_storage
    mock_brand_storage.get_brand = AsyncMock(return_value=None)
    
    # Mock LearningStorage
    mock_learning_storage = Mock()
    mock_learning_storage_class.return_value = mock_learning_storage
    mock_learning_storage.get_settings = AsyncMock(return_value=None)
    
    from mobius.api.errors import NotFoundError
    
    with pytest.raises(NotFoundError):
        await get_learning_settings_handler("nonexistent")


# Get Learning Dashboard Tests

@pytest.mark.asyncio
@patch("mobius.api.learning_routes.BrandStorage")
@patch("mobius.api.learning_routes.LearningStorage")
@patch("mobius.api.learning_routes.generate_request_id")
async def test_get_learning_dashboard_handler(
    mock_gen_id, mock_learning_storage_class, mock_brand_storage_class,
    sample_learning_settings, sample_brand_pattern
):
    """Test getting learning dashboard."""
    mock_gen_id.return_value = "req-123"
    
    # Mock BrandStorage
    mock_brand_storage = Mock()
    mock_brand_storage_class.return_value = mock_brand_storage
    mock_brand_storage.get_brand = AsyncMock(return_value=Mock(brand_id="brand-123", cohort=None))
    
    # Mock LearningStorage
    mock_learning_storage = Mock()
    mock_learning_storage_class.return_value = mock_learning_storage
    mock_learning_storage.get_settings = AsyncMock(return_value=sample_learning_settings)
    mock_learning_storage.get_brand_patterns = AsyncMock(return_value=[sample_brand_pattern])
    
    response = await get_learning_dashboard_handler("brand-123")
    
    assert response.brand_id == "brand-123"
    assert response.privacy_tier == "private"
    assert len(response.patterns_learned) == 1
    assert response.request_id == "req-123"


# Get Learning Patterns Tests

@pytest.mark.asyncio
@patch("mobius.api.learning_routes.BrandStorage")
@patch("mobius.api.learning_routes.LearningStorage")
@patch("mobius.api.learning_routes.generate_request_id")
async def test_get_learning_patterns_handler(
    mock_gen_id, mock_learning_storage_class, mock_brand_storage_class, sample_brand_pattern
):
    """Test getting learning patterns."""
    mock_gen_id.return_value = "req-123"
    
    # Mock BrandStorage
    mock_brand_storage = Mock()
    mock_brand_storage_class.return_value = mock_brand_storage
    mock_brand_storage.get_brand = AsyncMock(return_value=Mock(brand_id="brand-123"))
    
    # Mock LearningStorage
    mock_learning_storage = Mock()
    mock_learning_storage_class.return_value = mock_learning_storage
    mock_learning_storage.get_brand_patterns = AsyncMock(return_value=[sample_brand_pattern])
    
    response = await get_learning_patterns_handler("brand-123")
    
    assert len(response.patterns) == 1
    assert response.patterns[0].pattern_id == "pattern-123"
    assert response.request_id == "req-123"


# Export Learning Data Tests

@pytest.mark.asyncio
@patch("mobius.api.learning_routes.BrandStorage")
@patch("mobius.api.learning_routes.PrivateLearningEngine")
@patch("mobius.api.learning_routes.generate_request_id")
async def test_export_learning_data_handler(
    mock_gen_id, mock_engine_class, mock_brand_storage_class, sample_learning_settings, sample_brand_pattern
):
    """Test exporting learning data."""
    mock_gen_id.return_value = "req-123"
    
    # Mock BrandStorage
    mock_brand_storage = Mock()
    mock_brand_storage_class.return_value = mock_brand_storage
    mock_brand_storage.get_brand = AsyncMock(return_value=Mock(brand_id="brand-123"))
    
    # Mock PrivateLearningEngine
    mock_engine = Mock()
    mock_engine_class.return_value = mock_engine
    mock_engine.export_learning_data = AsyncMock(return_value={
        "brand_id": "brand-123",
        "export_date": datetime.now(timezone.utc).isoformat(),
        "settings": sample_learning_settings.model_dump(),
        "patterns": [sample_brand_pattern.model_dump()],
        "audit_log": [],
        "metadata": {}
    })
    
    response = await export_learning_data_handler("brand-123")
    
    assert response.brand_id == "brand-123"
    assert response.settings is not None
    assert len(response.patterns) == 1
    assert response.request_id == "req-123"


# Delete Learning Data Tests

@pytest.mark.asyncio
@patch("mobius.api.learning_routes.BrandStorage")
@patch("mobius.api.learning_routes.PrivateLearningEngine")
@patch("mobius.api.learning_routes.generate_request_id")
async def test_delete_learning_data_handler(
    mock_gen_id, mock_engine_class, mock_brand_storage_class
):
    """Test deleting learning data."""
    mock_gen_id.return_value = "req-123"
    
    # Mock BrandStorage
    mock_brand_storage = Mock()
    mock_brand_storage_class.return_value = mock_brand_storage
    mock_brand_storage.get_brand = AsyncMock(return_value=Mock(brand_id="brand-123"))
    
    # Mock PrivateLearningEngine
    mock_engine = Mock()
    mock_engine_class.return_value = mock_engine
    mock_engine.delete_learning_data = AsyncMock(return_value=True)
    
    response = await delete_learning_data_handler("brand-123")
    
    assert response.brand_id == "brand-123"
    assert response.deleted == True
    assert response.request_id == "req-123"
    mock_engine.delete_learning_data.assert_called_once_with("brand-123")


# Get Learning Audit Log Tests

@pytest.mark.asyncio
@patch("mobius.api.learning_routes.BrandStorage")
@patch("mobius.api.learning_routes.LearningStorage")
@patch("mobius.api.learning_routes.generate_request_id")
async def test_get_learning_audit_log_handler(
    mock_gen_id, mock_learning_storage_class, mock_brand_storage_class, sample_audit_log
):
    """Test getting learning audit log."""
    mock_gen_id.return_value = "req-123"
    
    # Mock BrandStorage
    mock_brand_storage = Mock()
    mock_brand_storage_class.return_value = mock_brand_storage
    mock_brand_storage.get_brand = AsyncMock(return_value=Mock(brand_id="brand-123"))
    
    # Mock LearningStorage
    mock_learning_storage = Mock()
    mock_learning_storage_class.return_value = mock_learning_storage
    mock_learning_storage.get_audit_log = AsyncMock(return_value=[sample_audit_log])
    
    response = await get_learning_audit_log_handler("brand-123")
    
    assert len(response.entries) == 1
    assert response.entries[0].log_id == "log-123"
    assert response.request_id == "req-123"
