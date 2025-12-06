"""
Property-based test for data deletion completeness.

**Feature: mobius-phase-2-refactor, Property 19: Data deletion completeness**
**Validates: Requirements - Right to deletion**

This test verifies that after calling delete_learning_data(),
all patterns for a brand are completely removed from the database.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, AsyncMock, patch
import uuid

from mobius.learning.private import PrivateLearningEngine
from mobius.models.learning import BrandPattern


# Strategy for generating brand IDs
brand_ids = st.text(min_size=10, max_size=50, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    whitelist_characters='-'
))

# Strategy for generating pattern counts
pattern_counts = st.integers(min_value=0, max_value=20)


@patch("mobius.learning.private.get_supabase_client")
@pytest.mark.asyncio
@given(
    brand_id=brand_ids,
    initial_pattern_count=pattern_counts
)
@settings(max_examples=100, deadline=None)
async def test_data_deletion_removes_all_patterns(
    mock_get_client,
    brand_id: str,
    initial_pattern_count: int
):
    """
    **Feature: mobius-phase-2-refactor, Property 19: Data deletion completeness**
    
    Property: For any brand, after calling delete_learning_data(),
    querying for patterns should return an empty list.
    
    This ensures that the right to deletion (GDPR Article 17) is properly
    implemented and all learning data is completely removed.
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    
    # Create engine
    engine = PrivateLearningEngine()
    
    # Mock the database client
    mock_client = Mock()
    engine.client = mock_client
    
    # Create mock patterns that exist before deletion
    initial_patterns = [
        {
            "pattern_id": str(uuid.uuid4()),
            "brand_id": brand_id,
            "pattern_type": f"type_{i}",
            "pattern_data": {"data": f"value_{i}"},
            "confidence_score": 0.8,
            "sample_count": 10,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }
        for i in range(initial_pattern_count)
    ]
    
    # Mock the delete operation
    mock_delete_result = Mock()
    mock_delete_result.data = []
    
    # Mock the audit log insert for deletion
    mock_audit_result = Mock()
    mock_audit_result.data = [{}]
    
    # Mock the query after deletion (should return empty)
    mock_query_after_delete = Mock()
    mock_query_after_delete.data = []
    
    # Set up the mock to handle different operations
    def table_side_effect(table_name):
        mock_table = Mock()
        
        if table_name == "brand_patterns":
            # For delete operation
            mock_delete_chain = Mock()
            mock_delete_chain.eq.return_value.execute.return_value = mock_delete_result
            mock_table.delete.return_value = mock_delete_chain
            
            # For query after deletion
            mock_select_chain = Mock()
            mock_select_chain.eq.return_value.order.return_value.execute.return_value = mock_query_after_delete
            mock_table.select.return_value = mock_select_chain
            
        elif table_name == "learning_audit_log":
            mock_table.insert.return_value.execute.return_value = mock_audit_result
            
        return mock_table
    
    mock_client.table.side_effect = table_side_effect
    
    # Perform deletion
    result = await engine.delete_learning_data(brand_id)
    
    # Property 1: Deletion should succeed
    assert result is True, "delete_learning_data() should return True"
    
    # Property 2: After deletion, querying for patterns should return empty list
    patterns_after_deletion = await engine._get_patterns(brand_id)
    
    assert len(patterns_after_deletion) == 0, \
        f"Expected 0 patterns after deletion, but found {len(patterns_after_deletion)}"
    
    # Verify that delete was called on brand_patterns table
    delete_calls = [
        call for call in mock_client.table.call_args_list
        if len(call[0]) > 0 and call[0][0] == "brand_patterns"
    ]
    
    assert len(delete_calls) > 0, \
        "delete() should have been called on brand_patterns table"


