"""
Property-Based Tests for Mobius Brand Governance Engine

Uses Hypothesis for property-based testing with minimum 100 iterations per test.
"""

import sys
import os
from unittest.mock import MagicMock, patch

# Mock Modal before importing orchestrator (Modal doesn't support Python 3.14+)
sys.modules['modal'] = MagicMock()

import pytest
from hypothesis import given, strategies as st, settings
from typing import List

# Import the module under test
from orchestrator import JobState, MobiusJobRequest, generate_node, audit_node, correct_node, persist_state, route_decision, _run_mobius_job_impl
from langgraph.graph import END


# ============================================================================
# Test Strategies (Generators)
# ============================================================================

@st.composite
def job_state_strategy(draw, with_image_url=False, with_audit_history=False):
    """
    Smart generator for JobState that constrains to valid input domain.
    
    Args:
        with_image_url: If True, generates states with non-None image URLs
        with_audit_history: If True, generates states with audit history
    """
    prompt = draw(st.text(min_size=1, max_size=200))
    
    # Generate 1-5 valid hex color codes
    hex_codes = draw(st.lists(
        st.from_regex(r"#[0-9A-Fa-f]{6}", fullmatch=True),
        min_size=1,
        max_size=5
    ))
    
    brand_rules = draw(st.text(min_size=10, max_size=500))
    
    # Generate image URL if requested
    if with_image_url:
        current_image_url = draw(st.from_regex(
            r"https://generativelanguage\.googleapis\.com/v1beta/files/[a-zA-Z0-9_-]+",
            fullmatch=True
        ))
    else:
        current_image_url = None
    
    attempt_count = draw(st.integers(min_value=0, max_value=2))
    
    # Generate audit history if requested
    if with_audit_history:
        audit_history = draw(st.lists(
            st.fixed_dictionaries({
                "approved": st.booleans(),
                "reason": st.text(min_size=5, max_size=100),
                "fix_suggestion": st.text(min_size=0, max_size=100)
            }),
            min_size=1,
            max_size=3
        ))
    else:
        audit_history = []
    
    is_approved = draw(st.booleans())
    
    return JobState(
        prompt=prompt,
        brand_hex_codes=hex_codes,
        brand_rules=brand_rules,
        current_image_url=current_image_url,
        attempt_count=attempt_count,
        audit_history=audit_history,
        is_approved=is_approved
    )


# ============================================================================
# Property-Based Tests for Generation Node
# ============================================================================

