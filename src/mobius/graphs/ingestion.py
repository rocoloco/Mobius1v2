"""
Brand ingestion workflow using LangGraph.

Orchestrates the extraction and structuring of brand guidelines from PDFs:
1. Extract text from PDF
2. Extract visual elements (colors, logos)
3. Structure into BrandGuidelines schema
4. Validate and persist to database

Includes error handling and validation loops for ambiguous data.
"""

from langgraph.graph import StateGraph, END
from mobius.models.state import IngestionState
from mobius.nodes import extract_text, extract_visual, structure
import structlog

logger = structlog.get_logger()


def create_ingestion_workflow():
    """
    Create the brand ingestion LangGraph workflow.

    The workflow follows this flow:
    - extract_text: Extract raw text from PDF
    - extract_visual: Extract visual elements using Gemini Vision
    - structure: Map to BrandGuidelines schema and persist
    - Validation: If BrandGuidelines validation fails, populate needs_review

    Returns:
        Compiled LangGraph workflow
    """
    logger.info("creating_ingestion_workflow")

    workflow = StateGraph(IngestionState)

    # Add nodes
    workflow.add_node("extract_text", extract_text.extract_text_node)
    workflow.add_node("extract_visual", extract_visual.extract_visual_node)
    workflow.add_node("structure", structure.structure_node)

    # Set entry point
    workflow.set_entry_point("extract_text")

    # Add edges with error handling
    workflow.add_conditional_edges(
        "extract_text", route_after_text_extraction, {"continue": "extract_visual", "failed": END}
    )

    workflow.add_conditional_edges(
        "extract_visual",
        route_after_visual_extraction,
        {"continue": "structure", "failed": END},
    )

    workflow.add_edge("structure", END)

    logger.info("ingestion_workflow_created")
    return workflow.compile()


def route_after_text_extraction(state: IngestionState) -> str:
    """
    Route after text extraction based on status.

    Args:
        state: Current workflow state

    Returns:
        Next node name or "failed"
    """
    status = state.get("status", "")

    if status == "failed":
        logger.warning("text_extraction_failed_routing", brand_id=state["brand_id"])
        return "failed"

    if status == "text_extracted":
        logger.debug("text_extraction_success_routing", brand_id=state["brand_id"])
        return "continue"

    # Default to continue even with warnings
    logger.debug("text_extraction_continue_with_warnings", brand_id=state["brand_id"])
    return "continue"


def route_after_visual_extraction(state: IngestionState) -> str:
    """
    Route after visual extraction based on status.

    Even if visual extraction fails partially, we continue to structuring
    to attempt creating a Brand entity with available data.

    Args:
        state: Current workflow state

    Returns:
        Next node name
    """
    status = state.get("status", "")

    if status == "failed":
        logger.warning("visual_extraction_failed_routing", brand_id=state["brand_id"])
        return "failed"

    # Continue even with partial extraction
    logger.debug("visual_extraction_routing", brand_id=state["brand_id"], status=status)
    return "continue"


async def run_ingestion_workflow(
    brand_id: str,
    organization_id: str,
    brand_name: str,
    pdf_url: str,
) -> IngestionState:
    """
    Execute the brand ingestion workflow.

    Args:
        brand_id: Unique brand identifier
        organization_id: Organization this brand belongs to
        brand_name: Brand name
        pdf_url: URL to the brand guidelines PDF

    Returns:
        Final workflow state with results

    Raises:
        Exception: If workflow execution fails
    """
    logger.info(
        "starting_ingestion_workflow",
        brand_id=brand_id,
        organization_id=organization_id,
        brand_name=brand_name,
    )

    # Initialize state
    initial_state: IngestionState = {
        "brand_id": brand_id,
        "organization_id": organization_id,
        "brand_name": brand_name,
        "pdf_url": pdf_url,
        "extracted_text": None,
        "extracted_colors": [],
        "extracted_fonts": [],
        "extracted_rules": [],
        "needs_review": [],
        "status": "uploading",
    }

    try:
        # Create and run workflow
        workflow = create_ingestion_workflow()
        final_state = await workflow.ainvoke(initial_state)

        logger.info(
            "ingestion_workflow_completed",
            brand_id=brand_id,
            status=final_state.get("status"),
            needs_review_count=len(final_state.get("needs_review", [])),
        )

        return final_state

    except Exception as e:
        logger.error("ingestion_workflow_failed", brand_id=brand_id, error=str(e))
        raise
