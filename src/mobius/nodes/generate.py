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
    
    # Validate required fields
    brand_id = state.get("brand_id")
    if not brand_id:
        logger.error(
            "generate_node_missing_brand_id",
            job_id=state.get("job_id"),
            state_keys=list(state.keys()),
            operation_type=operation_type
        )
        raise ValueError("brand_id is required in state but was not found")
    
    logger.info(
        "generate_node_start",
        job_id=state.get("job_id"),
        brand_id=brand_id,
        attempt_count=state.get("attempt_count", 0),
        operation_type=operation_type
    )
    
    try:
        # Initialize clients
        gemini_client = GeminiClient()
        brand_storage = BrandStorage()
        
        # Load brand with compressed twin
        brand = await brand_storage.get_brand(brand_id)
        
        if not brand:
            logger.error(
                "brand_not_found",
                job_id=state.get("job_id"),
                brand_id=brand_id,
                operation_type=operation_type
            )
            raise ValueError(f"Brand {brand_id} not found")
        
        if not brand.compressed_twin:
            logger.warning(
                "compressed_twin_missing_creating_fallback",
                job_id=state.get("job_id"),
                brand_id=brand_id,
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
                brand_id=brand_id,
                primary_colors=len(compressed_twin.primary_colors),
                secondary_colors=len(compressed_twin.secondary_colors),
                accent_colors=len(compressed_twin.accent_colors),
                operation_type=operation_type
            )
        
        logger.info(
            "compressed_twin_loaded",
            job_id=state.get("job_id"),
            brand_id=brand_id,
            token_estimate=brand.compressed_twin.estimate_tokens(),
            primary_colors=len(brand.compressed_twin.primary_colors),
            secondary_colors=len(brand.compressed_twin.secondary_colors),
            accent_colors=len(brand.compressed_twin.accent_colors),
            operation_type=operation_type
        )
        
        # Extract generation parameters from state
        generation_params = state.get("generation_params", {})
        
        # Remove 'prompt' from generation_params if it exists to avoid conflicts
        # (prompt is passed explicitly as optimized_prompt)
        generation_params = {k: v for k, v in generation_params.items() if k != "prompt"}

        # Determine if we need logos for this generation
        # Use smart strategy: always fetch on first attempt, conditionally on corrections
        current_attempt = state.get("attempt_count", 0) + 1
        continue_conversation = current_attempt > 1
        
        # Check if this is a tweak with a previous image
        previous_image_url = state.get("current_image_url")
        is_tweak = continue_conversation and previous_image_url
        
        if is_tweak:
            logger.info(
                "tweak_with_previous_image",
                job_id=state.get("job_id"),
                has_previous_image=bool(previous_image_url),
                previous_image_url=previous_image_url[:100] if previous_image_url else None,
                operation_type=operation_type
            )

        # Smart logo strategy
        needs_logos = False
        if not continue_conversation:
            # Always fetch logos on first attempt
            needs_logos = True
        elif state.get("user_tweak_instruction"):
            # Check if user's instruction mentions logo
            instruction = state["user_tweak_instruction"].lower()
            logo_keywords = ['logo', 'brand mark', 'icon', 'symbol', 'emblem']
            needs_logos = any(kw in instruction for kw in logo_keywords)

            if needs_logos:
                logger.info(
                    "logo_mentioned_in_correction",
                    job_id=state.get("job_id"),
                    instruction=state["user_tweak_instruction"],
                    operation_type=operation_type
                )

        # Fetch brand logos from storage if needed
        logo_bytes_list = []
        if needs_logos and brand.guidelines and brand.guidelines.logos:
            logger.info(
                "fetching_brand_logos",
                job_id=state.get("job_id"),
                logo_count=len(brand.guidelines.logos),
                is_correction=continue_conversation,
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

        # Multi-turn conversation determined above in smart logo strategy
        job_id = state.get("job_id")
        
        # Fetch previous image bytes if this is a tweak
        previous_image_bytes = None
        if is_tweak and previous_image_url:
            try:
                import httpx
                import base64
                
                # Handle data URI (base64 encoded image)
                if previous_image_url.startswith("data:image"):
                    # Extract base64 data from data URI
                    # Format: data:image/jpeg;base64,<base64_data>
                    base64_data = previous_image_url.split(",", 1)[1]
                    previous_image_bytes = base64.b64decode(base64_data)
                    logger.info(
                        "previous_image_decoded_from_data_uri",
                        job_id=job_id,
                        image_size_bytes=len(previous_image_bytes),
                        operation_type=operation_type
                    )
                else:
                    # Fetch from URL
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.get(previous_image_url)
                        response.raise_for_status()
                        previous_image_bytes = response.content
                    logger.info(
                        "previous_image_fetched",
                        job_id=job_id,
                        image_size_bytes=len(previous_image_bytes),
                        operation_type=operation_type
                    )
            except Exception as e:
                logger.warning(
                    "previous_image_fetch_failed",
                    job_id=job_id,
                    error=str(e),
                    operation_type=operation_type
                )
                # Continue without previous image - will generate new one

        # Generate image with Vision Model (with logos if available)
        result = await gemini_client.generate_image(
            prompt=optimized_prompt,
            compressed_twin=brand.compressed_twin,
            logo_bytes=logo_bytes_list if logo_bytes_list else None,
            original_prompt=original_prompt,  # Pass original for text intent detection
            job_id=job_id,
            continue_conversation=continue_conversation,
            previous_image_bytes=previous_image_bytes,  # Pass previous image for tweaks
            **generation_params
        )

        # Extract image_uri and session_id from result
        image_uri = result["image_uri"]
        session_id = result.get("session_id")
        
        # Upload image to Supabase Storage (convert base64 to CDN URL)
        # This reduces database size and improves performance
        stored_image_url = image_uri  # Default to original if upload fails
        if image_uri and image_uri.startswith("data:image"):
            try:
                from mobius.storage.files import FileStorage
                file_storage = FileStorage()
                stored_image_url = await file_storage.upload_generated_image(
                    image_data_uri=image_uri,
                    job_id=job_id,
                    attempt=current_attempt
                )
                logger.info(
                    "image_stored_to_supabase",
                    job_id=job_id,
                    original_size=len(image_uri),
                    stored_url=stored_image_url[:100] if stored_image_url else None,
                    operation_type=operation_type
                )
            except Exception as storage_error:
                logger.warning(
                    "image_storage_failed_using_base64",
                    job_id=job_id,
                    error=str(storage_error),
                    operation_type=operation_type
                )
                # Fall back to base64 if storage fails
                stored_image_url = image_uri

        latency_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "image_generated",
            job_id=job_id,
            brand_id=brand_id,
            image_uri=stored_image_url[:100] if stored_image_url else None,
            attempt_count=current_attempt,
            continue_conversation=continue_conversation,
            session_id=session_id,
            operation_type=operation_type,
            latency_ms=latency_ms
        )

        # Return updated state with stored URL (CDN URL instead of base64)
        return {
            "current_image_url": stored_image_url,
            "attempt_count": current_attempt,
            "session_id": session_id,
            "status": "generated"
        }
        
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        
        logger.error(
            "generate_node_failed",
            job_id=state.get("job_id"),
            brand_id=brand_id,
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
