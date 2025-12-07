"""
Property-Based Tests for Graceful Audit Degradation.

**Feature: gemini-3-dual-architecture, Property 20: Graceful Audit Degradation**
**Validates: Requirements 9.5**

Tests that when audit analysis fails, the system returns a partial compliance score
with error annotations rather than failing completely.
"""

import pytest
from hypothesis import given, strategies as st, settings as hypothesis_settings
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from mobius.tools.gemini import GeminiClient
from mobius.models.brand import BrandGuidelines, Color, Typography, LogoRule, VoiceTone, BrandRule
from mobius.models.compliance import ComplianceScore, CategoryScore, Violation, Severity
from google.api_core import exceptions as google_exceptions
import structlog
import asyncio


# Strategy for generating image URIs
image_uris_strategy = st.sampled_from([
    "https://example.com/image.jpg",
    "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
    "https://storage.googleapis.com/test/image.png"
])


# Strategy for generating brand guidelines
@st.composite
def brand_guidelines(draw):
    """Generate valid BrandGuidelines instances."""
    return BrandGuidelines(
        colors=[
            Color(
                name=draw(st.sampled_from(["Primary Blue", "Secondary Red", "Accent Yellow"])),
                hex=draw(st.sampled_from(["#0000FF", "#FF0000", "#FFFF00"])),
                usage=draw(st.sampled_from(["primary", "secondary", "accent", "neutral"])),
                usage_weight=draw(st.floats(min_value=0.0, max_value=1.0))
            )
        ],
        typography=[
            Typography(
                family=draw(st.sampled_from(["Arial", "Helvetica", "Times New Roman"])),
                weights=draw(st.lists(st.sampled_from(["400", "700"]), min_size=1, max_size=2)),
                usage=draw(st.text(min_size=5, max_size=50))
            )
        ],
        logos=[],
        voice=None,
        rules=[]
    )


# Strategy for generating various error types
@st.composite
def audit_errors(draw):
    """Generate various error types that might occur during audit."""
    error_choices = [
        google_exceptions.ResourceExhausted("Rate limit exceeded"),
        google_exceptions.Unauthenticated("Invalid API key"),
        google_exceptions.DeadlineExceeded("Request timeout"),
        google_exceptions.ServiceUnavailable("Service unavailable"),
        Exception("Generic API error"),
        ValueError("Invalid image format"),
        asyncio.TimeoutError("Async operation timed out"),
    ]
    return draw(st.sampled_from(error_choices))


@given(
    image_uri=image_uris_strategy,
    guidelines=brand_guidelines(),
    error=audit_errors()
)
@hypothesis_settings(max_examples=30, deadline=None)
@pytest.mark.asyncio
async def test_audit_failure_returns_partial_score(image_uri, guidelines, error):
    """
    **Feature: gemini-3-dual-architecture, Property 20: Graceful Audit Degradation**
    **Validates: Requirements 9.5**
    
    Property: For any audit analysis failure, the system should return a partial
    compliance score rather than raising an exception.
    
    This ensures the system degrades gracefully and provides useful feedback even
    when the audit service fails.
    """
    # Create client with mocked models
    with patch("mobius.tools.gemini.genai.configure"):
        with patch("mobius.tools.gemini.genai.GenerativeModel") as mock_model_class:
            # Mock reasoning model to always fail
            mock_reasoning_model = Mock()
            mock_reasoning_model.generate_content = MagicMock(side_effect=error)
            mock_model_class.return_value = mock_reasoning_model
            
            client = GeminiClient()
            client.reasoning_model = mock_reasoning_model
            
            # Mock httpx for image download
            with patch("httpx.AsyncClient") as mock_client:
                mock_response = Mock()
                mock_response.content = b"fake_image_data"
                mock_response.headers = {"content-type": "image/jpeg"}
                mock_response.raise_for_status = Mock()
                
                mock_context = AsyncMock()
                mock_context.__aenter__ = AsyncMock(return_value=mock_context)
                mock_context.__aexit__ = AsyncMock()
                mock_context.get = AsyncMock(return_value=mock_response)
                mock_client.return_value = mock_context
                
                # Call audit_compliance - should NOT raise exception
                result = await client.audit_compliance(image_uri, guidelines)
                
                # Verify result is a ComplianceScore (not an exception)
                assert isinstance(result, ComplianceScore), (
                    f"Expected ComplianceScore, got {type(result)}"
                )
                
                # Verify it's a partial score (overall_score should be 0.0)
                assert result.overall_score == 0.0, (
                    f"Expected overall_score=0.0 for failed audit, got {result.overall_score}"
                )
                
                # Verify approved is False
                assert result.approved is False, (
                    f"Expected approved=False for failed audit, got {result.approved}"
                )