@settings(max_examples=100)
@given(state=job_state_strategy())
def test_property_1_generation_produces_image_url(state):
    """
    **Feature: mobius-brand-governance, Property 1: Generation produces image URL**
    
    For any JobState with a valid prompt and brand_hex_codes, when the generation 
    node executes successfully, the resulting state should contain a non-None 
    current_image_url.
    
    **Validates: Requirements 1.2**
    """
    # Mock the Gemini API to return a successful result
    with patch("orchestrator.genai.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.text = "https://generativelanguage.googleapis.com/v1beta/files/test-image-123"
        mock_client.return_value.models.generate_content.return_value = mock_response
        
        # Execute the generation node
        result_state = generate_node(state)
        
        # Property: Successful generation produces non-None image URL
        assert result_state["current_image_url"] is not None
        assert isinstance(result_state["current_image_url"], str)
        assert len(result_state["current_image_url"]) > 0


@settings(max_examples=100)
@given(state=job_state_strategy())
def test_property_8_attempt_count_monotonically_increases(state):
    """
    **Feature: mobius-brand-governance, Property 8: Attempt count monotonically increases**
    
    For any JobState, after executing the generation node, the attempt_count in 
    the resulting state should be exactly one greater than the input state's 
    attempt_count.
    
    **Validates: Requirements 1.2**
    """
    # Mock the Gemini API to return a successful result
    with patch("orchestrator.genai.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.text = "https://generativelanguage.googleapis.com/v1beta/files/test-image-456"
        mock_client.return_value.models.generate_content.return_value = mock_response
        
        # Store original attempt count
        original_attempt_count = state["attempt_count"]
        
        # Execute the generation node
        result_state = generate_node(state)
        
        # Property: Attempt count increases by exactly 1
        assert result_state["attempt_count"] == original_attempt_count + 1


@settings(max_examples=100)
@given(state=job_state_strategy())
def test_property_8_attempt_count_increases_even_on_error(state):
    """
    **Feature: mobius-brand-governance, Property 8: Attempt count monotonically increases**
    
    For any JobState, after executing the generation node (even with API errors), 
    the attempt_count should still increase by exactly one.
    
    **Validates: Requirements 1.2**
    """
    # Mock the Gemini API to raise an exception
    with patch("orchestrator.genai.Client") as mock_client:
        mock_client.return_value.models.generate_content.side_effect = Exception("API Error: Service unavailable")
        
        # Store original attempt count
        original_attempt_count = state["attempt_count"]
        
        # Execute the generation node
        result_state = generate_node(state)
        
        # Property: Attempt count increases by exactly 1 even on error
        assert result_state["attempt_count"] == original_attempt_count + 1
        
        # Additionally verify that image URL is None on error
        assert result_state["current_image_url"] is None


# ============================================================================
# Property-Based Tests for Audit Node
# ============================================================================

@settings(max_examples=100)
@given(state=job_state_strategy(with_image_url=True))
def test_property_2_audit_result_schema_compliance(state):
    """
    **Feature: mobius-brand-governance, Property 2: Audit result schema compliance**
    
    For any audit result in the audit_history, it must contain exactly three keys: 
    "approved" (boolean), "reason" (string), and "fix_suggestion" (string).
    
    **Validates: Requirements 2.1**
    """
    # Mock the Gemini API to return a valid audit result
    with patch("orchestrator.genai.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.text = '{"approved": true, "reason": "Complies with brand guidelines", "fix_suggestion": ""}'
        mock_client.return_value.models.generate_content.return_value = mock_response
        
        # Execute the audit node
        result_state = audit_node(state)
        
        # Property: All audit results must have the correct schema
        for audit_result in result_state["audit_history"]:
            # Must have exactly three keys
            assert set(audit_result.keys()) == {"approved", "reason", "fix_suggestion"}
            
            # Verify types
            assert isinstance(audit_result["approved"], bool)
            assert isinstance(audit_result["reason"], str)
            assert isinstance(audit_result["fix_suggestion"], str)



@settings(max_examples=100)
@given(state=job_state_strategy(with_image_url=True, with_audit_history=True))
def test_property_3_audit_appends_to_history(state):
    """
    **Feature: mobius-brand-governance, Property 3: Audit appends to history**
    
    For any JobState with an image URL, when the audit node executes, the 
    resulting state should have audit_history length increased by exactly one.
    
    **Validates: Requirements 1.3**
    """
    # Mock the Gemini API to return a valid audit result
    with patch("orchestrator.genai.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.text = '{"approved": false, "reason": "Missing brand colors", "fix_suggestion": "Add more brand colors"}'
        mock_client.return_value.models.generate_content.return_value = mock_response
        
        # Store original audit history length
        original_history_length = len(state["audit_history"])
        
        # Execute the audit node
        result_state = audit_node(state)
        
        # Property: Audit history length increases by exactly 1
        assert len(result_state["audit_history"]) == original_history_length + 1


# ============================================================================
# Property-Based Tests for Correction Node
# ============================================================================

@settings(max_examples=100)
@given(state=job_state_strategy(with_audit_history=True))
def test_property_4_correction_appends_fix_suggestion(state):
    """
    **Feature: mobius-brand-governance, Property 4: Correction appends fix suggestion**
    
    For any JobState with at least one audit result containing a fix_suggestion, 
    when the correction node executes, the resulting prompt should contain both 
    the original prompt text and the fix_suggestion text.
    
    **Validates: Requirements 2.2**
    """
    # Ensure the last audit result has a non-empty fix_suggestion
    if len(state["audit_history"]) > 0:
        # Modify the last audit to ensure it has a fix_suggestion
        last_audit = state["audit_history"][-1].copy()
        
        # Only test if there's a non-empty fix_suggestion
        if last_audit.get("fix_suggestion", ""):
            fix_suggestion = last_audit["fix_suggestion"]
            original_prompt = state["prompt"]
            
            # Execute the correction node
            result_state = correct_node(state)
            
            # Property: Resulting prompt contains both original prompt and fix_suggestion
            assert original_prompt in result_state["prompt"], \
                f"Original prompt '{original_prompt}' not found in result '{result_state['prompt']}'"
            assert fix_suggestion in result_state["prompt"], \
                f"Fix suggestion '{fix_suggestion}' not found in result '{result_state['prompt']}'"


# ============================================================================
# Property-Based Tests for Persistence Helper
# ============================================================================

@settings(max_examples=100)
@given(
    state=job_state_strategy(with_image_url=True, with_audit_history=True),
    status=st.sampled_from(["GENERATED", "AUDITED", "CORRECTED"])
)
def test_property_9_graceful_degradation_without_credentials(state, status):
    """
    **Feature: mobius-brand-governance, Property 9: Graceful degradation without credentials**
    
    For any JobState and status string, calling persist_state with missing 
    SUPABASE_URL or SUPABASE_KEY environment variables should not raise an exception.
    
    **Validates: Requirements 4.4**
    """
    # Save original environment variables
    original_url = os.environ.get("SUPABASE_URL")
    original_key = os.environ.get("SUPABASE_KEY")
    
    try:
        # Remove Supabase credentials from environment
        if "SUPABASE_URL" in os.environ:
            del os.environ["SUPABASE_URL"]
        if "SUPABASE_KEY" in os.environ:
            del os.environ["SUPABASE_KEY"]
        
        # Property: persist_state should not raise an exception
        # This should complete without raising any exception
        persist_state(state, status)
        
        # If we reach here, the test passes (no exception was raised)
        assert True
        
    finally:
        # Restore original environment variables
        if original_url is not None:
            os.environ["SUPABASE_URL"] = original_url
        if original_key is not None:
            os.environ["SUPABASE_KEY"] = original_key


@settings(max_examples=100)
@given(
    state=job_state_strategy(with_image_url=True, with_audit_history=True),
    status=st.sampled_from(["GENERATED", "AUDITED", "CORRECTED"])
)
def test_property_9_graceful_degradation_with_connection_error(state, status):
    """
    **Feature: mobius-brand-governance, Property 9: Graceful degradation without credentials**
    
    For any JobState and status string, calling persist_state with invalid 
    Supabase credentials (causing connection errors) should not raise an exception.
    
    **Validates: Requirements 4.4**
    """
    # Save original environment variables
    original_url = os.environ.get("SUPABASE_URL")
    original_key = os.environ.get("SUPABASE_KEY")
    
    try:
        # Set invalid Supabase credentials
        os.environ["SUPABASE_URL"] = "https://invalid-url.supabase.co"
        os.environ["SUPABASE_KEY"] = "invalid-key-12345"
        
        # Mock create_client to raise an exception
        with patch("orchestrator.create_client") as mock_create_client:
            mock_create_client.side_effect = Exception("Connection failed")
            
            # Property: persist_state should not raise an exception
            # This should complete without raising any exception
            persist_state(state, status)
            
            # If we reach here, the test passes (no exception was raised)
            assert True
        
    finally:
        # Restore original environment variables
        if original_url is not None:
            os.environ["SUPABASE_URL"] = original_url
        elif "SUPABASE_URL" in os.environ:
            del os.environ["SUPABASE_URL"]
            
        if original_key is not None:
            os.environ["SUPABASE_KEY"] = original_key
        elif "SUPABASE_KEY" in os.environ:
            del os.environ["SUPABASE_KEY"]


# ============================================================================
# Property-Based Tests for Routing Logic
# ============================================================================

@settings(max_examples=100)
@given(state=job_state_strategy())
def test_property_5_non_approved_states_route_to_correction(state):
    """
    **Feature: mobius-brand-governance, Property 5: Non-approved states route to correction**
    
    For any JobState where is_approved is False and attempt_count is less than 3, 
    the route_decision function should return "correct" (not END).
    
    **Validates: Requirements 1.4**
    """
    # Ensure the state meets the preconditions
    test_state = state.copy()
    test_state["is_approved"] = False
    test_state["attempt_count"] = 0  # Start with 0 to ensure < 3
    
    # Test with attempt_count values 0, 1, 2 (all less than 3)
    for attempt_count in [0, 1, 2]:
        test_state["attempt_count"] = attempt_count
        
        # Execute routing decision
        result = route_decision(test_state)
        
        # Property: Non-approved states with attempts < 3 should route to "correct"
        assert result == "correct", \
            f"Expected 'correct' but got {result} for attempt_count={attempt_count}, is_approved=False"


@settings(max_examples=100)
@given(state=job_state_strategy())
def test_property_6_approved_states_complete_workflow(state):
    """
    **Feature: mobius-brand-governance, Property 6: Approved states complete workflow**
    
    For any JobState where is_approved is True, the route_decision function 
    should return END regardless of attempt_count.
    
    **Validates: Requirements 1.5**
    """
    # Ensure the state is approved
    test_state = state.copy()
    test_state["is_approved"] = True
    
    # Test with various attempt_count values (0, 1, 2, 3, 5)
    for attempt_count in [0, 1, 2, 3, 5]:
        test_state["attempt_count"] = attempt_count
        
        # Execute routing decision
        result = route_decision(test_state)
        
        # Property: Approved states should always return END
        assert result == END, \
            f"Expected END but got {result} for attempt_count={attempt_count}, is_approved=True"


@settings(max_examples=100)
@given(state=job_state_strategy())
def test_property_7_max_attempts_enforces_termination(state):
    """
    **Feature: mobius-brand-governance, Property 7: Max attempts enforces termination**
    
    For any JobState where attempt_count is greater than or equal to 3 and 
    is_approved is False, the route_decision function should return END.
    
    **Validates: Requirements 6.1, 6.2**
    """
    # Ensure the state is not approved
    test_state = state.copy()
    test_state["is_approved"] = False
    
    # Test with attempt_count values >= 3 (3, 4, 5, 10)
    for attempt_count in [3, 4, 5, 10]:
        test_state["attempt_count"] = attempt_count
        
        # Execute routing decision
        result = route_decision(test_state)
        
        # Property: Max attempts should enforce termination (return END)
        assert result == END, \
            f"Expected END but got {result} for attempt_count={attempt_count}, is_approved=False"


# ============================================================================
# Unit Tests for HTTP Endpoint
# ============================================================================

def test_http_endpoint_successful_workflow_completion():
    """
    Test that successful workflow completion returns 200 with approved state.
    
    **Validates: Requirements 7.3**
    """
    # Create a valid request
    request = MobiusJobRequest(
        prompt="A modern tech startup logo",
        brand_hex_codes=["#FF6B6B", "#4ECDC4"],
        brand_rules="Minimalist design, sans-serif fonts"
    )
    
    # Mock the workflow execution to return an approved state
    with patch("orchestrator.genai.Client") as mock_gemini:
        
        # Mock successful image generation and audit
        mock_gen_response = MagicMock()
        mock_gen_response.text = "https://generativelanguage.googleapis.com/v1beta/files/approved-image-123"
        
        # Mock audit that approves on first attempt
        mock_audit_response = MagicMock()
        mock_audit_response.text = '{"approved": true, "reason": "Complies with all brand guidelines", "fix_suggestion": ""}'
        
        # Configure mock to return different responses for generation and audit
        mock_gemini.return_value.models.generate_content.side_effect = [mock_gen_response, mock_audit_response]
        
        # Execute the endpoint implementation directly
        result = _run_mobius_job_impl(request)
        
        # Verify response structure
        assert result["status"] == "success"
        assert "final_state" in result
        assert result["final_state"]["is_approved"] is True
        assert result["final_state"]["current_image_url"] is not None


def test_http_endpoint_max_retries():
    """
    Test that max retries returns 200 with failure status.
    
    **Validates: Requirements 7.4**
    """
    # Create a valid request
    request = MobiusJobRequest(
        prompt="A modern tech startup logo",
        brand_hex_codes=["#FF6B6B", "#4ECDC4"],
        brand_rules="Minimalist design, sans-serif fonts"
    )
    
    # Mock the workflow execution to reject all attempts
    with patch("orchestrator.genai.Client") as mock_gemini:
        
        # Mock successful image generation
        mock_gen_response = MagicMock()
        mock_gen_response.text = "https://generativelanguage.googleapis.com/v1beta/files/rejected-image-456"
        
        # Mock audit that always rejects
        mock_audit_response = MagicMock()
        mock_audit_response.text = '{"approved": false, "reason": "Does not comply with brand guidelines", "fix_suggestion": "use more geometric shapes"}'
        
        # Configure mock to alternate between generation and audit responses
        mock_gemini.return_value.models.generate_content.side_effect = [
            mock_gen_response, mock_audit_response,  # Attempt 1
            mock_gen_response, mock_audit_response,  # Attempt 2
            mock_gen_response, mock_audit_response,  # Attempt 3
        ]
        
        # Execute the endpoint implementation directly
        result = _run_mobius_job_impl(request)
        
        # Verify response structure for max retries
        assert result["status"] == "failed"
        assert result["reason"] == "max_retries_reached"
        assert "final_state" in result
        assert result["final_state"]["is_approved"] is False
        assert result["final_state"]["attempt_count"] >= 3


def test_http_endpoint_internal_error():
    """
    Test that internal errors return 500 with error message.
    
    **Validates: Requirements 7.5**
    """
    # Create a valid request
    request = MobiusJobRequest(
        prompt="A modern tech startup logo",
        brand_hex_codes=["#FF6B6B", "#4ECDC4"],
        brand_rules="Minimalist design, sans-serif fonts"
    )
    
    # Mock the workflow to raise an exception during graph compilation
    with patch("orchestrator.StateGraph") as mock_state_graph:
        mock_state_graph.side_effect = Exception("Graph compilation failed")
        
        # Execute the endpoint implementation directly
        result = _run_mobius_job_impl(request)
        
        # Verify error response structure
        assert result["status"] == "error"
        assert "message" in result
        assert "Internal workflow error" in result["message"]
        assert "Graph compilation failed" in result["message"]
