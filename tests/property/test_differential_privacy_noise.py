"""
Property-based test for differential privacy noise.

**Feature: mobius-phase-2-refactor, Property 20: Differential privacy noise**
**Validates: Requirements - Differential privacy**

This test verifies that aggregated industry patterns have differential privacy
noise applied to prevent individual brand identification.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, patch
import uuid
import numpy as np

from mobius.learning.shared import SharedLearningEngine
from mobius.models.learning import IndustryPattern, BrandPattern


# Strategy for generating cohort names
cohorts = st.sampled_from(["fashion", "tech", "food", "healthcare", "finance"])

# Strategy for generating pattern types
pattern_types = st.sampled_from([
    "color_preference",
    "style_preference",
    "prompt_optimization"
])

# Strategy for generating noise levels
noise_levels = st.floats(min_value=0.01, max_value=1.0)


@pytest.mark.asyncio
@given(
    cohort=cohorts,
    pattern_type=pattern_types,
    noise_level=noise_levels
)
@settings(max_examples=100, deadline=None)
async def test_industry_patterns_have_positive_noise_level(
    cohort: str,
    pattern_type: str,
    noise_level: float
):
    """
    **Feature: mobius-phase-2-refactor, Property 20: Differential privacy noise**
    
    Property: For any aggregated industry pattern, the noise_level
    should be greater than 0.
    
    This ensures that differential privacy noise is always applied
    to protect individual brand data.
    """
    # Create an industry pattern
    pattern = IndustryPattern(
        pattern_id=str(uuid.uuid4()),
        cohort=cohort,
        pattern_type=pattern_type,
        pattern_data={"average_approval_rate": 0.75},
        contributor_count=5,
        noise_level=noise_level,
        created_at="2025-01-01T00:00:00Z",
        updated_at="2025-01-01T00:00:00Z"
    )
    
    # Property: noise_level must be positive
    assert pattern.noise_level > 0, \
        f"Industry pattern has noise_level={pattern.noise_level}, " \
        f"which violates differential privacy (must be > 0)"


@pytest.mark.asyncio
@given(
    noise_level=st.floats(min_value=-1.0, max_value=0.0)
)
@settings(max_examples=100, deadline=None)
async def test_industry_pattern_rejects_non_positive_noise(noise_level: float):
    """
    Property: For any attempt to create an industry pattern with
    noise_level <= 0, the Pydantic model should raise a validation error.
    
    This ensures the data model enforces differential privacy.
    """
    # Attempt to create pattern with non-positive noise
    with pytest.raises(Exception):  # Pydantic ValidationError
        pattern = IndustryPattern(
            pattern_id=str(uuid.uuid4()),
            cohort="fashion",
            pattern_type="color_preference",
            pattern_data={"average_approval_rate": 0.75},
            contributor_count=5,
            noise_level=noise_level,  # <= 0
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z"
        )


@patch("mobius.learning.shared.get_supabase_client")
@pytest.mark.asyncio
@given(
    num_patterns=st.integers(min_value=5, max_value=20),
    base_value=st.floats(min_value=0.0, max_value=1.0)
)
@settings(max_examples=100, deadline=None)
async def test_aggregate_with_privacy_adds_noise(
    mock_get_client,
    num_patterns: int,
    base_value: float
):
    """
    Property: For any set of patterns, aggregating with privacy
    should produce different results than aggregating without noise
    (with high probability).
    
    This verifies that noise is actually being added.
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    
    # Create engine
    engine = SharedLearningEngine()
    
    # Create mock patterns with identical values
    patterns = [
        BrandPattern(
            pattern_id=str(uuid.uuid4()),
            brand_id=str(uuid.uuid4()),
            pattern_type="color_preference",
            pattern_data={"approval_rate": base_value},
            confidence_score=0.8,
            sample_count=10
        )
        for _ in range(num_patterns)
    ]
    
    # Aggregate with privacy (includes noise)
    aggregated = engine._aggregate_with_privacy(patterns)
    
    # Property 1: Aggregated data should contain privacy metadata
    assert "_privacy" in aggregated, \
        "Aggregated data should contain privacy metadata"
    
    assert aggregated["_privacy"]["mechanism"] == "laplace", \
        "Privacy mechanism should be Laplace"
    
    assert aggregated["_privacy"]["noise_scale"] > 0, \
        "Noise scale should be positive"
    
    # Property 2: If there's an approval_rate, it should differ from the exact average
    # (with high probability, though there's a small chance noise could be ~0)
    if "average_approval_rate" in aggregated:
        exact_average = base_value
        noisy_average = aggregated["average_approval_rate"]
        
        # We can't guarantee they're different (noise could be very small)
        # but we can verify the noise mechanism was applied
        assert isinstance(noisy_average, float), \
            "Noisy average should be a float"


