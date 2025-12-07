"""
Audit Node Module

This module implements the audit node for the generation workflow.
It acts as the "Compliance Officer," using Gemini to strictly evaluate 
generated assets against brand guidelines and specific hex codes.
"""

from typing import Dict, Any, List

import structlog
import time

# Internal imports based on your Project Structure (Week 1)
from mobius.models.state import JobState
from mobius.models.compliance import ComplianceScore, CategoryScore
from mobius.tools.gemini import GeminiClient
from mobius.storage.brands import BrandStorage
from mobius.constants import CATEGORY_WEIGHTS

logger = structlog.get_logger()


def calculate_overall_score(categories: List[CategoryScore]) -> float:
    """
    Calculate weighted average compliance score from category scores.
    
    Uses CATEGORY_WEIGHTS to compute a weighted average. Categories not in
    CATEGORY_WEIGHTS are assigned equal weight from remaining allocation.
    
    Note: This function is kept for backward compatibility with tests.
    The GeminiClient.audit_compliance method now handles score calculation internally.
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
    Audit image for brand compliance using Reasoning Model with multimodal vision.
    
    This node uses the GeminiClient.audit_compliance method which:
    - Uses the Reasoning Model explicitly for superior reasoning capabilities
    - Accepts image_uri for multimodal input (no download needed in this node)
    - Uses full BrandGuidelines for comprehensive compliance checking
    
    Requirements: 4.1, 4.2, 4.3, 4.4
    """
    operation_type = "audit_node"
    start_time = time.time()
    
    logger.info(
        "audit_node_start",
        job_id=state.get("job_id"),
        operation_type=operation_type
    )
    
    try:
        # 1. Get image_uri from state (passed from generation node)
        image_uri = state.get("current_image_url")
        if not image_uri:
            raise ValueError("No image_uri found in state")
        
        # 2. Load full brand guidelines from database
        brand_id = state.get("brand_id")
        if not brand_id:
            raise ValueError("No brand_id found in state")
        
        brand_storage = BrandStorage()
        brand = await brand_storage.get_brand(brand_id)
        if not brand:
            raise ValueError(f"Brand not found: {brand_id}")
        
        if not brand.guidelines:
            raise ValueError(f"Brand guidelines not found for brand: {brand_id}")
        
        # 3. Use GeminiClient.audit_compliance with Reasoning Model
        # This method:
        # - Uses reasoning_model explicitly (Requirement 4.1, 6.4)
        # - Accepts image_uri as multimodal input (Requirement 4.2)
        # - Uses full BrandGuidelines for comprehensive auditing (Requirement 4.3)
        # - Returns structured ComplianceScore (Requirement 4.4)
        client = GeminiClient()
        compliance = await client.audit_compliance(
            image_uri=image_uri,
            brand_guidelines=brand.guidelines
        )

        latency_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "audit_complete", 
            job_id=state.get("job_id"), 
            score=compliance.overall_score, 
            approved=compliance.approved,
            operation_type=operation_type,
            latency_ms=latency_ms
        )

        return {
            "audit_history": state.get("audit_history", []) + [compliance.model_dump()],
            "compliance_scores": state.get("compliance_scores", []) + [compliance.model_dump()],
            "is_approved": compliance.approved,
            "status": "audited"
        }

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        
        logger.error(
            "audit_failed",
            job_id=state.get("job_id"),
            error=str(e),
            operation_type=operation_type,
            latency_ms=latency_ms
        )
        
        # Graceful degradation: Return partial compliance score with error annotations
        # (Requirement 9.5)
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