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

    brand_id: str = Field(description="Brand ID to use for generation", min_length=1)
    prompt: str = Field(description="Generation prompt", min_length=1)
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


# Learning API Schemas
class UpdateLearningSettingsRequest(BaseModel):
    """Request schema for updating learning privacy settings."""

    privacy_tier: str = Field(
        description="Privacy tier: off, private, or shared",
        pattern="^(off|private|shared)$"
    )
    consent_date: Optional[datetime] = Field(
        None,
        description="Consent timestamp (auto-set if not provided)"
    )
    data_retention_days: Optional[int] = Field(
        None,
        description="Data retention period in days",
        ge=1
    )

    class Config:
        json_schema_extra = {
            "example": {
                "privacy_tier": "private",
                "data_retention_days": 365
            }
        }


class LearningSettingsResponse(BaseModel):
    """Response schema for learning settings."""

    brand_id: str
    privacy_tier: str
    consent_date: Optional[datetime]
    consent_version: str
    data_retention_days: int
    created_at: datetime
    updated_at: datetime
    request_id: str


class BrandPatternResponse(BaseModel):
    """Response schema for brand pattern."""

    pattern_id: str
    brand_id: str
    pattern_type: str
    pattern_data: Dict[str, Any]
    confidence_score: float
    sample_count: int
    created_at: datetime
    updated_at: datetime


class LearningPatternsResponse(BaseModel):
    """Response schema for learned patterns."""

    brand_id: str
    patterns: List[BrandPatternResponse]
    total: int
    request_id: str


class LearningDashboardResponse(BaseModel):
    """Response schema for learning transparency dashboard."""

    brand_id: str
    privacy_tier: str
    patterns_learned: List[Dict[str, Any]]
    data_sources: str
    impact_metrics: Dict[str, Any]
    last_updated: datetime
    request_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "brand_id": "brand-123",
                "privacy_tier": "private",
                "patterns_learned": [
                    {
                        "type": "color_preference",
                        "description": "Warm colors preferred",
                        "confidence": 0.85
                    }
                ],
                "data_sources": "Your brand only",
                "impact_metrics": {
                    "compliance_improvement": 12.5,
                    "approval_rate_increase": 8.3
                },
                "last_updated": "2025-12-05T10:30:00Z",
                "request_id": "req_xyz789"
            }
        }


class LearningAuditLogEntry(BaseModel):
    """Audit log entry."""

    log_id: str
    action: str
    details: Dict[str, Any]
    timestamp: datetime


class LearningAuditLogResponse(BaseModel):
    """Response schema for learning audit log."""

    brand_id: str
    entries: List[LearningAuditLogEntry]
    total: int
    request_id: str


class ExportLearningDataResponse(BaseModel):
    """Response schema for learning data export."""

    brand_id: str
    export_date: datetime
    settings: Optional[Dict[str, Any]]
    patterns: List[Dict[str, Any]]
    audit_log: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    request_id: str


class DeleteLearningDataResponse(BaseModel):
    """Response schema for learning data deletion."""

    brand_id: str
    deleted: bool
    message: str
    request_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "brand_id": "brand-123",
                "deleted": True,
                "message": "All learning data has been permanently deleted",
                "request_id": "req_abc123"
            }
        }