@given(
    image_uri=image_uris_strategy,
    guidelines=brand_guidelines(),
    error=audit_errors()
)
@hypothesis_settings(max_examples=30, deadline=None)
@pytest.mark.asyncio
async def test_partial_score_contains_error_annotations(image_uri, guidelines, error):
    """
    **Feature: gemini-3-dual-architecture, Property 20: Graceful Audit Degradation**
    **Validates: Requirements 9.5**
    
    Property: For any audit analysis failure, the partial compliance score should
    contain error annotations describing what went wrong.
    
    This helps operators understand why the audit failed and what action to take.
    """
    # Create client with mocked models
    with patch("mobius.tools.gemini.genai.configure"):
        with patch("mobius.tools.gemini.genai.GenerativeModel") as mock_model_class:
            # Mock reasoning model to always fail
            mock_reasoning_model = Mock()
            mock_reasoning_model.generate_content = MagicMock(side_effect=error)
            mock_model_class.return_value = mock_reasoning_model
            
            client = GeminiClient()
            client.reasoning_model = mock_reasoning_model
            
            # Mock httpx for image download
            with patch("httpx.AsyncClient") as mock_client:
                mock_response = Mock()
                mock_response.content = b"fake_image_data"
                mock_response.headers = {"content-type": "image/jpeg"}
                mock_response.raise_for_status = Mock()
                
                mock_context = AsyncMock()
                mock_context.__aenter__ = AsyncMock(return_value=mock_context)
                mock_context.__aexit__ = AsyncMock()
                mock_context.get = AsyncMock(return_value=mock_response)
                mock_client.return_value = mock_context
                
                # Call audit_compliance
                result = await client.audit_compliance(image_uri, guidelines)
                
                # Verify categories contain error violations
                assert len(result.categories) > 0, "Expected at least one category in partial score"
                
                # Check that at least one category has violations
                has_violations = any(len(cat.violations) > 0 for cat in result.categories)
                assert has_violations, "Expected error violations in partial score categories"
                
                # Verify violations contain error information
                all_violations = [v for cat in result.categories for v in cat.violations]
                assert len(all_violations) > 0, "Expected at least one violation"
                
                # Check that violations mention the error
                error_mentioned = any(
                    "audit failed" in v.description.lower() or "error" in v.description.lower()
                    for v in all_violations
                )
                assert error_mentioned, (
                    f"Expected error to be mentioned in violations. "
                    f"Violations: {[v.description for v in all_violations]}"
                )


@given(
    image_uri=image_uris_strategy,
    guidelines=brand_guidelines(),
    error=audit_errors()
)
@hypothesis_settings(max_examples=30, deadline=None)
@pytest.mark.asyncio
async def test_partial_score_summary_indicates_failure(image_uri, guidelines, error):
    """
    **Feature: gemini-3-dual-architecture, Property 20: Graceful Audit Degradation**
    **Validates: Requirements 9.5**
    
    Property: For any audit analysis failure, the partial compliance score summary
    should clearly indicate that the audit failed and manual review is required.
    
    This ensures users understand the score is not a real audit result.
    """
    # Create client with mocked models
    with patch("mobius.tools.gemini.genai.configure"):
        with patch("mobius.tools.gemini.genai.GenerativeModel") as mock_model_class:
            # Mock reasoning model to always fail
            mock_reasoning_model = Mock()
            mock_reasoning_model.generate_content = MagicMock(side_effect=error)
            mock_model_class.return_value = mock_reasoning_model
            
            client = GeminiClient()
            client.reasoning_model = mock_reasoning_model
            
            # Mock httpx for image download
            with patch("httpx.AsyncClient") as mock_client:
                mock_response = Mock()
                mock_response.content = b"fake_image_data"
                mock_response.headers = {"content-type": "image/jpeg"}
                mock_response.raise_for_status = Mock()
                
                mock_context = AsyncMock()
                mock_context.__aenter__ = AsyncMock(return_value=mock_context)
                mock_context.__aexit__ = AsyncMock()
                mock_context.get = AsyncMock(return_value=mock_response)
                mock_client.return_value = mock_context
                
                # Call audit_compliance
                result = await client.audit_compliance(image_uri, guidelines)
                
                # Verify summary indicates failure
                summary_lower = result.summary.lower()
                
                failure_indicators = ["audit failed", "error", "manual review"]
                has_failure_indicator = any(
                    indicator in summary_lower
                    for indicator in failure_indicators
                )
                
                assert has_failure_indicator, (
                    f"Expected summary to indicate audit failure. "
                    f"Summary: {result.summary}"
                )


