"""
Property-based tests for webhook retry exhaustion.

**Feature: mobius-phase-2-refactor, Property 10: Webhook retry exhaustion**
**Validates: Requirements 6.5**

Property: For any webhook URL that fails delivery, after 5 retry attempts
with exponential backoff, the system should mark the webhook as failed
and stop retrying.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, AsyncMock, patch
import asyncio

from mobius.api.webhooks import deliver_webhook


# Strategy for generating webhook URLs
webhook_urls = st.one_of(
    st.just("https://example.com/webhook"),
    st.just("https://test.com/callback"),
    st.just("https://api.example.com/notifications"),
)

# Strategy for generating job IDs
job_ids = st.text(min_size=10, max_size=50, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    whitelist_characters='-_'
))


@given(
    webhook_url=webhook_urls,
    job_id=job_ids,
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_webhook_retry_exhaustion(webhook_url, job_id):
    """
    Property: Webhook retry exhaustion.
    
    For any webhook URL that fails delivery, after 5 retry attempts
    with exponential backoff, the system should mark the webhook as failed
    and stop retrying.
    
    This ensures that the system doesn't retry indefinitely and properly
    handles persistent webhook failures.
    """
    payload = {"job_id": job_id, "status": "completed"}
    
    # Mock asyncio.sleep to avoid actual delays
    with patch('mobius.api.webhooks.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Mock httpx.AsyncClient to always fail
        with patch('mobius.api.webhooks.httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("Connection failed")
            
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            
            mock_client_class.return_value = mock_client
            
            # Call deliver_webhook with max_attempts=5
            result = await deliver_webhook(
                url=webhook_url,
                payload=payload,
                job_id=job_id,
                attempt=1,
                max_attempts=5,
            )
        
            # Property: After 5 failed attempts, should return False
            assert result is False, (
                f"Webhook delivery should return False after exhausting all retries. "
                f"Got: {result}"
            )
            
            # Property: Should have attempted exactly 5 times
            assert mock_client.post.call_count == 5, (
                f"Webhook should be attempted exactly 5 times. "
                f"Got: {mock_client.post.call_count} attempts"
            )


@given(
    webhook_url=webhook_urls,
    job_id=job_ids,
    max_attempts=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_webhook_retry_respects_max_attempts(webhook_url, job_id, max_attempts):
    """
    Property: Webhook retry respects max_attempts parameter.
    
    For any max_attempts value, the system should attempt delivery exactly
    that many times before giving up.
    
    This ensures that the retry logic correctly honors the configured
    maximum number of attempts.
    """
    payload = {"job_id": job_id, "status": "completed"}
    
    # Mock asyncio.sleep to avoid actual delays
    with patch('mobius.api.webhooks.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Mock httpx.AsyncClient to always fail
        with patch('mobius.api.webhooks.httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("Connection failed")
            
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            
            mock_client_class.return_value = mock_client
            
            # Call deliver_webhook with custom max_attempts
            result = await deliver_webhook(
                url=webhook_url,
                payload=payload,
                job_id=job_id,
                attempt=1,
                max_attempts=max_attempts,
            )
            
            # Property: Should return False after exhausting retries
            assert result is False
            
            # Property: Should have attempted exactly max_attempts times
            assert mock_client.post.call_count == max_attempts, (
                f"Webhook should be attempted exactly {max_attempts} times. "
                f"Got: {mock_client.post.call_count} attempts"
            )


@given(
    webhook_url=webhook_urls,
    job_id=job_ids,
    success_on_attempt=st.integers(min_value=1, max_value=5),
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_webhook_succeeds_before_exhaustion(webhook_url, job_id, success_on_attempt):
    """
    Property: Webhook succeeds before exhaustion.
    
    For any webhook that succeeds on attempt N (where N <= max_attempts),
    the system should return True and stop retrying after N attempts.
    
    This ensures that the system doesn't continue retrying after a
    successful delivery.
    """
    payload = {"job_id": job_id, "status": "completed"}
    
    # Mock asyncio.sleep to avoid actual delays
    with patch('mobius.api.webhooks.asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Mock httpx.AsyncClient to succeed on specific attempt
        with patch('mobius.api.webhooks.httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            
            # Track call count
            call_count = [0]
            
            async def mock_post(*args, **kwargs):
                call_count[0] += 1
                mock_response = Mock()
                
                if call_count[0] == success_on_attempt:
                    # Succeed on this attempt
                    mock_response.raise_for_status = Mock()
                    mock_response.status_code = 200
                else:
                    # Fail on other attempts
                    mock_response.raise_for_status.side_effect = Exception("Connection failed")
                
                return mock_response
            
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = mock_post
            
            mock_client_class.return_value = mock_client
            
            # Call deliver_webhook
            result = await deliver_webhook(
                url=webhook_url,
                payload=payload,
                job_id=job_id,
                attempt=1,
                max_attempts=5,
            )
            
            # Property: Should return True when successful
            assert result is True, (
                f"Webhook delivery should return True when successful on attempt {success_on_attempt}. "
                f"Got: {result}"
            )
            
            # Property: Should have attempted exactly success_on_attempt times
            assert call_count[0] == success_on_attempt, (
                f"Webhook should stop after successful delivery on attempt {success_on_attempt}. "
                f"Got: {call_count[0]} attempts"
            )


@given(
    webhook_url=webhook_urls,
    job_id=job_ids,
)
@settings(max_examples=50, deadline=None)
@pytest.mark.asyncio
async def test_webhook_exponential_backoff(webhook_url, job_id):
    """
    Property: Webhook uses exponential backoff.
    
    For any failing webhook, the system should wait progressively longer
    between retries using exponential backoff (2^attempt seconds).
    
    This ensures that the system doesn't overwhelm the webhook endpoint
    with rapid retries.
    """
    payload = {"job_id": job_id, "status": "completed"}
    
    # Track sleep calls to verify backoff
    sleep_calls = []
    
    async def mock_sleep(seconds):
        sleep_calls.append(seconds)
    
    # Mock httpx.AsyncClient to always fail
    with patch('mobius.api.webhooks.httpx.AsyncClient') as mock_client_class:
        with patch('mobius.api.webhooks.asyncio.sleep', side_effect=mock_sleep):
            mock_client = Mock()
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("Connection failed")
            
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            
            mock_client_class.return_value = mock_client
            
            # Call deliver_webhook
            await deliver_webhook(
                url=webhook_url,
                payload=payload,
                job_id=job_id,
                attempt=1,
                max_attempts=5,
            )
            
            # Property: Should have 3 sleep calls (between attempts 2-5)
            # Note: First attempt has no sleep, then sleep before attempts 2, 3, 4
            # Attempt 5 is the last attempt, so no sleep after it
            assert len(sleep_calls) == 3, (
                f"Should have 3 sleep calls between 5 attempts. "
                f"Got: {len(sleep_calls)} sleep calls"
            )
            
            # Property: Sleep durations should follow exponential backoff
            # Before attempt 2: 2^2 = 4s
            # Before attempt 3: 2^3 = 8s
            # Before attempt 4: 2^4 = 16s
            # (No sleep before attempt 5 in current implementation)
            expected_backoffs = [4, 8, 16]
            assert sleep_calls == expected_backoffs, (
                f"Sleep durations should follow exponential backoff pattern {expected_backoffs}. "
                f"Got: {sleep_calls}"
            )