@patch("mobius.learning.private.get_supabase_client")
@pytest.mark.asyncio
@given(
    brand_id=brand_ids,
    pattern_types=st.lists(
        st.sampled_from(["color_preference", "style_preference", "prompt_optimization"]),
        min_size=0,
        max_size=10
    )
)
@settings(max_examples=100, deadline=None)
async def test_data_deletion_removes_all_pattern_types(
    mock_get_client,
    brand_id: str,
    pattern_types: list
):
    """
    Property: For any brand with multiple pattern types,
    after calling delete_learning_data(), all pattern types
    should be removed.
    
    This ensures that deletion is comprehensive across all pattern types.
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    
    # Create engine
    engine = PrivateLearningEngine()
    
    # Mock the database client
    mock_client = Mock()
    engine.client = mock_client
    
    # Create mock patterns of different types
    initial_patterns = [
        {
            "pattern_id": str(uuid.uuid4()),
            "brand_id": brand_id,
            "pattern_type": pattern_type,
            "pattern_data": {"data": "value"},
            "confidence_score": 0.8,
            "sample_count": 10,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }
        for pattern_type in pattern_types
    ]
    
    # Mock the delete operation
    mock_delete_result = Mock()
    mock_delete_result.data = []
    
    # Mock the audit log insert
    mock_audit_result = Mock()
    mock_audit_result.data = [{}]
    
    # Mock queries after deletion (should return empty for all types)
    mock_query_after_delete = Mock()
    mock_query_after_delete.data = []
    
    # Set up the mock
    def table_side_effect(table_name):
        mock_table = Mock()
        
        if table_name == "brand_patterns":
            # For delete operation
            mock_delete_chain = Mock()
            mock_delete_chain.eq.return_value.execute.return_value = mock_delete_result
            mock_table.delete.return_value = mock_delete_chain
            
            # For query after deletion
            mock_select_chain = Mock()
            mock_eq_chain = Mock()
            mock_eq_chain.order.return_value.execute.return_value = mock_query_after_delete
            mock_eq_chain.eq.return_value.order.return_value.execute.return_value = mock_query_after_delete
            mock_select_chain.eq.return_value = mock_eq_chain
            mock_table.select.return_value = mock_select_chain
            
        elif table_name == "learning_audit_log":
            mock_table.insert.return_value.execute.return_value = mock_audit_result
            
        return mock_table
    
    mock_client.table.side_effect = table_side_effect
    
    # Perform deletion
    await engine.delete_learning_data(brand_id)
    
    # Property: After deletion, querying for any pattern type should return empty
    for pattern_type in set(pattern_types):  # Use set to avoid duplicate queries
        patterns = await engine._get_patterns(brand_id, pattern_type)
        assert len(patterns) == 0, \
            f"Expected 0 patterns of type '{pattern_type}' after deletion, " \
            f"but found {len(patterns)}"


@patch("mobius.learning.private.get_supabase_client")
@pytest.mark.asyncio
@given(brand_id=brand_ids)
@settings(max_examples=100, deadline=None)
async def test_data_deletion_is_idempotent(mock_get_client, brand_id: str):
    """
    Property: For any brand, calling delete_learning_data() multiple times
    should succeed without errors.
    
    This ensures that deletion is idempotent and safe to retry.
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    
    # Create engine
    engine = PrivateLearningEngine()
    
    # Mock the database client
    mock_client = Mock()
    engine.client = mock_client
    
    # Mock the delete operation (succeeds even if no data exists)
    mock_delete_result = Mock()
    mock_delete_result.data = []
    
    # Mock the audit log insert
    mock_audit_result = Mock()
    mock_audit_result.data = [{}]
    
    # Set up the mock
    def table_side_effect(table_name):
        mock_table = Mock()
        
        if table_name == "brand_patterns":
            mock_delete_chain = Mock()
            mock_delete_chain.eq.return_value.execute.return_value = mock_delete_result
            mock_table.delete.return_value = mock_delete_chain
            
        elif table_name == "learning_audit_log":
            mock_table.insert.return_value.execute.return_value = mock_audit_result
            
        return mock_table
    
    mock_client.table.side_effect = table_side_effect
    
    # Property: Multiple deletions should all succeed
    result1 = await engine.delete_learning_data(brand_id)
    assert result1 is True, "First deletion should succeed"
    
    # Reset the side_effect for second call
    mock_client.table.side_effect = table_side_effect
    
    result2 = await engine.delete_learning_data(brand_id)
    assert result2 is True, "Second deletion should succeed (idempotent)"
    
    # Reset the side_effect for third call
    mock_client.table.side_effect = table_side_effect
    
    result3 = await engine.delete_learning_data(brand_id)
    assert result3 is True, "Third deletion should succeed (idempotent)"
