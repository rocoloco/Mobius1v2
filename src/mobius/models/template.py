"""
Template entity models.

Defines the structure for reusable generation templates.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class Template(BaseModel):
    """Reusable generation template."""

    template_id: str = Field(description="Unique template identifier")
    brand_id: str = Field(description="Associated brand ID")
    name: str = Field(description="Template name")
    description: str = Field(description="Template description")
    generation_params: Dict[str, Any] = Field(description="Stored generation parameters")
    thumbnail_url: str = Field(description="Preview thumbnail URL")
    source_asset_id: Optional[str] = Field(
        None, description="Asset ID this template was created from"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "template_id": "template-123",
                "brand_id": "brand-456",
                "name": "Social Media Post",
                "description": "Standard social media post template",
                "generation_params": {
                    "prompt": "Create a social media post",
                    "style": "modern",
                    "aspect_ratio": "1:1",
                },
                "thumbnail_url": "https://cdn.example.com/thumbnail.png",
            }
        }
    )
