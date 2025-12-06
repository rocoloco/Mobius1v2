"""
Unit tests for feedback operations.

Tests feedback storage, count updates, learning_active flag, and statistics.
Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
"""

import pytest
import uuid
from unittest.mock import Mock, patch
from mobius.storage.feedback import FeedbackStorage
from mobius.models.brand import Brand, BrandGuidelines, Color
from mobius.models.asset import Asset
from mobius.constants import LEARNING_ACTIVATION_THRESHOLD
from datetime import datetime, timezone


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    client = Mock()
    client.table = Mock(return_value=Mock())
    return client


@pytest.fixture
def test_brand():
    """Fixture for creating a test brand."""
    brand_id = str(uuid.uuid4())
    organization_id = str(uuid.uuid4())
    
    brand = Brand(
        brand_id=brand_id,
        organization_id=organization_id,
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=[
                Color(name="Red", hex="#FF0000", usage="primary"),
                Color(name="Green", hex="#00FF00", usage="secondary"),
            ]
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    return brand


@pytest.fixture
def test_asset(test_brand):
    """Fixture for creating a test asset."""
    asset_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    
    asset = Asset(
        asset_id=asset_id,
        brand_id=test_brand.brand_id,
        job_id=job_id,
        prompt="test prompt",
        image_url="https://example.com/image.png",
        compliance_score=85.0,
        generation_params={"prompt": "test prompt"},
        status="approved",
    )
    return asset


@pytest.mark.asyncio
@patch("mobius.storage.feedback.get_supabase_client")
async def test_create_feedback_approve(mock_get_client, mock_supabase_client, test_asset, test_brand):
    """
    Test feedback storage for approve action.
    
    Validates: Requirements 7.1
    """
    mock_get_client.return_value = mock_supabase_client
    
    feedback_id = str(uuid.uuid4())
    feedback_data = {
        "feedback_id": feedback_id,
        "asset_id": test_asset.asset_id,
        "brand_id": test_brand.brand_id,
        "action": "approve",
        "reason": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    # Mock the insert response
    mock_execute = Mock()
    mock_execute.data = [feedback_data]
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_execute
    
    # Create approve feedback
    feedback_storage = FeedbackStorage()
    feedback = await feedback_storage.create_feedback(
        asset_id=test_asset.asset_id,
        brand_id=test_brand.brand_id,
        action="approve",
        reason=None,
    )
    
    # Verify feedback was created
    assert feedback.feedback_id == feedback_id
    assert feedback.asset_id == test_asset.asset_id
    assert feedback.brand_id == test_brand.brand_id
    assert feedback.action == "approve"
    assert feedback.reason is None
    assert feedback.created_at is not None


@pytest.mark.asyncio
@patch("mobius.storage.feedback.get_supabase_client")
async def test_create_feedback_reject(mock_get_client, mock_supabase_client, test_asset, test_brand):
    """
    Test feedback storage for reject action with reason.
    
    Validates: Requirements 7.2
    """
    mock_get_client.return_value = mock_supabase_client
    
    feedback_id = str(uuid.uuid4())
    reason = "Colors don't match brand guidelines"
    feedback_data = {
        "feedback_id": feedback_id,
        "asset_id": test_asset.asset_id,
        "brand_id": test_brand.brand_id,
        "action": "reject",
        "reason": reason,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    # Mock the insert response
    mock_execute = Mock()
    mock_execute.data = [feedback_data]
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_execute
    
    # Create reject feedback
    feedback_storage = FeedbackStorage()
    feedback = await feedback_storage.create_feedback(
        asset_id=test_asset.asset_id,
        brand_id=test_brand.brand_id,
        action="reject",
        reason=reason,
    )
    
    # Verify feedback was created
    assert feedback.feedback_id == feedback_id
    assert feedback.asset_id == test_asset.asset_id
    assert feedback.brand_id == test_brand.brand_id
    assert feedback.action == "reject"
    assert feedback.reason == reason
    assert feedback.created_at is not None


@pytest.mark.asyncio
@patch("mobius.storage.feedback.get_supabase_client")
async def test_get_feedback_stats(mock_get_client, mock_supabase_client, test_brand):
    """
    Test feedback statistics retrieval.
    
    Validates: Requirements 7.4, 7.5
    """
    mock_get_client.return_value = mock_supabase_client
    
    # Mock feedback data
    feedback_data = [
        {"action": "approve"},
        {"action": "approve"},
        {"action": "approve"},
        {"action": "reject"},
        {"action": "reject"},
    ]
    
    # Mock brand data
    brand_data = [{"learning_active": False}]
    
    # Setup mocks
    mock_feedback_execute = Mock()
    mock_feedback_execute.data = feedback_data
    
    mock_brand_execute = Mock()
    mock_brand_execute.data = brand_data
    
    # Mock the select chains
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
        mock_feedback_execute,
        mock_brand_execute,
    ]
    
    # Get statistics
    feedback_storage = FeedbackStorage()
    stats = await feedback_storage.get_feedback_stats(test_brand.brand_id)
    
    # Verify statistics
    assert stats["total_feedback"] == 5
    assert stats["approvals"] == 3
    assert stats["rejections"] == 2
    assert stats["learning_active"] is False


@pytest.mark.asyncio
@patch("mobius.storage.feedback.get_supabase_client")
async def test_learning_active_at_threshold(mock_get_client, mock_supabase_client, test_brand):
    """
    Test learning_active flag at 50 feedback threshold.
    
    Validates: Requirements 7.3
    """
    mock_get_client.return_value = mock_supabase_client
    
    # Mock feedback data with exactly LEARNING_ACTIVATION_THRESHOLD items
    feedback_data = [{"action": "approve"} for _ in range(LEARNING_ACTIVATION_THRESHOLD)]
    
    # Mock brand data with learning_active = True
    brand_data = [{"learning_active": True}]
    
    # Setup mocks
    mock_feedback_execute = Mock()
    mock_feedback_execute.data = feedback_data
    
    mock_brand_execute = Mock()
    mock_brand_execute.data = brand_data
    
    # Mock the select chains
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
        mock_feedback_execute,
        mock_brand_execute,
    ]
    
    # Get statistics
    feedback_storage = FeedbackStorage()
    stats = await feedback_storage.get_feedback_stats(test_brand.brand_id)
    
    # Verify learning_active is True at threshold
    assert stats["total_feedback"] == LEARNING_ACTIVATION_THRESHOLD
    assert stats["learning_active"] is True


@pytest.mark.asyncio
@patch("mobius.storage.feedback.get_supabase_client")
async def test_learning_active_below_threshold(mock_get_client, mock_supabase_client, test_brand):
    """
    Test learning_active remains False below threshold.
    
    Validates: Requirements 7.3
    """
    mock_get_client.return_value = mock_supabase_client
    
    # Mock feedback data below threshold
    feedback_count = LEARNING_ACTIVATION_THRESHOLD - 1
    feedback_data = [{"action": "approve"} for _ in range(feedback_count)]
    
    # Mock brand data with learning_active = False
    brand_data = [{"learning_active": False}]
    
    # Setup mocks
    mock_feedback_execute = Mock()
    mock_feedback_execute.data = feedback_data
    
    mock_brand_execute = Mock()
    mock_brand_execute.data = brand_data
    
    # Mock the select chains
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
        mock_feedback_execute,
        mock_brand_execute,
    ]
    
    # Get statistics
    feedback_storage = FeedbackStorage()
    stats = await feedback_storage.get_feedback_stats(test_brand.brand_id)
    
    # Verify learning_active is still False
    assert stats["total_feedback"] == feedback_count
    assert stats["learning_active"] is False


