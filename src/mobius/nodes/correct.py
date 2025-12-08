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
    
    # Check if user provided a custom tweak instruction FIRST
    # This takes priority over audit-based corrections
    user_instruction = state.get("user_tweak_instruction")

    if user_instruction:
        # Use user's custom instruction for targeted editing
        correction_prompt = (
            f"Looking at the image you just generated in our previous conversation, "
            f"please make this specific modification: {user_instruction}. "
            f"\n\nIMPORTANT: Edit the existing image, do not create a new one from scratch. "
            f"Keep all elements that are working well (composition, layout, colors, positioning) "
            f"and only change what I've requested."
        )

        logger.info(
            "applying_user_tweak",
            job_id=state.get("job_id"),
            user_instruction=user_instruction,
            correction_prompt=correction_prompt
        )

        return {
            "prompt": correction_prompt,
            "user_tweak_instruction": None,  # Clear after use
            "status": "correcting"
        }

    # Check if we have audit history for AI-based corrections
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
    violation_severities = []

    for category in categories:
        violations = category.get("violations", [])
        for violation in violations:
            if violation and isinstance(violation, dict):
                # Extract the fix_suggestion from the violation dict
                fix_text = violation.get("fix_suggestion") or violation.get("description")
                severity = violation.get("severity", "medium")
                if fix_text:
                    violation_suggestions.append(fix_text)
                    violation_severities.append(severity)

    if violation_suggestions:
        # Prioritize high/critical violations
        prioritized_suggestions = []
        for suggestion, severity in zip(violation_suggestions, violation_severities):
            if severity in ["high", "critical"]:
                prioritized_suggestions.insert(0, suggestion)
            else:
                prioritized_suggestions.append(suggestion)

        fix_suggestion = " ".join(prioritized_suggestions[:3])  # Use top 3 violations

    # Apply correction if we have a fix suggestion
    if fix_suggestion and fix_suggestion.lower() not in ["null", "none", ""]:
        # Build list of critical/high violations for explicit instructions
        fix_instructions = []
        for suggestion, severity in zip(violation_suggestions, violation_severities):
            if severity in ["critical", "high"]:
                fix_instructions.append(f"- {suggestion}")

        # Create targeted edit prompt for multi-turn conversation
        if fix_instructions:
            correction_prompt = (
                f"Looking at the image you just generated in our previous conversation, "
                f"please make these specific changes:\n"
                f"{chr(10).join(fix_instructions)}\n\n"
                f"IMPORTANT: Edit the existing image, do not create a new one from scratch. "
                f"Preserve all elements that are brand-compliant and only fix the violations listed above."
            )
        else:
            # Fallback for general suggestions
            correction_prompt = (
                f"Looking at the image you just generated in our previous conversation, "
                f"please modify it: {fix_suggestion}. "
                f"\n\nIMPORTANT: Edit the existing image, do not create a new one from scratch. "
                f"Preserve all elements that are working well."
            )

        logger.info(
            "applying_ai_correction",
            job_id=state.get("job_id"),
            fix_suggestion=fix_suggestion,
            correction_prompt=correction_prompt,
            violation_count=len(violation_suggestions)
        )

        return {
            "prompt": correction_prompt,
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
