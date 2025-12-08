"""
Generation workflow with enhanced compliance scoring.

This module defines the LangGraph workflow for asset generation with
automatic compliance auditing and correction loops.
"""

from typing import Literal, Optional
import uuid
import structlog
from datetime import datetime

from langgraph.graph import StateGraph, END

from mobius.models.state import JobState
from mobius.nodes.generate import generate_node
from mobius.nodes.audit import audit_node
from mobius.nodes.correct import correct_node
from mobius.constants import DEFAULT_MAX_ATTEMPTS, DEFAULT_COMPLIANCE_THRESHOLD
from mobius.config import settings
from datetime import timezone

logger = structlog.get_logger()


def needs_review_node(state: JobState) -> dict:
    """
    Terminal node that pauses workflow for user review.

    This node is reached when the compliance score is between 70-95%.
    The workflow pauses here and waits for user decision via the review API endpoint.

    Args:
        state: Current job state

    Returns:
        Updated state dict with needs_review flag set
    """
    logger.info(
        "needs_review_node",
        job_id=state.get("job_id"),
        current_score=state.get("compliance_scores", [])[-1].get("overall_score") if state.get("compliance_scores") else None
    )

    return {
        "status": "needs_review",
        "needs_review": True,
        "review_requested_at": datetime.now(timezone.utc).isoformat()
    }


def complete_node(state: JobState) -> dict:
    """
    Terminal node for successful completion.

    Cleans up session and marks job as completed.

    Args:
        state: Current job state

    Returns:
        Updated state dict with completed status
    """
    from mobius.tools.gemini import GeminiClient

    job_id = state.get("job_id")
    session_id = state.get("session_id")

    # Clean up session if exists
    if session_id:
        try:
            gemini_client = GeminiClient()
            gemini_client.clear_session(job_id)

            logger.info(
                "session_cleaned_on_completion",
                job_id=job_id,
                session_id=session_id
            )
        except Exception as e:
            logger.warning(
                "session_cleanup_failed",
                job_id=job_id,
                error=str(e)
            )

    logger.info(
        "job_completed",
        job_id=job_id,
        approval_override=state.get("approval_override", False)
    )

    return {
        "status": "completed",
        "session_id": None
    }


def failed_node(state: JobState) -> dict:
    """
    Terminal node for failed jobs.

    Cleans up session and marks job as failed.

    Args:
        state: Current job state

    Returns:
        Updated state dict with failed status
    """
    from mobius.tools.gemini import GeminiClient

    job_id = state.get("job_id")
    session_id = state.get("session_id")

    # Clean up session if exists
    if session_id:
        try:
            gemini_client = GeminiClient()
            gemini_client.clear_session(job_id)

            logger.info(
                "session_cleaned_on_failure",
                job_id=job_id,
                session_id=session_id
            )
        except Exception as e:
            logger.warning(
                "session_cleanup_failed",
                job_id=job_id,
                error=str(e)
            )

    logger.info(
        "job_failed",
        job_id=job_id,
        attempt_count=state.get("attempt_count", 0)
    )

    return {
        "status": "failed",
        "session_id": None
    }


def route_after_audit(state: JobState) -> Literal["correct", "complete", "failed", "needs_review"]:
    """
    Route workflow after audit based on compliance score and attempt count.

    Routing logic:
    - If user already made a decision (approve/tweak/regenerate): handle accordingly
    - If approved: route to "complete"
    - If score is 70-95%: route to "needs_review" (pause for user decision)
    - If max attempts reached: route to "failed"
    - Otherwise: route to "correct" for another attempt

    Args:
        state: Current job state with audit results

    Returns:
        Next node to execute: "correct", "complete", "failed", or "needs_review"

    Examples:
        >>> state = {"is_approved": True, "attempt_count": 1}
        >>> route_after_audit(state)
        'complete'

        >>> state = {"is_approved": False, "attempt_count": 3}
        >>> route_after_audit(state)
        'failed'

        >>> state = {"is_approved": False, "attempt_count": 1, "compliance_scores": [{"overall_score": 80}]}
        >>> route_after_audit(state)
        'needs_review'
    """
    # Check if user already made a decision (resumed workflow)
    user_decision = state.get("user_decision")
    if user_decision == "approve":
        return "complete"

    # Auto-approve if compliant (check this BEFORE user_decision to allow tweaked images to complete)
    if state.get("is_approved"):
        return "complete"

    # Only route to correct if user requested tweak AND there's still a tweak instruction pending
    # (user_tweak_instruction is cleared after being applied in correct_node)
    if user_decision in ["regenerate", "tweak"] and state.get("user_tweak_instruction"):
        return "correct"

    # Check compliance score and route accordingly
    compliance_scores = state.get("compliance_scores", [])
    if compliance_scores:
        latest_score = compliance_scores[-1]
        overall_score = latest_score.get("overall_score", 0)

        # If score is between 70-95%, pause for user review
        if 70 <= overall_score < 95:
            logger.info(
                "routing_to_needs_review",
                job_id=state.get("job_id"),
                overall_score=overall_score,
                threshold_range="70-95%"
            )
            return "needs_review"
        
        # If score is below 70% on first attempt, pause for user review
        # (Don't auto-correct without user input)
        if overall_score < 70 and state["attempt_count"] == 1:
            logger.info(
                "routing_to_needs_review_low_score",
                job_id=state.get("job_id"),
                overall_score=overall_score,
                reason="First attempt scored below 70%, needs user review"
            )
            return "needs_review"

    # Auto-fail if max attempts reached
    max_attempts = getattr(settings, 'max_generation_attempts', DEFAULT_MAX_ATTEMPTS)
    if state["attempt_count"] >= max_attempts:
        return "failed"

    # Auto-correct if below threshold and attempts remain (only after user decision)
    return "correct"


