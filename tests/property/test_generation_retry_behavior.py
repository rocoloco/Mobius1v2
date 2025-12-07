"""
Property-based tests for generation retry behavior.

**Feature: gemini-3-dual-architecture, Property 9: Generation Retry Behavior**

Tests that image generation implements proper retry logic with exponential backoff.
"""

from hypothesis import given, strategies as st, settings as hypothesis_settings
import pytest
from unittest.mock import patch, MagicMock, AsyncMock, call
from mobius.tools.gemini import GeminiClient
from mobius.config import settings
from mobius.models.brand import CompressedDigitalTwin
import asyncio
import time


# Strategy for generating CompressedDigitalTwin
@st.composite
def compressed_twin_strategy(draw):
    """Generate random CompressedDigitalTwin instances."""
    return CompressedDigitalTwin(
        primary_colors=draw(st.lists(
            st.from_regex(r"#[0-9A-F]{6}", fullmatch=True),
            min_size=1,
            max_size=3
        ))
    )


# Strategy for generating error types
@st.composite
def error_type_strategy(draw):
    """Generate various error types that might occur during generation."""
    error_types = [
        Exception("API rate limit exceeded"),
        Exception("Service temporarily unavailable"),
        Exception("Network timeout"),
        Exception("Internal server error"),
        ConnectionError("Connection refused"),
        TimeoutError("Request timed out"),
    ]
    return draw(st.sampled_from(error_types))


# Property 9: Generation Retry Behavior
@given(
    prompt=st.text(min_size=10, max_size=200),
    compressed_twin=compressed_twin_strategy(),
    error=error_type_strategy()
)
@hypothesis_settings(max_examples=50)
async def test_generate_image_retries_on_failure(
    prompt: str,
    compressed_twin: CompressedDigitalTwin,
    error: Exception
):
    """
    **Feature: gemini-3-dual-architecture, Property 9: Generation Retry Behavior**
    
    *For any* failed image generation, the system should retry up to 3 times with 
    exponential backoff before returning an error.
    
    **Validates: Requirements 3.4**
    
    This property test verifies retry logic is properly implemented.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('asyncio.sleep', new_callable=AsyncMock):
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock the generate_content method to always fail
        mock_vision_model.generate_content = MagicMock(side_effect=error)
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image and expect it to fail after retries
        with pytest.raises(Exception):
            await client.generate_image(prompt, compressed_twin)
        
        # Verify generate_content was called exactly 3 times (max attempts)
        assert mock_vision_model.generate_content.call_count == 3, (
            f"generate_content should be called 3 times (max attempts), "
            f"got {mock_vision_model.generate_content.call_count}"
        )
        
        print(f"✓ generate_image retries 3 times on failure for error: {type(error).__name__}")


@given(
    compressed_twin=compressed_twin_strategy(),
    failure_count=st.integers(min_value=1, max_value=2)
)
@hypothesis_settings(max_examples=50)
async def test_generate_image_succeeds_after_retries(
    compressed_twin: CompressedDigitalTwin,
    failure_count: int
):
    """
    **Feature: gemini-3-dual-architecture, Property 9: Generation Retry Behavior**
    
    *For any* generation that fails initially but succeeds on retry, the system 
    should return the successful result.
    
    **Validates: Requirements 3.4**
    
    This property test verifies that retries can lead to success.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('asyncio.sleep', new_callable=AsyncMock):
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Create a side effect that fails N times then succeeds
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= failure_count:
                raise Exception(f"Failure {call_count}")
            else:
                # Success
                mock_result = MagicMock()
                mock_result.text = "data:image/png;base64,success"
                mock_result.parts = []
                return mock_result
        
        mock_vision_model.generate_content = MagicMock(side_effect=side_effect)
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image - should succeed after retries
        result = await client.generate_image("test prompt", compressed_twin)
        
        # Verify we got a successful result
        assert result is not None, "Should return a result after successful retry"
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"
        
        # Verify the correct number of attempts were made
        assert call_count == failure_count + 1, (
            f"Should make {failure_count + 1} attempts (fail {failure_count}, succeed 1), "
            f"got {call_count}"
        )
        
        print(f"✓ generate_image succeeds after {failure_count} failures")


