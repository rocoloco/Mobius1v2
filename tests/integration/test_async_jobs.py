"""
Integration tests for async job management.

Tests the complete async job workflow including:
- Job creation and background processing
- Job status polling
- Webhook delivery
- Webhook retry logic
- Idempotency key behavior
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta, timezone
import uuid

from mobius.api.routes import generate_handler, get_job_status_handler, cancel_job_handler
from mobius.api.webhooks import deliver_webhook, notify_job_completion
from mobius.models.brand import Brand, BrandGuidelines, Color
from mobius.models.job import Job


@pytest.fixture
def mock_brand():
    """Create a mock brand for testing."""
    return Brand(
        brand_id="test-brand-123",
        organization_id="test-org-456",
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=[Color(name="Red", hex="#FF0000", usage="primary")],
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


@pytest.fixture
def mock_job():
    """Create a mock job for testing."""
    return Job(
        job_id="test-job-789",
        brand_id="test-brand-123",
        status="pending",
        progress=0.0,
        state={"prompt": "Test prompt"},
        webhook_url="https://example.com/webhook",
        idempotency_key="test-key-123",
    )


@pytest.mark.asyncio
async def test_async_job_creation_and_background_processing(mock_brand):
    """
    Test async job creation and background processing.
    
    Validates: Requirements 6.1, 6.2
    """
    # Mock the BrandStorage
    with patch('mobius.api.routes.BrandStorage') as mock_storage_class:
        mock_storage = Mock()
        mock_storage.get_brand = AsyncMock(return_value=mock_brand)
        mock_storage_class.return_value = mock_storage
        
        # Mock JobStorage
        with patch('mobius.api.routes.JobStorage') as mock_job_storage_class:
            mock_job_storage = Mock()
            mock_job_storage.get_by_idempotency_key = AsyncMock(return_value=None)
            mock_job_storage.create_job = AsyncMock(return_value=None)
            mock_job_storage_class.return_value = mock_job_storage
            
            # Create async job
            response = await generate_handler(
                brand_id="test-brand-123",
                prompt="Create a social media post",
                async_mode=True,
                webhook_url="https://example.com/webhook",
                idempotency_key=None,
            )
            
            # Verify job was created
            assert "job_id" in response
            assert response["status"] == "pending"
            assert "job_id" in response
            
            # Verify create_job was called
            mock_job_storage.create_job.assert_called_once()
            
            # Verify the job has correct structure
            call_args = mock_job_storage.create_job.call_args
            created_job = call_args[0][0]
            assert created_job.brand_id == "test-brand-123"
            assert created_job.status == "pending"
            assert created_job.webhook_url == "https://example.com/webhook"


@pytest.mark.asyncio
async def test_job_status_polling(mock_brand, mock_job):
    """
    Test job status polling.
    
    Validates: Requirements 6.2, 6.4
    """
    # Mock JobStorage to return a job
    with patch('mobius.api.routes.JobStorage') as mock_job_storage_class:
        mock_job_storage = Mock()
        mock_job_storage.get_job = AsyncMock(return_value=mock_job)
        mock_job_storage_class.return_value = mock_job_storage
        
        # Get job status
        response = await get_job_status_handler(job_id="test-job-789")
        
        # Verify response
        assert response["job_id"] == "test-job-789"
        assert response["status"] == "pending"
        assert response["progress"] == 0.0
        assert "request_id" in response
        
        # Verify get_job was called
        mock_job_storage.get_job.assert_called_once_with("test-job-789")


@pytest.mark.asyncio
async def test_job_status_not_found():
    """
    Test job status when job doesn't exist.
    
    Validates: Requirements 6.4
    """
    from mobius.api.errors import NotFoundError
    
    # Mock JobStorage to return None
    with patch('mobius.api.routes.JobStorage') as mock_job_storage_class:
        mock_job_storage = Mock()
        mock_job_storage.get_job = AsyncMock(return_value=None)
        mock_job_storage_class.return_value = mock_job_storage
        
        # Get job status should raise NotFoundError
        with pytest.raises(NotFoundError) as exc_info:
            await get_job_status_handler(job_id="nonexistent-job")
        
        assert "job" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_webhook_delivery_success():
    """
    Test successful webhook delivery.
    
    Validates: Requirements 6.3
    """
    payload = {"job_id": "test-job-123", "status": "completed"}
    
    # Mock httpx.AsyncClient to succeed
    with patch('mobius.api.webhooks.httpx.AsyncClient') as mock_client_class:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        # Deliver webhook
        result = await deliver_webhook(
            url="https://example.com/webhook",
            payload=payload,
            job_id="test-job-123",
        )
        
        # Verify success
        assert result is True
        
        # Verify POST was called once
        mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_webhook_retry_logic():
    """
    Test webhook retry logic with failures.
    
    Validates: Requirements 6.5
    """
    payload = {"job_id": "test-job-123", "status": "completed"}
    
    # Mock httpx.AsyncClient to fail 3 times then succeed
    with patch('mobius.api.webhooks.httpx.AsyncClient') as mock_client_class:
        mock_client = Mock()
        
        call_count = [0]
        
        async def mock_post(*args, **kwargs):
            call_count[0] += 1
            mock_response = Mock()
            
            if call_count[0] <= 3:
                # Fail first 3 attempts
                mock_response.raise_for_status.side_effect = Exception("Connection failed")
            else:
                # Succeed on 4th attempt
                mock_response.raise_for_status = Mock()
                mock_response.status_code = 200
            
            return mock_response
        
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = mock_post
        
        mock_client_class.return_value = mock_client
        
        # Mock asyncio.sleep to speed up test
        with patch('mobius.api.webhooks.asyncio.sleep', new_callable=AsyncMock):
            # Deliver webhook
            result = await deliver_webhook(
                url="https://example.com/webhook",
                payload=payload,
                job_id="test-job-123",
                max_attempts=5,
            )
            
            # Verify success after retries
            assert result is True
            
            # Verify it took 4 attempts
            assert call_count[0] == 4


@pytest.mark.asyncio
async def test_webhook_retry_exhaustion():
    """
    Test webhook retry exhaustion after max attempts.
    
    Validates: Requirements 6.5
    """
    payload = {"job_id": "test-job-123", "status": "completed"}
    
    # Mock httpx.AsyncClient to always fail
    with patch('mobius.api.webhooks.httpx.AsyncClient') as mock_client_class:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Connection failed")
        
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        # Mock asyncio.sleep to speed up test
        with patch('mobius.api.webhooks.asyncio.sleep', new_callable=AsyncMock):
            # Deliver webhook
            result = await deliver_webhook(
                url="https://example.com/webhook",
                payload=payload,
                job_id="test-job-123",
                max_attempts=5,
            )
            
            # Verify failure after exhausting retries
            assert result is False
            
            # Verify it attempted 5 times
            assert mock_client.post.call_count == 5


@pytest.mark.asyncio
async def test_idempotency_key_behavior(mock_brand):
    """
    Test idempotency key prevents duplicate job creation.
    
    Validates: Requirements 6.1 (enhanced)
    """
    idempotency_key = "test-idempotency-key-123"
    
    # Create a mock existing job
    existing_job = Job(
        job_id="existing-job-456",
        brand_id="test-brand-123",
        status="pending",
        progress=0.0,
        state={"prompt": "Original prompt"},
        idempotency_key=idempotency_key,
    )
    
    # Mock the BrandStorage
    with patch('mobius.api.routes.BrandStorage') as mock_storage_class:
        mock_storage = Mock()
        mock_storage.get_brand = AsyncMock(return_value=mock_brand)
        mock_storage_class.return_value = mock_storage
        
        # Mock JobStorage to return existing job
        with patch('mobius.api.routes.JobStorage') as mock_job_storage_class:
            mock_job_storage = Mock()
            mock_job_storage.get_by_idempotency_key = AsyncMock(return_value=existing_job)
            mock_job_storage.create_job = AsyncMock(return_value=None)
            mock_job_storage_class.return_value = mock_job_storage
            
            # Try to create job with same idempotency key
            response = await generate_handler(
                brand_id="test-brand-123",
                prompt="Different prompt",  # Different prompt
                async_mode=True,
                webhook_url=None,
                idempotency_key=idempotency_key,
            )
            
            # Verify existing job was returned
            assert response["job_id"] == "existing-job-456"
            assert "idempotent" in response["message"].lower() or "existing" in response["message"].lower()
            
            # Verify create_job was NOT called
            mock_job_storage.create_job.assert_not_called()


@pytest.mark.asyncio
async def test_job_cancellation(mock_job):
    """
    Test job cancellation.
    
    Validates: Requirements 6.4
    """
    # Mock JobStorage
    with patch('mobius.api.routes.JobStorage') as mock_job_storage_class:
        mock_job_storage = Mock()
        mock_job_storage.get_job = AsyncMock(return_value=mock_job)
        mock_job_storage.update_job = AsyncMock(return_value=None)
        mock_job_storage_class.return_value = mock_job_storage
        
        # Cancel job
        response = await cancel_job_handler(job_id="test-job-789")
        
        # Verify response
        assert response["job_id"] == "test-job-789"
        assert response["status"] == "cancelled"
        assert "cancelled" in response["message"].lower()
        
        # Verify update_job was called with cancelled status
        mock_job_storage.update_job.assert_called_once()
        call_args = mock_job_storage.update_job.call_args
        assert call_args[0][0] == "test-job-789"
        assert call_args[0][1]["status"] == "cancelled"


@pytest.mark.asyncio
async def test_job_cancellation_already_completed():
    """
    Test that completed jobs cannot be cancelled.
    
    Validates: Requirements 6.4
    """
    from mobius.api.errors import ValidationError
    
    # Create a completed job
    completed_job = Job(
        job_id="completed-job-123",
        brand_id="test-brand-123",
        status="completed",
        progress=100.0,
        state={"prompt": "Test prompt"},
    )
    
    # Mock JobStorage
    with patch('mobius.api.routes.JobStorage') as mock_job_storage_class:
        mock_job_storage = Mock()
        mock_job_storage.get_job = AsyncMock(return_value=completed_job)
        mock_job_storage_class.return_value = mock_job_storage
        
        # Try to cancel completed job
        with pytest.raises(ValidationError) as exc_info:
            await cancel_job_handler(job_id="completed-job-123")
        
        assert "cannot be cancelled" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_notify_job_completion_updates_webhook_attempts():
    """
    Test that notify_job_completion updates webhook_attempts counter.
    
    Validates: Requirements 6.3, 6.5
    """
    job_id = "test-job-123"
    webhook_url = "https://example.com/webhook"
    
    # Create a mock job
    mock_job = Job(
        job_id=job_id,
        brand_id="test-brand-123",
        status="completed",
        progress=100.0,
        state={"prompt": "Test prompt"},
        webhook_url=webhook_url,
        webhook_attempts=0,
    )
    
    # Mock httpx.AsyncClient to succeed
    with patch('mobius.api.webhooks.httpx.AsyncClient') as mock_client_class:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        # Mock JobStorage
        with patch('mobius.storage.jobs.JobStorage') as mock_job_storage_class:
            mock_job_storage = Mock()
            mock_job_storage.get_job = AsyncMock(return_value=mock_job)
            mock_job_storage.update_job = AsyncMock(return_value=None)
            mock_job_storage_class.return_value = mock_job_storage
            
            # Notify job completion
            result = await notify_job_completion(
                job_id=job_id,
                webhook_url=webhook_url,
                status="completed",
                result={"image_url": "https://example.com/image.png"},
            )
            
            # Verify success
            assert result is True
            
            # Verify webhook_attempts was updated
            mock_job_storage.update_job.assert_called_once()
            call_args = mock_job_storage.update_job.call_args
            assert call_args[1]["updates"]["webhook_attempts"] == 1
