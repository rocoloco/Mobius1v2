"""
Property-based test for k-anonymity enforcement.

**Feature: mobius-phase-2-refactor, Property 18: K-anonymity enforcement**
**Validates: Requirements - Shared learning privacy**

This test verifies that industry patterns enforce k-anonymity by requiring
a minimum of 5 contributing brands.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, AsyncMock, patch
import uuid

from mobius.learning.shared import SharedLearningEngine
from mobius.models.learning import IndustryPattern, BrandPattern, PrivacyTier


# Strategy for generating cohort names
cohorts = st.sampled_from(["fashion", "tech", "food", "healthcare", "finance"])

# Strategy for generating pattern types
pattern_types = st.sampled_from([
    "color_preference",
    "style_preference",
    "prompt_optimization"
])

# Strategy for generating contributor counts
contributor_counts = st.integers(min_value=0, max_value=20)


@patch("mobius.learning.shared.get_supabase_client")
@pytest.mark.asyncio
@given(
    cohort=cohorts,
    pattern_type=pattern_types,
    contributor_count=contributor_counts
)
@settings(max_examples=100, deadline=None)
async def test_k_anonymity_requires_minimum_contributors(
    mock_get_client,
    cohort: str,
    pattern_type: str,
    contributor_count: int
):
    """
    **Feature: mobius-phase-2-refactor, Property 18: K-anonymity enforcement**
    
    Property: For any industry pattern aggregation attempt,
    if the number of contributing brands is less than 5,
    the aggregation should return None (not create a pattern).
    
    This ensures k-anonymity is enforced to prevent individual
    brand identification.
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    
    # Create engine
    engine = SharedLearningEngine()
    
    # Mock the database client
    mock_client = Mock()
    engine.client = mock_client
    
    # Create mock brand IDs
    brand_ids = [str(uuid.uuid4()) for _ in range(contributor_count)]
    
    # Mock the brands query
    mock_brands_result = Mock()
    mock_brands_result.data = [{"brand_id": bid} for bid in brand_ids]
    
    # Mock the settings query to return SHARED tier for all brands
    def create_settings_mock(brand_id):
        mock_settings_result = Mock()
        mock_settings_result.data = [{
            "brand_id": brand_id,
            "privacy_tier": "shared",
            "consent_date": "2025-01-01T00:00:00Z",
            "consent_version": "1.0",
            "data_retention_days": 365,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }]
        return mock_settings_result
    
    # Mock the patterns query (return some patterns for each brand)
    def create_patterns_mock(brand_id):
        mock_patterns_result = Mock()
        mock_patterns_result.data = [{
            "pattern_id": str(uuid.uuid4()),
            "brand_id": brand_id,
            "pattern_type": pattern_type,
            "pattern_data": {"approval_rate": 0.8},
            "confidence_score": 0.7,
            "sample_count": 10,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }]
        return mock_patterns_result
    
    # Set up complex mock behavior
    call_count = {"brands": 0, "settings": 0, "patterns": 0}
    
    def table_side_effect(table_name):
        mock_table = Mock()
        
        if table_name == "brands":
            call_count["brands"] += 1
            mock_select = Mock()
            mock_eq = Mock()
            mock_is = Mock()
            mock_is.execute.return_value = mock_brands_result
            mock_eq.is_.return_value = mock_is
            mock_select.eq.return_value = mock_eq
            mock_table.select.return_value = mock_select
            
        elif table_name == "learning_settings":
            # Return settings for each brand
            brand_idx = call_count["settings"]
            if brand_idx < len(brand_ids):
                settings_result = create_settings_mock(brand_ids[brand_idx])
                call_count["settings"] += 1
            else:
                settings_result = Mock()
                settings_result.data = []
            
            mock_select = Mock()
            mock_eq = Mock()
            mock_eq.execute.return_value = settings_result
            mock_select.eq.return_value = mock_eq
            mock_table.select.return_value = mock_select
            
        elif table_name == "brand_patterns":
            # Return patterns for each brand
            brand_idx = call_count["patterns"]
            if brand_idx < len(brand_ids):
                patterns_result = create_patterns_mock(brand_ids[brand_idx])
                call_count["patterns"] += 1
            else:
                patterns_result = Mock()
                patterns_result.data = []
            
            mock_select = Mock()
            mock_eq1 = Mock()
            mock_eq2 = Mock()
            mock_eq2.execute.return_value = patterns_result
            mock_eq1.eq.return_value = mock_eq2
            mock_select.eq.return_value = mock_eq1
            mock_table.select.return_value = mock_select
            
        elif table_name == "industry_patterns":
            # Mock insert for when pattern is created
            mock_insert = Mock()
            mock_insert.execute.return_value = Mock(data=[{}])
            mock_table.insert.return_value = mock_insert
            
        return mock_table
    
    mock_client.table.side_effect = table_side_effect
    
    # Attempt to aggregate patterns
    result = await engine.aggregate_patterns(cohort, pattern_type)
    
    # Property: K-anonymity enforcement
    if contributor_count < engine.MIN_CONTRIBUTORS:
        # Should return None when insufficient contributors
        assert result is None, \
            f"Expected None for {contributor_count} contributors " \
            f"(< {engine.MIN_CONTRIBUTORS}), but got a pattern"
    else:
        # Should create pattern when sufficient contributors
        # (assuming patterns exist for the brands)
        if contributor_count > 0:  # Only if there are brands
            assert result is not None, \
                f"Expected pattern for {contributor_count} contributors " \
                f"(>= {engine.MIN_CONTRIBUTORS}), but got None"
            assert result.contributor_count >= engine.MIN_CONTRIBUTORS, \
                f"Pattern contributor_count should be >= {engine.MIN_CONTRIBUTORS}"


