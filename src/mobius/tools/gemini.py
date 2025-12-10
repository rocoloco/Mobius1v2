"""
Google Gemini Vision API client.

Provides image analysis and PDF visual extraction using Gemini 1.5 Pro.
Supports structured output with Pydantic models via response_schema.
"""

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.api_core import exceptions as google_exceptions
from mobius.config import settings
from mobius.models.brand import BrandGuidelines
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel
import structlog
import json
import asyncio
import time

logger = structlog.get_logger()


class GeminiClient:
    """
    Client for Google Gemini API with dual-model architecture.
    
    Uses separate models for different tasks:
    - Reasoning Model (gemini-3-pro-preview): PDF parsing, compliance auditing
    - Vision Model (gemini-3-pro-image-preview): Image generation
    """

    def __init__(self):
        """Initialize Gemini client with both reasoning and vision models."""
        genai.configure(api_key=settings.gemini_api_key)

        # Initialize both model instances
        self.reasoning_model = genai.GenerativeModel(settings.reasoning_model)

        # Initialize vision model for image generation
        self.vision_model = genai.GenerativeModel(
            model_name=settings.vision_model,
            generation_config=GenerationConfig(
                temperature=0.7,
            )
        )

        # Session management for multi-turn conversations
        self.active_sessions: Dict[str, Any] = {}
        self.session_created_at: Dict[str, float] = {}
        self.session_ttl: int = 3600  # 1 hour TTL for sessions

        logger.info(
            "gemini_client_initialized",
            reasoning_model=settings.reasoning_model,
            vision_model=settings.vision_model,
            operation_type="client_initialization"
        )
    
    def _estimate_token_count(self, text: str) -> int:
        """
        Estimate token count for text input.
        
        Uses a simple heuristic: ~4 characters per token for English text.
        This is an approximation; actual token count may vary.
        
        Args:
            text: Input text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        return len(text) // 4
    
    def _handle_api_error(self, error: Exception, model_name: str, operation_type: str) -> Exception:
        """
        Handle and log Gemini API errors with comprehensive context.
        
        Provides structured error handling for:
        - Rate limit errors (429)
        - Authentication errors (401)
        - Timeout errors
        - General API errors
        
        Args:
            error: The original exception
            model_name: Name of the model being used
            operation_type: Type of operation (e.g., "image_analysis", "pdf_analysis")
            
        Returns:
            A more specific exception with enhanced error context
        """
        error_details = {
            "model_name": model_name,
            "operation_type": operation_type,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        # Handle rate limit errors (429)
        if isinstance(error, google_exceptions.ResourceExhausted) or "429" in str(error):
            logger.error(
                "gemini_rate_limit_exceeded",
                **error_details,
                retry_after=60  # Suggest 60 second retry
            )
            return Exception(f"Rate limit exceeded for {model_name}. Please retry after 60 seconds.")
        
        # Handle authentication errors (401)
        elif isinstance(error, google_exceptions.Unauthenticated) or "401" in str(error):
            logger.error(
                "gemini_authentication_failed",
                **error_details
            )
            return Exception(f"Authentication failed for {model_name}. Please check your API key.")
        
        # Handle timeout errors
        elif isinstance(error, (asyncio.TimeoutError, TimeoutError)) or "timeout" in str(error).lower():
            logger.error(
                "gemini_request_timeout",
                **error_details
            )
            return Exception(f"Request timeout for {model_name}. The operation took too long.")
        
        # Handle general API errors
        else:
            logger.error(
                "gemini_api_error",
                **error_details
            )
            return error

    def get_or_create_session(self, job_id: str, system_prompt: str) -> Any:
        """
        Get existing chat session or create a new one for multi-turn conversations.

        Args:
            job_id: Unique job identifier
            system_prompt: System prompt for the session

        Returns:
            ChatSession instance
        """
        # Clean up expired sessions first
        self._cleanup_expired_sessions()

        # Return existing session if found
        if job_id in self.active_sessions:
            session_age = time.time() - self.session_created_at[job_id]
            logger.info(
                "session_reused",
                job_id=job_id,
                session_age_seconds=round(session_age, 2),
                operation_type="session_management"
            )
            return self.active_sessions[job_id]

        # Create new session
        session = self.vision_model.start_chat(history=[])
        self.active_sessions[job_id] = session
        self.session_created_at[job_id] = time.time()

        logger.info(
            "session_created",
            job_id=job_id,
            total_active_sessions=len(self.active_sessions),
            operation_type="session_management"
        )

        return session

    def clear_session(self, job_id: str) -> None:
        """
        Clear a specific session from memory.

        Args:
            job_id: Job identifier for the session to clear
        """
        if job_id in self.active_sessions:
            del self.active_sessions[job_id]
            del self.session_created_at[job_id]

            logger.info(
                "session_cleared",
                job_id=job_id,
                operation_type="session_management"
            )

    def _cleanup_expired_sessions(self) -> None:
        """Remove sessions older than TTL."""
        current_time = time.time()
        expired_jobs = [
            job_id
            for job_id, created_at in self.session_created_at.items()
            if current_time - created_at > self.session_ttl
        ]

        for job_id in expired_jobs:
            self.clear_session(job_id)

        if expired_jobs:
            logger.info(
                "sessions_expired",
                count=len(expired_jobs),
                operation_type="session_management"
            )

    async def analyze_image(
        self,
        image_url: str,
        prompt: str,
        response_format: str = "text",
        response_schema: Optional[Type[BaseModel]] = None,
    ) -> Any:
        """
        Analyze an image using Reasoning Model.

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
        model_name = settings.reasoning_model
        operation_type = "image_analysis"
        start_time = time.time()
        
        # Estimate input token count
        input_token_count = self._estimate_token_count(prompt)
        
        logger.info(
            "analyzing_image",
            image_url=image_url[:50],
            format=response_format,
            model_name=model_name,
            operation_type=operation_type,
            token_count=input_token_count,
            analysis_prompt=prompt  # Log the full prompt for audit trail
        )

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

            # Generate content using reasoning model
            result = self.reasoning_model.generate_content(
                [prompt, {"mime_type": "image/jpeg", "data": image_bytes}],
                generation_config=generation_config,
            )

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Estimate output token count
            output_token_count = self._estimate_token_count(result.text)
            total_token_count = input_token_count + output_token_count

            # Parse response
            if response_schema:
                # Parse as Pydantic model
                parsed = response_schema.model_validate_json(result.text)
                logger.info(
                    "image_analyzed",
                    format="pydantic_model",
                    model_name=model_name,
                    operation_type=operation_type,
                    latency_ms=latency_ms,
                    token_count=total_token_count
                )
                return parsed
            elif response_format == "json":
                parsed = json.loads(result.text)
                logger.info(
                    "image_analyzed",
                    format="json",
                    model_name=model_name,
                    operation_type=operation_type,
                    latency_ms=latency_ms,
                    token_count=total_token_count
                )
                return parsed
            else:
                logger.info(
                    "image_analyzed",
                    format="text",
                    model_name=model_name,
                    operation_type=operation_type,
                    latency_ms=latency_ms,
                    token_count=total_token_count
                )
                return result.text

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            handled_error = self._handle_api_error(e, model_name, operation_type)
            logger.error(
                "image_analysis_failed",
                model_name=model_name,
                operation_type=operation_type,
                latency_ms=latency_ms,
                error=str(e)
            )
            raise handled_error

    async def analyze_pdf(
        self,
        pdf_bytes: bytes,
        prompt: str,
        response_format: str = "json",
        response_schema: Optional[Type[BaseModel]] = None,
    ) -> Any:
        """
        Analyze a PDF using Reasoning Model.

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
        model_name = settings.reasoning_model
        operation_type = "pdf_analysis"
        start_time = time.time()
        
        # Estimate input token count
        input_token_count = self._estimate_token_count(prompt)
        
        logger.info(
            "analyzing_pdf",
            size_bytes=len(pdf_bytes),
            format=response_format,
            model_name=model_name,
            operation_type=operation_type,
            token_count=input_token_count
        )

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

            # Generate content with PDF using reasoning model
            result = self.reasoning_model.generate_content(
                [prompt, {"mime_type": "application/pdf", "data": pdf_bytes}],
                generation_config=generation_config,
            )

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Estimate output token count
            output_token_count = self._estimate_token_count(result.text)
            total_token_count = input_token_count + output_token_count

            # Parse response
            if response_schema:
                # Parse as Pydantic model
                parsed = response_schema.model_validate_json(result.text)
                logger.info(
                    "pdf_analyzed",
                    format="pydantic_model",
                    model_name=model_name,
                    operation_type=operation_type,
                    latency_ms=latency_ms,
                    token_count=total_token_count
                )
                return parsed
            elif response_format == "json":
                parsed = json.loads(result.text)
                logger.info(
                    "pdf_analyzed",
                    format="json",
                    model_name=model_name,
                    operation_type=operation_type,
                    latency_ms=latency_ms,
                    token_count=total_token_count
                )
                return parsed
            else:
                logger.info(
                    "pdf_analyzed",
                    format="text",
                    model_name=model_name,
                    operation_type=operation_type,
                    latency_ms=latency_ms,
                    token_count=total_token_count
                )
                return result.text

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            handled_error = self._handle_api_error(e, model_name, operation_type)
            logger.error(
                "pdf_analysis_failed",
                model_name=model_name,
                operation_type=operation_type,
                latency_ms=latency_ms,
                error=str(e)
            )
            raise handled_error

    async def extract_compressed_guidelines(
        self, pdf_bytes: bytes
    ) -> "CompressedDigitalTwin":
        """
        Extract compressed brand guidelines using Reasoning Model.
        
        Returns only essential visual rules optimized for Vision Model context.
        Ensures the compressed twin fits within 60k token limit.
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            CompressedDigitalTwin instance optimized for Vision Model context
            
        Raises:
            Exception: If extraction fails or compression cannot meet token limit
        """
        from mobius.models.brand import CompressedDigitalTwin
        
        model_name = settings.reasoning_model
        operation_type = "compressed_extraction"
        start_time = time.time()
        
        logger.info(
            "extracting_compressed_guidelines",
            size_bytes=len(pdf_bytes),
            model_name=model_name,
            operation_type=operation_type
        )
        
        # Prompt for extracting only essential visual rules
        prompt = """
        Analyze this brand guidelines PDF and extract ONLY the essential visual rules 
        needed for image generation. Be extremely concise.
        
        Extract:
        
        1. **Colors by Semantic Role** (hex codes only):
           - primary_colors: Dominant brand identity (logos, headers)
           - secondary_colors: Supporting elements (shapes, icons)
           - accent_colors: High-visibility CTAs (buttons, links) - use sparingly
           - neutral_colors: Backgrounds, body text (white, black, greys)
           - semantic_colors: Functional states (success, error, warning)
           
           Use the semantic mapping rules:
           - PRIMARY: "Primary", "Core", "Dominant", "Main", "Logo Color"
           - SECONDARY: "Secondary", "Supporting", "Complementary"
           - ACCENT: "Accent", "Highlight", "CTA", "Button", "Link"
           - NEUTRAL: "Neutral", "Background", "Base", "Text", "Body Copy"
           - SEMANTIC: "Success", "Error", "Warning", "Alert"
        
        2. **Font Families** (names only, no weights or details):
           - Just the font family names as strings
        
        3. **Visual Dos** (concise positive rules):
           - Short bullet points (max 100 chars each)
           - Only critical visual constraints
           - Example: "Use primary colors for headers"
        
        4. **Visual Donts** (concise negative rules):
           - Short bullet points (max 100 chars each)
           - Only critical prohibitions
           - Example: "Never distort logo aspect ratio"
        
        5. **Logo Placement** (single string, optional):
           - Concise placement rule
           - Example: "top-left or center"
        
        6. **Logo Min Size** (single string, optional):
           - Minimum size requirement
           - Example: "100px width"
        
        CRITICAL: Be extremely concise. Exclude:
        - Verbose descriptions
        - Historical context
        - Brand story
        - Detailed explanations
        - Non-visual content
        
        The output MUST fit within 60,000 tokens.
        """
        
        try:
            # Extract compressed guidelines using reasoning model
            compressed_twin = await self.analyze_pdf(
                pdf_bytes=pdf_bytes,
                prompt=prompt,
                response_schema=CompressedDigitalTwin,
            )
            
            # Validate token count
            token_count = compressed_twin.estimate_tokens()
            latency_ms = int((time.time() - start_time) * 1000)
            
            logger.info(
                "compressed_guidelines_extracted",
                token_count=token_count,
                model_name=model_name,
                operation_type=operation_type,
                latency_ms=latency_ms
            )
            
            # If initial extraction exceeds limit, apply fallback compression
            if not compressed_twin.validate_size():
                logger.warning(
                    "compressed_twin_exceeds_limit",
                    token_count=token_count,
                    applying_fallback=True,
                    model_name=model_name,
                    operation_type=operation_type
                )
                
                # Fallback: Truncate lists to fit within limit
                compressed_twin = self._apply_fallback_compression(compressed_twin)
                
                # Validate again
                token_count = compressed_twin.estimate_tokens()
                if not compressed_twin.validate_size():
                    raise ValueError(
                        f"Compressed twin still exceeds 60k token limit after fallback: {token_count} tokens"
                    )
                
                logger.info(
                    "fallback_compression_applied",
                    new_token_count=token_count,
                    model_name=model_name,
                    operation_type=operation_type
                )
            
            return compressed_twin
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            handled_error = self._handle_api_error(e, model_name, operation_type)
            logger.error(
                "compressed_extraction_failed",
                model_name=model_name,
                operation_type=operation_type,
                latency_ms=latency_ms,
                error=str(e)
            )
            raise handled_error
    
    def _apply_fallback_compression(self, compressed_twin: "CompressedDigitalTwin") -> "CompressedDigitalTwin":
        """
        Apply fallback compression to reduce token count.
        
        Truncates lists to essential items while preserving structure.
        
        Args:
            compressed_twin: Original compressed twin that exceeds limit
            
        Returns:
            Compressed twin with reduced token count
        """
        from mobius.models.brand import CompressedDigitalTwin
        
        # Truncate color lists (keep most important)
        primary_colors = compressed_twin.primary_colors[:5]
        secondary_colors = compressed_twin.secondary_colors[:5]
        accent_colors = compressed_twin.accent_colors[:3]
        neutral_colors = compressed_twin.neutral_colors[:5]
        semantic_colors = compressed_twin.semantic_colors[:3]
        
        # Truncate font families
        font_families = compressed_twin.font_families[:5]
        
        # Truncate visual rules (keep most critical)
        visual_dos = compressed_twin.visual_dos[:20]
        visual_donts = compressed_twin.visual_donts[:20]
        
        # Keep logo requirements as-is (already concise)
        logo_placement = compressed_twin.logo_placement
        logo_min_size = compressed_twin.logo_min_size
        
        return CompressedDigitalTwin(
            primary_colors=primary_colors,
            secondary_colors=secondary_colors,
            accent_colors=accent_colors,
            neutral_colors=neutral_colors,
            semantic_colors=semantic_colors,
            font_families=font_families,
            visual_dos=visual_dos,
            visual_donts=visual_donts,
            logo_placement=logo_placement,
            logo_min_size=logo_min_size
        )

    async def optimize_prompt(
        self,
        user_prompt: str,
        compressed_twin: "CompressedDigitalTwin",
        has_logo: bool = False
    ) -> str:
        """
        Use Reasoning Model to optimize user prompt for brand-compliant generation.

        Takes a simple user prompt and enhances it with:
        - Specific brand color references
        - Typography guidance
        - Logo placement instructions
        - Visual style alignment

        Args:
            user_prompt: Original user prompt
            compressed_twin: Brand guidelines context
            has_logo: Whether brand logo will be provided as multi-modal input

        Returns:
            Optimized prompt for Vision Model
        """
        operation_type = "prompt_optimization"
        start_time = time.time()

        logger.info(
            "optimizing_prompt",
            user_prompt=user_prompt,
            has_logo=has_logo,
            operation_type=operation_type
        )

        # Detect if user explicitly wants text in the image
        text_keywords = ['text', 'headline', 'caption', 'slogan', 'tagline', 'copy', 'words', 'saying', 'quote', 'message', 'ad', 'advertisement', 'banner', 'poster']
        user_wants_text = any(keyword in user_prompt.lower() for keyword in text_keywords)
        
        logger.info(
            "prompt_analysis",
            user_wants_text=user_wants_text,
            operation_type=operation_type
        )

        # Build optimization context
        optimization_prompt = f"""You are a brand-compliant prompt engineer. Optimize this user prompt to ensure brand compliance while maintaining creative intent.

