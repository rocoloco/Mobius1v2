"""
Property-Based Tests for Error Logging Completeness.

**Feature: gemini-3-dual-architecture, Property 18: Error Logging Completeness**
**Validates: Requirements 9.1**

Tests that all Gemini API failures are logged with complete context including
model name, operation type, and error details.
"""

import pytest
from hypothesis import given, strategies as st, settings as hypothesis_settings
from unittest.mock import Mock, patch, AsyncMock
from mobius.tools.gemini import GeminiClient
from google.api_core import exceptions as google_exceptions
import structlog
import asyncio


# Strategy for generating various error types
@st.composite
def error_types(draw):
    """Generate various error types that might occur during API calls."""
    error_choices = [
        google_exceptions.ResourceExhausted("Rate limit exceeded"),
        google_exceptions.Unauthenticated("Invalid API key"),
        google_exceptions.DeadlineExceeded("Request timeout"),
        google_exceptions.ServiceUnavailable("Service unavailable"),
        Exception("Generic API error"),
        TimeoutError("Operation timed out"),
        asyncio.TimeoutError("Async operation timed out"),
    ]
    return draw(st.sampled_from(error_choices))


# Strategy for operation types
operation_types_strategy = st.sampled_from([
    "image_analysis",
    "pdf_analysis",
    "compressed_extraction",
    "image_generation",
    "compliance_audit",
    "brand_extraction"
])


@given(
    error=error_types(),
    operation_type=operation_types_strategy
)
@hypothesis_settings(max_examples=50, deadline=None)
@pytest.mark.asyncio
async def test_error_logging_includes_model_name(error, operation_type):
    """
    **Feature: gemini-3-dual-architecture, Property 18: Error Logging Completeness**
    **Validates: Requirements 9.1**
    
    Property: For any Gemini API failure, the error log should contain the model name.
    
    This ensures that when debugging issues, operators can quickly identify which
    model (reasoning or vision) encountered the error.
    """
    # Capture logs
    captured_logs = []
    
    def capture_log(logger, method_name, event_dict):
        captured_logs.append(event_dict)
        return ""  # Return empty string to satisfy logger
    
    # Configure structlog to capture logs with a simple logger factory
    structlog.configure(
        processors=[capture_log],
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=lambda: structlog.PrintLogger(file=None),
    )
    
    # Create client (mock the API key to avoid initialization issues)
    with patch("mobius.tools.gemini.genai.configure"):
        with patch("mobius.tools.gemini.genai.GenerativeModel"):
            client = GeminiClient()
    
    # Determine which model should be used based on operation type
    if operation_type in ["image_generation"]:
        expected_model = client.vision_model
        model_name = "gemini-3-pro-image-preview"
    else:
        expected_model = client.reasoning_model
        model_name = "gemini-3-pro-preview"
    
    # Call the error handler
    handled_error = client._handle_api_error(error, model_name, operation_type)
    
    # Verify that at least one log entry contains the model name
    assert len(captured_logs) > 0, f"No logs were captured. Captured: {captured_logs}"
    
    # Check that the error log contains model_name (look at all logs, not just those with "error" in event)
    # The _handle_api_error method logs with specific event names like "gemini_rate_limit_exceeded"
    error_logs = captured_logs  # Use all captured logs
    
    # Verify model_name is in at least one log
    model_name_found = any(
        log.get("model_name") == model_name
        for log in error_logs
    )
    assert model_name_found, f"model_name '{model_name}' not found in logs: {error_logs}"


@given(
    error=error_types(),
    operation_type=operation_types_strategy
)
@hypothesis_settings(max_examples=50, deadline=None)
@pytest.mark.asyncio
async def test_error_logging_includes_operation_type(error, operation_type):
    """
    **Feature: gemini-3-dual-architecture, Property 18: Error Logging Completeness**
    **Validates: Requirements 9.1**
    
    Property: For any Gemini API failure, the error log should contain the operation type.
    
    This helps operators understand what operation was being performed when the error occurred.
    """
    # Capture logs
    captured_logs = []
    
    def capture_log(logger, method_name, event_dict):
        captured_logs.append(event_dict)
        return ""  # Return empty string to satisfy logger
    
    # Configure structlog to capture logs with a simple logger factory
    structlog.configure(
        processors=[capture_log],
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=lambda: structlog.PrintLogger(file=None),
    )
    
    # Create client (mock the API key to avoid initialization issues)
    with patch("mobius.tools.gemini.genai.configure"):
        with patch("mobius.tools.gemini.genai.GenerativeModel"):
            client = GeminiClient()
    
    # Determine model name
    if operation_type in ["image_generation"]:
        model_name = "gemini-3-pro-image-preview"
    else:
        model_name = "gemini-3-pro-preview"
    
    # Call the error handler
    handled_error = client._handle_api_error(error, model_name, operation_type)
    
    # Verify that at least one log entry contains the operation type
    assert len(captured_logs) > 0, f"No logs were captured. Captured: {captured_logs}"
    
    # Check that the error log contains operation_type (look at all logs)
    error_logs = captured_logs  # Use all captured logs
    
    # Verify operation_type is in at least one log
    operation_type_found = any(
        log.get("operation_type") == operation_type
        for log in error_logs
    )
    assert operation_type_found, f"operation_type '{operation_type}' not found in logs: {error_logs}"


