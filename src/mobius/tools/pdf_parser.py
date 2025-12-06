"""
PDF parsing utilities using pdfplumber.

Provides text extraction from brand guidelines PDFs with section detection.
"""

import pdfplumber
from typing import List, Optional
import io
import structlog

logger = structlog.get_logger()


class PDFParser:
    """PDF text extraction and section detection."""

    def extract_text(self, pdf_bytes: bytes) -> str:
        """
        Extract all text from a PDF file.

        Args:
            pdf_bytes: PDF file as bytes

        Returns:
            Extracted text as a single string

        Raises:
            Exception: If PDF cannot be parsed
        """
        logger.info("extracting_pdf_text", size_bytes=len(pdf_bytes))

        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                text_parts = []
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                        logger.debug("page_extracted", page_num=page_num, chars=len(page_text))

                full_text = "\n\n".join(text_parts)
                logger.info("pdf_text_extracted", total_chars=len(full_text), pages=len(pdf.pages))
                return full_text

        except Exception as e:
            logger.error("pdf_extraction_failed", error=str(e))
            raise

    def find_section(self, text: str, keywords: List[str]) -> Optional[str]:
        """
        Find a section in the text based on keywords.

        Searches for sections that contain any of the provided keywords
        and extracts the relevant portion of text.

        Args:
            text: Full text to search
            keywords: List of keywords to search for (case-insensitive)

        Returns:
            Extracted section text, or None if not found
        """
        logger.debug("finding_section", keywords=keywords)

        text_lower = text.lower()
        lines = text.split("\n")

        # Find lines containing keywords
        matching_indices = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword.lower() in line_lower for keyword in keywords):
                matching_indices.append(i)

        if not matching_indices:
            logger.debug("section_not_found", keywords=keywords)
            return None

        # Extract section around first match (10 lines before and after)
        start_idx = max(0, matching_indices[0] - 10)
        end_idx = min(len(lines), matching_indices[0] + 50)

        section = "\n".join(lines[start_idx:end_idx])
        logger.debug("section_found", keywords=keywords, chars=len(section))
        return section

    def extract_hex_codes(self, text: str) -> List[str]:
        """
        Extract hex color codes from text.

        Args:
            text: Text to search for hex codes

        Returns:
            List of hex codes found (with # prefix)
        """
        import re

        # Match hex codes with or without # prefix
        pattern = r"#?([0-9A-Fa-f]{6})\b"
        matches = re.findall(pattern, text)

        # Normalize to include # prefix
        hex_codes = [f"#{code.upper()}" for code in matches]

        logger.debug("hex_codes_extracted", count=len(hex_codes))
        return hex_codes

    def extract_font_names(self, text: str) -> List[str]:
        """
        Extract font family names from text.

        Uses common patterns to identify font names in brand guidelines.

        Args:
            text: Text to search for font names

        Returns:
            List of font family names found
        """
        import re

        # Common font name patterns
        # Look for capitalized words near "font", "typeface", "family"
        font_keywords = ["font", "typeface", "family", "typography"]

        fonts = []
        lines = text.split("\n")

        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in font_keywords):
                # Extract capitalized words (potential font names)
                words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", line)
                fonts.extend(words)

        # Remove duplicates while preserving order
        unique_fonts = []
        seen = set()
        for font in fonts:
            if font not in seen and font not in font_keywords:
                unique_fonts.append(font)
                seen.add(font)

        logger.debug("font_names_extracted", count=len(unique_fonts))
        return unique_fonts[:10]  # Limit to 10 fonts
