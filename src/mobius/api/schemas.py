"""
Pydantic request/response schemas for API endpoints.

Defines all API request and response models with validation.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime


# Generation API Schemas
class GenerateRequest(BaseModel):
    """Request schema for asset generation."""

    brand_id: str = Field(description="Brand ID to use for generation")
    prompt: str = Field(description="Generation prompt")
    template_id: Optional[str] = Field(None, description="Optional template ID to use")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for async completion")
    async_mode: bool = Field(default=False, description="Whether to run asynchronously")
    idempotency_key: Optional[str] = Field(
        None,
        description="Client-provided key to prevent duplicate job creation. "
        "If a job with this key exists and is not expired, "
        "returns the existing job instead of creating a new one.",
        max_length=64,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "brand_id": "brand-123",
                "prompt": "Create a social media post about our new product",
                "async_mode": True,
                "webhook_url": "https://example.com/webhook",
                "idempotency_key": "client-request-456",
            }
        }


class GenerateResponse(BaseModel):
    """Response schema for asset generation."""

    job_id: str
    status: str
    message: str
    image_url: Optional[str] = None
    compliance_score: Optional[float] = None
    request_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job-789",
                "status": "pending",
                "message": "Job created successfully",
                "request_id": "req_abc123",
            }
        }


# Brand Ingestion API Schemas
class IngestBrandRequest(BaseModel):
    """Request schema for brand ingestion."""

    organization_id: str = Field(description="Organization ID")
    brand_name: str = Field(description="Brand name")
    # PDF file uploaded as multipart/form-data


class IngestBrandResponse(BaseModel):
    """Response schema for brand ingestion."""

    brand_id: str
    status: str
    pdf_url: str
    needs_review: List[str] = Field(default_factory=list)
    request_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "brand_id": "brand-123",
                "status": "processing",
                "pdf_url": "https://cdn.example.com/brand-123/guidelines.pdf",
                "needs_review": [],
                "request_id": "req_def456",
            }
        }


# Brand Management API Schemas
class BrandListItem(BaseModel):
    """Brand list item with summary information."""

    brand_id: str
    name: str
    logo_thumbnail_url: Optional[str]
    asset_count: int
    avg_compliance_score: float
    last_activity: datetime


class BrandListResponse(BaseModel):
    """Response schema for brand list."""

    brands: List[BrandListItem]
    total: int
    request_id: str


class BrandDetailResponse(BaseModel):
    """Response schema for brand details."""

    brand_id: str
    organization_id: str
    name: str
    guidelines: Dict[str, Any]
    pdf_url: Optional[str]
    logo_thumbnail_url: Optional[str]
    needs_review: List[str]
    learning_active: bool
    feedback_count: int
    created_at: datetime
    updated_at: datetime
    request_id: str


class UpdateBrandRequest(BaseModel):
    """Request schema for updating brand metadata."""

    name: Optional[str] = None
    logo_thumbnail_url: Optional[str] = None


# Template API Schemas
class SaveTemplateRequest(BaseModel):
    """Request schema for saving a template."""

    asset_id: str = Field(description="Asset ID to create template from")
    template_name: str = Field(description="Template name")
    description: str = Field(description="Template description")


class TemplateResponse(BaseModel):
    """Response schema for template operations."""

    template_id: str
    brand_id: str
    name: str
    description: str
    generation_params: Dict[str, Any]
    thumbnail_url: str
    created_at: datetime
    request_id: str


class TemplateListResponse(BaseModel):
    """Response schema for template list."""

    templates: List[TemplateResponse]
    total: int
    request_id: str


# Feedback API Schemas
class SubmitFeedbackRequest(BaseModel):
    """Request schema for submitting feedback."""

    asset_id: str = Field(description="Asset ID")
    action: str = Field(description="Action (approve or reject)", pattern="^(approve|reject)$")
    reason: Optional[str] = Field(None, description="Optional reason for rejection")


class FeedbackResponse(BaseModel):
    """Response schema for feedback submission."""

    feedback_id: str
    brand_id: str
    total_feedback_count: int
    learning_active: bool
    request_id: str


class FeedbackStatsResponse(BaseModel):
    """Response schema for feedback statistics."""

    brand_id: str
    total_approvals: int
    total_rejections: int
    learning_active: bool
    request_id: str


# Job Status API Schemas
class JobStatusResponse(BaseModel):
    """Response schema for job status."""

    job_id: str
    status: str
    progress: float = Field(ge=0, le=100)
    current_image_url: Optional[str]
    compliance_score: Optional[float]
    error: Optional[str]
    created_at: datetime
    updated_at: datetime
    request_id: str


# System API Schemas
class HealthCheckResponse(BaseModel):
    """Response schema for health check."""

    status: str
    database: str
    storage: str
    api: str
    timestamp: datetime
    request_id: str


class CancelJobResponse(BaseModel):
    """Response schema for job cancellation."""

    job_id: str
    status: str
    message: str
    request_id: str
