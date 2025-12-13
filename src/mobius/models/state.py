"""
LangGraph workflow state definitions.

These TypedDicts define the state structure for LangGraph workflows.
"""

from typing import TypedDict, List, Optional, Any
from datetime import datetime


class JobState(TypedDict, total=False):
    """State for the generation workflow."""

    # Required fields
    job_id: str
    brand_id: str
    prompt: str
    brand_hex_codes: List[str]
    brand_rules: str
    current_image_url: Optional[str]
    attempt_count: int
    audit_history: List[dict]
    compliance_scores: List[dict]
    is_approved: bool
    status: str  # "pending", "generating", "auditing", "correcting", "needs_review", "completed", "failed"
    created_at: datetime
    updated_at: datetime
    webhook_url: Optional[str]
    template_id: Optional[str]
    generation_params: Optional[dict]

    # Session management fields
    session_id: Optional[str]

    # Interactive review fields
    needs_review: bool
    review_requested_at: Optional[str]  # ISO timestamp
    user_decision: Optional[str]  # "approve" | "tweak" | "regenerate"
    user_tweak_instruction: Optional[str]
    approval_override: bool  # True if user approved despite low score
    
    # Logo configuration preservation for tweaks
    original_had_logos: bool  # Whether the original generation included logos


class IngestionState(TypedDict):
    """State for the brand ingestion workflow."""

    brand_id: str
    organization_id: str
    brand_name: str
    pdf_url: str
    extracted_text: Optional[str]
    extracted_colors: List[str]
    extracted_fonts: List[str]
    extracted_rules: List[str]
    compressed_twin: Optional[Any]  # CompressedDigitalTwin - using Any to avoid circular import
    needs_review: List[str]
    status: str  # "uploading", "extracting_text", "extracting_visual", "structuring", "completed", "failed"