def create_generation_workflow():
    """
    Create the generation workflow with audit and correction loops.
    
    Workflow structure:
        generate -> audit -> [correct -> generate] (loop) or complete/failed
    
    The workflow uses the new generate_node which:
    - Loads the Compressed Digital Twin from brand storage
    - Uses the Vision Model (gemini-3-pro-image-preview) for generation
    - Returns image_uri for downstream processing
    
    Returns:
        Compiled LangGraph workflow
        
    Requirements: 3.1, 7.2
    """
    logger.info("creating_generation_workflow")
    
    workflow = StateGraph(JobState)

    # Add nodes
    workflow.add_node("generate", generate_node)
    workflow.add_node("audit", audit_node)
    workflow.add_node("correct", correct_node)
    workflow.add_node("needs_review", needs_review_node)
    workflow.add_node("complete", complete_node)
    workflow.add_node("failed", failed_node)

    # Set entry point
    workflow.set_entry_point("generate")

    # Add edges
    workflow.add_edge("generate", "audit")

    # Add conditional routing after audit
    workflow.add_conditional_edges(
        "audit",
        route_after_audit,
        {
            "correct": "correct",
            "complete": "complete",  # Route to cleanup node
            "failed": "failed",  # Route to cleanup node
            "needs_review": "needs_review"  # Pause for user review
        }
    )

    # Correction loop back to generation
    workflow.add_edge("correct", "generate")

    # Terminal nodes route to END after cleanup
    workflow.add_edge("complete", END)
    workflow.add_edge("failed", END)
    # needs_review is also a terminal node (pauses workflow, waits for API call to resume)
    
    logger.info("generation_workflow_created")
    return workflow.compile()



async def run_generation_workflow(
    brand_id: str,
    prompt: str,
    job_id: Optional[str] = None,
    webhook_url: Optional[str] = None,
    template_id: Optional[str] = None,
    **generation_params,
) -> dict:
    """
    Execute the generation workflow for a brand.

    This function creates and executes the LangGraph workflow that:
    1. Generates an image using the Vision Model with Compressed Digital Twin
    2. Audits the image using the Reasoning Model
    3. Applies corrections and retries if needed (up to max_attempts)

    Args:
        brand_id: Brand ID to generate for
        prompt: Generation prompt
        job_id: Optional job ID to use (will generate UUID if not provided)
        webhook_url: Optional webhook URL for completion notification
        template_id: Optional template ID to use
        **generation_params: Additional generation parameters

    Returns:
        Dictionary with workflow results including:
        - job_id: Unique job identifier
        - status: Job status (completed, failed, etc.)
        - current_image_url: URL of generated image (image_uri)
        - is_approved: Whether asset passed compliance
        - compliance_scores: List of compliance score dictionaries
        - attempt_count: Number of generation attempts made

    Requirements: 3.1, 7.2
    """
    if not job_id:
        job_id = str(uuid.uuid4())
    
    logger.info(
        "generation_workflow_started",
        job_id=job_id,
        brand_id=brand_id,
        prompt=prompt,
        template_id=template_id,
    )
    
    # Initialize state
    initial_state: JobState = {
        "job_id": job_id,
        "brand_id": brand_id,
        "prompt": prompt,
        "brand_hex_codes": [],  # Will be loaded from brand in generate_node
        "brand_rules": "",  # Will be loaded from brand in audit_node
        "current_image_url": None,
        "attempt_count": 0,
        "audit_history": [],
        "compliance_scores": [],
        "is_approved": False,
        "status": "pending",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "webhook_url": webhook_url,
        "template_id": template_id,
        "generation_params": generation_params,
    }
    
    try:
        # Create and run workflow
        workflow = create_generation_workflow()
        final_state = await workflow.ainvoke(initial_state)
        
        # Determine final status
        if final_state.get("is_approved"):
            status = "completed"
        elif final_state.get("attempt_count", 0) >= getattr(settings, 'max_generation_attempts', DEFAULT_MAX_ATTEMPTS):
            status = "failed"
        else:
            status = final_state.get("status", "unknown")
        
        result = {
            "job_id": job_id,
            "brand_id": brand_id,
            "status": status,
            "current_image_url": final_state.get("current_image_url"),
            "is_approved": final_state.get("is_approved", False),
            "compliance_scores": final_state.get("compliance_scores", []),
            "attempt_count": final_state.get("attempt_count", 0),
            "prompt": final_state.get("prompt", prompt),
            "template_id": template_id,
            "generation_params": generation_params,
        }
        
        logger.info(
            "generation_workflow_completed",
            job_id=job_id,
            status=result["status"],
            is_approved=result["is_approved"],
            attempt_count=result["attempt_count"],
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "generation_workflow_failed",
            job_id=job_id,
            brand_id=brand_id,
            error=str(e)
        )
        
        # Return error result
        return {
            "job_id": job_id,
            "brand_id": brand_id,
            "status": "failed",
            "current_image_url": None,
            "is_approved": False,
            "compliance_scores": [],
            "attempt_count": 0,
            "prompt": prompt,
            "template_id": template_id,
            "generation_params": generation_params,
            "error": str(e),
        }
