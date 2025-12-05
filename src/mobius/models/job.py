"""
Job entity models.

Defines the structure for async job tracking.
"""

from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class Job(BaseModel):
    """Async job entity."""

    job_id: str = Field(description="Unique job identifier")
    brand_id: str = Field(description="Associated brand ID")
    status: str = Field(
        description="Job status (pending, generating, auditing, correcting, completed, failed)"
    )
    progress: float = Field(default=0.0, ge=0, le=100, description="Job progress percentage")
    state: Dict[str, Any] = Field(description="Complete job state")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for completion notification")
    webhook_attempts: int = Field(default=0, description="Number of webhook delivery attempts")
    idempotency_key: Optional[str] = Field(
        None, max_length=64, description="Client-provided idempotency key"
    )
    error: Optional[str] = Field(None, description="Error message if job failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=24),
        description="Job expiration timestamp",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "job-123",
                "brand_id": "brand-456",
                "status": "generating",
                "progress": 50.0,
                "state": {"attempt_count": 1, "current_image_url": None},
                "webhook_url": "https://example.com/webhook",
            }
        }
    )
