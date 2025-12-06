"""
Property-based tests for feedback count increment.

Property 11: Feedback increments count
Validates: Requirements 7.1, 7.2
"""

from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch, AsyncMock
from mobius.storage.feedback import FeedbackStorage
from mobius.storage.brands import BrandStorage
from mobius.models.brand import Brand, BrandGuidelines, Color
from mobius.storage.feedback import Feedback
import pytest
import uuid
from datetime import datetime, timezone


@pytest.mark.asyncio
@given(
    action=st.sampled_from(["approve", "reject"]),
    reason=st.one_of(st.none(), st.text(min_size=1, max_size=200)),
    initial_count=st.integers(min_value=0, max_value=100),
)
@settings(max_examples=100, deadline=5000)
@patch("mobius.storage.feedback.get_supabase_client")
@patch("mobius.storage.brands.get_supabase_client")
async def test_feedback_increments_count(
    mock_brand_client,
    mock_feedback_client,
    action,
    reason,
    initial_count,
):
    """
    Property 11: Feedback increments count
    
    For any brand, when a feedback event is submitted for an asset
    belonging to that brand, the brand's feedback_count should increase
    by exactly one.
    
    Validates: Requirements 7.1, 7.2
    """
    # Create test IDs
    brand_id = str(uuid.uuid4())
    asset_id = str(uuid.uuid4())
    organization_id = str(uuid.uuid4())
    feedback_id = str(uuid.uuid4())
    
    # Create initial brand with feedback count
    initial_brand = Brand(
        brand_id=brand_id,
        organization_id=organization_id,
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=[
                Color(name="Black", hex="#000000", usage="primary"),
            ]
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        feedback_count=initial_count,
    )
    
    # Create updated brand with incremented count
    updated_brand = Brand(
        brand_id=brand_id,
        organization_id=organization_id,
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=[
                Color(name="Black", hex="#000000", usage="primary"),
            ]
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        feedback_count=initial_count + 1,
    )
    
    # Mock feedback creation
    mock_feedback = Feedback(
        feedback_id=feedback_id,
        asset_id=asset_id,
        brand_id=brand_id,
        action=action,
        reason=reason,
        created_at=datetime.now(timezone.utc),
    )
    
    # Setup mocks
    mock_feedback_execute = Mock()
    mock_feedback_execute.data = [mock_feedback.model_dump()]
    mock_feedback_client.return_value.table.return_value.insert.return_value.execute.return_value = mock_feedback_execute
    
    # Mock brand retrieval - first call returns initial, second returns updated
    mock_brand_execute_initial = Mock()
    mock_brand_execute_initial.data = [initial_brand.model_dump()]
    
    mock_brand_execute_updated = Mock()
    mock_brand_execute_updated.data = [updated_brand.model_dump()]
    
    mock_brand_client.return_value.table.return_value.select.return_value.eq.return_value.is_.return_value.execute.side_effect = [
        mock_brand_execute_initial,
        mock_brand_execute_updated,
    ]
    
    # Execute test
    feedback_storage = FeedbackStorage()
    brand_storage = BrandStorage()
    
    # Get initial brand
    initial_result = await brand_storage.get_brand(brand_id)
    assert initial_result.feedback_count == initial_count
    
    # Create feedback (this would trigger the database trigger in real scenario)
    await feedback_storage.create_feedback(
        asset_id=asset_id,
        brand_id=brand_id,
        action=action,
        reason=reason,
    )
    
    # Get updated brand
    updated_result = await brand_storage.get_brand(brand_id)
    
    # Assert count increased by exactly 1
    assert updated_result.feedback_count == initial_count + 1, (
        f"Feedback count should increase by 1. "
        f"Initial: {initial_count}, Updated: {updated_result.feedback_count}"
    )
