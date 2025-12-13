"""
Generation Node Module

This module implements the generation node for the generation workflow.
It uses the Vision Model to generate brand-compliant images with the
Compressed Digital Twin injected into the system prompt.

Enhanced with real-time WebSocket broadcasting for monitoring interfaces.
"""

from typing import Dict, Any, List
import structlog
import time
import asyncio
import httpx

from mobius.models.state import JobState
from mobius.tools.gemini import GeminiClient
from mobius.storage.brands import BrandStorage
from mobius.utils.media import LogoRasterizer
from mobius.models.brand import LogoRule, Brand
from functools import lru_cache
from typing import Optional
from mobius.utils.performance import timer, performance_monitor
from datetime import datetime, timezone

logger = structlog.get_logger()

# Brand cache with TTL (5 minutes)
_brand_cache: Dict[str, tuple[Brand, float]] = {}
_cache_ttl = 300  # 5 minutes

async def get_cached_brand(brand_id: str) -> Optional[Brand]:
    """
    Get brand from cache or database with TTL-based caching.
    
    Reduces database queries for frequently accessed brands during generation.
    Cache expires after 5 minutes to ensure data freshness.
    
    Args:
        brand_id: Brand ID to fetch
        
    Returns:
        Brand object or None if not found
    """
    current_time = time.time()
    
    # Check cache first
    if brand_id in _brand_cache:
        brand, cached_at = _brand_cache[brand_id]
        if current_time - cached_at < _cache_ttl:
            logger.info(
                "brand_cache_hit",
                brand_id=brand_id,
                cache_age_seconds=int(current_time - cached_at),
                operation_type="brand_caching"
            )
            return brand
        else:
            # Cache expired, remove entry
            del _brand_cache[brand_id]
    
    # Fetch from database
    brand_storage = BrandStorage()
    brand = await brand_storage.get_brand(brand_id)
    
    if brand:
        # Cache the result
        _brand_cache[brand_id] = (brand, current_time)
        logger.info(
            "brand_cached",
            brand_id=brand_id,
            cache_size=len(_brand_cache),
            operation_type="brand_caching"
        )
    
    return brand


async def fetch_and_process_logos_parallel(
    logos: List[LogoRule],
    job_id: str,
    operation_type: str
) -> List[bytes]:
    """
    Fetch and process brand logos in parallel for significant performance improvement.
    
    This replaces the sequential logo processing with parallel downloads and processing,
    reducing logo processing time from ~2-3 seconds to ~0.5-1 second for multiple logos.
    
    Args:
        logos: List of logo rules to process
        job_id: Job ID for logging
        operation_type: Operation type for logging
        
    Returns:
        List of processed logo bytes (successful ones only)
    """
    if not logos:
        return []
    
    # Create shared HTTP client for connection pooling
    async with httpx.AsyncClient(
        timeout=60.0,  # Increased to 60 seconds for logo downloads
        limits=httpx.Limits(max_connections=5, max_keepalive_connections=3)
    ) as shared_client:
        
        async def process_single_logo(logo: LogoRule) -> bytes | None:
            """Process a single logo with error handling using shared HTTP client."""
            try:
                # Download logo using shared client (connection pooling)
                response = await shared_client.get(logo.url)
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
                
                # Validate that processed logo is readable before returning
                # This prevents corrupted logos from breaking generation
                try:
                    from PIL import Image
                    import io
                    test_img = Image.open(io.BytesIO(processed_logo))
                    test_img.verify()
                    
                    logger.info(
                        "logo_processed_parallel",
                        job_id=job_id,
                        logo_variant=logo.variant_name,
                        mime_type=mime_type,
                        original_size_bytes=original_size,
                        processed_size_bytes=processed_size,
                        operation_type=operation_type
                    )
                    
                    return processed_logo
                    
                except Exception as validation_error:
                    logger.error(
                        "logo_validation_failed_after_processing",
                        job_id=job_id,
                        logo_variant=logo.variant_name,
                        mime_type=mime_type,
                        error=str(validation_error),
                        solution="Skipping corrupted logo - re-ingest brand with valid logo file",
                        operation_type=operation_type
                    )
                    return None
                    
            except Exception as e:
                logger.warning(
                    "logo_download_failed_parallel",
                    job_id=job_id,
                    logo_url=logo.url,
                    error=str(e),
                    operation_type=operation_type
                )
                return None
        
        # Process all logos in parallel using shared HTTP client
        start_time = time.time()
        tasks = [process_single_logo(logo) for logo in logos]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        successful_logos = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(
                    "logo_processing_exception",
                    job_id=job_id,
                    logo_variant=logos[i].variant_name,
                    error=str(result),
                    operation_type=operation_type
                )
            elif result is not None:
                successful_logos.append(result)
        
        processing_time = time.time() - start_time
        logger.info(
            "parallel_logo_processing_complete",
            job_id=job_id,
            total_logos=len(logos),
            successful_logos=len(successful_logos),
            processing_time_ms=int(processing_time * 1000),
            operation_type=operation_type
        )
        
        return successful_logos