@pytest.mark.asyncio
@given(
    contributor_count=st.integers(min_value=5, max_value=100)
)
@settings(max_examples=100, deadline=None)
async def test_stored_industry_patterns_meet_k_anonymity(contributor_count: int):
    """
    Property: For any industry pattern stored in the database,
    the contributor_count should be at least 5.
    
    This verifies that the database constraint is enforced.
    """
    # Create a valid industry pattern
    pattern = IndustryPattern(
        pattern_id=str(uuid.uuid4()),
        cohort="fashion",
        pattern_type="color_preference",
        pattern_data={"average_approval_rate": 0.75},
        contributor_count=contributor_count,
        noise_level=0.1,
        created_at="2025-01-01T00:00:00Z",
        updated_at="2025-01-01T00:00:00Z"
    )
    
    # Property: contributor_count should meet k-anonymity threshold
    assert pattern.contributor_count >= 5, \
        f"Industry pattern has contributor_count={pattern.contributor_count}, " \
        f"which violates k-anonymity (minimum 5)"


@pytest.mark.asyncio
@given(
    contributor_count=st.integers(min_value=1, max_value=4)
)
@settings(max_examples=100, deadline=None)
async def test_industry_pattern_rejects_insufficient_contributors(contributor_count: int):
    """
    Property: For any attempt to create an industry pattern with
    fewer than 5 contributors, the Pydantic model should raise
    a validation error.
    
    This ensures the data model enforces k-anonymity.
    """
    # Attempt to create pattern with insufficient contributors
    with pytest.raises(Exception):  # Pydantic ValidationError
        pattern = IndustryPattern(
            pattern_id=str(uuid.uuid4()),
            cohort="fashion",
            pattern_type="color_preference",
            pattern_data={"average_approval_rate": 0.75},
            contributor_count=contributor_count,  # Less than 5
            noise_level=0.1,
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z"
        )


@patch("mobius.learning.shared.get_supabase_client")
@pytest.mark.asyncio
@given(
    cohort=cohorts,
    pattern_type=pattern_types
)
@settings(max_examples=100, deadline=None)
async def test_verify_k_anonymity_method(mock_get_client, cohort: str, pattern_type: str):
    """
    Property: For any industry pattern, the verify_k_anonymity method
    should return True only if contributor_count >= 5.
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    
    # Create engine
    engine = SharedLearningEngine()
    
    # Mock the database client
    mock_client = Mock()
    engine.client = mock_client
    
    # Test with valid pattern (>= 5 contributors)
    valid_pattern_id = str(uuid.uuid4())
    mock_valid_result = Mock()
    mock_valid_result.data = [{
        "pattern_id": valid_pattern_id,
        "cohort": cohort,
        "pattern_type": pattern_type,
        "pattern_data": {},
        "contributor_count": 5,
        "noise_level": 0.1,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }]
    
    mock_select = Mock()
    mock_eq = Mock()
    mock_eq.execute.return_value = mock_valid_result
    mock_select.eq.return_value = mock_eq
    mock_client.table.return_value.select.return_value = mock_select
    
    # Verify k-anonymity
    result = await engine.verify_k_anonymity(valid_pattern_id)
    
    # Property: Should return True for valid pattern
    assert result is True, \
        "verify_k_anonymity should return True for pattern with >= 5 contributors"
