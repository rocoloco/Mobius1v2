"""
Brand structuring node for ingestion workflow.

Maps extracted data to BrandGuidelines schema and persists to database.
"""

from mobius.models.state import IngestionState
from mobius.models.brand import (
    Brand,
    BrandGuidelines,
    Color,
    Typography,
    LogoRule,
    VoiceTone,
    BrandRule,
)
from mobius.storage.brands import BrandStorage
from mobius.tools.gemini import GeminiClient
from datetime import datetime, timezone
import httpx
import structlog

logger = structlog.get_logger()


async def structure_node(state: IngestionState) -> dict:
    """
    Structure extracted data into Brand entity and persist to database.

    Uses Gemini with response_schema to create a fully structured BrandGuidelines
    object from the extracted text and visual data. Handles validation and
    defaults for Enum fields.

    Args:
        state: Current ingestion workflow state

    Returns:
        Updated state dict with completion status
    """
    logger.info("structure_start", brand_id=state["brand_id"])

    try:
        # Download PDF for final structured extraction
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(state["pdf_url"])
            response.raise_for_status()
            pdf_bytes = response.content

        # Use Gemini with response_schema for structured extraction
        gemini = GeminiClient()
        guidelines = await gemini.extract_brand_guidelines(
            pdf_bytes=pdf_bytes, extracted_text=state.get("extracted_text")
        )

        # Validate and apply defaults for usage Enums
        for color in guidelines.colors:
            if not color.usage:
                # Default to "primary" if unspecified
                color.usage = "primary"
                logger.debug("color_usage_defaulted", color_name=color.name)

        # Check if guidelines are minimally valid
        needs_review = list(state.get("needs_review", []))

        if len(guidelines.colors) == 0:
            needs_review.append("No colors extracted - manual review required")

        if len(guidelines.typography) == 0:
            needs_review.append("No typography extracted - manual review required")

        if len(guidelines.rules) == 0:
            needs_review.append("No governance rules extracted - manual review required")

        # Add metadata
        guidelines.source_filename = state.get("pdf_url", "").split("/")[-1]
        guidelines.ingested_at = datetime.now(timezone.utc).isoformat()

        # Create Brand entity
        brand = Brand(
            brand_id=state["brand_id"],
            organization_id=state["organization_id"],
            name=state.get("brand_name", f"Brand {state['brand_id'][:8]}"),
            website=None,
            guidelines=guidelines,
            pdf_url=state["pdf_url"],
            logo_thumbnail_url=None,  # TODO: Extract logo thumbnail
            needs_review=needs_review,
            learning_active=False,
            feedback_count=0,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
            deleted_at=None,
        )

        # Persist to database
        storage = BrandStorage()
        await storage.create_brand(brand)

        logger.info(
            "brand_structured_and_persisted",
            brand_id=state["brand_id"],
            colors=len(guidelines.colors),
            typography=len(guidelines.typography),
            logos=len(guidelines.logos),
            rules=len(guidelines.rules),
            needs_review_count=len(needs_review),
        )

        return {"status": "completed", "needs_review": needs_review}

    except Exception as e:
        logger.error("structuring_failed", brand_id=state["brand_id"], error=str(e))
        return {
            "status": "failed",
            "needs_review": state.get("needs_review", []) + [f"Structuring failed: {str(e)}"],
        }
