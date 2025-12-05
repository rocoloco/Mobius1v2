"""
Brand entity Pydantic models.

Defines the structure for brand guidelines and brand entities.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class BrandColors(BaseModel):
    """Brand color palette."""

    primary: List[str] = Field(description="Primary brand hex codes", default_factory=list)
    secondary: List[str] = Field(description="Secondary brand hex codes", default_factory=list)


class BrandTypography(BaseModel):
    """Brand typography guidelines."""

    font_families: List[str] = Field(default_factory=list)
    sizes: Optional[Dict[str, Any]] = None
    weights: Optional[List[str]] = None


class BrandLogo(BaseModel):
    """Brand logo usage guidelines."""

    clear_space: Optional[str] = None
    minimum_size: Optional[str] = None
    prohibited_modifications: List[str] = Field(default_factory=list)


class BrandGuidelines(BaseModel):
    """Complete brand guidelines structure."""

    colors: BrandColors
    typography: BrandTypography
    logo: BrandLogo
    tone_of_voice: List[str] = Field(default_factory=list)
    visual_rules: List[str] = Field(default_factory=list)
    dos_and_donts: Dict[str, Any] = Field(default_factory=dict)


class Brand(BaseModel):
    """Brand entity with complete metadata."""

    brand_id: str
    organization_id: str
    name: str
    guidelines: BrandGuidelines
    pdf_url: Optional[str] = None
    logo_thumbnail_url: Optional[str] = None
    needs_review: List[str] = Field(default_factory=list)
    learning_active: bool = False
    feedback_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "brand_id": "brand-123",
                "organization_id": "org-456",
                "name": "Acme Corp",
                "guidelines": {
                    "colors": {"primary": ["#FF0000"], "secondary": ["#0000FF"]},
                    "typography": {"font_families": ["Arial"]},
                    "logo": {},
                    "tone_of_voice": ["Professional", "Friendly"],
                    "visual_rules": ["Use bold colors"],
                    "dos_and_donts": {},
                },
            }
        }
    )