def test_generate_image_exponential_backoff():
    """
    **Feature: gemini-3-dual-architecture, Property 9: Generation Retry Behavior**
    
    Verify that retry delays follow exponential backoff pattern (1s, 2s, 4s).
    
    **Validates: Requirements 3.4**
    
    This test ensures proper backoff timing between retries.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('asyncio.sleep') as mock_sleep:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock to always fail
        mock_vision_model.generate_content = MagicMock(
            side_effect=Exception("Always fails")
        )
        
        # Make sleep async
        async def async_sleep(delay):
            pass
        mock_sleep.side_effect = async_sleep
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image and expect failure
        compressed_twin = CompressedDigitalTwin(primary_colors=["#FF0000"])
        
        with pytest.raises(Exception):
            asyncio.run(client.generate_image("test prompt", compressed_twin))
        
        # Verify sleep was called with exponential backoff delays
        # After attempt 1: sleep(1)
        # After attempt 2: sleep(2)
        # No sleep after attempt 3 (last attempt)
        assert mock_sleep.call_count == 2, (
            f"sleep should be called 2 times (between 3 attempts), "
            f"got {mock_sleep.call_count}"
        )
        
        # Check the delay values
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        
        # Exponential backoff: 1s, 2s
        expected_delays = [1.0, 2.0]
        assert sleep_calls == expected_delays, (
            f"Sleep delays should follow exponential backoff {expected_delays}, "
            f"got {sleep_calls}"
        )
        
        print(f"✓ Retry delays follow exponential backoff: {sleep_calls}")


def test_generate_image_no_sleep_after_last_attempt():
    """
    **Feature: gemini-3-dual-architecture, Property 9: Generation Retry Behavior**
    
    Verify that no sleep occurs after the final retry attempt.
    
    **Validates: Requirements 3.4**
    
    This test ensures efficient failure handling.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('asyncio.sleep') as mock_sleep:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock to always fail
        mock_vision_model.generate_content = MagicMock(
            side_effect=Exception("Always fails")
        )
        
        # Make sleep async
        async def async_sleep(delay):
            pass
        mock_sleep.side_effect = async_sleep
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image and expect failure
        compressed_twin = CompressedDigitalTwin(primary_colors=["#FF0000"])
        
        with pytest.raises(Exception):
            asyncio.run(client.generate_image("test prompt", compressed_twin))
        
        # Verify sleep was NOT called 3 times (should be 2 times, not after last attempt)
        assert mock_sleep.call_count == 2, (
            f"sleep should be called 2 times (not after last attempt), "
            f"got {mock_sleep.call_count}"
        )
        
        print(f"✓ No sleep after final retry attempt")


