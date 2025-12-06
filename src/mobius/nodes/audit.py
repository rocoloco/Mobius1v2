"""
Audit Node Module

This module implements the audit node for the generation workflow.
It acts as the "Compliance Officer," using Gemini to strictly evaluate 
generated assets against brand guidelines and specific hex codes.
"""

import json
from typing import Dict, Any, List

import structlog
import google.generativeai as genai

# Internal imports based on your Project Structure (Week 1)
from mobius.models.state import JobState
from mobius.models.compliance import ComplianceScore, CategoryScore, Violation
from mobius.config import settings
from mobius.constants import CATEGORY_WEIGHTS
from mobius.tools.gemini import GeminiClient

logger = structlog.get_logger()

def calculate_overall_score(categories: List[CategoryScore]) -> float:
    """
    Calculate weighted average compliance score from category scores.
    
    Uses CATEGORY_WEIGHTS to compute a weighted average. Categories not in
    CATEGORY_WEIGHTS are assigned equal weight from remaining allocation.
    """
    if not categories:
        return 0.0
    
    total_score = 0.0
    total_weight = 0.0
    
    for cat in categories:
        # Default weight is 0.25 if not specified in constants
        weight = CATEGORY_WEIGHTS.get(cat.category, 0.25)
        total_score += cat.score * weight
        total_weight += weight
    
    # Normalize if weights don't sum to 1.0
    if total_weight > 0:
        return total_score / total_weight
    
    return 0.0

async def audit_node(state: JobState) -> Dict[str, Any]:
    """
    Audit image for brand compliance with detailed category scoring.
    
    This node acts as a 'Bad Cop', strictly enforcing brand rules.
    It uses Gemini with a JSON schema to ensure structured output.
    """
    logger.info("audit_node_start", job_id=state.get("job_id"))
    
    # 1. Setup Gemini with strict JSON enforcement
    client = GeminiClient()
    
    # Define the schema for strict typing (Native JSON mode)
    compliance_schema = genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "categories": genai.protos.Schema(
                type=genai.protos.Type.ARRAY,
                items=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "category": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "score": genai.protos.Schema(type=genai.protos.Type.NUMBER),
                        "passed": genai.protos.Schema(type=genai.protos.Type.BOOLEAN),
                        "violations": genai.protos.Schema(
                            type=genai.protos.Type.ARRAY,
                            items=genai.protos.Schema(
                                type=genai.protos.Type.OBJECT,
                                properties={
                                    "category": genai.protos.Schema(type=genai.protos.Type.STRING),
                                    "description": genai.protos.Schema(type=genai.protos.Type.STRING),
                                    "severity": genai.protos.Schema(type=genai.protos.Type.STRING),
                                    "fix_suggestion": genai.protos.Schema(type=genai.protos.Type.STRING)
                                }
                            )
                        )
                    }
                )
            ),
            "summary": genai.protos.Schema(type=genai.protos.Type.STRING)
        }
    )

    try:
        # 2. The "Bad Cop" Prompt
        # Explicitly treats the LLM as a Compliance Officer to reduce leniency.
        prompt = f"""
        You are a strict Brand Compliance Officer. Your job is to REJECT content that violates guidelines.
        Do not be lenient. If a rule is slightly broken, mark it as a violation.

        BRAND GUIDELINES:
        {state.get('brand_rules', 'No strict rules provided.')}

        STRICT HEX CODE ENFORCEMENT:
        Allowed Colors: {', '.join(state.get('brand_hex_codes', []))}
        * If the image uses colors outside this palette (except for natural lighting/photos), penalize the Color score.
        
        REQUIRED TASKS:
        1. Analyze 'Colors': precise hex matching.
        2. Analyze 'Typography': font style and weight usage.
        3. Analyze 'Logo': clear space, non-distorted, correct placement.
        
        CRITICAL: For every violation, provide:
        - category: the category name (colors, typography, logo, etc.)
        - severity: one of "low", "medium", "high", or "critical" (lowercase only)
        - description: detailed explanation of the violation
        - fix_suggestion: an INSTRUCTION for an AI generator
        
        Example violation:
        {{
            "category": "colors",
            "severity": "high",
            "description": "Background uses #FF0000 which is not in brand palette",
            "fix_suggestion": "Change the background to brand hex #0057B8"
        }}
        """

        # 3. Call Gemini
        # We use temperature=0.0 for maximum determinism
        response = await client.model.generate_content_async(
            contents=[prompt, state["current_image_url"]],
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
                response_mime_type="application/json", 
                response_schema=compliance_schema
            )
        )
        
        # 4. Parse Result
        raw_result = json.loads(response.text)
        
        # Map raw result to internal Pydantic models
        categories = []
        for cat in raw_result.get("categories", []):
             categories.append(CategoryScore(
                 category=cat.get("category", "unknown"),
                 score=cat.get("score", 0),
                 passed=cat.get("score", 0) > 70, # Internal threshold for category pass
                 violations=[Violation(**v) for v in cat.get("violations", [])]
             ))

        # Recalculate overall score (Python Logic > LLM Math)
        final_score = calculate_overall_score(categories)
        
        # Determine approval based on global settings
        threshold_percentage = settings.compliance_threshold * 100
        is_approved = final_score >= threshold_percentage

        compliance = ComplianceScore(
            overall_score=final_score,
            categories=categories,
            approved=is_approved,
            summary=raw_result.get("summary", "Audit completed.")
        )

        logger.info(
            "audit_complete", 
            job_id=state.get("job_id"), 
            score=final_score, 
            approved=is_approved
        )

        return {
            "audit_history": state.get("audit_history", []) + [compliance.model_dump()],
            "compliance_scores": state.get("compliance_scores", []) + [compliance.model_dump()],
            "is_approved": is_approved,
            "status": "audited"
        }

    except Exception as e:
        logger.error("audit_failed", job_id=state.get("job_id"), error=str(e))
        
        # Fail-safe: Return a rejected state so the loop doesn't hang
        error_compliance = ComplianceScore(
            overall_score=0.0,
            categories=[],
            approved=False,
            summary=f"Audit failed due to system error: {str(e)}"
        )
        
        return {
            "audit_history": state.get("audit_history", []) + [error_compliance.model_dump()],
            "is_approved": False,
            "status": "audit_error"
        }