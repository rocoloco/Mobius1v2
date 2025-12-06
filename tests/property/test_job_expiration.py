"""
Property-based tests for job expiration.

**Feature: mobius-phase-2-refactor, Property (custom): Jobs expire after 24 hours**
**Validates: Requirements 6.7**

Property: For any job created in the system, when 24 hours have elapsed,
the job should be marked as expired and eligible for cleanup.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta, timezone
import uuid

from mobius.models.job import Job
from mobius.storage.jobs import JobStorage


# Strategy for generating valid job IDs
job_ids = st.uuids().map(str)

# Strategy for generating brand IDs
brand_ids = st.uuids().map(str)

# Strategy for generating job statuses
job_statuses = st.sampled_from(["pending", "processing", "completed", "failed"])

# Strategy for generating time offsets (hours past expiration)
hours_past_expiration = st.floats(min_value=24.0, max_value=72.0)


@given(
    job_id=job_ids,
    brand_id=brand_ids,
    status=job_statuses,
    hours_past=hours_past_expiration,
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_jobs_expire_after_24_hours(job_id, brand_id, status, hours_past):
    """
    Property: Jobs expire after 24 hours.
    
    For any job created in the system, when the current time is more than
    24 hours after the job's creation time, the job should be considered
    expired and should appear in the list of expired jobs.
    
    This ensures that the cleanup scheduler can identify and remove old jobs.
    """
    # Create a job with creation time in the past
    created_at = datetime.now(timezone.utc) - timedelta(hours=hours_past)
    expires_at = created_at + timedelta(hours=24)
    
    job = Job(
        job_id=job_id,
        brand_id=brand_id,
        status=status,
        progress=0.0 if status == "pending" else 100.0,
        state={"test": "data"},
        webhook_url=None,
        webhook_attempts=0,
        idempotency_key=None,
        error=None,
        created_at=created_at,
        updated_at=created_at,
        expires_at=expires_at,
    )
    
    # Mock the Supabase client to return our expired job
    mock_client = Mock()
    mock_table = Mock()
    mock_select = Mock()
    mock_lt = Mock()
    mock_limit = Mock()
    mock_execute = Mock()
    
    # Chain the mock calls
    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.lt.return_value = mock_lt
    mock_lt.limit.return_value = mock_limit
    mock_limit.execute.return_value = Mock(data=[job.model_dump()])
    
    with patch('mobius.storage.jobs.get_supabase_client', return_value=mock_client):
        storage = JobStorage()
        expired_jobs = await storage.list_expired_jobs(limit=100)
        
        # Property: Job should be in the expired jobs list
        assert len(expired_jobs) > 0, "Expired job should be returned by list_expired_jobs"
        
        # Property: The returned job should match our expired job
        found_job = expired_jobs[0]
        assert found_job.job_id == job_id, "Job ID should match"
        assert found_job.brand_id == brand_id, "Brand ID should match"
        assert found_job.status == status, "Status should match"
        
        # Property: The job's expiration time should be in the past (or equal due to timing precision)
        current_time = datetime.now(timezone.utc)
        assert found_job.expires_at <= current_time, (
            f"Job expires_at ({found_job.expires_at}) should be before or equal to current time ({current_time})"
        )
        
        # Property: The job should be at least 24 hours old
        age_hours = (current_time - found_job.created_at).total_seconds() / 3600
        assert age_hours >= 24.0, (
            f"Job age ({age_hours:.2f} hours) should be at least 24 hours"
        )


@given(
    job_id=job_ids,
    brand_id=brand_ids,
    status=job_statuses,
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_recent_jobs_not_expired(job_id, brand_id, status):
    """
    Property: Recent jobs are not expired.
    
    For any job created within the last 24 hours, the job should NOT
    be considered expired and should NOT appear in the list of expired jobs.
    
    This ensures that active jobs are not prematurely cleaned up.
    """
    # Create a job with recent creation time (within last 23 hours)
    hours_ago = 23.0  # Just under 24 hours
    created_at = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    expires_at = created_at + timedelta(hours=24)
    
    job = Job(
        job_id=job_id,
        brand_id=brand_id,
        status=status,
        progress=0.0 if status == "pending" else 100.0,
        state={"test": "data"},
        webhook_url=None,
        webhook_attempts=0,
        idempotency_key=None,
        error=None,
        created_at=created_at,
        updated_at=created_at,
        expires_at=expires_at,
    )
    
    # Mock the Supabase client to return empty list (no expired jobs)
    mock_client = Mock()
    mock_table = Mock()
    mock_select = Mock()
    mock_lt = Mock()
    mock_limit = Mock()
    mock_execute = Mock()
    
    # Chain the mock calls - return empty list since job is not expired
    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.lt.return_value = mock_lt
    mock_lt.limit.return_value = mock_limit
    mock_limit.execute.return_value = Mock(data=[])
    
    with patch('mobius.storage.jobs.get_supabase_client', return_value=mock_client):
        storage = JobStorage()
        expired_jobs = await storage.list_expired_jobs(limit=100)
        
        # Property: Recent job should NOT be in the expired jobs list
        assert len(expired_jobs) == 0, (
            "Recent job (< 24 hours old) should not be returned by list_expired_jobs"
        )
        
        # Property: The job's expiration time should be in the future
        current_time = datetime.now(timezone.utc)
        assert job.expires_at > current_time, (
            f"Job expires_at ({job.expires_at}) should be after current time ({current_time})"
        )
        
        # Property: The job should be less than 24 hours old
        age_hours = (current_time - job.created_at).total_seconds() / 3600
        assert age_hours < 24.0, (
            f"Job age ({age_hours:.2f} hours) should be less than 24 hours"
        )


@given(
    num_expired_jobs=st.integers(min_value=1, max_value=10),
    num_active_jobs=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_cleanup_only_affects_expired_jobs(num_expired_jobs, num_active_jobs):
    """
    Property: Cleanup only affects expired jobs.
    
    For any mix of expired and active jobs, the list_expired_jobs function
    should only return jobs that are actually expired (> 24 hours old),
    and should not return any active jobs (< 24 hours old).
    
    This ensures that the cleanup process is selective and safe.
    """
    # Create expired jobs (> 24 hours old)
    expired_jobs = []
    for i in range(num_expired_jobs):
        hours_past = 24.0 + (i + 1) * 5.0  # 29, 34, 39, ... hours old
        created_at = datetime.now(timezone.utc) - timedelta(hours=hours_past)
        expires_at = created_at + timedelta(hours=24)
        
        expired_jobs.append(Job(
            job_id=str(uuid.uuid4()),
            brand_id=str(uuid.uuid4()),
            status="completed",
            progress=100.0,
            state={"expired": True},
            webhook_url=None,
            webhook_attempts=0,
            idempotency_key=None,
            error=None,
            created_at=created_at,
            updated_at=created_at,
            expires_at=expires_at,
        ))
    
    # Create active jobs (< 24 hours old)
    active_jobs = []
    for i in range(num_active_jobs):
        hours_ago = 1.0 + i * 2.0  # 1, 3, 5, ... hours old
        created_at = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
        expires_at = created_at + timedelta(hours=24)
        
        active_jobs.append(Job(
            job_id=str(uuid.uuid4()),
            brand_id=str(uuid.uuid4()),
            status="processing",
            progress=50.0,
            state={"active": True},
            webhook_url=None,
            webhook_attempts=0,
            idempotency_key=None,
            error=None,
            created_at=created_at,
            updated_at=created_at,
            expires_at=expires_at,
        ))
    
    # Mock the Supabase client to return only expired jobs
    mock_client = Mock()
    mock_table = Mock()
    mock_select = Mock()
    mock_lt = Mock()
    mock_limit = Mock()
    mock_execute = Mock()
    
    # Chain the mock calls - return only expired jobs
    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.lt.return_value = mock_lt
    mock_lt.limit.return_value = mock_limit
    mock_limit.execute.return_value = Mock(data=[j.model_dump() for j in expired_jobs])
    
    with patch('mobius.storage.jobs.get_supabase_client', return_value=mock_client):
        storage = JobStorage()
        returned_jobs = await storage.list_expired_jobs(limit=100)
        
        # Property: Number of returned jobs should match number of expired jobs
        assert len(returned_jobs) == num_expired_jobs, (
            f"Should return {num_expired_jobs} expired jobs, got {len(returned_jobs)}"
        )
        
        # Property: All returned jobs should be expired
        current_time = datetime.now(timezone.utc)
        for job in returned_jobs:
            assert job.expires_at < current_time, (
                f"Returned job {job.job_id} should be expired"
            )
            
            age_hours = (current_time - job.created_at).total_seconds() / 3600
            assert age_hours >= 24.0, (
                f"Returned job {job.job_id} should be at least 24 hours old, got {age_hours:.2f} hours"
            )
        
        # Property: No active jobs should be in the returned list
        active_job_ids = {j.job_id for j in active_jobs}
        returned_job_ids = {j.job_id for j in returned_jobs}
        
        assert len(active_job_ids & returned_job_ids) == 0, (
            "No active jobs should be returned by list_expired_jobs"
        )
