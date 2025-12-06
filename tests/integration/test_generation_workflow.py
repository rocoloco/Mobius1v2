"""
Integration tests for the generation workflow.

These tests verify the complete workflow execution including compliance
scoring, correction loops, and approval logic.
"""

import pytest
from datetime import datetime
from mobius.models.state import JobState
from mobius.nodes.audit import audit_node, calculate_overall_score
from mobius.graphs.generation import route_after_audit
from mobius.models.compliance import CategoryScore


@pytest.mark.asyncio
async def test_complete_workflow_with_compliance_scoring():
    """
    Test complete workflow with compliance scoring.
    
    Validates: Requirements 1.4, 3.4, 3.5
    """
    # Create initial job state
    state = JobState(
        job_id="test-job-001",
        brand_id="test-brand-001",
        prompt="Create a modern tech logo",
        brand_hex_codes=["#FF0000", "#00FF00", "#0000FF"],
        brand_rules="Use primary colors, modern sans-serif fonts, clean layout",
        current_image_url="https://example.com/test-image.png",
        attempt_count=1,
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
    
    # Run audit node
    result = await audit_node(state)
    
    # Verify audit results are added to state
    assert "audit_history" in result
    assert len(result["audit_history"]) > 0
    assert "compliance_scores" in result
    assert len(result["compliance_scores"]) > 0
    assert "is_approved" in result
    assert "status" in result
    assert result["status"] == "audited"
    
    # Verify compliance score structure
    compliance = result["compliance_scores"][0]
    assert "overall_score" in compliance
    assert "categories" in compliance
    assert "approved" in compliance
    assert "summary" in compliance
    
    # Verify score bounds
    assert 0 <= compliance["overall_score"] <= 100


@pytest.mark.asyncio
async def test_correction_loop_triggered_by_low_scores():
    """
    Test correction loop triggered by low scores.
    
    Validates: Requirements 3.4
    """
    # Create state with low compliance (below 80% threshold)
    state = JobState(
        job_id="test-job-002",
        brand_id="test-brand-002",
        prompt="Create a logo",
        brand_hex_codes=["#FF0000"],
        brand_rules="Use red color",
        current_image_url="https://example.com/test-image-2.png",
        attempt_count=1,
        audit_history=[],
        compliance_scores=[{"overall_score": 65.0}],
        is_approved=False,
        status="audited",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        webhook_url=None,
        template_id=None,
        generation_params=None
    )
    
    # Route after audit
    next_node = route_after_audit(state)
    
    # Should route to correction
    assert next_node == "correct", \
        f"Low compliance should trigger correction, got {next_node}"


@pytest.mark.asyncio
async def test_approval_on_high_scores():
    """
    Test approval on high scores.
    
    Validates: Requirements 3.5
    """
    # Create state with high compliance (above 80% threshold)
    state = JobState(
        job_id="test-job-003",
        brand_id="test-brand-003",
        prompt="Create a logo",
        brand_hex_codes=["#FF0000"],
        brand_rules="Use red color",
        current_image_url="https://example.com/test-image-3.png",
        attempt_count=1,
        audit_history=[],
        compliance_scores=[{"overall_score": 92.0}],
        is_approved=True,
        status="audited",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        webhook_url=None,
        template_id=None,
        generation_params=None
    )
    
    # Route after audit
    next_node = route_after_audit(state)
    
    # Should route to complete
    assert next_node == "complete", \
        f"High compliance should complete workflow, got {next_node}"


@pytest.mark.asyncio
async def test_max_attempts_failure():
    """
    Test that workflow fails after max attempts.
    
    Validates: Requirements 3.4
    """
    # Create state with max attempts reached
    state = JobState(
        job_id="test-job-004",
        brand_id="test-brand-004",
        prompt="Create a logo",
        brand_hex_codes=["#FF0000"],
        brand_rules="Use red color",
        current_image_url="https://example.com/test-image-4.png",
        attempt_count=3,  # Max attempts
        audit_history=[],
        compliance_scores=[{"overall_score": 65.0}],
        is_approved=False,
        status="audited",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        webhook_url=None,
        template_id=None,
        generation_params=None
    )
    
    # Route after audit
    next_node = route_after_audit(state)
    
    # Should route to failed
    assert next_node == "failed", \
        f"Max attempts should fail workflow, got {next_node}"


def test_category_score_calculation():
    """
    Test weighted category score calculation.
    
    Validates: Requirements 3.2
    """
    categories = [
        CategoryScore(
            category="colors",
            score=90.0,
            passed=True,
            violations=[]
        ),
        CategoryScore(
            category="typography",
            score=80.0,
            passed=True,
            violations=[]
        ),
        CategoryScore(
            category="layout",
            score=85.0,
            passed=True,
            violations=[]
        ),
        CategoryScore(
            category="logo_usage",
            score=75.0,
            passed=True,
            violations=[]
        )
    ]
    
    overall = calculate_overall_score(categories)
    
    # Verify weighted calculation
    # colors: 90 * 0.30 = 27.0
    # typography: 80 * 0.25 = 20.0
    # layout: 85 * 0.25 = 21.25
    # logo_usage: 75 * 0.20 = 15.0
    # Total: 83.25
    expected = 83.25
    assert abs(overall - expected) < 0.01, \
        f"Expected {expected}, got {overall}"


@pytest.mark.asyncio
async def test_audit_returns_valid_structure():
    """
    Test that audit node returns valid structure.
    
    Note: Currently uses mock response. When Gemini API is integrated,
    this test should be updated to test actual error handling.
    
    Validates: Requirements 3.1
    """
    # Create state
    state = JobState(
        job_id="test-job-005",
        brand_id="test-brand-005",
        prompt="Create a logo",
        brand_hex_codes=["#FF0000"],
        brand_rules="Use red color",
        current_image_url="https://example.com/test.png",
        attempt_count=1,
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
    
    # Run audit node
    result = await audit_node(state)
    
    # Should return valid structure
    assert "audit_history" in result
    assert "is_approved" in result
    assert "status" in result
    assert result["status"] == "audited"
    
    # Verify compliance score is present and valid
    assert len(result["compliance_scores"]) > 0
    compliance = result["compliance_scores"][0]
    assert 0 <= compliance["overall_score"] <= 100
