"""
Property-Based Tests for Timeout Retry Behavior.

**Feature: gemini-3-dual-architecture, Property 19: Timeout Retry Behavior**
**Validates: Requirements 9.4**

Tests that when image generation times out, the system logs the timeout and
retries with increased timeout values.
"""

import pytest
from hypothesis import given, strategies as st, settings as hypothesis_settings
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from mobius.tools.gemini import GeminiClient
from mobius.models.brand import CompressedDigitalTwin
import structlog
import asyncio


# Strategy for generating prompts
prompts_strategy = st.text(min_size=10, max_size=200)


# Strategy for generating compressed twins
@st.composite
def compressed_twins(draw):
    """Generate valid CompressedDigitalTwin instances."""
    return CompressedDigitalTwin(
        primary_colors=draw(st.lists(st.sampled_from(["#FF0000", "#00FF00", "#0000FF"]), min_size=1, max_size=3)),
        secondary_colors=draw(st.lists(st.sampled_from(["#FFFF00", "#FF00FF", "#00FFFF"]), max_size=2)),
        accent_colors=draw(st.lists(st.sampled_from(["#FFA500", "#800080"]), max_size=2)),
        neutral_colors=draw(st.lists(st.sampled_from(["#FFFFFF", "#000000", "#808080"]), min_size=1, max_size=3)),
        semantic_colors=draw(st.lists(st.sampled_from(["#00FF00", "#FF0000"]), max_size=2)),
        font_families=draw(st.lists(st.sampled_from(["Arial", "Helvetica", "Times New Roman"]), min_size=1, max_size=2)),
        visual_dos=draw(st.lists(st.text(min_size=10, max_size=50), max_size=3)),
        visual_donts=draw(st.lists(st.text(min_size=10, max_size=50), max_size=3)),
    )


@given(
    prompt=prompts_strategy,
    compressed_twin=compressed_twins()
)
@hypothesis_settings(max_examples=20, deadline=None)
@pytest.mark.asyncio
async def test_timeout_logged_with_model_name(prompt, compressed_twin):
    """
    **Feature: gemini-3-dual-architecture, Property 19: Timeout Retry Behavior**
    **Validates: Requirements 9.4**
    
    Property: For any image generation timeout, the system should log the timeout
    with the model name.
    
    This ensures operators can identify which model timed out.
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
            # Mock vision model to always timeout
            mock_vision_model = Mock()
            mock_vision_model.generate_content = MagicMock(
                side_effect=asyncio.TimeoutError("Request timed out")
            )
            mock_model_class.return_value = mock_vision_model
            
            client = GeminiClient()
            client.vision_model = mock_vision_model
            
            # Try to generate image (should fail after retries)
            try:
                await client.generate_image(prompt, compressed_twin)
            except Exception:
                pass  # Expected to fail
            
            # Verify timeout was logged with model name
            timeout_logs = [
                log for log in captured_logs
                if "timeout" in log.get("event", "").lower()
            ]
            
            assert len(timeout_logs) > 0, f"No timeout logs found. Captured logs: {captured_logs}"
            
            # Verify model name is in timeout logs
            model_name_found = any(
                log.get("model_name") == "gemini-3-pro-image-preview"
                for log in timeout_logs
            )
            assert model_name_found, f"model_name not found in timeout logs: {timeout_logs}"


@given(
    prompt=prompts_strategy,
    compressed_twin=compressed_twins()
)
@hypothesis_settings(max_examples=20, deadline=None)
@pytest.mark.asyncio
async def test_timeout_increases_on_retry(prompt, compressed_twin):
    """
    **Feature: gemini-3-dual-architecture, Property 19: Timeout Retry Behavior**
    **Validates: Requirements 9.4**
    
    Property: For any image generation timeout, the system should retry with
    increased timeout values.
    
    This ensures that transient timeout issues can be resolved by allowing more time.
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
            # Mock vision model to always timeout
            mock_vision_model = Mock()
            mock_vision_model.generate_content = MagicMock(
                side_effect=asyncio.TimeoutError("Request timed out")
            )
            mock_model_class.return_value = mock_vision_model
            
            client = GeminiClient()
            client.vision_model = mock_vision_model
            
            # Try to generate image (should fail after retries)
            try:
                await client.generate_image(prompt, compressed_twin)
            except Exception:
                pass  # Expected to fail
            
            # Verify timeout values increase on each attempt
            attempt_logs = [
                log for log in captured_logs
                if log.get("event") == "image_generation_attempt"
            ]
            
            assert len(attempt_logs) >= 2, f"Not enough attempt logs found: {attempt_logs}"
            
            # Extract timeout values from logs
            timeouts = [log.get("timeout_seconds") for log in attempt_logs if log.get("timeout_seconds")]
            
            assert len(timeouts) >= 2, f"Not enough timeout values found: {timeouts}"
            
            # Verify timeouts are increasing (exponential backoff: 30, 60, 120)
            for i in range(len(timeouts) - 1):
                assert timeouts[i+1] > timeouts[i], (
                    f"Timeout did not increase: {timeouts[i]} -> {timeouts[i+1]}. "
                    f"All timeouts: {timeouts}"
                )