def test_generate_image_logs_retry_attempts():
    """
    **Feature: gemini-3-dual-architecture, Property 9: Generation Retry Behavior**
    
    Verify that retry attempts are properly logged.
    
    **Validates: Requirements 3.4**
    
    This test ensures observability of retry behavior.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('asyncio.sleep', new_callable=lambda: MagicMock(return_value=asyncio.sleep(0))), \
         patch('mobius.tools.gemini.logger') as mock_logger:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock to always fail
        mock_vision_model.generate_content = MagicMock(
            side_effect=Exception("Test failure")
        )
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image and expect failure
        compressed_twin = CompressedDigitalTwin(primary_colors=["#FF0000"])
        
        with pytest.raises(Exception):
            asyncio.run(client.generate_image("test prompt", compressed_twin))
        
        # Verify logger was called for each attempt
        log_calls = [str(call) for call in mock_logger.info.call_args_list + mock_logger.warning.call_args_list]
        
        # Check that attempts were logged
        attempt_logs = [log for log in log_calls if "attempt" in log.lower()]
        
        assert len(attempt_logs) >= 3, (
            f"Should log at least 3 attempts, found {len(attempt_logs)} attempt logs"
        )
        
        print(f"✓ Retry attempts are properly logged")


def test_generate_image_raises_exception_after_max_retries():
    """
    **Feature: gemini-3-dual-architecture, Property 9: Generation Retry Behavior**
    
    Verify that an exception is raised after all retry attempts are exhausted.
    
    **Validates: Requirements 3.4**
    
    This test ensures proper error propagation.
    """
    async def run_test():
        with patch('google.generativeai.configure') as mock_configure, \
             patch('google.generativeai.GenerativeModel') as mock_model_class, \
             patch('asyncio.sleep', new_callable=AsyncMock):
            
            # Create mock model instances
            mock_vision_model = MagicMock()
            mock_model_class.return_value = mock_vision_model
            
            # Mock to always fail
            original_error = Exception("Persistent failure")
            mock_vision_model.generate_content = MagicMock(side_effect=original_error)
            
            # Initialize client
            client = GeminiClient()
            
            # Call generate_image and expect exception
            compressed_twin = CompressedDigitalTwin(primary_colors=["#FF0000"])
            
            with pytest.raises(Exception) as exc_info:
                await client.generate_image("test prompt", compressed_twin)
            
            # Verify the exception message mentions retry attempts
            error_message = str(exc_info.value)
            assert "3 attempts" in error_message or "after 3" in error_message, (
                f"Error message should mention 3 attempts, got: {error_message}"
            )
            
            print(f"✓ Exception raised after max retries with proper message")
    
    asyncio.run(run_test())


@given(
    compressed_twin=compressed_twin_strategy()
)
@hypothesis_settings(max_examples=50)
async def test_generate_image_first_attempt_success_no_retry(
    compressed_twin: CompressedDigitalTwin
):
    """
    **Feature: gemini-3-dual-architecture, Property 9: Generation Retry Behavior**
    
    *For any* generation that succeeds on first attempt, no retries should occur.
    
    **Validates: Requirements 3.4**
    
    This property test verifies efficient success path.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('asyncio.sleep') as mock_sleep:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock to succeed immediately
        mock_result = MagicMock()
        mock_result.text = "data:image/png;base64,success"
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image
        result = await client.generate_image("test prompt", compressed_twin)
        
        # Verify success
        assert result is not None, "Should return a result"
        
        # Verify generate_content was called exactly once
        assert mock_vision_model.generate_content.call_count == 1, (
            f"generate_content should be called once on success, "
            f"got {mock_vision_model.generate_content.call_count}"
        )
        
        # Verify sleep was never called (no retries)
        assert mock_sleep.call_count == 0, (
            f"sleep should not be called on first attempt success, "
            f"got {mock_sleep.call_count} calls"
        )
        
        print(f"✓ No retries on first attempt success")


def test_generate_image_retry_count_is_exactly_three():
    """
    **Feature: gemini-3-dual-architecture, Property 9: Generation Retry Behavior**
    
    Verify that the maximum retry count is exactly 3 attempts.
    
    **Validates: Requirements 3.4**
    
    This test ensures the retry limit matches requirements.
    """
    async def run_test():
        with patch('google.generativeai.configure') as mock_configure, \
             patch('google.generativeai.GenerativeModel') as mock_model_class, \
             patch('asyncio.sleep', new_callable=AsyncMock):
            
            # Create mock model instances
            mock_vision_model = MagicMock()
            mock_model_class.return_value = mock_vision_model
            
            # Mock to always fail
            mock_vision_model.generate_content = MagicMock(
                side_effect=Exception("Always fails")
            )
            
            # Initialize client
            client = GeminiClient()
            
            # Call generate_image and expect failure
            compressed_twin = CompressedDigitalTwin(primary_colors=["#FF0000"])
            
            with pytest.raises(Exception):
                await client.generate_image("test prompt", compressed_twin)
            
            # Verify exactly 3 attempts were made
            assert mock_vision_model.generate_content.call_count == 3, (
                f"Should make exactly 3 attempts, got {mock_vision_model.generate_content.call_count}"
            )
            
            print(f"✓ Retry count is exactly 3 attempts")
    
    asyncio.run(run_test())
