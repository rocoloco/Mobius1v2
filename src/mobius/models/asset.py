"""
Asset entity models.

Defines the structure for generated assets.
"""

from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class Asset(BaseModel):
    """Generated asset entity."""

    asset_id: str = Field(description="Unique asset identifier")
    brand_id: str = Field(description="Associated brand ID")
    job_id: str = Field(description="Job that created this asset")
    prompt: str = Field(description="Generation prompt used")
    image_url: str = Field(description="URL to the generated image")
    compliance_score: Optional[float] = Field(
        None, ge=0, le=100, description="Overall compliance score"
    )
    compliance_details: Optional[Dict[str, Any]] = Field(
        None, description="Detailed compliance breakdown"
    )
    generation_params: Optional[Dict[str, Any]] = Field(
        None, description="Parameters used for generation"
    )
    status: str = Field(description="Asset status (approved, rejected, pending)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "asset-123",
                "brand_id": "brand-456",
                "job_id": "job-789",
                "prompt": "Create a social media post",
                "image_url": "https://cdn.example.com/image.png",
                "compliance_score": 92.5,
                "status": "approved",
            }
        }
    )