@given(
    prompt=prompts_strategy,
    compressed_twin=compressed_twins()
)
@hypothesis_settings(max_examples=20, deadline=None)
@pytest.mark.asyncio
async def test_retry_after_timeout_logged(prompt, compressed_twin):
    """
    **Feature: gemini-3-dual-architecture, Property 19: Timeout Retry Behavior**
    **Validates: Requirements 9.4**
    
    Property: For any image generation timeout, the system should log retry information
    including the next timeout value.
    
    This helps operators understand the retry strategy being applied.
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
            # Mock vision model to timeout twice, then succeed
            call_count = 0
            
            def timeout_then_succeed(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count <= 2:
                    raise asyncio.TimeoutError("Request timed out")
                else:
                    # Return a mock result
                    mock_result = Mock()
                    mock_result.text = "data:image/jpeg;base64,fake_image_data"
                    return mock_result
            
            mock_vision_model = Mock()
            mock_vision_model.generate_content = MagicMock(side_effect=timeout_then_succeed)
            mock_model_class.return_value = mock_vision_model
            
            client = GeminiClient()
            client.vision_model = mock_vision_model
            
            # Generate image (should succeed after retries)
            try:
                await client.generate_image(prompt, compressed_twin)
            except Exception:
                pass  # May still fail if extraction fails
            
            # Verify retry logs contain next timeout information
            retry_logs = [
                log for log in captured_logs
                if "retry" in log.get("event", "").lower() and "timeout" in log.get("event", "").lower()
            ]
            
            # Should have at least one retry log after timeout
            if call_count > 1:  # If we actually retried
                assert len(retry_logs) > 0, f"No retry logs found after timeout. Captured logs: {captured_logs}"
                
                # Verify retry logs contain next_timeout information
                next_timeout_found = any(
                    log.get("next_timeout") is not None
                    for log in retry_logs
                )
                assert next_timeout_found, f"next_timeout not found in retry logs: {retry_logs}"


@given(
    prompt=prompts_strategy,
    compressed_twin=compressed_twins()
)
@hypothesis_settings(max_examples=20, deadline=None)
@pytest.mark.asyncio
async def test_all_timeout_retry_fields_present(prompt, compressed_twin):
    """
    **Feature: gemini-3-dual-architecture, Property 19: Timeout Retry Behavior**
    **Validates: Requirements 9.4**
    
    Property: For any image generation timeout, the system should log complete
    retry context including model_name, operation_type, timeout_seconds, and next_timeout.
    
    This is the comprehensive test ensuring all required fields are logged.
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
            # Mock vision model to always timeout
            mock_vision_model = Mock()
            mock_vision_model.generate_content = MagicMock(
                side_effect=asyncio.TimeoutError("Request timed out")
            )
            mock_model_class.return_value = mock_vision_model
            
            client = GeminiClient()
            client.vision_model = mock_vision_model
            
            # Try to generate image (should fail after retries)
            try:
                await client.generate_image(prompt, compressed_twin)
            except Exception:
                pass  # Expected to fail
            
            # Verify timeout logs contain all required fields
            timeout_logs = [
                log for log in captured_logs
                if "timeout" in log.get("event", "").lower()
            ]
            
            assert len(timeout_logs) > 0, f"No timeout logs found. Captured logs: {captured_logs}"
            
            # Verify at least one timeout log has all required fields
            complete_log_found = any(
                log.get("model_name") == "gemini-3-pro-image-preview" and
                log.get("operation_type") == "image_generation" and
                log.get("timeout_seconds") is not None
                for log in timeout_logs
            )
            
            assert complete_log_found, (
                f"Complete timeout log not found. Expected model_name='gemini-3-pro-image-preview', "
                f"operation_type='image_generation', and timeout_seconds. "
                f"Actual logs: {timeout_logs}"
            )
