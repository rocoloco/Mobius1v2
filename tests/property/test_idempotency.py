"""
Property-based tests for idempotency key behavior.

**Feature: mobius-phase-2-refactor, Property 16: Idempotency key prevents duplicates**
**Validates: Requirements 6.1 (enhanced)**

Property: For any two generation requests with the same non-null idempotency_key
submitted within the job expiry window, the system should return the same job_id
for both requests.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta, timezone
import uuid

from mobius.api.routes import generate_handler
from mobius.models.brand import Brand, BrandGuidelines, Color
from mobius.models.job import Job


# Strategy for generating valid brand IDs
brand_ids = st.text(min_size=10, max_size=50, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    whitelist_characters='-_'
))

# Strategy for generating prompts
prompts = st.text(min_size=5, max_size=200)

# Strategy for generating idempotency keys
idempotency_keys = st.text(min_size=10, max_size=64, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    whitelist_characters='-_'
))


@given(
    brand_id=brand_ids,
    prompt=prompts,
    idempotency_key=idempotency_keys,
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_idempotency_key_prevents_duplicates(brand_id, prompt, idempotency_key):
    """
    Property: Idempotency key prevents duplicates.
    
    For any two generation requests with the same non-null idempotency_key
    submitted within the job expiry window, the system should return the
    same job_id for both requests.
    
    This ensures that network retries or accidental duplicate submissions
    don't create multiple jobs for the same logical request.
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
    
    # Create a mock existing job that would be returned on second request
    existing_job_id = str(uuid.uuid4())
    mock_existing_job = Job(
        job_id=existing_job_id,
        brand_id=brand_id,
        status="pending",
        progress=0.0,
        state={"prompt": prompt},
        idempotency_key=idempotency_key,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    
    # Mock the BrandStorage
    with patch('mobius.api.routes.BrandStorage') as mock_storage_class:
        mock_storage = Mock()
        mock_storage.get_brand = AsyncMock(return_value=mock_brand)
        mock_storage_class.return_value = mock_storage
        
        # Mock JobStorage for first request (no existing job)
        with patch('mobius.api.routes.JobStorage') as mock_job_storage_class:
            mock_job_storage = Mock()
            
            # First request: no existing job
            mock_job_storage.get_by_idempotency_key = AsyncMock(return_value=None)
            mock_job_storage.create_job = AsyncMock(return_value=None)
            mock_job_storage_class.return_value = mock_job_storage
            
            # Make first request
            first_response = await generate_handler(
                brand_id=brand_id,
                prompt=prompt,
                async_mode=True,
                webhook_url=None,
                idempotency_key=idempotency_key,
            )
            
            first_job_id = first_response["job_id"]
            
            # Property: First request should create a new job
            assert first_job_id is not None
            assert len(first_job_id) > 0
            
        # Mock JobStorage for second request (existing job found)
        with patch('mobius.api.routes.JobStorage') as mock_job_storage_class2:
            mock_job_storage2 = Mock()
            
            # Second request: existing job found
            mock_job_storage2.get_by_idempotency_key = AsyncMock(return_value=mock_existing_job)
            mock_job_storage2.create_job = AsyncMock(return_value=None)
            mock_job_storage_class2.return_value = mock_job_storage2
            
            # Make second request with same idempotency key
            second_response = await generate_handler(
                brand_id=brand_id,
                prompt=prompt,
                async_mode=True,
                webhook_url=None,
                idempotency_key=idempotency_key,
            )
            
            second_job_id = second_response["job_id"]
            
            # Property: Second request should return the existing job_id
            assert second_job_id == existing_job_id, (
                f"Idempotency key '{idempotency_key}' should return the same job_id. "
                f"Expected: {existing_job_id}, Got: {second_job_id}"
            )
            
            # Property: Response should indicate it's an idempotent request
            assert "idempotent" in second_response["message"].lower() or "existing" in second_response["message"].lower(), (
                "Response message should indicate this is an idempotent request"
            )
            
            # Property: create_job should NOT be called on second request
            mock_job_storage2.create_job.assert_not_called()


@given(
    brand_id=brand_ids,
    prompt1=prompts,
    prompt2=prompts,
    idempotency_key=idempotency_keys,
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_idempotency_ignores_different_prompts(brand_id, prompt1, prompt2, idempotency_key):
    """
    Property: Idempotency key takes precedence over request parameters.
    
    For any two requests with the same idempotency_key but different prompts,
    the system should return the same job_id, ignoring the different prompt.
    
    This ensures that the idempotency key is the sole determinant of uniqueness,
    not the request parameters.
    """
    # Skip if prompts are the same (not testing anything interesting)
    if prompt1 == prompt2:
        return
    
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
    
    # Create a mock existing job
    existing_job_id = str(uuid.uuid4())
    mock_existing_job = Job(
        job_id=existing_job_id,
        brand_id=brand_id,
        status="pending",
        progress=0.0,
        state={"prompt": prompt1},  # Original prompt
        idempotency_key=idempotency_key,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    
    # Mock the BrandStorage
    with patch('mobius.api.routes.BrandStorage') as mock_storage_class:
        mock_storage = Mock()
        mock_storage.get_brand = AsyncMock(return_value=mock_brand)
        mock_storage_class.return_value = mock_storage
        
        # Mock JobStorage to return existing job
        with patch('mobius.api.routes.JobStorage') as mock_job_storage_class:
            mock_job_storage = Mock()
            mock_job_storage.get_by_idempotency_key = AsyncMock(return_value=mock_existing_job)
            mock_job_storage.create_job = AsyncMock(return_value=None)
            mock_job_storage_class.return_value = mock_job_storage
            
            # Make request with different prompt but same idempotency key
            response = await generate_handler(
                brand_id=brand_id,
                prompt=prompt2,  # Different prompt
                async_mode=True,
                webhook_url=None,
                idempotency_key=idempotency_key,
            )
            
            # Property: Should return the existing job_id despite different prompt
            assert response["job_id"] == existing_job_id, (
                f"Idempotency key should take precedence over request parameters. "
                f"Expected job_id: {existing_job_id}, Got: {response['job_id']}"
            )
            
            # Property: Should not create a new job
            mock_job_storage.create_job.assert_not_called()


@given(
    brand_id=brand_ids,
    prompt=prompts,
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_no_idempotency_key_creates_new_jobs(brand_id, prompt):
    """
    Property: Requests without idempotency keys always create new jobs.
    
    For any two requests without idempotency_key, the system should create
    separate jobs with different job_ids.
    
    This ensures that the absence of an idempotency key allows duplicate
    job creation, which is the expected behavior.
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
        
        # Mock JobStorage for first request
        with patch('mobius.api.routes.JobStorage') as mock_job_storage_class1:
            mock_job_storage1 = Mock()
            mock_job_storage1.get_by_idempotency_key = AsyncMock(return_value=None)
            mock_job_storage1.create_job = AsyncMock(return_value=None)
            mock_job_storage_class1.return_value = mock_job_storage1
            
            # Make first request without idempotency key
            first_response = await generate_handler(
                brand_id=brand_id,
                prompt=prompt,
                async_mode=True,
                webhook_url=None,
                idempotency_key=None,  # No idempotency key
            )
            
            first_job_id = first_response["job_id"]
            
        # Mock JobStorage for second request
        with patch('mobius.api.routes.JobStorage') as mock_job_storage_class2:
            mock_job_storage2 = Mock()
            mock_job_storage2.get_by_idempotency_key = AsyncMock(return_value=None)
            mock_job_storage2.create_job = AsyncMock(return_value=None)
            mock_job_storage_class2.return_value = mock_job_storage2
            
            # Make second request without idempotency key
            second_response = await generate_handler(
                brand_id=brand_id,
                prompt=prompt,
                async_mode=True,
                webhook_url=None,
                idempotency_key=None,  # No idempotency key
            )
            
            second_job_id = second_response["job_id"]
            
            # Property: Without idempotency keys, job_ids should be different
            assert first_job_id != second_job_id, (
                "Requests without idempotency keys should create separate jobs with different job_ids"
            )
            
            # Property: Both create_job calls should have been made
            mock_job_storage1.create_job.assert_called_once()
            mock_job_storage2.create_job.assert_called_once()
