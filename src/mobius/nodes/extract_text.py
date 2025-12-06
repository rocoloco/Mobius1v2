"""
PDF text extraction node for brand ingestion workflow.

Extracts raw text from brand guidelines PDFs using pdfplumber.
"""

from mobius.models.state import IngestionState
from mobius.tools.pdf_parser import PDFParser
import httpx
import structlog

logger = structlog.get_logger()


async def extract_text_node(state: IngestionState) -> dict:
    """
    Extract text content from brand guidelines PDF.

    Downloads the PDF from the provided URL and extracts all text content
    using pdfplumber. Also attempts to extract hex codes and font names
    from the text for initial processing.

    Args:
        state: Current ingestion workflow state

    Returns:
        Updated state dict with extracted_text and status
    """
    logger.info("extract_text_start", brand_id=state["brand_id"])

    parser = PDFParser()

    try:
        # Download PDF from URL
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(state["pdf_url"])
            response.raise_for_status()
            pdf_bytes = response.content

        logger.debug("pdf_downloaded", brand_id=state["brand_id"], size_bytes=len(pdf_bytes))

        # Extract text using pdfplumber
        text = parser.extract_text(pdf_bytes)

        if not text or len(text.strip()) < 100:
            logger.warning("pdf_text_too_short", brand_id=state["brand_id"], chars=len(text))
            return {
                "extracted_text": text,
                "status": "text_extracted",
                "needs_review": state.get("needs_review", [])
                + ["PDF text extraction yielded minimal content"],
            }

        # Extract preliminary hex codes and fonts from text
        hex_codes = parser.extract_hex_codes(text)
        font_names = parser.extract_font_names(text)

        logger.info(
            "text_extraction_complete",
            brand_id=state["brand_id"],
            chars=len(text),
            hex_codes=len(hex_codes),
            fonts=len(font_names),
        )

        return {
            "extracted_text": text,
            "extracted_colors": hex_codes,  # Preliminary colors from text
            "extracted_fonts": font_names,  # Preliminary fonts from text
            "status": "text_extracted",
        }

    except httpx.HTTPError as e:
        logger.error("pdf_download_failed", brand_id=state["brand_id"], error=str(e))
        return {
            "status": "failed",
            "needs_review": state.get("needs_review", []) + [f"PDF download failed: {str(e)}"],
        }

    except Exception as e:
        logger.error("text_extraction_failed", brand_id=state["brand_id"], error=str(e))
        return {
            "status": "failed",
            "needs_review": state.get("needs_review", [])
            + [f"Text extraction failed: {str(e)}"],
        }
