"""
Property-based tests for async job response time.

**Feature: mobius-phase-2-refactor, Property 9: Async job returns immediately**
**Validates: Requirements 6.1**

Property: For any generation request with async_mode set to true,
the API should return a job_id within 500 milliseconds.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, AsyncMock, patch
import time
from datetime import datetime, timedelta, timezone
import uuid

from mobius.api.routes import generate_handler
from mobius.models.brand import Brand, BrandGuidelines, Color


# Strategy for generating valid brand IDs
brand_ids = st.text(min_size=10, max_size=50, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    whitelist_characters='-_'
))

# Strategy for generating prompts
prompts = st.text(min_size=5, max_size=200)


@given(
    brand_id=brand_ids,
    prompt=prompts,
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_async_job_returns_immediately(brand_id, prompt):
    """
    Property: Async job returns immediately.
    
    For any generation request with async_mode=True, the API should
    return a job_id within 500 milliseconds.
    
    This ensures that async jobs don't block the API response while
    the generation workflow executes in the background.
    """
    # Create a mock brand
    mock_brand = Brand(
        brand_id=brand_id,
        organization_id="test-org",
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=[Color(name="Red", hex="#FF0000", usage="primary")],
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    
    # Mock the BrandStorage to return our mock brand
    with patch('mobius.api.routes.BrandStorage') as mock_storage_class:
        mock_storage = Mock()
        mock_storage.get_brand = AsyncMock(return_value=mock_brand)
        mock_storage_class.return_value = mock_storage
        
        # Mock JobStorage to avoid database calls
        with patch('mobius.api.routes.JobStorage') as mock_job_storage_class:
            mock_job_storage = Mock()
            mock_job_storage.get_by_idempotency_key = AsyncMock(return_value=None)
            mock_job_storage.create_job = AsyncMock(return_value=None)
            mock_job_storage_class.return_value = mock_job_storage
            
            # Measure response time
            start_time = time.time()
            
            try:
                response = await generate_handler(
                    brand_id=brand_id,
                    prompt=prompt,
                    async_mode=True,
                    webhook_url=None,
                    idempotency_key=None,
                )
                
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                # Property: Response time should be under 500ms
                assert response_time_ms < 500, (
                    f"Async job response took {response_time_ms:.2f}ms, "
                    f"which exceeds the 500ms requirement"
                )
                
                # Property: Response should contain a job_id
                assert "job_id" in response, "Response must contain job_id"
                assert response["job_id"] is not None, "job_id must not be None"
                assert len(response["job_id"]) > 0, "job_id must not be empty"
                
                # Property: Status should indicate async processing
                assert "status" in response, "Response must contain status"
                assert response["status"] in ["pending", "processing"], (
                    f"Async job status should be 'pending' or 'processing', got '{response['status']}'"
                )
                
            except Exception as e:
                # If the handler fails for reasons other than timing,
                # we still want to verify it fails quickly
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                # Even failures should be fast
                assert response_time_ms < 500, (
                    f"Async job failure took {response_time_ms:.2f}ms, "
                    f"which exceeds the 500ms requirement"
                )
                
                # Re-raise if it's not a validation error we expect
                raise


@given(
    brand_id=brand_ids,
    prompt=prompts,
    webhook_url=st.one_of(
        st.none(),
        st.just("https://example.com/webhook"),
        st.just("https://test.com/callback"),
    ),
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_async_job_with_webhook_returns_immediately(brand_id, prompt, webhook_url):
    """
    Property: Async job with webhook returns immediately.
    
    For any generation request with async_mode=True and a webhook_url,
    the API should still return within 500ms, regardless of webhook configuration.
    """
    # Create a mock brand
    mock_brand = Brand(
        brand_id=brand_id,
        organization_id="test-org",
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=[Color(name="Red", hex="#FF0000", usage="primary")],
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    
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
            
            # Measure response time
            start_time = time.time()
            
            response = await generate_handler(
                brand_id=brand_id,
                prompt=prompt,
                async_mode=True,
                webhook_url=webhook_url,
                idempotency_key=None,
            )
            
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            # Property: Response time should be under 500ms even with webhook
            assert response_time_ms < 500, (
                f"Async job with webhook response took {response_time_ms:.2f}ms, "
                f"which exceeds the 500ms requirement"
            )
            
            # Property: Response should contain a job_id
            assert "job_id" in response
            assert response["job_id"] is not None
