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
import json
import tiktoken


# --- Component 1: The Visual DNA ---


class Color(BaseModel):
    """
    Brand color specification with semantic design tokens.

    Defines a single color with its semantic role and usage weight.
    This prevents the "Confetti Problem" where colors are technically correct
    but aesthetically chaotic due to lack of usage hierarchy.
    
    The semantic role allows the Vision Model to understand HOW to use each color,
    not just THAT it's approved. The usage_weight enables enforcement of the
    60-30-10 design rule for proper visual hierarchy.
    """

    name: str = Field(description="Color name, e.g., 'Midnight Blue'")
    hex: str = Field(description="Hex code, e.g., '#0057B8'")
    usage: Literal["primary", "secondary", "accent", "neutral", "semantic"] = Field(
        description=(
            "Semantic role of this color:\n"
            "- primary: Dominant brand identity (logos, headers)\n"
            "- secondary: Supporting elements (shapes, icons)\n"
            "- accent: High-visibility CTAs (buttons, links) - use sparingly\n"
            "- neutral: Backgrounds, body text (white, black, greys)\n"
            "- semantic: Functional states (success green, error red)"
        )
    )
    usage_weight: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description=(
            "Estimated usage frequency in the source PDF (0.0 to 1.0). "
            "Used to enforce the 60-30-10 design rule. "
            "Inferred by Reasoning Model based on visual analysis of the PDF."
        )
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


class IdentityCore(BaseModel):
    """
    Brand identity archetype and voice vectors.
    
    This is the "soul" of the brand - the strategic positioning that informs
    all creative decisions. By capturing this as structured data, we create
    lock-in: clients cannot easily migrate to another platform because we
    own the machine-readable definition of their brand identity.
    """
    
    archetype: Optional[str] = Field(
        None,
        description=(
            "Brand archetype (e.g., 'The Sage', 'The Hero', 'The Rebel'). "
            "Based on Jungian archetypes, this guides tone and visual style."
        )
    )
    
    voice_vectors: Dict[str, float] = Field(
        default_factory=dict,
        description=(
            "Voice dimensions as 0.0-1.0 scores. Examples:\n"
            "- formal: 0.8 (very formal) vs 0.2 (casual)\n"
            "- witty: 0.7 (playful) vs 0.1 (serious)\n"
            "- urgent: 0.9 (time-sensitive) vs 0.2 (relaxed)\n"
            "- technical: 0.8 (jargon-heavy) vs 0.2 (accessible)\n"
            "These vectors enable fine-grained tone control in generation."
        )
    )
    
    negative_constraints: List[str] = Field(
        default_factory=list,
        description=(
            "High-level 'never do this' rules that apply across all contexts. "
            "Examples: 'No drop shadows', 'No neon colors', 'Never use gradients on text'"
        )
    )


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


class ContextualRule(BaseModel):
    """
    Context-specific brand rule for different channels and mediums.
    
    This enables channel-specific governance (LinkedIn vs. Instagram,
    print vs. digital) which is critical for enterprise brands that
    need different rules for different contexts.
    
    MOAT VALUE: By capturing context-specific rules, we make it harder
    for clients to migrate because this nuanced governance logic is
    difficult to replicate.
    """
    
    context: str = Field(
        description=(
            "Context identifier. Examples:\n"
            "- 'social_media_linkedin' - LinkedIn posts\n"
            "- 'social_media_instagram' - Instagram posts\n"
            "- 'print_packaging' - Physical packaging\n"
            "- 'email_marketing' - Email campaigns\n"
            "- 'web_landing_page' - Website landing pages"
        )
    )
    
    rule: str = Field(
        description=(
            "Context-specific rule text. Examples:\n"
            "- 'Images must contain human subjects; 20% overlay opacity maximum'\n"
            "- 'CMYK only; minimal whitespace 15mm'\n"
            "- 'Maximum 3 colors per composition'"
        )
    )
    
    priority: int = Field(
        description=(
            "Rule priority (1-10, higher = more important). "
            "Used to resolve conflicts when multiple rules apply."
        ),
        ge=1,
        le=10
    )
    
    applies_to: List[str] = Field(
        default_factory=list,
        description=(
            "Asset types this rule applies to. Examples: "
            "['image', 'video', 'document']. Empty list = applies to all."
        )
    )


# --- The Aggregate Digital Twin ---


class AssetGraph(BaseModel):
    """
    Structured asset inventory for the brand.
    
    Instead of just storing logo URLs in LogoRule, we maintain a
    comprehensive asset graph that tracks all brand assets with
    metadata and relationships.
    
    MOAT VALUE: This becomes the single source of truth for all
    brand assets, making it difficult for clients to migrate.
    """
    
    logos: Dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Logo variants with semantic keys. Examples:\n"
            "- 'primary': 's3://.../logo_main.svg'\n"
            "- 'reversed': 's3://.../logo_white.svg'\n"
            "- 'icon': 's3://.../logo_icon.png'\n"
            "- 'wordmark': 's3://.../logo_wordmark.svg'"
        )
    )
    
    templates: Dict[str, str] = Field(
        default_factory=dict,
        description="Approved templates with semantic keys (e.g., 'social_post', 'email_header')"
    )
    
    patterns: Dict[str, str] = Field(
        default_factory=dict,
        description="Design patterns and textures (e.g., 'background_texture', 'divider_pattern')"
    )
    
    photography_style: Optional[str] = Field(
        None,
        description="URL to photography style guide or example images"
    )


