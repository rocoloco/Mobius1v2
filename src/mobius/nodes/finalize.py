"""
Finalize Node Module

This module implements the finalize node for the generation workflow.
It handles final tasks after successful generation and audit:
- Upload image to Supabase Storage for permanent storage
- Update job with final status and CDN URLs
- Clean up temporary data
"""

from typing import Dict, Any
import structlog
import time

from mobius.models.state import JobState

logger = structlog.get_logger()


async def finalize_node(state: JobState) -> Dict[str, Any]:
    """
    Finalize the generation workflow after successful audit.
    
    This node:
    1. Uploads the base64 image to Supabase Storage for permanent storage
    2. Updates the job with the final CDN URL
    3. Cleans up any temporary data
    
    Args:
        state: Current job state with generated image and audit results
        
    Returns:
        Updated state dict with final image URL and completion status
    """
    operation_type = "finalize_node"
    start_time = time.time()
    job_id = state.get("job_id")
    
    logger.info(
        "finalize_node_start",
        job_id=job_id,
        operation_type=operation_type
    )
    
    try:
        # Get the base64 image from state
        image_uri = state.get("current_image_url")
        if not image_uri or not image_uri.startswith("data:image"):
            # Image already uploaded or not base64 - nothing to do
            logger.info(
                "finalize_skipped_no_base64_image",
                job_id=job_id,
                image_type=image_uri.split(':')[0] if image_uri else "none",
                operation_type=operation_type
            )
            return {"status": "finalized"}
        
        # Upload image to Supabase Storage for permanent storage
        from mobius.storage.files import FileStorage
        file_storage = FileStorage()
        
        attempt_count = state.get("attempt_count", 1)
        
        logger.info(
            "uploading_final_image_to_storage",
            job_id=job_id,
            image_size_bytes=len(image_uri),
            attempt=attempt_count,
            operation_type=operation_type
        )
        
        stored_image_url = await file_storage.upload_generated_image(
            image_data_uri=image_uri,
            job_id=job_id,
            attempt=attempt_count
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "final_image_uploaded",
            job_id=job_id,
            stored_url=stored_image_url[:100] if stored_image_url else None,
            original_size=len(image_uri),
            operation_type=operation_type,
            latency_ms=latency_ms
        )
        
        # Return updated state with CDN URL
        return {
            "current_image_url": stored_image_url,
            "status": "finalized",
            "original_had_logos": state.get("original_had_logos", False)  # Preserve logo config
        }
        
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        
        logger.error(
            "finalize_failed",
            job_id=job_id,
            error=str(e),
            operation_type=operation_type,
            latency_ms=latency_ms
        )
        
        # Don't fail the entire workflow if upload fails
        # Keep the base64 image as fallback
        logger.warning(
            "keeping_base64_image_as_fallback",
            job_id=job_id,
            operation_type=operation_type
        )
        
        return {
            "status": "finalized_with_fallback",
            "finalize_error": str(e),
            "original_had_logos": state.get("original_had_logos", False)  # Preserve logo config
        }