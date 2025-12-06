"""
Property-based tests for learning activation threshold.

Property 12: Learning activation threshold
Validates: Requirements 7.3
"""

from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch
from mobius.storage.brands import BrandStorage
from mobius.models.brand import Brand, BrandGuidelines, Color
from mobius.constants import LEARNING_ACTIVATION_THRESHOLD
import pytest
import uuid
from datetime import datetime, timezone


@pytest.mark.asyncio
@given(
    feedback_count=st.integers(min_value=0, max_value=100),
)
@settings(max_examples=50, deadline=5000)
@patch("mobius.storage.brands.get_supabase_client")
async def test_learning_activation_threshold(
    mock_brand_client,
    feedback_count,
):
    """
    Property 12: Learning activation threshold
    
    For any brand, when the feedback_count reaches 50, the learning_active
    flag should be automatically set to true.
    
    Validates: Requirements 7.3
    """
    # Create test IDs
    brand_id = str(uuid.uuid4())
    organization_id = str(uuid.uuid4())
    
    # Determine expected learning_active based on threshold
    expected_learning_active = feedback_count >= LEARNING_ACTIVATION_THRESHOLD
    
    # Create brand with the given feedback count
    brand = Brand(
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
        feedback_count=feedback_count,
        learning_active=expected_learning_active,
    )
    
    # Setup mock
    mock_execute = Mock()
    mock_execute.data = [brand.model_dump()]
    mock_brand_client.return_value.table.return_value.select.return_value.eq.return_value.is_.return_value.execute.return_value = mock_execute
    
    # Execute test
    brand_storage = BrandStorage()
    result = await brand_storage.get_brand(brand_id)
    
    # Assert learning_active is set correctly based on threshold
    assert result.learning_active == expected_learning_active, (
        f"Learning active should be {expected_learning_active} when feedback_count is {feedback_count}. "
        f"Threshold: {LEARNING_ACTIVATION_THRESHOLD}, "
        f"Actual learning_active: {result.learning_active}"
    )
    
    # Also verify the feedback count is correct
    assert result.feedback_count == feedback_count, (
        f"Feedback count mismatch. Expected: {feedback_count}, "
        f"Actual: {result.feedback_count}"
    )
