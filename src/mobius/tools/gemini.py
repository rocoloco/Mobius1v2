"""
Google Gemini Vision API client.

Provides image analysis and PDF visual extraction using Gemini 1.5 Pro.
Supports structured output with Pydantic models via response_schema.
"""

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from mobius.config import settings
from mobius.models.brand import BrandGuidelines
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel
import structlog
import json

logger = structlog.get_logger()


class GeminiClient:
    """Client for Google Gemini Vision API."""

    def __init__(self):
        """Initialize Gemini client with API key from settings."""
        genai.configure(api_key=settings.gemini_api_key)
        # Use gemini-3-pro-preview for vision tasks
        self.model = genai.GenerativeModel("gemini-3-pro-preview")
        logger.info("gemini_client_initialized")

    async def analyze_image(
        self,
        image_url: str,
        prompt: str,
        response_format: str = "text",
        response_schema: Optional[Type[BaseModel]] = None,
    ) -> Any:
        """
        Analyze an image using Gemini Vision.

        Args:
            image_url: URL of the image to analyze
            prompt: Analysis prompt
            response_format: "text" or "json"
            response_schema: Optional Pydantic model for structured output

        Returns:
            Analysis result (str for text, dict for json, or Pydantic model instance)

        Raises:
            Exception: If analysis fails
        """
        logger.info("analyzing_image", image_url=image_url[:50], format=response_format)

        try:
            # Download image
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_bytes = response.content

            # Configure generation
            generation_config = GenerationConfig(
                temperature=0.1,  # Low temperature for consistent analysis
            )

            if response_format == "json":
                generation_config.response_mime_type = "application/json"

            if response_schema:
                # Use response_schema for structured output
                generation_config.response_schema = response_schema

            # Generate content
            result = self.model.generate_content(
                [prompt, {"mime_type": "image/jpeg", "data": image_bytes}],
                generation_config=generation_config,
            )

            # Parse response
            if response_schema:
                # Parse as Pydantic model
                parsed = response_schema.model_validate_json(result.text)
                logger.info("image_analyzed", format="pydantic_model")
                return parsed
            elif response_format == "json":
                parsed = json.loads(result.text)
                logger.info("image_analyzed", format="json")
                return parsed
            else:
                logger.info("image_analyzed", format="text")
                return result.text

        except Exception as e:
            logger.error("image_analysis_failed", error=str(e))
            raise

    async def analyze_pdf(
        self,
        pdf_bytes: bytes,
        prompt: str,
        response_format: str = "json",
        response_schema: Optional[Type[BaseModel]] = None,
    ) -> Any:
        """
        Analyze a PDF using Gemini Vision.

        Extracts visual elements like colors, logos, and layout from PDF pages.

        Args:
            pdf_bytes: PDF file as bytes
            prompt: Analysis prompt
            response_format: "text" or "json"
            response_schema: Optional Pydantic model for structured output

        Returns:
            Analysis result (str for text, dict for json, or Pydantic model instance)

        Raises:
            Exception: If analysis fails
        """
        logger.info("analyzing_pdf", size_bytes=len(pdf_bytes), format=response_format)

        try:
            # Configure generation
            generation_config = GenerationConfig(
                temperature=0.1,  # Low temperature for consistent extraction
            )

            if response_format == "json":
                generation_config.response_mime_type = "application/json"

            if response_schema:
                # Use response_schema for structured output
                generation_config.response_schema = response_schema

            # Generate content with PDF
            result = self.model.generate_content(
                [prompt, {"mime_type": "application/pdf", "data": pdf_bytes}],
                generation_config=generation_config,
            )

            # Parse response
            if response_schema:
                # Parse as Pydantic model
                parsed = response_schema.model_validate_json(result.text)
                logger.info("pdf_analyzed", format="pydantic_model")
                return parsed
            elif response_format == "json":
                parsed = json.loads(result.text)
                logger.info("pdf_analyzed", format="json")
                return parsed
            else:
                logger.info("pdf_analyzed", format="text")
                return result.text

        except Exception as e:
            logger.error("pdf_analysis_failed", error=str(e))
            raise

    async def extract_brand_guidelines(
        self, pdf_bytes: bytes, extracted_text: Optional[str] = None
    ) -> BrandGuidelines:
        """
        Extract structured brand guidelines from a PDF.

        Uses Gemini with response_schema to ensure output matches BrandGuidelines model.
        Explicitly handles negative_constraint detection for "Do Not" rules.

        Args:
            pdf_bytes: PDF file as bytes
            extracted_text: Optional pre-extracted text to provide context

        Returns:
            BrandGuidelines Pydantic model instance

        Raises:
            Exception: If extraction fails
        """
        logger.info("extracting_brand_guidelines", size_bytes=len(pdf_bytes))

        # Construct detailed prompt with negative_constraint guidance
        prompt = """
        Analyze this brand guidelines PDF and extract structured information.
        
        Extract the following elements:
        
        1. **Colors**: All brand colors with their names, hex codes, and usage categories.
           - Usage must be one of: "primary", "secondary", "accent", "background"
           - Include any context about when/how to use each color
        
        2. **Typography**: Font families with their weights and usage guidelines.
           - Extract font family names, available weights, and usage instructions
        
        3. **Logos**: Logo usage rules including variants, sizing, and constraints.
           - Extract logo variant names, minimum sizes, clear space requirements
           - List forbidden background colors as hex codes
        
        4. **Voice**: Brand voice and tone guidelines.
           - Extract adjectives describing the brand voice
           - Identify forbidden words or phrases
           - Include example phrases that embody the brand voice
        
        5. **Rules**: Governance rules for automated auditing.
           - Category must be one of: "visual", "verbal", "legal"
           - Severity must be one of: "warning", "critical"
           - **CRITICAL**: Set negative_constraint=true for "Do Not" instructions
           - **CRITICAL**: Set negative_constraint=false for "Do" instructions
           
           Examples:
           - "Do not use Comic Sans" → negative_constraint=true
           - "Always include logo" → negative_constraint=false
           - "Never use red on green" → negative_constraint=true
           - "Use primary colors for headers" → negative_constraint=false
        
        If any information is ambiguous or missing, use empty lists or null values.
        Do not make up information that isn't in the PDF.
        """

        if extracted_text:
            prompt += f"\n\nExtracted text for context:\n{extracted_text[:2000]}"

        try:
            # Use response_schema to ensure structured output
            guidelines = await self.analyze_pdf(
                pdf_bytes=pdf_bytes,
                prompt=prompt,
                response_schema=BrandGuidelines,
            )

            logger.info(
                "brand_guidelines_extracted",
                colors=len(guidelines.colors),
                typography=len(guidelines.typography),
                logos=len(guidelines.logos),
                rules=len(guidelines.rules),
            )

            return guidelines

        except Exception as e:
            logger.error("brand_guidelines_extraction_failed", error=str(e))
            raise
