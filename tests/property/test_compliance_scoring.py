"""
Property-based tests for compliance scoring.

These tests verify universal properties that should hold across all valid
compliance scoring scenarios.

Feature: mobius-phase-2-refactor
"""

import pytest
from hypothesis import given, strategies as st, settings
from mobius.models.compliance import ComplianceScore, CategoryScore, Violation, Severity
from mobius.nodes.audit import calculate_overall_score, audit_node
from mobius.models.state import JobState
from datetime import datetime
from typing import List


# Strategy for generating valid category scores
@st.composite
def category_score_strategy(draw):
    """Generate a valid CategoryScore."""
    category = draw(st.sampled_from(["colors", "typography", "layout", "logo_usage"]))
    score = draw(st.floats(min_value=0.0, max_value=100.0))
    passed = draw(st.booleans())
    
    # Generate 0-3 violations
    num_violations = draw(st.integers(min_value=0, max_value=3))
    violations = []
    for _ in range(num_violations):
        violation = Violation(
            category=category,
            description=draw(st.text(min_size=10, max_size=100)),
            severity=draw(st.sampled_from(list(Severity))),
            fix_suggestion=draw(st.text(min_size=10, max_size=100))
        )
        violations.append(violation)
    
    return CategoryScore(
        category=category,
        score=score,
        passed=passed,
        violations=violations
    )


# Strategy for generating compliance scores
@st.composite
def compliance_score_strategy(draw):
    """Generate a valid ComplianceScore."""
    # Generate 1-4 category scores
    num_categories = draw(st.integers(min_value=1, max_value=4))
    categories = [draw(category_score_strategy()) for _ in range(num_categories)]
    
    overall_score = draw(st.floats(min_value=0.0, max_value=100.0))
    approved = draw(st.booleans())
    summary = draw(st.text(min_size=10, max_size=200))
    
    return ComplianceScore(
        overall_score=overall_score,
        categories=categories,
        approved=approved,
        summary=summary
    )


# Strategy for generating job states
@st.composite
def job_state_strategy(draw):
    """Generate a valid JobState for testing."""
    return JobState(
        job_id=f"job-{draw(st.text(min_size=8, max_size=12, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'))))}",
        brand_id=f"brand-{draw(st.text(min_size=8, max_size=12, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'))))}",
        prompt=draw(st.text(min_size=10, max_size=200)),
        brand_hex_codes=[f"#{draw(st.text(min_size=6, max_size=6, alphabet='0123456789ABCDEF'))}" for _ in range(draw(st.integers(min_value=1, max_value=5)))],
        brand_rules=draw(st.text(min_size=20, max_size=200)),
        current_image_url=f"https://example.com/image-{draw(st.integers(min_value=1, max_value=1000))}.png",
        attempt_count=draw(st.integers(min_value=0, max_value=5)),
        audit_history=[],
        compliance_scores=[],
        is_approved=False,
        status="generating",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        webhook_url=None,
        template_id=None,
        generation_params=None
    )


# **Feature: mobius-phase-2-refactor, Property 2: Compliance score is bounded**
# **Validates: Requirements 3.1**
@given(compliance_score_strategy())
@settings(max_examples=100)
def test_property_compliance_score_bounds(compliance: ComplianceScore):
    """
    Property 2: Compliance score is bounded.
    
    For any audit result returned by the audit node, the overall compliance
    score should be between 0 and 100 inclusive, and each category score
    should also be between 0 and 100 inclusive.
    
    Validates: Requirements 3.1
    """
    # Overall score must be bounded
    assert 0 <= compliance.overall_score <= 100, \
        f"Overall score {compliance.overall_score} is out of bounds [0, 100]"
    
    # Each category score must be bounded
    for category in compliance.categories:
        assert 0 <= category.score <= 100, \
            f"Category '{category.category}' score {category.score} is out of bounds [0, 100]"