@pytest.mark.asyncio
@patch("mobius.storage.feedback.get_supabase_client")
async def test_list_feedback_by_brand(mock_get_client, mock_supabase_client, test_brand):
    """
    Test listing feedback by brand.
    
    Validates: Requirements 7.5
    """
    mock_get_client.return_value = mock_supabase_client
    
    # Mock feedback data
    feedback_data = [
        {
            "feedback_id": str(uuid.uuid4()),
            "asset_id": str(uuid.uuid4()),
            "brand_id": test_brand.brand_id,
            "action": "approve",
            "reason": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        for _ in range(5)
    ]
    
    # Setup mock
    mock_execute = Mock()
    mock_execute.data = feedback_data
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_execute
    
    # List feedback
    feedback_storage = FeedbackStorage()
    feedback_list = await feedback_storage.list_feedback_by_brand(
        test_brand.brand_id,
        limit=10,
    )
    
    # Verify list
    assert len(feedback_list) == 5
    
    # Verify all feedback belongs to the brand
    for feedback in feedback_list:
        assert feedback.brand_id == test_brand.brand_id


@pytest.mark.asyncio
@patch("mobius.storage.feedback.get_supabase_client")
async def test_list_feedback_by_asset(mock_get_client, mock_supabase_client, test_asset, test_brand):
    """
    Test listing feedback by asset.
    
    Validates: Requirements 7.5
    """
    mock_get_client.return_value = mock_supabase_client
    
    # Mock feedback data
    feedback_data = [
        {
            "feedback_id": str(uuid.uuid4()),
            "asset_id": test_asset.asset_id,
            "brand_id": test_brand.brand_id,
            "action": "approve" if i % 2 == 0 else "reject",
            "reason": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        for i in range(3)
    ]
    
    # Setup mock
    mock_execute = Mock()
    mock_execute.data = feedback_data
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_execute
    
    # List feedback
    feedback_storage = FeedbackStorage()
    feedback_list = await feedback_storage.list_feedback_by_asset(test_asset.asset_id)
    
    # Verify list
    assert len(feedback_list) == 3
    
    # Verify all feedback belongs to the asset
    for feedback in feedback_list:
        assert feedback.asset_id == test_asset.asset_id
        assert feedback.brand_id == test_brand.brand_id