## User's Original Prompt:
{user_prompt}

## Brand Guidelines to Follow:
"""

        # Add brand context
        if compressed_twin.primary_colors:
            optimization_prompt += f"\n- Primary Colors: {', '.join(compressed_twin.primary_colors)}"
        if compressed_twin.accent_colors:
            optimization_prompt += f"\n- Accent Colors: {', '.join(compressed_twin.accent_colors)}"
        if compressed_twin.font_families:
            optimization_prompt += f"\n- Typography: {', '.join(compressed_twin.font_families)}"
        if compressed_twin.visual_dos:
            optimization_prompt += f"\n- Visual Guidelines (DO): {'; '.join(compressed_twin.visual_dos[:5])}"
        if compressed_twin.visual_donts:
            optimization_prompt += f"\n- Visual Guidelines (DON'T): {'; '.join(compressed_twin.visual_donts[:5])}"

        if has_logo:
            optimization_prompt += "\n- The brand logo image will be provided separately as visual reference"

        optimization_prompt += """

## Your Task:
Enhance the user's prompt to be more specific and brand-compliant. Include:
1. Specific color hex codes from the brand palette where appropriate
2. Visual style guidance aligned with brand rules
3. Typography guidance if text is requested (use approved fonts)
4. If the user mentions "logo" or "our logo", note that the logo will be included as a reference image
5. Maintain the user's creative intent while ensuring brand compliance
6. Keep it concise - one clear sentence