@given(
    image_uri=image_uris_strategy,
    guidelines=brand_guidelines(),
    error=audit_errors()
)
@hypothesis_settings(max_examples=30, deadline=None)
@pytest.mark.asyncio
async def test_partial_score_has_all_standard_categories(image_uri, guidelines, error):
    """
    **Feature: gemini-3-dual-architecture, Property 20: Graceful Audit Degradation**
    **Validates: Requirements 9.5**
    
    Property: For any audit analysis failure, the partial compliance score should
    include all standard categories (colors, typography, layout, logo_usage) with
    error annotations.
    
    This ensures the response structure is consistent with successful audits.
    """
    # Create client with mocked models
    with patch("mobius.tools.gemini.genai.configure"):
        with patch("mobius.tools.gemini.genai.GenerativeModel") as mock_model_class:
            # Mock reasoning model to always fail
            mock_reasoning_model = Mock()
            mock_reasoning_model.generate_content = MagicMock(side_effect=error)
            mock_model_class.return_value = mock_reasoning_model
            
            client = GeminiClient()
            client.reasoning_model = mock_reasoning_model
            
            # Mock httpx for image download
            with patch("httpx.AsyncClient") as mock_client:
                mock_response = Mock()
                mock_response.content = b"fake_image_data"
                mock_response.headers = {"content-type": "image/jpeg"}
                mock_response.raise_for_status = Mock()
                
                mock_context = AsyncMock()
                mock_context.__aenter__ = AsyncMock(return_value=mock_context)
                mock_context.__aexit__ = AsyncMock()
                mock_context.get = AsyncMock(return_value=mock_response)
                mock_client.return_value = mock_context
                
                # Call audit_compliance
                result = await client.audit_compliance(image_uri, guidelines)
                
                # Verify all standard categories are present
                expected_categories = {"colors", "typography", "layout", "logo_usage"}
                actual_categories = {cat.category for cat in result.categories}
                
                assert expected_categories == actual_categories, (
                    f"Expected categories {expected_categories}, got {actual_categories}"
                )
                
                # Verify all categories have passed=False
                all_failed = all(not cat.passed for cat in result.categories)
                assert all_failed, "Expected all categories to have passed=False in partial score"
                
                # Verify all categories have score=0.0
                all_zero = all(cat.score == 0.0 for cat in result.categories)
                assert all_zero, "Expected all categories to have score=0.0 in partial score"


@given(
    image_uri=image_uris_strategy,
    guidelines=brand_guidelines(),
    error=audit_errors()
)
@hypothesis_settings(max_examples=30, deadline=None)
@pytest.mark.asyncio
async def test_graceful_degradation_logged(image_uri, guidelines, error):
    """
    **Feature: gemini-3-dual-architecture, Property 20: Graceful Audit Degradation**
    **Validates: Requirements 9.5**
    
    Property: For any audit analysis failure, the system should log that it's
    returning a partial score due to graceful degradation.
    
    This helps operators understand that the system is functioning as designed.
    """
    # Capture logs
    captured_logs = []
    
    def capture_log(logger, method_name, event_dict):
        captured_logs.append(event_dict)
        return ""  # Return empty string to satisfy logger
    
    # Configure structlog to capture logs
    structlog.configure(
        processors=[capture_log],
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=lambda: structlog.PrintLogger(file=None),
    )
    
    # Create client with mocked models
    with patch("mobius.tools.gemini.genai.configure"):
        with patch("mobius.tools.gemini.genai.GenerativeModel") as mock_model_class:
            # Mock reasoning model to always fail
            mock_reasoning_model = Mock()
            mock_reasoning_model.generate_content = MagicMock(side_effect=error)
            mock_model_class.return_value = mock_reasoning_model
            
            client = GeminiClient()
            client.reasoning_model = mock_reasoning_model
            
            # Mock httpx for image download
            with patch("httpx.AsyncClient") as mock_client:
                mock_response = Mock()
                mock_response.content = b"fake_image_data"
                mock_response.headers = {"content-type": "image/jpeg"}
                mock_response.raise_for_status = Mock()
                
                mock_context = AsyncMock()
                mock_context.__aenter__ = AsyncMock(return_value=mock_context)
                mock_context.__aexit__ = AsyncMock()
                mock_context.get = AsyncMock(return_value=mock_response)
                mock_client.return_value = mock_context
                
                # Call audit_compliance
                result = await client.audit_compliance(image_uri, guidelines)
                
                # Verify graceful degradation was logged
                partial_logs = [
                    log for log in captured_logs
                    if "partial" in log.get("event", "").lower()
                ]
                
                assert len(partial_logs) > 0, (
                    f"Expected partial score log. Captured logs: {captured_logs}"
                )
                
                # Verify the log indicates it's returning a partial score
                partial_returned = any(
                    "partial" in log.get("event", "").lower() and
                    "return" in log.get("event", "").lower()
                    for log in captured_logs
                )
                
                assert partial_returned, (
                    f"Expected log indicating partial score return. "
                    f"Captured logs: {captured_logs}"
                )