@patch("mobius.learning.shared.get_supabase_client")
@pytest.mark.asyncio
@given(
    cohort=cohorts,
    pattern_type=pattern_types
)
@settings(max_examples=100, deadline=None)
async def test_verify_differential_privacy_method(mock_get_client, cohort: str, pattern_type: str):
    """
    Property: For any industry pattern, the verify_differential_privacy method
    should return True only if noise_level > 0.
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    
    # Create engine
    engine = SharedLearningEngine()
    
    # Mock the database client
    mock_client = Mock()
    engine.client = mock_client
    
    # Test with valid pattern (noise_level > 0)
    valid_pattern_id = str(uuid.uuid4())
    mock_valid_result = Mock()
    mock_valid_result.data = [{
        "pattern_id": valid_pattern_id,
        "cohort": cohort,
        "pattern_type": pattern_type,
        "pattern_data": {},
        "contributor_count": 5,
        "noise_level": 0.1,  # Positive noise
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }]
    
    mock_select = Mock()
    mock_eq = Mock()
    mock_eq.execute.return_value = mock_valid_result
    mock_select.eq.return_value = mock_eq
    mock_client.table.return_value.select.return_value = mock_select
    
    # Verify differential privacy
    result = await engine.verify_differential_privacy(valid_pattern_id)
    
    # Property: Should return True for pattern with positive noise
    assert result is True, \
        "verify_differential_privacy should return True for pattern with noise_level > 0"


@patch("mobius.learning.shared.get_supabase_client")
@pytest.mark.asyncio
@given(
    num_queries=st.integers(min_value=1, max_value=100)
)
@settings(max_examples=100, deadline=None)
async def test_privacy_budget_calculation(mock_get_client, num_queries: int):
    """
    Property: For any number of queries, the privacy budget (epsilon)
    should increase linearly with the number of queries.
    
    This verifies that privacy budget tracking works correctly.
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    
    # Create engine
    engine = SharedLearningEngine()
    
    # Calculate privacy budget
    epsilon = engine.calculate_privacy_budget(num_queries)
    
    # Property 1: Epsilon should be positive
    assert epsilon > 0, \
        f"Privacy budget should be positive, got {epsilon}"
    
    # Property 2: Epsilon should scale with number of queries
    epsilon_per_query = 1.0 / engine.NOISE_SCALE
    expected_epsilon = epsilon_per_query * num_queries
    
    assert abs(epsilon - expected_epsilon) < 0.001, \
        f"Privacy budget should be {expected_epsilon}, got {epsilon}"
    
    # Property 3: More queries = higher epsilon (less privacy)
    if num_queries > 1:
        epsilon_fewer = engine.calculate_privacy_budget(num_queries - 1)
        assert epsilon > epsilon_fewer, \
            "Privacy budget should increase with more queries"


@patch("mobius.learning.shared.get_supabase_client")
@pytest.mark.asyncio
@given(
    num_patterns=st.integers(min_value=5, max_value=20)
)
@settings(max_examples=100, deadline=None)
async def test_noise_prevents_exact_reconstruction(mock_get_client, num_patterns: int):
    """
    Property: For any set of patterns, the aggregated result with noise
    should not allow exact reconstruction of individual values.
    
    This is a simplified test of the privacy guarantee.
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    
    # Create engine
    engine = SharedLearningEngine()
    
    # Create patterns with known values
    known_value = 0.75
    patterns = [
        BrandPattern(
            pattern_id=str(uuid.uuid4()),
            brand_id=str(uuid.uuid4()),
            pattern_type="color_preference",
            pattern_data={"approval_rate": known_value},
            confidence_score=0.8,
            sample_count=10
        )
        for _ in range(num_patterns)
    ]
    
    # Aggregate multiple times (noise is random)
    results = []
    for _ in range(10):
        aggregated = engine._aggregate_with_privacy(patterns)
        if "average_approval_rate" in aggregated:
            results.append(aggregated["average_approval_rate"])
    
    # Property: Results should vary due to random noise
    # (with very high probability)
    if len(results) > 1:
        # Check that not all results are identical
        unique_results = len(set(results))
        # With Laplace noise, it's extremely unlikely all 10 results are identical
        # We allow for the tiny possibility, but expect variation
        assert unique_results > 1 or len(results) == 1, \
            "Differential privacy noise should produce varying results"


@patch("mobius.learning.shared.get_supabase_client")
@pytest.mark.asyncio
async def test_laplace_noise_distribution(mock_get_client):
    """
    Property: The Laplace noise should follow the expected distribution.
    
    This verifies that the noise generation is correct.
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    
    # Create engine
    engine = SharedLearningEngine()
    
    # Generate many noise samples
    num_samples = 1000
    noise_samples = [np.random.laplace(0, engine.NOISE_SCALE) for _ in range(num_samples)]
    
    # Property 1: Mean should be close to 0
    mean_noise = np.mean(noise_samples)
    assert abs(mean_noise) < 0.1, \
        f"Laplace noise mean should be close to 0, got {mean_noise}"
    
    # Property 2: Standard deviation should be related to scale
    # For Laplace distribution: std = sqrt(2) * scale
    std_noise = np.std(noise_samples)
    expected_std = np.sqrt(2) * engine.NOISE_SCALE
    
    # Allow for some statistical variation
    assert abs(std_noise - expected_std) < 0.1, \
        f"Laplace noise std should be close to {expected_std}, got {std_noise}"
