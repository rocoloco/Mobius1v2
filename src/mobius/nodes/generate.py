"""
Generation Node Module

This module implements the generation node for the generation workflow.
It uses the Vision Model to generate brand-compliant images with the
Compressed Digital Twin injected into the system prompt.
"""

from typing import Dict, Any
import structlog
import time

from mobius.models.state import JobState
from mobius.tools.gemini import GeminiClient
from mobius.storage.brands import BrandStorage

logger = structlog.get_logger()


async def generate_node(state: JobState) -> Dict[str, Any]:
    """
    Generate image using Vision Model with compressed brand context.
    
    This node loads the Compressed Digital Twin from brand storage and
    uses it to generate brand-compliant images via the Vision Model.
    The compressed twin is injected into the system prompt to ensure
    the generated image follows brand guidelines.
    
    Args:
        state: Current job state containing brand_id, prompt, and generation params
        
    Returns:
        Updated state dict with:
        - current_image_url: URI of the generated image
        - attempt_count: Incremented attempt counter
        - status: Updated to "generated"
        
    Raises:
        Exception: If brand not found or generation fails
    """
    operation_type = "generate_node"
    start_time = time.time()
    
    logger.info(
        "generate_node_start",
        job_id=state.get("job_id"),
        brand_id=state["brand_id"],
        attempt_count=state.get("attempt_count", 0),
        operation_type=operation_type
    )
    
    try:
        # Initialize clients
        gemini_client = GeminiClient()
        brand_storage = BrandStorage()
        
        # Load brand with compressed twin
        brand = await brand_storage.get_brand(state["brand_id"])
        
        if not brand:
            logger.error(
                "brand_not_found",
                job_id=state.get("job_id"),
                brand_id=state["brand_id"],
                operation_type=operation_type
            )
            raise ValueError(f"Brand {state['brand_id']} not found")
        
        if not brand.compressed_twin:
            logger.error(
                "compressed_twin_missing",
                job_id=state.get("job_id"),
                brand_id=state["brand_id"],
                operation_type=operation_type
            )
            raise ValueError(
                f"Brand {state['brand_id']} has no compressed twin. "
                "Please re-ingest the brand to generate the compressed twin."
            )
        
        logger.info(
            "compressed_twin_loaded",
            job_id=state.get("job_id"),
            brand_id=state["brand_id"],
            token_estimate=brand.compressed_twin.estimate_tokens(),
            primary_colors=len(brand.compressed_twin.primary_colors),
            secondary_colors=len(brand.compressed_twin.secondary_colors),
            accent_colors=len(brand.compressed_twin.accent_colors),
            operation_type=operation_type
        )
        
        # Extract generation parameters from state
        generation_params = state.get("generation_params", {})
        
        # Generate image with Vision Model
        image_uri = await gemini_client.generate_image(
            prompt=state["prompt"],
            compressed_twin=brand.compressed_twin,
            **generation_params
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "image_generated",
            job_id=state.get("job_id"),
            brand_id=state["brand_id"],
            image_uri=image_uri[:100] if image_uri else None,
            attempt_count=state.get("attempt_count", 0) + 1,
            operation_type=operation_type,
            latency_ms=latency_ms
        )
        
        # Return updated state
        return {
            "current_image_url": image_uri,
            "attempt_count": state.get("attempt_count", 0) + 1,
            "status": "generated"
        }
        
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        
        logger.error(
            "generate_node_failed",
            job_id=state.get("job_id"),
            brand_id=state["brand_id"],
            error=str(e),
            attempt_count=state.get("attempt_count", 0),
            operation_type=operation_type,
            latency_ms=latency_ms
        )
        
        # Return error state
        return {
            "status": "generation_error",
            "attempt_count": state.get("attempt_count", 0) + 1,
            "error": str(e)
        }
