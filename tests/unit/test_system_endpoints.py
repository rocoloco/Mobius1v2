"""
Unit tests for system endpoints.

Tests health check and API documentation endpoints.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

from mobius.api.routes import health_check_handler, get_api_docs_handler, cleanup_expired_jobs
from mobius.models.job import Job


@pytest.mark.asyncio
@patch("mobius.storage.database.get_supabase_client")
async def test_health_check_all_healthy(mock_get_client):
    """Test health check when all services are healthy."""
    # Mock Supabase client
    mock_client = Mock()
    mock_get_client.return_value = mock_client

    # Mock database query
    mock_result = Mock()
    mock_result.data = [{"brand_id": "test-brand"}]
    mock_client.table.return_value.select.return_value.limit.return_value.execute.return_value = mock_result

    # Mock storage access
    mock_client.storage.from_.return_value.list.return_value = []

    response = await health_check_handler()

    # Check response structure
    assert "status" in response
    assert "database" in response
    assert "storage" in response
    assert "api" in response
    assert "timestamp" in response
    assert "request_id" in response

    # All services should be healthy
    assert response["status"] == "healthy"
    assert response["database"] == "healthy"
    assert response["storage"] == "healthy"
    assert response["api"] == "healthy"

    # Timestamp should be a datetime
    assert isinstance(response["timestamp"], datetime)

    # Request ID should be present
    assert response["request_id"].startswith("req_")


@pytest.mark.asyncio
@patch("mobius.storage.database.get_supabase_client")
async def test_health_check_database_unhealthy(mock_get_client):
    """Test health check when database is unhealthy."""
    # Mock Supabase client that fails on database check
    mock_client = Mock()
    mock_get_client.return_value = mock_client

    # Database check fails
    mock_client.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception("Database connection failed")

    # Storage check succeeds
    mock_client.storage.from_.return_value.list.return_value = []

    response = await health_check_handler()

    # Overall status should be degraded
    assert response["status"] == "degraded"

    # Database should be unhealthy
    assert response["database"] == "unhealthy"

    # Storage and API should still be healthy
    assert response["storage"] == "healthy"
    assert response["api"] == "healthy"


@pytest.mark.asyncio
@patch("mobius.storage.database.get_supabase_client")
async def test_health_check_storage_unhealthy(mock_get_client):
    """Test health check when storage is unhealthy."""
    # Mock Supabase client that fails on storage check
    mock_client = Mock()
    mock_get_client.return_value = mock_client

    # Mock database query
    mock_result = Mock()
    mock_result.data = [{"brand_id": "test-brand"}]
    mock_client.table.return_value.select.return_value.limit.return_value.execute.return_value = mock_result

    # Storage check fails
    mock_client.storage.from_.return_value.list.side_effect = Exception("Storage connection failed")

    response = await health_check_handler()

    # Overall status should be degraded
    assert response["status"] == "degraded"

    # Storage should be unhealthy
    assert response["storage"] == "unhealthy"

    # Database and API should still be healthy
    assert response["database"] == "healthy"
    assert response["api"] == "healthy"


@pytest.mark.asyncio
@patch("mobius.storage.database.get_supabase_client")
async def test_health_check_multiple_services_unhealthy(mock_get_client):
    """Test health check when multiple services are unhealthy."""
    # Mock Supabase client that fails on both checks
    mock_client = Mock()
    mock_get_client.return_value = mock_client

    # Database check fails
    mock_client.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception("Database connection failed")

    # Storage check fails
    mock_client.storage.from_.return_value.list.side_effect = Exception("Storage connection failed")

    response = await health_check_handler()

    # Overall status should be degraded
    assert response["status"] == "degraded"

    # Both database and storage should be unhealthy
    assert response["database"] == "unhealthy"
    assert response["storage"] == "unhealthy"

    # API should still be healthy (since we got a response)
    assert response["api"] == "healthy"


@pytest.mark.asyncio
async def test_get_api_docs():
    """Test API documentation endpoint."""
    response = await get_api_docs_handler()

    # Check OpenAPI structure
    assert "openapi" in response
    assert response["openapi"] == "3.0.0"

    assert "info" in response
    assert "title" in response["info"]
    assert "version" in response["info"]
    assert "description" in response["info"]

    assert "servers" in response
    assert len(response["servers"]) > 0
    assert response["servers"][0]["url"] == "/v1"

    assert "paths" in response
    assert "components" in response
    assert "tags" in response

    # Check that key endpoints are documented
    assert "/health" in response["paths"]
    assert "/docs" in response["paths"]
    assert "/brands/ingest" in response["paths"]
    assert "/brands" in response["paths"]
    assert "/generate" in response["paths"]
    assert "/jobs/{job_id}" in response["paths"]
    assert "/templates" in response["paths"]


@pytest.mark.asyncio
async def test_get_api_docs_health_endpoint():
    """Test that health endpoint is properly documented."""
    response = await get_api_docs_handler()

    health_path = response["paths"]["/health"]

    # Should have GET method
    assert "get" in health_path

    # Check GET method details
    get_method = health_path["get"]
    assert get_method["summary"] == "Health check"
    assert "System" in get_method["tags"]
    assert "200" in get_method["responses"]


@pytest.mark.asyncio
async def test_get_api_docs_docs_endpoint():
    """Test that docs endpoint is properly documented."""
    response = await get_api_docs_handler()

    docs_path = response["paths"]["/docs"]

    # Should have GET method
    assert "get" in docs_path

    # Check GET method details
    get_method = docs_path["get"]
    assert get_method["summary"] == "API documentation"
    assert "System" in get_method["tags"]
    assert "200" in get_method["responses"]


@pytest.mark.asyncio
async def test_cleanup_expired_jobs_success():
    """Test successful cleanup of expired jobs."""
    # Create mock expired jobs
    expired_jobs = [
        Job(
            job_id=f"job-{i}",
            brand_id="brand-123",
            status="failed" if i % 2 == 0 else "completed",
            progress=100.0,
            state={"test": "data"},
            webhook_url=None,
            webhook_attempts=0,
            idempotency_key=None,
            error=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc),
        )
        for i in range(5)
    ]

    # Mock Supabase client
    mock_client = Mock()
    
    # Mock JobStorage methods - patch get_supabase_client in both modules
    with patch("mobius.storage.jobs.get_supabase_client", return_value=mock_client):
        with patch("mobius.storage.files.get_supabase_client", return_value=mock_client):
            with patch("mobius.storage.jobs.JobStorage.list_expired_jobs", new_callable=AsyncMock, return_value=expired_jobs):
                with patch("mobius.storage.jobs.JobStorage.delete_job", new_callable=AsyncMock, return_value=True) as mock_delete_job:
                    with patch("mobius.storage.files.FileStorage.delete_file", new_callable=AsyncMock, return_value=True) as mock_delete_file:
                        response = await cleanup_expired_jobs()

                        # Check response
                        assert response["status"] == "completed"
                        assert response["jobs_deleted"] == 5
                        assert "timestamp" in response

                        # Verify that delete_job was called for each job
                        assert mock_delete_job.call_count == 5

                        # Verify that delete_file was called for failed jobs (3 out of 5)
                        # Jobs with even indices (0, 2, 4) have status "failed"
                        assert mock_delete_file.call_count == 3


@pytest.mark.asyncio
async def test_cleanup_expired_jobs_no_expired_jobs():
    """Test cleanup when there are no expired jobs."""
    # Mock Supabase client
    mock_client = Mock()

    # Mock JobStorage methods with no expired jobs
    with patch("mobius.storage.jobs.get_supabase_client", return_value=mock_client):
        with patch("mobius.storage.files.get_supabase_client", return_value=mock_client):
            with patch("mobius.storage.jobs.JobStorage.list_expired_jobs", new_callable=AsyncMock, return_value=[]):
                with patch("mobius.storage.jobs.JobStorage.delete_job", new_callable=AsyncMock, return_value=True) as mock_delete_job:
                    with patch("mobius.storage.files.FileStorage.delete_file", new_callable=AsyncMock, return_value=True) as mock_delete_file:
                        response = await cleanup_expired_jobs()

                        # Check response
                        assert response["status"] == "completed"
                        assert response["jobs_deleted"] == 0
                        assert response["files_deleted"] == 0

                        # Verify that delete methods were not called
                        assert mock_delete_job.call_count == 0
                        assert mock_delete_file.call_count == 0


@pytest.mark.asyncio
async def test_cleanup_expired_jobs_partial_failure():
    """Test cleanup when some job deletions fail."""
    # Mock Supabase client
    mock_client = Mock()

    # Create mock expired jobs
    expired_jobs = [
        Job(
            job_id=f"job-{i}",
            brand_id="brand-123",
            status="completed",
            progress=100.0,
            state={"test": "data"},
            webhook_url=None,
            webhook_attempts=0,
            idempotency_key=None,
            error=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc),
        )
        for i in range(3)
    ]

    # Make the second deletion fail
    async def delete_job_side_effect(job_id):
        if job_id == "job-1":
            raise Exception("Database error")
        return True

    # Mock JobStorage methods
    with patch("mobius.storage.jobs.get_supabase_client", return_value=mock_client):
        with patch("mobius.storage.files.get_supabase_client", return_value=mock_client):
            with patch("mobius.storage.jobs.JobStorage.list_expired_jobs", new_callable=AsyncMock, return_value=expired_jobs):
                with patch("mobius.storage.jobs.JobStorage.delete_job", new_callable=AsyncMock, side_effect=delete_job_side_effect):
                    with patch("mobius.storage.files.FileStorage.delete_file", new_callable=AsyncMock, return_value=True):
                        response = await cleanup_expired_jobs()

                        # Check response
                        assert response["status"] == "completed"
                        assert response["jobs_deleted"] == 2  # Only 2 succeeded
                        assert len(response["errors"]) == 1  # One error
                        assert "job-1" in response["errors"][0]


@pytest.mark.asyncio
async def test_cleanup_expired_jobs_complete_failure():
    """Test cleanup when the entire operation fails."""
    # Mock Supabase client
    mock_client = Mock()

    # Mock JobStorage method that fails on list_expired_jobs
    with patch("mobius.storage.jobs.get_supabase_client", return_value=mock_client):
        with patch("mobius.storage.files.get_supabase_client", return_value=mock_client):
            with patch("mobius.storage.jobs.JobStorage.list_expired_jobs", new_callable=AsyncMock, side_effect=Exception("Database connection failed")):
                response = await cleanup_expired_jobs()

                # Check response
                assert response["status"] == "failed"
                assert "error" in response
                assert "Database connection failed" in response["error"]
                assert "timestamp" in response


@pytest.mark.asyncio
async def test_cleanup_expired_jobs_file_deletion_failure():
    """Test cleanup when file deletion fails but job deletion succeeds."""
    # Mock Supabase client
    mock_client = Mock()

    # Create mock expired job with failed status
    expired_jobs = [
        Job(
            job_id="job-failed",
            brand_id="brand-123",
            status="failed",
            progress=50.0,
            state={"test": "data"},
            webhook_url=None,
            webhook_attempts=0,
            idempotency_key=None,
            error="Generation failed",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc),
        )
    ]

    # Mock JobStorage methods
    with patch("mobius.storage.jobs.get_supabase_client", return_value=mock_client):
        with patch("mobius.storage.files.get_supabase_client", return_value=mock_client):
            with patch("mobius.storage.jobs.JobStorage.list_expired_jobs", new_callable=AsyncMock, return_value=expired_jobs):
                with patch("mobius.storage.jobs.JobStorage.delete_job", new_callable=AsyncMock, return_value=True) as mock_delete_job:
                    with patch("mobius.storage.files.FileStorage.delete_file", new_callable=AsyncMock, side_effect=Exception("File not found")):
                        response = await cleanup_expired_jobs()

                        # Check response - should still succeed since file deletion failure is ignored
                        assert response["status"] == "completed"
                        assert response["jobs_deleted"] == 1
                        assert response["files_deleted"] == 0  # File deletion failed but was ignored

                        # Verify that job was still deleted
                        assert mock_delete_job.call_count == 1
