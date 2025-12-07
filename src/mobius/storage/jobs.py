"""
Job storage operations.

Provides CRUD operations for job entities in Supabase.
"""

from mobius.models.job import Job
from mobius.storage.database import get_supabase_client
from typing import List, Optional
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger()


class JobStorage:
    """Storage operations for job entities."""

    def __init__(self):
        self.client = get_supabase_client()

    async def create_job(self, job: Job) -> Job:
        """
        Create a new job in the database.

        Args:
            job: Job entity to create

        Returns:
            Job: Created job with database-generated fields

        Raises:
            Exception: If database operation fails
        """
        logger.info(
            "creating_job",
            job_id=job.job_id,
            brand_id=job.brand_id,
            idempotency_key=job.idempotency_key,
        )

        # Serialize with mode='json' to convert datetime to ISO strings
        data = job.model_dump(mode='json')
        result = self.client.table("jobs").insert(data).execute()

        logger.info("job_created", job_id=job.job_id)
        return Job.model_validate(result.data[0])

    async def get_job(self, job_id: str) -> Optional[Job]:
        """
        Retrieve a job by ID.

        Args:
            job_id: UUID of the job

        Returns:
            Job if found, None otherwise
        """
        logger.debug("fetching_job", job_id=job_id)

        result = (
            self.client.table("jobs").select("*").eq("job_id", job_id).execute()
        )

        if result.data:
            return Job.model_validate(result.data[0])
        return None

    async def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Job]:
        """
        Retrieve a non-expired job by idempotency key.

        This enables idempotent job creation - if a job with the same
        idempotency_key exists and hasn't expired, return it instead
        of creating a duplicate.

        Args:
            idempotency_key: Client-provided idempotency key

        Returns:
            Job if found and not expired, None otherwise
        """
        logger.debug("fetching_job_by_idempotency_key", idempotency_key=idempotency_key)

        result = (
            self.client.table("jobs")
            .select("*")
            .eq("idempotency_key", idempotency_key)
            .gt("expires_at", datetime.now(timezone.utc).isoformat())
            .execute()
        )

        if result.data:
            logger.info(
                "idempotent_job_found",
                idempotency_key=idempotency_key,
                job_id=result.data[0]["job_id"],
            )
            return Job.model_validate(result.data[0])

        return None

    async def list_jobs(
        self,
        brand_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Job]:
        """
        List jobs with optional filtering.

        Args:
            brand_id: Optional UUID of the brand to filter by
            status: Optional status to filter by
            limit: Maximum number of jobs to return
            offset: Number of jobs to skip

        Returns:
            List of Job entities
        """
        logger.debug(
            "listing_jobs",
            brand_id=brand_id,
            status=status,
            limit=limit,
            offset=offset,
        )

        query = self.client.table("jobs").select("*")

        if brand_id:
            query = query.eq("brand_id", brand_id)

        if status:
            query = query.eq("status", status)

        result = (
            query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        )

        return [Job.model_validate(j) for j in result.data]

    async def update_job(self, job_id: str, updates: dict) -> Job:
        """
        Update job fields.

        Args:
            job_id: UUID of the job
            updates: Dictionary of fields to update

        Returns:
            Updated Job entity

        Raises:
            Exception: If job not found or update fails
        """
        logger.info("updating_job", job_id=job_id, fields=list(updates.keys()))

        # Add updated_at timestamp
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        result = (
            self.client.table("jobs").update(updates).eq("job_id", job_id).execute()
        )

        if not result.data:
            raise ValueError(f"Job {job_id} not found")

        logger.info("job_updated", job_id=job_id)
        return Job.model_validate(result.data[0])

    async def delete_job(self, job_id: str) -> bool:
        """
        Delete a job.

        Hard delete - removes the record from the database.
        Used by cleanup scheduler for expired jobs.

        Args:
            job_id: UUID of the job

        Returns:
            True if successful

        Raises:
            Exception: If job not found or delete fails
        """
        logger.info("deleting_job", job_id=job_id)

        result = self.client.table("jobs").delete().eq("job_id", job_id).execute()

        if not result.data:
            raise ValueError(f"Job {job_id} not found")

        logger.info("job_deleted", job_id=job_id)
        return True

    async def list_expired_jobs(self, limit: int = 100) -> List[Job]:
        """
        List expired jobs for cleanup.

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of expired Job entities
        """
        logger.debug("listing_expired_jobs", limit=limit)

        result = (
            self.client.table("jobs")
            .select("*")
            .lt("expires_at", datetime.now(timezone.utc).isoformat())
            .limit(limit)
            .execute()
        )

        return [Job.model_validate(j) for j in result.data]
