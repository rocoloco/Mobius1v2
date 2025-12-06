"""
Brand data models with Digital Twin schema.

Implements strict Pydantic models for brand guidelines to support
automated governance and compliance checking in the Audit Node.

The Digital Twin approach provides:
- Programmatic access to specific brand elements (colors, typography, logos)
- Structured rules with severity levels for automated auditing
- Negative constraints for "Do Not" instructions
- Version tracking and metadata
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any


# --- Component 1: The Visual DNA ---


class Color(BaseModel):
    """
    Brand color specification.

    Defines a single color with its usage context and constraints.
    Used by Audit Node to validate color compliance in generated assets.
    """

    name: str = Field(description="Color name, e.g., 'Midnight Blue'")
    hex: str = Field(description="Hex code, e.g., '#0057B8'")
    usage: Literal["primary", "secondary", "accent", "background"] = Field(
        description="Color usage category"
    )
    context: Optional[str] = Field(None, description="Additional usage context or constraints")


class Typography(BaseModel):
    """
    Typography specification for brand fonts.

    Defines font families, weights, and usage guidelines.
    """

    family: str = Field(description="Font family name")
    weights: List[str] = Field(description="Available font weights")
    usage: str = Field(description="Usage guidelines for this typography")


class LogoRule(BaseModel):
    """
    Logo usage rules and constraints.

    Defines specific requirements for logo placement, sizing, and context.
    Used by Audit Node to validate logo compliance.
    """

    variant_name: str = Field(description="Logo variant identifier")
    url: str = Field(description="URL to logo asset")
    min_width_px: int = Field(description="Minimum width in pixels")
    clear_space_ratio: float = Field(description="Required clear space as ratio of logo size")
    forbidden_backgrounds: List[str] = Field(
        description="List of forbidden background colors (hex codes)"
    )


# --- Component 2: The Verbal Soul ---


class VoiceTone(BaseModel):
    """
    Brand voice and tone guidelines.

    Defines the verbal identity of the brand including tone adjectives,
    forbidden words, and example phrases.
    """

    adjectives: List[str] = Field(description="Adjectives describing brand voice")
    forbidden_words: List[str] = Field(description="Words that should never be used")
    example_phrases: List[str] = Field(description="Example phrases that embody the brand voice")


# --- Component 3: The Hard Rules (Audit Logic) ---


class BrandRule(BaseModel):
    """
    Brand governance rule for automated auditing.

    Defines a specific rule with category, severity, and constraint type.
    The negative_constraint field is critical for Audit Node logic:
    - If True: This is a "Do Not" instruction (violation if present)
    - If False: This is a "Do" instruction (violation if absent)
    """

    category: Literal["visual", "verbal", "legal"] = Field(description="Rule category")
    instruction: str = Field(description="The rule instruction text")
    severity: Literal["warning", "critical"] = Field(description="Violation severity level")
    negative_constraint: bool = Field(
        default=False,
        description="If True, Audit Node treats this as a 'Do Not' instruction",
    )


# --- The Aggregate Digital Twin ---


class BrandGuidelines(BaseModel):
    """
    Complete brand guidelines as a Digital Twin.

    Aggregates all brand elements into a structured, queryable format
    that supports automated compliance checking and governance.
    """

    colors: List[Color] = Field(
        default_factory=list, description="Brand color palette with usage rules"
    )
    typography: List[Typography] = Field(
        default_factory=list, description="Typography specifications"
    )
    logos: List[LogoRule] = Field(default_factory=list, description="Logo usage rules")
    voice: Optional[VoiceTone] = Field(None, description="Brand voice and tone guidelines")
    rules: List[BrandRule] = Field(
        default_factory=list, description="Governance rules for automated auditing"
    )

    # Metadata for versioning
    source_filename: Optional[str] = Field(None, description="Original PDF filename")
    ingested_at: Optional[str] = Field(None, description="ISO timestamp of ingestion")


class Brand(BaseModel):
    """
    Complete brand entity with Digital Twin guidelines.

    Represents a brand in the system with all associated metadata
    and structured guidelines for automated governance.
    """

    brand_id: str = Field(description="Unique brand identifier")
    organization_id: str = Field(description="Organization this brand belongs to")
    name: str = Field(description="Brand name")
    website: Optional[str] = Field(None, description="Brand website URL")

    # The Digital Twin Field
    guidelines: BrandGuidelines = Field(description="Structured brand guidelines")

    # Timestamps
    created_at: str = Field(description="ISO timestamp of creation")
    updated_at: str = Field(description="ISO timestamp of last update")
    deleted_at: Optional[str] = Field(None, description="ISO timestamp of soft deletion")

    # Additional metadata fields for compatibility
    pdf_url: Optional[str] = Field(None, description="URL to original brand guidelines PDF")
    logo_thumbnail_url: Optional[str] = Field(None, description="URL to logo thumbnail")
    needs_review: List[str] = Field(
        default_factory=list, description="Items flagged for manual review during ingestion"
    )
    learning_active: bool = Field(
        default=False, description="Whether ML learning is active for this brand"
    )
    feedback_count: int = Field(default=0, description="Total feedback events for this brand")