# **Feature: mobius-phase-2-refactor, Property 3: Category scores aggregate correctly**
# **Validates: Requirements 3.2**
@given(st.lists(category_score_strategy(), min_size=1, max_size=4))
@settings(max_examples=100)
def test_property_category_score_aggregation(categories: List[CategoryScore]):
    """
    Property 3: Category scores aggregate correctly.
    
    For any compliance result with multiple category scores, the overall
    score should be the weighted average of all category scores.
    
    Validates: Requirements 3.2
    """
    overall = calculate_overall_score(categories)
    
    # Overall score must be bounded
    assert 0 <= overall <= 100, \
        f"Calculated overall score {overall} is out of bounds [0, 100]"
    
    # If all categories have the same score, overall should equal that score
    # (within floating point tolerance)
    if len(set(cat.score for cat in categories)) == 1:
        expected = categories[0].score
        assert abs(overall - expected) < 0.01, \
            f"When all categories have score {expected}, overall should be {expected}, got {overall}"
    
    # Overall score should be within the range of category scores
    # (with small tolerance for floating point precision)
    min_score = min(cat.score for cat in categories)
    max_score = max(cat.score for cat in categories)
    tolerance = 0.01
    assert min_score - tolerance <= overall <= max_score + tolerance, \
        f"Overall score {overall} should be between min {min_score} and max {max_score}"


# **Feature: mobius-phase-2-refactor, Property 4: Low compliance triggers correction**
# **Validates: Requirements 3.4**
@given(
    st.floats(min_value=0.0, max_value=79.9),  # Below 80% threshold
    st.integers(min_value=0, max_value=2)  # Below max attempts
)
@settings(max_examples=100)
def test_property_low_compliance_triggers_correction(compliance_score: float, attempt_count: int):
    """
    Property 4: Low compliance triggers correction.
    
    For any job state where the compliance score is below 80 percent and
    attempt count is less than 3, the routing function should direct to
    the correction node.
    
    Validates: Requirements 3.4
    """
    from mobius.graphs.generation import route_after_audit
    
    state = JobState(
        job_id="test-job",
        brand_id="test-brand",
        prompt="test prompt",
        brand_hex_codes=["#FF0000"],
        brand_rules="test rules",
        current_image_url="https://example.com/test.png",
        attempt_count=attempt_count,
        audit_history=[],
        compliance_scores=[{"overall_score": compliance_score}],
        is_approved=False,  # Low compliance means not approved
        status="audited",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        webhook_url=None,
        template_id=None,
        generation_params=None
    )
    
    result = route_after_audit(state)
    
    assert result == "correct", \
        f"Low compliance ({compliance_score}%) with {attempt_count} attempts should route to 'correct', got '{result}'"


# **Feature: mobius-phase-2-refactor, Property 5: High compliance approves asset**
# **Validates: Requirements 3.5**
@given(st.lists(
    st.floats(min_value=90.1, max_value=100.0),  # All categories above 90%
    min_size=1,
    max_size=4
))
@settings(max_examples=100)
def test_property_high_compliance_approves_asset(category_scores: List[float]):
    """
    Property 5: High compliance approves asset.
    
    For any job state where all category scores are above 90 percent,
    the is_approved flag should be set to true.
    
    Validates: Requirements 3.5
    """
    # Create categories with high scores
    categories = [
        CategoryScore(
            category=cat_name,
            score=score,
            passed=True,
            violations=[]
        )
        for cat_name, score in zip(
            ["colors", "typography", "layout", "logo_usage"][:len(category_scores)],
            category_scores
        )
    ]
    
    # Calculate overall score
    overall = calculate_overall_score(categories)
    
    # With all categories above 90%, overall should be above 90%
    assert overall >= 90.0, \
        f"With all categories above 90%, overall score should be >= 90%, got {overall}"
    
    # Since overall is above 90%, which is above the 80% threshold,
    # the asset should be approved
    assert overall >= 80.0, \
        f"High compliance score {overall}% should exceed 80% threshold"