@given(
    error=error_types(),
    operation_type=operation_types_strategy
)
@hypothesis_settings(max_examples=50, deadline=None)
@pytest.mark.asyncio
async def test_error_logging_includes_error_details(error, operation_type):
    """
    **Feature: gemini-3-dual-architecture, Property 18: Error Logging Completeness**
    **Validates: Requirements 9.1**
    
    Property: For any Gemini API failure, the error log should contain error details.
    
    This ensures operators have sufficient information to diagnose and resolve issues.
    """
    # Capture logs
    captured_logs = []
    
    def capture_log(logger, method_name, event_dict):
        captured_logs.append(event_dict)
        return ""  # Return empty string to satisfy logger
    
    # Configure structlog to capture logs with a simple logger factory
    structlog.configure(
        processors=[capture_log],
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=lambda: structlog.PrintLogger(file=None),
    )
    
    # Create client (mock the API key to avoid initialization issues)
    with patch("mobius.tools.gemini.genai.configure"):
        with patch("mobius.tools.gemini.genai.GenerativeModel"):
            client = GeminiClient()
    
    # Determine model name
    if operation_type in ["image_generation"]:
        model_name = "gemini-3-pro-image-preview"
    else:
        model_name = "gemini-3-pro-preview"
    
    # Call the error handler
    handled_error = client._handle_api_error(error, model_name, operation_type)
    
    # Verify that at least one log entry contains error details
    assert len(captured_logs) > 0, f"No logs were captured. Captured: {captured_logs}"
    
    # Check that the error log contains error information (look at all logs)
    error_logs = captured_logs  # Use all captured logs
    
    # Verify error details are in at least one log (error_type or error_message)
    error_details_found = any(
        log.get("error_type") is not None or log.get("error_message") is not None
        for log in error_logs
    )
    assert error_details_found, f"Error details not found in logs: {error_logs}"


@given(
    error=error_types(),
    operation_type=operation_types_strategy
)
@hypothesis_settings(max_examples=50, deadline=None)
@pytest.mark.asyncio
async def test_all_required_fields_present_in_error_log(error, operation_type):
    """
    **Feature: gemini-3-dual-architecture, Property 18: Error Logging Completeness**
    **Validates: Requirements 9.1**
    
    Property: For any Gemini API failure, the error log should contain ALL required fields:
    model_name, operation_type, and error details.
    
    This is the comprehensive test that ensures complete error context is always logged.
    """
    # Capture logs
    captured_logs = []
    
    def capture_log(logger, method_name, event_dict):
        captured_logs.append(event_dict)
        return ""  # Return empty string to satisfy logger
    
    # Configure structlog to capture logs with a simple logger factory
    structlog.configure(
        processors=[capture_log],
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=lambda: structlog.PrintLogger(file=None),
    )
    
    # Create client (mock the API key to avoid initialization issues)
    with patch("mobius.tools.gemini.genai.configure"):
        with patch("mobius.tools.gemini.genai.GenerativeModel"):
            client = GeminiClient()
    
    # Determine model name
    if operation_type in ["image_generation"]:
        model_name = "gemini-3-pro-image-preview"
    else:
        model_name = "gemini-3-pro-preview"
    
    # Call the error handler
    handled_error = client._handle_api_error(error, model_name, operation_type)
    
    # Verify that at least one log entry contains all required fields
    assert len(captured_logs) > 0, f"No logs were captured. Captured: {captured_logs}"
    
    # Check that the error log contains all required fields (look at all logs)
    error_logs = captured_logs  # Use all captured logs
    
    # Verify all required fields are present in at least one log
    complete_log_found = any(
        log.get("model_name") == model_name and
        log.get("operation_type") == operation_type and
        (log.get("error_type") is not None or log.get("error_message") is not None)
        for log in error_logs
    )
    
    assert complete_log_found, (
        f"Complete error log not found. Expected model_name='{model_name}', "
        f"operation_type='{operation_type}', and error details. "
        f"Actual logs: {error_logs}"
    )
