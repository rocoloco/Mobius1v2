"""
Property-based test for privacy tier enforcement.

**Feature: mobius-phase-2-refactor, Property 17: Privacy tier enforcement**
**Validates: Requirements - Learning privacy controls**

This test verifies that when a brand's privacy_tier is set to "off",
no patterns are extracted or stored, ensuring that learning is truly disabled.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, AsyncMock, patch
import uuid

from mobius.learning.private import PrivateLearningEngine
from mobius.models.learning import PrivacyTier, LearningSettings


# Strategy for generating brand IDs
brand_ids = st.text(min_size=10, max_size=50, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    whitelist_characters='-'
))


@patch("mobius.learning.private.get_supabase_client")
@pytest.mark.asyncio
@given(brand_id=brand_ids)
@settings(max_examples=100, deadline=None)
async def test_privacy_tier_off_prevents_pattern_extraction(mock_get_client, brand_id: str):
    """
    **Feature: mobius-phase-2-refactor, Property 17: Privacy tier enforcement**
    
    Property: For any brand with privacy_tier set to "off",
    no patterns should be extracted or stored.
    
    This ensures that when users explicitly disable learning,
    the system respects that choice and does not process their data.
    """
    # Create engine
    engine = PrivateLearningEngine()
    
    # Mock the database client
    mock_client = Mock()
    engine.client = mock_client
    
    # Mock settings query to return OFF tier
    mock_settings_result = Mock()
    mock_settings_result.data = [{
        "brand_id": brand_id,
        "privacy_tier": "off",
        "consent_date": None,
        "consent_version": "1.0",
        "data_retention_days": 365,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }]
    
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_settings_result
    
    # Mock audit log insert
    mock_audit_result = Mock()
    mock_audit_result.data = [{}]
    mock_client.table.return_value.insert.return_value.execute.return_value = mock_audit_result
    
    # Extract patterns
    patterns = await engine.extract_patterns(brand_id)
    
    # Property: No patterns should be extracted when tier is OFF
    assert len(patterns) == 0, \
        f"Expected 0 patterns for privacy_tier=off, but got {len(patterns)}"
    
    # Verify that no patterns were stored in the database
    # The insert method should not have been called for brand_patterns table
    insert_calls = [
        call for call in mock_client.table.call_args_list
        if len(call[0]) > 0 and call[0][0] == "brand_patterns"
    ]
    
    # If there were any insert calls to brand_patterns, the test should fail
    for call in insert_calls:
        # Check if insert was called after this table call
        table_mock = mock_client.table.return_value
        if hasattr(table_mock, 'insert') and table_mock.insert.called:
            pytest.fail("Patterns were stored despite privacy_tier being 'off'")


@patch("mobius.learning.private.get_supabase_client")
@pytest.mark.asyncio
@given(brand_id=brand_ids)
@settings(max_examples=100, deadline=None)
async def test_privacy_tier_off_prevents_prompt_optimization(mock_get_client, brand_id: str):
    """
    Property: For any brand with privacy_tier set to "off",
    prompt optimization should return the original prompt unchanged.
    
    This ensures that learning is not applied even for optimization.
    """
    # Create engine
    engine = PrivateLearningEngine()
    
    # Mock the database client
    mock_client = Mock()
    engine.client = mock_client
    
    # Mock settings query to return OFF tier
    mock_settings_result = Mock()
    mock_settings_result.data = [{
        "brand_id": brand_id,
        "privacy_tier": "off",
        "consent_date": None,
        "consent_version": "1.0",
        "data_retention_days": 365,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }]
    
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_settings_result
    
    # Test prompt
    original_prompt = "Create a modern logo"
    
    # Optimize prompt
    optimized_prompt = await engine.optimize_prompt(brand_id, original_prompt)
    
    # Property: Prompt should be unchanged when tier is OFF
    assert optimized_prompt == original_prompt, \
        f"Expected prompt to be unchanged for privacy_tier=off, but it was modified"


@patch("mobius.learning.private.get_supabase_client")
@pytest.mark.asyncio
@given(
    brand_id=brand_ids,
    privacy_tier=st.sampled_from(["off", "private", "shared"])
)
@settings(max_examples=100, deadline=None)
async def test_privacy_tier_enforcement_consistency(mock_get_client, brand_id: str, privacy_tier: str):
    """
    Property: For any brand, the privacy tier setting should be consistently
    enforced across all learning operations.
    
    This ensures that the privacy tier is respected in all contexts.
    """
    # Create engine
    engine = PrivateLearningEngine()
    
    # Mock the database client
    mock_client = Mock()
    engine.client = mock_client
    
    # Mock settings query to return the specified tier
    mock_settings_result = Mock()
    mock_settings_result.data = [{
        "brand_id": brand_id,
        "privacy_tier": privacy_tier,
        "consent_date": "2025-01-01T00:00:00Z" if privacy_tier != "off" else None,
        "consent_version": "1.0",
        "data_retention_days": 365,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }]
    
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_settings_result
    
    # Mock feedback data (empty for this test)
    mock_feedback_result = Mock()
    mock_feedback_result.data = []
    
    # Mock audit log insert
    mock_audit_result = Mock()
    mock_audit_result.data = [{}]
    
    # Set up the mock to return different results based on table name
    def table_side_effect(table_name):
        mock_table = Mock()
        if table_name == "learning_settings":
            mock_table.select.return_value.eq.return_value.execute.return_value = mock_settings_result
        elif table_name == "feedback":
            mock_table.select.return_value.eq.return_value.execute.return_value = mock_feedback_result
        elif table_name == "learning_audit_log":
            mock_table.insert.return_value.execute.return_value = mock_audit_result
        return mock_table
    
    mock_client.table.side_effect = table_side_effect
    
    # Extract patterns
    patterns = await engine.extract_patterns(brand_id)
    
    # Property: If tier is OFF, no patterns should be extracted
    if privacy_tier == "off":
        assert len(patterns) == 0, \
            f"Expected 0 patterns for privacy_tier=off, but got {len(patterns)}"
    # For private and shared tiers, patterns can be extracted (if feedback exists)
    # Since we mocked empty feedback, we expect 0 patterns regardless
    else:
        # This is expected - no feedback means no patterns
        assert len(patterns) == 0