class BrandGuidelines(BaseModel):
    """
    Complete brand guidelines as a Digital Twin.

    Aggregates all brand elements into a structured, queryable format
    that supports automated compliance checking and governance.
    
    This is the "Brand Graph" - the machine-readable operating system
    for the brand that creates lock-in by owning the structured data.
    """

    # Core Identity (MOAT: Strategic positioning)
    identity_core: Optional[IdentityCore] = Field(
        None,
        description="Brand archetype, voice vectors, and negative constraints"
    )

    # Visual DNA
    colors: List[Color] = Field(
        default_factory=list, description="Brand color palette with usage rules"
    )
    typography: List[Typography] = Field(
        default_factory=list, description="Typography specifications"
    )
    logos: List[LogoRule] = Field(default_factory=list, description="Logo usage rules")
    
    # Verbal Soul
    voice: Optional[VoiceTone] = Field(None, description="Brand voice and tone guidelines")
    
    # Governance Rules
    rules: List[BrandRule] = Field(
        default_factory=list, description="Governance rules for automated auditing"
    )
    
    # Context-Specific Rules (MOAT: Channel-specific governance)
    contextual_rules: List[ContextualRule] = Field(
        default_factory=list,
        description="Context-specific rules for different channels and mediums"
    )
    
    # Asset Inventory (MOAT: Single source of truth for assets)
    asset_graph: Optional[AssetGraph] = Field(
        None,
        description="Structured inventory of all brand assets"
    )

    # Metadata for versioning
    source_filename: Optional[str] = Field(None, description="Original PDF filename")
    ingested_at: Optional[str] = Field(None, description="ISO timestamp of ingestion")
    version: str = Field(default="1.0.0", description="Brand guidelines version")


class CompressedDigitalTwin(BaseModel):
    """
    Optimized brand guidelines for Vision Model context window.
    
    Contains only essential visual rules to fit within 65k tokens.
    This compressed representation is used during image generation
    to provide brand context without exceeding the Vision Model's
    context window limit.
    
    CRITICAL: Preserves semantic color hierarchy to prevent the "Confetti Problem"
    where colors are technically correct but aesthetically chaotic. Each color
    role tells the Vision Model HOW to use the color, not just THAT it's approved.
    """
    
    # Semantic color hierarchy (prevents Confetti Problem)
    primary_colors: List[str] = Field(
        default_factory=list,
        description="Hex codes for dominant brand identity (logos, headers)"
    )
    secondary_colors: List[str] = Field(
        default_factory=list,
        description="Hex codes for supporting elements (shapes, icons)"
    )
    accent_colors: List[str] = Field(
        default_factory=list,
        description="Hex codes for high-visibility CTAs (buttons, links) - use sparingly"
    )
    neutral_colors: List[str] = Field(
        default_factory=list,
        description="Hex codes for backgrounds and body text (white, black, greys)"
    )
    semantic_colors: List[str] = Field(
        default_factory=list,
        description="Hex codes for functional states (success green, error red)"
    )
    
    # Typography
    font_families: List[str] = Field(
        default_factory=list,
        description="Font names only (e.g., ['Helvetica Neue', 'Georgia'])"
    )
    
    # Critical constraints (concise rules)
    visual_dos: List[str] = Field(
        default_factory=list,
        description="Positive visual rules (concise bullet points)"
    )
    visual_donts: List[str] = Field(
        default_factory=list,
        description="Negative visual rules (concise bullet points)"
    )
    
    # Logo requirements (essential only)
    logo_placement: Optional[str] = Field(
        None,
        description="Placement rule (e.g., 'top-left or center')"
    )
    logo_min_size: Optional[str] = Field(
        None,
        description="Minimum size (e.g., '100px width')"
    )
    
    def estimate_tokens(self) -> int:
        """
        Estimate token count for context window validation.
        
        Uses tiktoken with cl100k_base encoding (GPT-4 tokenizer)
        to estimate the number of tokens this compressed twin will
        consume in the Vision Model's context window.
        
        Returns:
            Estimated token count for the serialized JSON representation
        """
        # Serialize to JSON
        json_str = json.dumps(self.model_dump(), indent=2)
        
        # Use tiktoken to count tokens (cl100k_base is used by GPT-4 and Gemini)
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(json_str)
        
        return len(tokens)
    
    def validate_size(self) -> bool:
        """
        Ensure compressed twin fits within 60k token limit.
        
        The Vision Model has a 65k token context window. We use a
        60k token limit to leave headroom for the prompt and other
        context that will be included during generation.
        
        Returns:
            True if token count is under 60,000, False otherwise
        """
        token_count = self.estimate_tokens()
        return token_count < 60000


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
    
    # Compressed Digital Twin for generation
    compressed_twin: Optional[CompressedDigitalTwin] = Field(
        None,
        description="Compressed brand guidelines optimized for Vision Model context window"
    )

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
