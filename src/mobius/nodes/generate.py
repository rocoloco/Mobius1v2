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
from mobius.utils.media import LogoRasterizer

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
            logger.warning(
                "compressed_twin_missing_creating_fallback",
                job_id=state.get("job_id"),
                brand_id=state["brand_id"],
                operation_type=operation_type
            )
            # Create a basic compressed twin from the full guidelines
            from mobius.models.brand import CompressedDigitalTwin
            
            compressed_twin = CompressedDigitalTwin(
                primary_colors=[c.hex for c in brand.guidelines.colors if c.usage == "primary"],
                secondary_colors=[c.hex for c in brand.guidelines.colors if c.usage == "secondary"],
                accent_colors=[c.hex for c in brand.guidelines.colors if c.usage == "accent"],
                neutral_colors=[c.hex for c in brand.guidelines.colors if c.usage == "neutral"],
                semantic_colors=[c.hex for c in brand.guidelines.colors if c.usage == "semantic"],
                font_families=[t.family for t in brand.guidelines.typography],
                visual_dos=[r.instruction for r in brand.guidelines.rules if r.category == "visual" and not r.negative_constraint][:20],
                visual_donts=[r.instruction for r in brand.guidelines.rules if r.category == "visual" and r.negative_constraint][:20],
            )
            brand.compressed_twin = compressed_twin
            
            logger.info(
                "fallback_compressed_twin_created",
                job_id=state.get("job_id"),
                brand_id=state["brand_id"],
                primary_colors=len(compressed_twin.primary_colors),
                secondary_colors=len(compressed_twin.secondary_colors),
                accent_colors=len(compressed_twin.accent_colors),
                operation_type=operation_type
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

        # Fetch brand logos from storage if available
        logo_bytes_list = []
        if brand.guidelines and brand.guidelines.logos:
            logger.info(
                "fetching_brand_logos",
                job_id=state.get("job_id"),
                logo_count=len(brand.guidelines.logos),
                operation_type=operation_type
            )

            import httpx

            for logo in brand.guidelines.logos:
                try:
                    # Download logo from public URL
                    # The logo.url is a Supabase Storage public URL
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.get(logo.url)
                        response.raise_for_status()
                        logo_data = response.content
                        
                        # Extract MIME type from response headers
                        mime_type = response.headers.get('content-type', 'image/png')

                    # Process logo for Vision Model (rasterize SVG or upscale low-res)
                    original_size = len(logo_data)
                    processed_logo = LogoRasterizer.prepare_for_vision(
                        logo_bytes=logo_data,
                        mime_type=mime_type
                    )
                    processed_size = len(processed_logo)
                    
                    # Validate that processed logo is readable before adding to list
                    # This prevents corrupted logos from breaking generation
                    try:
                        from PIL import Image
                        import io
                        test_img = Image.open(io.BytesIO(processed_logo))
                        test_img.verify()
                        
                        logo_bytes_list.append(processed_logo)
                        
                        logger.info(
                            "logo_processed",
                            job_id=state.get("job_id"),
                            logo_variant=logo.variant_name,
                            mime_type=mime_type,
                            original_size_bytes=original_size,
                            processed_size_bytes=processed_size,
                            operation_type=operation_type
                        )
                    except Exception as validation_error:
                        logger.error(
                            "logo_validation_failed_after_processing",
                            job_id=state.get("job_id"),
                            logo_variant=logo.variant_name,
                            mime_type=mime_type,
                            error=str(validation_error),
                            solution="Skipping corrupted logo - re-ingest brand with valid logo file",
                            operation_type=operation_type
                        )
                except Exception as e:
                    logger.warning(
                        "logo_download_failed",
                        job_id=state.get("job_id"),
                        logo_url=logo.url,
                        error=str(e),
                        operation_type=operation_type
                    )

        # Store original prompt for intent detection
        original_prompt = state["prompt"]
        
        # Optimize user prompt with Reasoning Model
        optimized_prompt = await gemini_client.optimize_prompt(
            user_prompt=original_prompt,
            compressed_twin=brand.compressed_twin,
            has_logo=bool(logo_bytes_list)
        )
        
        # Log the optimization result for visibility
        logger.info(
            "prompt_optimization_complete",
            job_id=state.get("job_id"),
            original_prompt=original_prompt,
            optimized_prompt=optimized_prompt,
            operation_type=operation_type
        )

        # Generate image with Vision Model (with logos if available)
        image_uri = await gemini_client.generate_image(
            prompt=optimized_prompt,
            compressed_twin=brand.compressed_twin,
            logo_bytes=logo_bytes_list if logo_bytes_list else None,
            original_prompt=original_prompt,  # Pass original for text intent detection
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
