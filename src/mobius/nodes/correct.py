"""
Correction Node Module

This module implements the correction node for the generation workflow.
It applies fixes from audit feedback to improve the prompt for the next
generation attempt.
"""

from typing import Dict, Any
import structlog

from mobius.models.state import JobState

logger = structlog.get_logger()


async def correct_node(state: JobState) -> Dict[str, Any]:
    """
    Apply corrections from audit feedback to the prompt.
    
    This node examines the most recent audit result and applies any
    suggested fixes to the prompt for the next generation attempt.
    If no specific fix is suggested, the original prompt is retained.
    
    Args:
        state: Current job state with audit history
        
    Returns:
        Updated state dict with:
        - prompt: Enhanced prompt with correction applied (if available)
        - status: Updated to "correcting"
        
    Note:
        This node does not increment attempt_count - that happens in generate_node
    """
    logger.info(
        "correct_node_start",
        job_id=state.get("job_id"),
        attempt_count=state.get("attempt_count", 0)
    )
    
    # Check if we have audit history
    audit_history = state.get("audit_history", [])
    if not audit_history:
        logger.warning(
            "no_audit_history",
            job_id=state.get("job_id")
        )
        return {
            "status": "correcting"
        }
    
    # Get the most recent audit result
    last_audit = audit_history[-1]
    
    # Extract fix suggestion from audit
    # The audit result structure includes a summary field that may contain suggestions
    fix_suggestion = None
    
    # Try to extract fix suggestion from summary
    summary = last_audit.get("summary", "")
    if summary and "suggest" in summary.lower():
        fix_suggestion = summary
    
    # Check if there are specific violations with suggestions
    categories = last_audit.get("categories", [])
    violation_suggestions = []
    for category in categories:
        violations = category.get("violations", [])
        for violation in violations:
            if violation:
                violation_suggestions.append(violation)
    
    if violation_suggestions:
        fix_suggestion = " ".join(violation_suggestions[:3])  # Use top 3 violations
    
    # Apply correction if we have a fix suggestion
    if fix_suggestion and fix_suggestion.lower() not in ["null", "none", ""]:
        original_prompt = state["prompt"]
        enhanced_prompt = f"{original_prompt}. IMPORTANT CORRECTION: {fix_suggestion}"
        
        logger.info(
            "applying_correction",
            job_id=state.get("job_id"),
            fix_suggestion=fix_suggestion[:100],
            original_prompt_length=len(original_prompt),
            enhanced_prompt_length=len(enhanced_prompt)
        )
        
        return {
            "prompt": enhanced_prompt,
            "status": "correcting"
        }
    else:
        logger.info(
            "no_correction_needed",
            job_id=state.get("job_id"),
            message="No specific fix suggested, retrying with original prompt"
        )
        
        return {
            "status": "correcting"
        }
