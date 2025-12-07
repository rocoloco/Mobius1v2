"""
PDF visual extraction node for brand ingestion workflow.

Extracts visual elements (colors, logos, layout) from PDFs using Gemini Vision.
"""

from mobius.models.state import IngestionState
from mobius.tools.gemini import GeminiClient
import httpx
import structlog
import time

logger = structlog.get_logger()


async def extract_visual_node(state: IngestionState) -> dict:
    """
    Extract visual elements from brand guidelines PDF using Gemini Vision.

    Uses Gemini's multimodal capabilities to analyze the PDF and extract:
    - Color swatches and palettes
    - Logo variations and usage rules
    - Typography examples
    - Visual style patterns
    - Compressed Digital Twin for generation

    Args:
        state: Current ingestion workflow state

    Returns:
        Updated state dict with visual extraction results and compressed twin
    """
    operation_type = "extract_visual_node"
    start_time = time.time()
    
    logger.info(
        "extract_visual_start",
        brand_id=state["brand_id"],
        operation_type=operation_type
    )

    gemini = GeminiClient()

    try:
        # Download PDF bytes for Gemini analysis
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(state["pdf_url"])
            response.raise_for_status()
            pdf_bytes = response.content

        logger.debug(
            "pdf_downloaded_for_visual",
            brand_id=state["brand_id"],
            operation_type=operation_type
        )

        # Extract compressed guidelines for generation
        compressed_twin = await gemini.extract_compressed_guidelines(pdf_bytes)
        
        logger.info(
            "compressed_twin_extracted",
            brand_id=state["brand_id"],
            token_estimate=compressed_twin.estimate_tokens(),
            primary_colors=len(compressed_twin.primary_colors),
            secondary_colors=len(compressed_twin.secondary_colors),
            accent_colors=len(compressed_twin.accent_colors),
            operation_type=operation_type
        )

        # Construct visual extraction prompt
        prompt = """
        Analyze this brand guidelines PDF and extract visual elements.
        
        Focus on:
        1. **Color Swatches**: Extract all visible color swatches with their hex codes
        2. **Logo Variations**: Identify different logo versions and their usage contexts
        3. **Typography Examples**: Extract font family names visible in the document
        4. **Visual Patterns**: Identify recurring visual elements or patterns
        
        Return JSON with this structure:
        {
          "colors": ["#HEX1", "#HEX2", ...],
          "fonts": ["Font Name 1", "Font Name 2", ...],
          "logo_rules": ["rule 1", "rule 2", ...],
          "visual_patterns": ["pattern 1", "pattern 2", ...]
        }
        
        Only include information that is clearly visible in the PDF.
        Do not make assumptions or invent information.
        """

        # Analyze PDF with Gemini
        result = await gemini.analyze_pdf(
            pdf_bytes=pdf_bytes, prompt=prompt, response_format="json"
        )

        # Merge visual colors with text-extracted colors
        visual_colors = result.get("colors", [])
        existing_colors = state.get("extracted_colors", [])

        # Combine and deduplicate colors
        all_colors = list(set(existing_colors + visual_colors))

        # Merge fonts
        visual_fonts = result.get("fonts", [])
        existing_fonts = state.get("extracted_fonts", [])
        all_fonts = list(set(existing_fonts + visual_fonts))

        latency_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "visual_extraction_complete",
            brand_id=state["brand_id"],
            total_colors=len(all_colors),
            total_fonts=len(all_fonts),
            logo_rules=len(result.get("logo_rules", [])),
            operation_type=operation_type,
            latency_ms=latency_ms
        )

        return {
            "extracted_colors": all_colors,
            "extracted_fonts": all_fonts,
            "extracted_rules": result.get("logo_rules", []) + result.get("visual_patterns", []),
            "compressed_twin": compressed_twin,
            "status": "visual_extracted",
        }

    except httpx.HTTPError as e:
        latency_ms = int((time.time() - start_time) * 1000)
        
        logger.error(
            "pdf_download_failed_visual",
            brand_id=state["brand_id"],
            error=str(e),
            operation_type=operation_type,
            latency_ms=latency_ms
        )
        # Continue with partial data
        return {
            "status": "partial_extraction",
            "needs_review": state.get("needs_review", [])
            + ["Visual extraction failed: PDF download error"],
        }

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        
        logger.error(
            "visual_extraction_failed",
            brand_id=state["brand_id"],
            error=str(e),
            operation_type=operation_type,
            latency_ms=latency_ms
        )
        # Continue with partial data
        return {
            "status": "partial_extraction",
            "needs_review": state.get("needs_review", [])
            + [f"Visual extraction incomplete: {str(e)}"],
        }