async def broadcast_websocket_event(job_id: str, event_type: str, data: dict):
    """
    Broadcast workflow events to WebSocket connections.
    
    Args:
        job_id: Job ID to broadcast to
        event_type: Type of event (status_change, reasoning_log, etc.)
        data: Event data to broadcast
    """
    try:
        from mobius.api.websocket_handlers import (
            broadcast_status_change,
            broadcast_reasoning_log,
            get_job_connection_count
        )
        
        # Only broadcast if there are active connections
        if get_job_connection_count(job_id) > 0:
            if event_type == "status_change":
                await broadcast_status_change(
                    job_id=job_id,
                    status=data.get("status", "unknown"),
                    progress=data.get("progress", 0),
                    current_step=data.get("current_step", "Processing")
                )
            elif event_type == "reasoning_log":
                await broadcast_reasoning_log(job_id, data)
                
    except Exception as e:
        # Don't fail workflow if WebSocket broadcasting fails
        logger.warning("websocket_broadcast_failed", job_id=job_id, error=str(e))


@performance_monitor("generate_node_total")
async def generate_node(state: JobState) -> Dict[str, Any]:
    """
    Generate image using Vision Model with compressed brand context.
    
    This node loads the Compressed Digital Twin from brand storage and
    uses it to generate brand-compliant images via the Vision Model.
    The compressed twin is injected into the system prompt to ensure
    the generated image follows brand guidelines.
    
    Broadcasts real-time updates via WebSocket for monitoring interfaces.
    
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
    job_id = state.get("job_id")
    
    if not brand_id:
        logger.error(
            "generate_node_missing_brand_id",
            job_id=job_id,
            state_keys=list(state.keys()),
            operation_type=operation_type
        )
        raise ValueError("brand_id is required in state but was not found")
    
    logger.info(
        "generate_node_start",
        job_id=job_id,
        brand_id=brand_id,
        attempt_count=state.get("attempt_count", 0),
        operation_type=operation_type
    )

    # Broadcast generation start
    await broadcast_websocket_event(job_id, "status_change", {
        "status": "generating",
        "progress": 25,
        "current_step": f"Generating image (attempt {state.get('attempt_count', 0) + 1})"
    })

    await broadcast_websocket_event(job_id, "reasoning_log", {
        "step": "Generation",
        "message": f"Starting image generation for brand {brand_id}",
        "level": "info"
    })
    
    try:
        # Initialize clients
        gemini_client = GeminiClient()
        
        # Load brand with compressed twin (using cache)
        with timer("brand_loading", job_id=job_id):
            brand = await get_cached_brand(brand_id)
        
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
        
        # Check if this is a tweak operation (resumed from needs_review with user instruction)
        # is_tweak flag is set by review_job_handler when user requests a tweak
        is_tweak_operation = state.get("is_tweak", False)
        previous_image_url = state.get("current_image_url")
        
        # Continue conversation if:
        # 1. This is a subsequent attempt (attempt > 1), OR
        # 2. This is a tweak operation with a previous image
        continue_conversation = current_attempt > 1 or (is_tweak_operation and previous_image_url)
        
        logger.info(
            "continue_conversation_logic",
            job_id=state.get("job_id"),
            current_attempt=current_attempt,
            is_tweak_operation=is_tweak_operation,
            has_previous_image=bool(previous_image_url),
            continue_conversation=continue_conversation,
            operation_type=operation_type
        )
        
        # Check if this is a tweak with a previous image
        is_tweak = continue_conversation and previous_image_url
        
        if is_tweak:
            logger.info(
                "tweak_with_previous_image",
                job_id=state.get("job_id"),
                has_previous_image=bool(previous_image_url),
                previous_image_url=previous_image_url[:100] if previous_image_url else None,
                is_tweak_operation=is_tweak_operation,
                current_attempt=current_attempt,
                operation_type=operation_type
            )

        # Smart logo strategy - FIXED: Preserve original logo configuration for tweaks
        needs_logos = False
        if not continue_conversation:
            # Always fetch logos on first attempt
            needs_logos = True
            logger.info(
                "logo_strategy_first_attempt",
                job_id=state.get("job_id"),
                needs_logos=needs_logos,
                operation_type=operation_type
            )
        else:
            # For tweaks/corrections, check if original generation had logos
            # This preserves the logo configuration from the parent job
            original_had_logos = state.get("original_had_logos", False)
            
            # Also check if user's instruction mentions logo (if instruction still exists)
            user_instruction = state.get("user_tweak_instruction")
            logo_mentioned_in_tweak = False
            if user_instruction:
                instruction = user_instruction.lower()
                logo_keywords = ['logo', 'brand mark', 'icon', 'symbol', 'emblem']
                logo_mentioned_in_tweak = any(kw in instruction for kw in logo_keywords)

            # Use logos if: original had logos OR user specifically mentions logo in tweak
            needs_logos = original_had_logos or logo_mentioned_in_tweak

            logger.info(
                "logo_strategy_for_tweak",
                job_id=state.get("job_id"),
                original_had_logos=original_had_logos,
                logo_mentioned_in_tweak=logo_mentioned_in_tweak,
                user_instruction=user_instruction,
                needs_logos=needs_logos,
                state_keys=list(state.keys()),
                operation_type=operation_type
            )

            if logo_mentioned_in_tweak:
                logger.info(
                    "logo_mentioned_in_correction",
                    job_id=state.get("job_id"),
                    instruction=user_instruction,
                    operation_type=operation_type
                )

        # Fetch brand logos from storage if needed (PARALLEL PROCESSING)
        logo_bytes_list = []
        
        logger.info(
            "logo_fetch_decision",
            job_id=state.get("job_id"),
            needs_logos=needs_logos,
            has_brand_guidelines=bool(brand.guidelines),
            has_logos=bool(brand.guidelines and brand.guidelines.logos),
            logo_count=len(brand.guidelines.logos) if brand.guidelines and brand.guidelines.logos else 0,
            operation_type=operation_type
        )
        
        if needs_logos and brand.guidelines and brand.guidelines.logos:
            logger.info(
                "fetching_brand_logos_parallel",
                job_id=state.get("job_id"),
                logo_count=len(brand.guidelines.logos),
                is_correction=continue_conversation,
                operation_type=operation_type
            )

            with timer("logo_processing_parallel", job_id=job_id):
                logo_bytes_list = await fetch_and_process_logos_parallel(
                    brand.guidelines.logos,
                    job_id=state.get("job_id"),
                    operation_type=operation_type
                )
        elif needs_logos:
            logger.warning(
                "logo_fetch_skipped",
                job_id=state.get("job_id"),
                reason="Brand has no logos or guidelines",
                has_brand_guidelines=bool(brand.guidelines),
                has_logos=bool(brand.guidelines and brand.guidelines.logos),
                operation_type=operation_type
            )
        else:
            logger.info(
                "logo_fetch_not_needed",
                job_id=state.get("job_id"),
                needs_logos=needs_logos,
                operation_type=operation_type
            )

        # Store original prompt for intent detection
        original_prompt = state["prompt"]
        
        # DISABLED: Prompt optimization removed - brand guidelines are already in system prompt
        # This saves ~2-5 seconds latency and preserves user intent
        # The compressed_twin is injected via _build_generation_system_prompt() in generate_image()
        optimized_prompt = original_prompt
        
        logger.info(
            "using_original_prompt",
            job_id=state.get("job_id"),
            prompt=original_prompt,
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

        # Broadcast generation progress
        await broadcast_websocket_event(job_id, "reasoning_log", {
            "step": "Vision Model",
            "message": f"Calling Vision Model with optimized prompt and {len(logo_bytes_list)} logo(s)",
            "level": "info"
        })

        # Log final logo decision before calling Gemini
        logger.info(
            "final_logo_decision_before_gemini",
            job_id=job_id,
            logo_bytes_count=len(logo_bytes_list),
            has_logo_bytes=bool(logo_bytes_list),
            needs_logos=needs_logos,
            continue_conversation=continue_conversation,
            operation_type=operation_type
        )

        # Generate image with Vision Model (with logos if available)
        with timer("image_generation_api", job_id=job_id):
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
        
        # Keep image as base64 for direct passing to audit node
        # Upload to Supabase will happen after audit completes
        stored_image_url = image_uri
        
        logger.info(
            "image_ready_for_audit",
            job_id=job_id,
            image_size_bytes=len(image_uri) if image_uri else 0,
            operation_type=operation_type
        )

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

        # Broadcast generation completion
        await broadcast_websocket_event(job_id, "status_change", {
            "status": "generated",
            "progress": 50,
            "current_step": "Image generated successfully, proceeding to audit"
        })

        await broadcast_websocket_event(job_id, "reasoning_log", {
            "step": "Generation Complete",
            "message": f"Image generated successfully in {latency_ms}ms (attempt {current_attempt})",
            "level": "success"
        })

        # Note: Progressive job updates removed - focusing on fixing root cause

        # Return updated state with stored URL (CDN URL instead of base64)
        return {
            "current_image_url": stored_image_url,
            "attempt_count": current_attempt,
            "session_id": session_id,
            "status": "generated",
            "original_had_logos": bool(logo_bytes_list)  # Preserve logo configuration for future tweaks
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