## IMPORTANT RULES:
"""

        if user_wants_text:
            optimization_prompt += """- The user HAS requested text/copy in the image - preserve this intent
- Specify which approved fonts to use for any text elements
- Ensure text follows brand voice and color guidelines
- DO NOT remove or ignore the user's request for text content"""
        else:
            optimization_prompt += """- The user has NOT requested text/copy in the image
- DO NOT add instructions for text, headlines, slogans, or marketing copy
- Focus purely on the photographic/visual scene
- When logos are mentioned, describe them as physical elements in the scene (e.g., "on the product")"""

        optimization_prompt += """

Return ONLY the optimized prompt, no explanations or preamble."""

        try:
            # Use Reasoning Model for optimization
            generation_config = GenerationConfig(temperature=0.7)

            result = await asyncio.to_thread(
                self.reasoning_model.generate_content,
                [optimization_prompt],
                generation_config=generation_config,
            )

            optimized_prompt = result.text.strip()

            latency_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "prompt_optimized",
                user_prompt=user_prompt,
                optimized_prompt=optimized_prompt,
                operation_type=operation_type,
                latency_ms=latency_ms
            )

            return optimized_prompt

        except Exception as e:
            logger.warning(
                "prompt_optimization_failed_using_original",
                error=str(e),
                operation_type=operation_type
            )
            # Fall back to original prompt if optimization fails
            return user_prompt

    async def generate_image(
        self,
        prompt: str,
        compressed_twin: "CompressedDigitalTwin",
        logo_bytes: list[bytes] = None,
        original_prompt: str = None,
        job_id: Optional[str] = None,
        continue_conversation: bool = False,
        previous_image_bytes: bytes = None,
        **generation_params
    ) -> Dict[str, str]:
        """
        Generate image using Vision Model with compressed brand context and optional logo.

        Supports multi-turn conversations for iterative refinement without full regeneration.
        Injects the Compressed Digital Twin into the system prompt to ensure
        brand-compliant image generation. Supports multi-modal input with logo images.
        Implements retry logic with exponential backoff and increased timeouts for resilience.

        Args:
            prompt: Optimized image generation prompt
            compressed_twin: Compressed brand guidelines for context
            logo_bytes: Optional list of logo images as bytes for multi-modal input
            original_prompt: Original user prompt (before optimization) for intent detection
            job_id: Optional job identifier for session tracking
            continue_conversation: If True, continues existing conversation for iterative edits
            previous_image_bytes: Optional bytes of previous image for tweak/edit operations
            **generation_params: Additional generation parameters (temperature, etc.)

        Returns:
            dict with 'image_uri' and 'session_id' keys

        Raises:
            Exception: If generation fails after all retry attempts
        """
        from mobius.models.brand import CompressedDigitalTwin
        
        model_name = settings.vision_model
        operation_type = "image_generation"
        max_attempts = 3
        base_delay = 1.0  # Start with 1 second delay
        base_timeout = 30.0  # Start with 30 second timeout
        start_time = time.time()
        
        # Estimate input token count (prompt + compressed twin)
        compressed_twin_tokens = compressed_twin.estimate_tokens()
        prompt_tokens = self._estimate_token_count(prompt)
        input_token_count = compressed_twin_tokens + prompt_tokens
        
        # Detect if user wants text in the image (use original prompt if available)
        prompt_to_check = original_prompt if original_prompt else prompt
        text_keywords = ['text', 'headline', 'caption', 'slogan', 'tagline', 'copy', 'words', 'saying', 'quote', 'message', 'ad', 'advertisement', 'banner', 'poster']
        user_wants_text = any(keyword in prompt_to_check.lower() for keyword in text_keywords)
        
        logger.info(
            "generating_image",
            prompt_length=len(prompt),
            has_logo=bool(logo_bytes),
            logo_count=len(logo_bytes) if logo_bytes else 0,
            has_previous_image=bool(previous_image_bytes),
            previous_image_size=len(previous_image_bytes) if previous_image_bytes else 0,
            user_wants_text=user_wants_text,
            model_name=model_name,
            operation_type=operation_type,
            token_count=input_token_count
        )

        # Build system prompt with compressed twin injection
        system_prompt = self._build_generation_system_prompt(
            compressed_twin,
            has_logo=bool(logo_bytes),
            allow_text=user_wants_text
        )

        # Determine if we're using multi-turn conversation
        use_session = job_id is not None and continue_conversation
        session = None
        session_id = None

        if use_session:
            # Get or create session for multi-turn conversation
            session = self.get_or_create_session(job_id, system_prompt)
            session_id = job_id

            logger.info(
                "using_multi_turn_conversation",
                job_id=job_id,
                session_id=session_id,
                operation_type=operation_type
            )

        # CRITICAL: Always send system prompt, even in multi-turn
        # Session preserves generated images but NOT system prompts or input images
        full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"

        # Log the full prompt for audit trail
        logger.info(
            "image_generation_prompt",
            system_prompt_length=len(system_prompt),
            user_prompt=prompt,
            full_prompt_length=len(full_prompt),
            has_logo=bool(logo_bytes),
            use_session=use_session,
            operation_type=operation_type
        )

        # Configure generation parameters
        generation_config = GenerationConfig(
            temperature=generation_params.get("temperature", 0.7),
        )

        # Build multi-modal content list
        # Format: [text_prompt, previous_image (if tweak), logo_image_1, logo_image_2, ...]
        content_parts = [full_prompt]
        
        # Add previous image if this is a tweak/edit operation
        # This gives Gemini context of what to modify
        if previous_image_bytes:
            content_parts.append({
                "mime_type": "image/jpeg",  # Previous images are typically JPEG
                "data": previous_image_bytes
            })
            logger.info(
                "adding_previous_image_for_tweak",
                image_size_bytes=len(previous_image_bytes),
                operation_type=operation_type
            )

        # Add logos only if provided (smart logo strategy from generate.py)
        if logo_bytes:
            for idx, logo_data in enumerate(logo_bytes):
                content_parts.append({
                    "mime_type": "image/png",  # Assume PNG, could be made dynamic
                    "data": logo_data
                })
                logger.info(
                    "adding_logo_to_generation",
                    logo_index=idx,
                    logo_size_bytes=len(logo_data),
                    operation_type=operation_type
                )
        
        # Retry loop with exponential backoff and increased timeouts
        last_exception = None
        for attempt in range(1, max_attempts + 1):
            try:
                # Increase timeout on each retry: 30s, 60s, 120s
                timeout = base_timeout * (2 ** (attempt - 1))
                
                logger.info(
                    "image_generation_attempt",
                    attempt=attempt,
                    max_attempts=max_attempts,
                    timeout_seconds=timeout,
                    model_name=model_name
                )

                # Generate image using vision model with timeout
                # Pass content_parts (text + optional logo images)
                if use_session and session:
                    # Use session for multi-turn conversation
                    logger.info(
                        "sending_message_to_session",
                        job_id=job_id,
                        content_part_count=len(content_parts),
                        content_types=[type(part).__name__ for part in content_parts],
                        is_correction=continue_conversation,
                        operation_type=operation_type
                    )
                    result = await asyncio.wait_for(
                        asyncio.to_thread(
                            session.send_message,
                            content_parts,
                            generation_config=generation_config,
                        ),
                        timeout=timeout
                    )
                else:
                    # Direct generation for new conversations
                    result = await asyncio.wait_for(
                        asyncio.to_thread(
                            self.vision_model.generate_content,
                            content_parts,
                            generation_config=generation_config,
                        ),
                        timeout=timeout
                    )
                
                # Extract image URI from response
                # Note: The actual implementation depends on Gemini's response format
                # For now, we'll extract from the response text or parts
                image_uri = self._extract_image_uri(result)
                
                # Calculate latency
                latency_ms = int((time.time() - start_time) * 1000)
                
                logger.info(
                    "image_generated",
                    attempt=attempt,
                    image_uri=image_uri[:100] if image_uri else None,
                    model_name=model_name,
                    operation_type=operation_type,
                    latency_ms=latency_ms,
                    token_count=input_token_count,
                    session_id=session_id
                )

                return {
                    "image_uri": image_uri,
                    "session_id": session_id
                }
                
            except (asyncio.TimeoutError, TimeoutError) as e:
                last_exception = e
                logger.warning(
                    "image_generation_timeout",
                    attempt=attempt,
                    max_attempts=max_attempts,
                    timeout_seconds=timeout,
                    model_name=model_name,
                    operation_type="image_generation"
                )
                
                # If this was the last attempt, don't sleep
                if attempt < max_attempts:
                    # Exponential backoff: 1s, 2s, 4s
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.info(
                        "retrying_after_timeout",
                        delay_seconds=delay,
                        next_attempt=attempt + 1,
                        next_timeout=base_timeout * (2 ** attempt)
                    )
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                last_exception = e
                
                # Use error handler for comprehensive logging
                handled_error = self._handle_api_error(e, model_name, "image_generation")
                
                logger.warning(
                    "image_generation_attempt_failed",
                    attempt=attempt,
                    max_attempts=max_attempts,
                    error=str(e),
                    model_name=model_name,
                    operation_type="image_generation"
                )
                
                # If this was the last attempt, don't sleep
                if attempt < max_attempts:
                    # Exponential backoff: 1s, 2s, 4s
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.info(
                        "retrying_after_delay",
                        delay_seconds=delay,
                        next_attempt=attempt + 1
                    )
                    await asyncio.sleep(delay)
        
        # All attempts failed - use error handler for final error
        latency_ms = int((time.time() - start_time) * 1000)
        handled_error = self._handle_api_error(last_exception, model_name, operation_type)
        logger.error(
            "image_generation_failed_all_attempts",
            max_attempts=max_attempts,
            error=str(last_exception),
            model_name=model_name,
            operation_type=operation_type,
            latency_ms=latency_ms,
            token_count=input_token_count
        )
        raise Exception(
            f"Image generation failed after {max_attempts} attempts: {str(handled_error)}"
        )
    
    def _build_generation_system_prompt(
        self, 
        compressed_twin: "CompressedDigitalTwin", 
        has_logo: bool = False,
        allow_text: bool = False
    ) -> str:
        """
        Build system prompt with compressed twin injection.

        Creates a structured prompt that provides the Vision Model with
        essential brand guidelines for compliant image generation.

        Args:
            compressed_twin: Compressed brand guidelines
            has_logo: Whether logo images are included as multi-modal input
            allow_text: Whether the user has requested text/copy in the image

        Returns:
            System prompt string with injected brand context
        """
        prompt_parts = [
            "You are a brand-compliant image generator. Generate images that strictly follow these brand guidelines:",
            "",
        ]

        if has_logo:
            prompt_parts.extend([
                "## Logo Usage:",
                "- Brand logo images are provided as reference",
                "- Use the provided logo(s) in the generated image when appropriate",
                "- Maintain logo integrity - do not distort, recolor, or modify the logo design",
                "- When placing logos on products (bottles, packaging, etc.), apply them as FLAT overlays that maintain proper proportions",
                "- DO NOT wrap logos around curved surfaces or apply perspective distortion",
                "- If a product surface is curved, place the logo on a flat label area or use a straight-on angle",
                "",
            ])

        prompt_parts.append("## Brand Colors (by semantic role):")
        
        # Add color guidelines by semantic role
        if compressed_twin.primary_colors:
            prompt_parts.append(f"- Primary (logos, headers): {', '.join(compressed_twin.primary_colors)}")
        if compressed_twin.secondary_colors:
            prompt_parts.append(f"- Secondary (supporting elements): {', '.join(compressed_twin.secondary_colors)}")
        if compressed_twin.accent_colors:
            prompt_parts.append(f"- Accent (CTAs, use sparingly): {', '.join(compressed_twin.accent_colors)}")
        if compressed_twin.neutral_colors:
            prompt_parts.append(f"- Neutral (backgrounds, text): {', '.join(compressed_twin.neutral_colors)}")
        if compressed_twin.semantic_colors:
            prompt_parts.append(f"- Semantic (status indicators): {', '.join(compressed_twin.semantic_colors)}")
        
        # Add typography
        if compressed_twin.font_families:
            prompt_parts.append("")
            prompt_parts.append("## Typography:")
            prompt_parts.append(f"- Approved fonts: {', '.join(compressed_twin.font_families)}")
        
        # Add visual dos
        if compressed_twin.visual_dos:
            prompt_parts.append("")
            prompt_parts.append("## Visual Guidelines (DO):")
            for rule in compressed_twin.visual_dos:
                prompt_parts.append(f"- {rule}")
        
        # Add visual donts
        if compressed_twin.visual_donts:
            prompt_parts.append("")
            prompt_parts.append("## Visual Guidelines (DON'T):")
            for rule in compressed_twin.visual_donts:
                prompt_parts.append(f"- {rule}")
        
        # Add logo requirements
        if compressed_twin.logo_placement or compressed_twin.logo_min_size:
            prompt_parts.append("")
            prompt_parts.append("## Logo Requirements:")
            if compressed_twin.logo_placement:
                prompt_parts.append(f"- Placement: {compressed_twin.logo_placement}")
            if compressed_twin.logo_min_size:
                prompt_parts.append(f"- Minimum size: {compressed_twin.logo_min_size}")
        
        prompt_parts.append("")
        prompt_parts.append("## CRITICAL VISUAL CONSTRAINTS:")

        if allow_text:
            # User wants text in the image (ad, poster, banner, etc.)
            prompt_parts.append("- If text/copy is requested, use ONLY the approved brand fonts")
            prompt_parts.append("- For text on dark backgrounds: Use light accent or neutral colors, add subtle drop shadows for separation")
            prompt_parts.append("- For text on light backgrounds: Use dark primary or neutral colors with crisp edges")
            prompt_parts.append("- Keep text concise and aligned with brand voice")
            prompt_parts.append("- DO NOT add text unless explicitly requested by the user")
        else:
            # User wants a pure photographic scene
            prompt_parts.append("- Generate PHOTOGRAPHIC images only - no text overlays, headlines, or marketing copy")
            prompt_parts.append("- DO NOT add any text, slogans, taglines, or written content to the image")
            prompt_parts.append("- Focus on the visual scene described in the user prompt")

        prompt_parts.append("- Follow the 60-30-10 design rule: 60% neutral, 30% primary/secondary, 10% accent")
        prompt_parts.append("")
        prompt_parts.append("## ADVANCED RENDERING TECHNIQUES:")
        prompt_parts.append("- For text on fabric: Add rim lighting or studio lighting to create edge contrast")
        prompt_parts.append("- For metallic/reflective surfaces: Use directional lighting to separate foreground from background")
        prompt_parts.append("- For dark backgrounds: Layer elements with drop shadows, halos, or lighter intermediate surfaces")
        prompt_parts.append("- Prioritize LEGIBILITY over strict color matching - lighting and contrast are more important than exact hex codes")
        
        return "\n".join(prompt_parts)
    
    def _extract_image_uri(self, result) -> str:
        """
        Extract image URI from Gemini generation result.
        
        The Gemini API may return images in different formats depending on
        the model and configuration. This method handles the extraction logic.
        
        Args:
            result: Gemini generation result
            
        Returns:
            Image URI string
            
        Raises:
            ValueError: If no image URI can be extracted
        """
        # Check if result has parts with inline_data (image bytes)
        if hasattr(result, 'parts'):
            for part in result.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    # For inline data, we need to convert to a URI
                    # This could be a data URI or we might need to upload to storage
                    mime_type = part.inline_data.mime_type
                    data = part.inline_data.data
                    
                    # Create data URI
                    import base64
                    encoded_data = base64.b64encode(data).decode('utf-8')
                    return f"data:{mime_type};base64,{encoded_data}"
        
        # Check if result has text that might contain a URI
        if hasattr(result, 'text') and result.text:
            # Look for URI patterns in the text
            import re
            uri_pattern = r'(https?://[^\s]+|data:[^;]+;base64,[^\s]+)'
            matches = re.findall(uri_pattern, result.text)
            if matches:
                return matches[0]
        
        # If we can't find an image URI, raise an error
        raise ValueError("No image URI found in generation result")

    async def audit_compliance(
        self,
        image_uri: str,
        brand_guidelines: BrandGuidelines
    ) -> "ComplianceScore":
        """
        Audit image compliance using Reasoning Model with multimodal vision.
        
        Uses the Reasoning Model's superior reasoning capabilities to evaluate
        brand compliance. Accepts image_uri for multimodal input and uses full
        Brand Guidelines (not compressed twin) for comprehensive compliance checking.
        
        Implements graceful degradation: if audit fails, returns a partial compliance
        score with error annotations rather than failing completely.
        
        Args:
            image_uri: URI reference to the generated image (can be URL or data URI)
            brand_guidelines: Full brand guidelines for comprehensive auditing
            
        Returns:
            ComplianceScore with category breakdowns and violation details
            (or partial score with error annotations if audit fails)
        """
        from mobius.models.compliance import ComplianceScore, CategoryScore, Violation, Severity
        
        model_name = settings.reasoning_model
        operation_type = "compliance_audit"
        start_time = time.time()
        
        logger.info(
            "auditing_compliance",
            image_uri=image_uri[:100] if image_uri else None,
            model_name=model_name,
            operation_type=operation_type
        )
        
        try:
            # Build audit prompt with full brand guidelines context
            audit_prompt = self._build_audit_prompt(brand_guidelines)

            # Estimate input token count
            input_token_count = self._estimate_token_count(audit_prompt)

            # Log the audit prompt for audit trail
            logger.info(
                "compliance_audit_prompt",
                audit_prompt=audit_prompt,
                prompt_length=len(audit_prompt),
                operation_type=operation_type
            )
            
            # Download image from URI if it's a URL
            image_data = None
            if image_uri.startswith('http://') or image_uri.startswith('https://'):
                import httpx
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(image_uri)
                    response.raise_for_status()
                    image_data = response.content
                    mime_type = response.headers.get('content-type', 'image/jpeg')
            elif image_uri.startswith('data:'):
                # Handle data URI
                import base64
                import re
                match = re.match(r'data:([^;]+);base64,(.+)', image_uri)
                if match:
                    mime_type = match.group(1)
                    encoded_data = match.group(2)
                    image_data = base64.b64decode(encoded_data)
                else:
                    raise ValueError(f"Invalid data URI format: {image_uri[:100]}")
            else:
                raise ValueError(f"Unsupported image URI format: {image_uri[:100]}")
            
            # Configure generation for structured output
            generation_config = GenerationConfig(
                temperature=0.1,  # Low temperature for consistent auditing
                response_mime_type="application/json",
            )
            generation_config.response_schema = ComplianceScore
            
            # Generate compliance audit using reasoning model with multimodal input
            # Add timeout to prevent hanging (120 seconds for audit)
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    self.reasoning_model.generate_content,
                    [audit_prompt, {"mime_type": mime_type, "data": image_data}],
                    generation_config=generation_config,
                ),
                timeout=120.0  # 2 minute timeout for audit
            )
            
            # Parse response as ComplianceScore
            compliance_score = ComplianceScore.model_validate_json(result.text)
            
            # Calculate latency and token count
            latency_ms = int((time.time() - start_time) * 1000)
            output_token_count = self._estimate_token_count(result.text)
            total_token_count = input_token_count + output_token_count
            
            # Log detailed audit results for audit trail
            category_details = [
                {
                    "category": cat.category,
                    "score": cat.score,
                    "passed": cat.passed,
                    "violations": [
                        {
                            "description": v.description,
                            "severity": v.severity,
                            "fix_suggestion": v.fix_suggestion
                        }
                        for v in cat.violations
                    ]
                }
                for cat in compliance_score.categories
            ]

            logger.info(
                "compliance_audited",
                overall_score=compliance_score.overall_score,
                approved=compliance_score.approved,
                summary=compliance_score.summary,
                categories=len(compliance_score.categories),
                category_details=category_details,
                model_name=model_name,
                operation_type=operation_type,
                latency_ms=latency_ms,
                token_count=total_token_count
            )
            
            return compliance_score
            
        except Exception as e:
            # Graceful degradation: return partial compliance score with error annotations
            latency_ms = int((time.time() - start_time) * 1000)
            handled_error = self._handle_api_error(e, model_name, operation_type)
            
            logger.warning(
                "compliance_audit_failed_returning_partial",
                error=str(e),
                model_name=model_name,
                operation_type=operation_type,
                latency_ms=latency_ms
            )
            
            # Create partial compliance score with error annotations
            error_violation = Violation(
                category="audit_error",
                description=f"Compliance audit failed: {str(handled_error)}",
                severity=Severity.CRITICAL,
                fix_suggestion="Manual review required - automated audit could not complete"
            )
            
            # Create error category for each standard category
            error_categories = [
                CategoryScore(
                    category=cat,
                    score=0.0,
                    passed=False,
                    violations=[error_violation]
                )
                for cat in ["colors", "typography", "layout", "logo_usage"]
            ]
            
            partial_score = ComplianceScore(
                overall_score=0.0,
                categories=error_categories,
                approved=False,
                summary=f"Audit failed with error: {str(handled_error)}. Manual review required."
            )
            
            logger.info(
                "partial_compliance_score_returned",
                model_name=model_name,
                operation_type=operation_type,
                latency_ms=latency_ms,
                error_type=type(e).__name__
            )
            
            return partial_score
    
    def _build_audit_prompt(self, brand_guidelines: BrandGuidelines) -> str:
        """
        Build audit prompt with full brand guidelines context.
        
        Creates a comprehensive prompt that provides the Reasoning Model with
        complete brand guidelines for thorough compliance checking.
        
        Args:
            brand_guidelines: Full brand guidelines
            
        Returns:
            Audit prompt string with complete brand context
        """
        prompt_parts = [
            "You are a brand compliance auditor. Analyze this image against the brand guidelines below.",
            "Provide detailed compliance scores for each category with specific violations.",
            "",
            "## Brand Guidelines:",
            "",
        ]
        
        # Add color guidelines
        if brand_guidelines.colors:
            prompt_parts.append("### Colors:")
            for color in brand_guidelines.colors:
                usage_info = f" (usage: {color.usage})" if color.usage else ""
                context_info = f" - {color.context}" if color.context else ""
                prompt_parts.append(f"- {color.name}: {color.hex}{usage_info}{context_info}")
            prompt_parts.append("")
        
        # Add typography guidelines
        if brand_guidelines.typography:
            prompt_parts.append("### Typography:")
            for typo in brand_guidelines.typography:
                weights_info = f" (weights: {', '.join(typo.weights)})" if typo.weights else ""
                prompt_parts.append(f"- {typo.family}{weights_info}")
                if typo.usage:
                    prompt_parts.append(f"  Usage: {typo.usage}")
            prompt_parts.append("")
        
        # Add logo guidelines
        if brand_guidelines.logos:
            prompt_parts.append("### Logo Guidelines:")
            for logo in brand_guidelines.logos:
                prompt_parts.append(f"- {logo.variant_name}")
                if logo.min_width_px:
                    prompt_parts.append(f"  Minimum size: {logo.min_width_px}px")
                if logo.clear_space_ratio:
                    prompt_parts.append(f"  Clear space: {logo.clear_space_ratio}")
                if logo.forbidden_backgrounds:
                    prompt_parts.append(f"  Forbidden backgrounds: {', '.join(logo.forbidden_backgrounds)}")
            prompt_parts.append("")
        
        # Add voice guidelines
        if brand_guidelines.voice:
            prompt_parts.append("### Brand Voice:")
            if brand_guidelines.voice.adjectives:
                prompt_parts.append(f"- Adjectives: {', '.join(brand_guidelines.voice.adjectives)}")
            if brand_guidelines.voice.forbidden_words:
                prompt_parts.append(f"- Forbidden words: {', '.join(brand_guidelines.voice.forbidden_words)}")
            if brand_guidelines.voice.example_phrases:
                prompt_parts.append("- Example phrases:")
                for phrase in brand_guidelines.voice.example_phrases:
                    prompt_parts.append(f"  - {phrase}")
            prompt_parts.append("")
        
        # Add governance rules
        if brand_guidelines.rules:
            prompt_parts.append("### Governance Rules:")
            for rule in brand_guidelines.rules:
                severity_marker = "⚠️" if rule.severity == "warning" else "🚨"
                constraint_type = "DON'T" if rule.negative_constraint else "DO"
                prompt_parts.append(f"- {severity_marker} [{rule.category.upper()}] {constraint_type}: {rule.instruction}")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "## Audit Instructions:",
            "",
            "Evaluate the image across these categories:",
            "1. **colors**: Check if colors match approved palette and usage guidelines",
            "2. **typography**: Verify font families match approved list",
            "3. **layout**: Assess composition, spacing, and visual hierarchy",
            "4. **logo_usage**: Check logo placement, sizing, and background compliance",
            "",
            "## CRITICAL CONTEXT RULES (Apply Visual Intelligence):",
            "- On **metallic, reflective, or 3D surfaces** (bottles, cans, packaging), technical contrast ratios may be lower due to lighting and environmental reflections",
            "- If text/logo is **clearly legible to a human observer** despite mathematical ratio failures, mark as PASSED with a note",
            "- Ignore **water droplets, highlights, rim lighting, and studio lighting effects** when calculating contrast",
            "- For **product photography with realistic lighting**, prioritize visual legibility over strict numerical ratios",
            "- **Fabric textures** (t-shirts, apparel) naturally create visual separation even with technically low contrast",
            "- **Drop shadows, halos, and edge lighting** are valid techniques that improve legibility beyond raw color contrast",
            "- If the image uses **flat labels, patches, or stickers** on products, apply standard contrast rules to those surfaces only",
            "",
            "## EXCEPTION: Premium Aesthetic Override",
            "For high-quality product photography where the brand aesthetic requires premium materials (gold on silver, metallic on dark, etc.):",
            "- If the image demonstrates **professional lighting** (rim lighting, studio setup, directional shadows)",
            "- AND the text/logo is **clearly readable** in the rendered image",
            "- Mark contrast violations as **WARNINGS** instead of CRITICAL",
            "- Note: \"Acceptable for premium product photography with proper lighting\"",
            "",
            "For each category, provide:",
            "- A score from 0-100",
            "- Whether it passed (score >= 80)",
            "- List of specific violations with severity and fix suggestions",
            "- **Apply contextual leniency** as described above before flagging violations",
            "",
            "Calculate overall_score as weighted average of categories.",
            "Set approved=true if overall_score >= 95.",
            "Provide a summary of the overall assessment with contextual notes.",
        ])
        
        return "\n".join(prompt_parts)

    async def extract_brand_guidelines(
        self, pdf_bytes: bytes, extracted_text: Optional[str] = None
    ) -> BrandGuidelines:
        """
        Extract structured brand guidelines from a PDF using Reasoning Model.

        Uses Gemini with response_schema to ensure output matches BrandGuidelines model.
        Temperature set to 0.0 for maximum consistency.

        Args:
            pdf_bytes: PDF file as bytes
            extracted_text: Optional pre-extracted text to provide context

        Returns:
            BrandGuidelines Pydantic model instance

        Raises:
            Exception: If extraction fails
        """
        model_name = settings.reasoning_model
        operation_type = "brand_extraction"
        start_time = time.time()
        
        logger.info(
            "extracting_brand_guidelines",
            size_bytes=len(pdf_bytes),
            model_name=model_name,
            operation_type=operation_type
        )

        # Construct extraction prompt
        prompt = """
        Analyze this brand guidelines PDF and extract structured information.
        
        Extract the following elements:
        
        1. **Colors**: All brand colors with their names, hex codes, and semantic usage roles.
           - Usage must be one of: "primary", "secondary", "accent", "neutral", "semantic"
           - Estimate usage_weight (0.0 to 1.0) based on visual prominence and surface area
           - Include any context about when/how to use each color
           
           **Semantic Color Mapping Rules:**
           - **PRIMARY** (Identity): Core brand color for logos and headers
             Trigger terms: "Primary", "Core", "Dominant", "Main", "Logo Color", "Brand Identity"
             Visual clue: Color used for largest headlines or logo
           
           - **SECONDARY** (Support): Supporting elements that don't dominate
             Trigger terms: "Secondary", "Supporting", "Complementary", "Palette B", "Shapes"
           
           - **ACCENT** (Action): High visibility, low frequency - drives user behavior
             Trigger terms: "Accent", "Highlight", "CTA", "Button", "Link", "Interaction"
             Example: "Use Heritage Gold for CTAs" → ACCENT
           
           - **NEUTRAL** (Canvas): Structure and whitespace
             Trigger terms: "Neutral", "Background", "Base", "Canvas", "Text", "Body Copy"
             CRITICAL: Typography colors (e.g., "Dark Charcoal") → NEUTRAL, NOT Primary
           
           - **SEMANTIC** (Functional): UI state indicators
             Trigger terms: "Success", "Error", "Warning", "Alert", "Info", "Validation"
           
           **Conflict Resolution**: If a color fits multiple categories, prioritize by surface area:
           - High surface area (backgrounds) → NEUTRAL or PRIMARY
           - Low surface area (buttons, links) → ACCENT
        
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
            prompt += f"\n\nExtracted text for context:\n{extracted_text[:5000]}"

        try:
            # Use response_schema with temperature=0.0 for consistency
            guidelines = await self.analyze_pdf(
                pdf_bytes=pdf_bytes,
                prompt=prompt,
                response_schema=BrandGuidelines,
            )

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Estimate token count from the serialized guidelines
            output_token_count = self._estimate_token_count(guidelines.model_dump_json())
            
            logger.info(
                "brand_guidelines_extracted",
                colors=len(guidelines.colors),
                typography=len(guidelines.typography),
                logos=len(guidelines.logos),
                rules=len(guidelines.rules),
                model_name=model_name,
                operation_type=operation_type,
                latency_ms=latency_ms,
                token_count=output_token_count
            )

            return guidelines

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            handled_error = self._handle_api_error(e, model_name, operation_type)
            logger.error(
                "brand_extraction_failed",
                model_name=model_name,
                operation_type=operation_type,
                latency_ms=latency_ms,
                error=str(e)
            )
            raise handled_error
