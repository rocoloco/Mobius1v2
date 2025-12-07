"""
PDF Parser for Brand Guidelines - Comprehensive Digital Twin Creation.

Creates a complete Digital Twin of a brand by extracting and structuring
all brand elements from PDF guidelines. A Brand Digital Twin is a machine-readable,
semantically rich representation that enables automated governance, compliance
checking, and intelligent asset generation.

Digital Twin Concept:
- Captures not just visual elements, but the relationships and rules between them
- Enables predictive compliance checking before asset creation
- Provides context-aware guidance for different use cases
- Supports continuous learning and refinement through feedback
"""

import structlog
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from mobius.config import settings
from mobius.tools.pdf_parser import PDFParser as BasePDFParser
from mobius.models.brand import (
    BrandGuidelines,
    Color,
    Typography,
    LogoRule,
    VoiceTone,
    BrandRule,
)

logger = structlog.get_logger()


class DigitalTwinPDFParser:
    """
    Parse brand guidelines PDFs into comprehensive Digital Twin format.
    
    A Brand Digital Twin goes beyond simple data extraction to create a
    semantic model of the brand that understands:
    - Visual hierarchy and relationships
    - Contextual usage rules
    - Brand personality and voice
    - Accessibility and technical constraints
    - Cross-channel consistency requirements
    """

    def __init__(self):
        """Initialize parser with Gemini API and base PDF tools."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-3-pro-preview")
        self.base_parser = BasePDFParser()

    async def parse_pdf(self, pdf_bytes: bytes, filename: str) -> tuple[BrandGuidelines, List[bytes]]:
        """
        Parse PDF into comprehensive Brand Digital Twin.

        This creates a multi-dimensional representation of the brand that includes:
        1. Visual DNA (colors, typography, imagery)
        2. Behavioral rules (usage guidelines, restrictions)
        3. Semantic relationships (how elements work together)
        4. Contextual intelligence (channel-specific adaptations)

        Args:
            pdf_bytes: Raw PDF file bytes
            filename: Original filename for metadata

        Returns:
            Tuple of (BrandGuidelines, List of logo image bytes)

        Raises:
            Exception: If parsing fails
        """
        logger.info(
            "creating_brand_digital_twin",
            filename=filename,
            size_bytes=len(pdf_bytes)
        )

        # Phase 1: Extract raw text
        text_content = self.base_parser.extract_text(pdf_bytes)
        logger.info("text_extracted", char_count=len(text_content))

        # Phase 2: Extract images (logos)
        logo_images = self.base_parser.extract_images(pdf_bytes, max_images=5)
        logger.info("logo_images_extracted", count=len(logo_images))

        # Phase 3: Extract structured sections
        sections = self._extract_sections(text_content)
        logger.info("sections_identified", count=len(sections))

        # Phase 4: Use Gemini for intelligent parsing
        guidelines = await self._parse_with_gemini(text_content, sections, filename)
        logger.info("digital_twin_created", filename=filename)

        # Phase 5: Validate and enrich
        guidelines = self._validate_and_enrich(guidelines)
        logger.info("digital_twin_validated", filename=filename)

        return guidelines, logo_images

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract key sections from the PDF text.
        
        Identifies major sections like colors, typography, logo usage, etc.
        This provides context for more accurate Gemini parsing.
        """
        sections = {}
        
        # Color section
        color_section = self.base_parser.find_section(
            text,
            ["color", "palette", "colour", "brand colors"]
        )
        if color_section:
            sections["colors"] = color_section
            # Also extract hex codes directly
            sections["hex_codes"] = self.base_parser.extract_hex_codes(color_section)

        # Typography section
        typo_section = self.base_parser.find_section(
            text,
            ["typography", "fonts", "typeface", "type system"]
        )
        if typo_section:
            sections["typography"] = typo_section
            sections["font_names"] = self.base_parser.extract_font_names(typo_section)

        # Logo section
        logo_section = self.base_parser.find_section(
            text,
            ["logo", "logomark", "brand mark", "symbol"]
        )
        if logo_section:
            sections["logo"] = logo_section

        # Voice and tone section
        voice_section = self.base_parser.find_section(
            text,
            ["voice", "tone", "messaging", "communication", "brand personality"]
        )
        if voice_section:
            sections["voice"] = voice_section

        # Imagery section
        imagery_section = self.base_parser.find_section(
            text,
            ["imagery", "photography", "illustration", "visual style"]
        )
        if imagery_section:
            sections["imagery"] = imagery_section

        # Layout and spacing
        layout_section = self.base_parser.find_section(
            text,
            ["layout", "grid", "spacing", "composition", "white space"]
        )
        if layout_section:
            sections["layout"] = layout_section

        return sections

    async def _parse_with_gemini(
        self,
        full_text: str,
        sections: Dict[str, str],
        filename: str
    ) -> BrandGuidelines:
        """
        Use Gemini to create comprehensive Digital Twin structure.
        
        This goes beyond simple extraction to understand:
        - Relationships between brand elements
        - Contextual usage rules
        - Brand personality and values
        - Technical constraints and requirements
        """
        prompt = self._build_comprehensive_prompt(full_text, sections)

        logger.info("calling_gemini_for_digital_twin", text_length=len(full_text))

        try:
            response = await self.model.generate_content_async(prompt)
            parsed_data = self._parse_gemini_response(response.text)
        except Exception as e:
            logger.error("gemini_parsing_failed", error=str(e))
            # Fallback to basic extraction
            parsed_data = self._fallback_extraction(sections)

        # Build comprehensive Digital Twin
        guidelines = BrandGuidelines(
            colors=self._extract_colors(parsed_data, sections),
            typography=self._extract_typography(parsed_data, sections),
            logos=self._extract_logo_rules(parsed_data, sections),
            voice=self._extract_voice_tone(parsed_data, sections),
            rules=self._extract_brand_rules(parsed_data, sections),
            source_filename=filename,
        )

        return guidelines

    def _build_comprehensive_prompt(
        self,
        full_text: str,
        sections: Dict[str, str]
    ) -> str:
        """
        Build comprehensive prompt for Digital Twin creation.
        
        This prompt guides Gemini to think like a brand strategist and
        extract not just data, but the semantic meaning and relationships.
        """
        # Include section hints if available
        section_context = ""
        if sections:
            section_context = "\n\nIDENTIFIED SECTIONS:\n"
            for key, value in sections.items():
                if isinstance(value, str):
                    section_context += f"\n{key.upper()}:\n{value[:500]}...\n"

        return f"""You are an expert brand strategist creating a Digital Twin - a complete, machine-readable model of a brand.

A Brand Digital Twin is more than data extraction. It captures:
1. Visual DNA (colors, typography, imagery with semantic meaning)
2. Brand Personality (voice, values, emotional attributes)
3. Usage Intelligence (context-aware rules and guidelines)
4. Relationships (how elements work together)
5. Constraints (technical, accessibility, legal requirements)

BRAND GUIDELINES DOCUMENT:
{full_text[:8000]}

{section_context}

Extract and return comprehensive brand information in JSON format:

{{
  "colors": [
    {{
      "name": "Forest Green",
      "hex": "#2D5016",
      "rgb": "45, 80, 22",
      "cmyk": "44, 0, 73, 69",
      "pantone": "349 C",
      "usage": "primary",
      "description": "Primary brand color representing growth and sustainability",
      "emotional_attributes": ["trustworthy", "natural", "stable"],
      "accessibility": {{
        "wcag_aa_compliant": true,
        "min_contrast_ratio": 4.5
      }},
      "usage_contexts": ["headers", "CTAs", "brand elements"],
      "avoid_contexts": ["body text on white", "small text"],
      "pairings": ["cream", "white", "charcoal"]
    }}
  ],
  "typography": [
    {{
      "family": "Helvetica Neue",
      "weights": ["regular", "medium", "bold"],
      "fallbacks": ["Helvetica", "Arial", "sans-serif"],
      "usage": "headlines",
      "size_range": "24-72px",
      "line_height": "1.2",
      "letter_spacing": "-0.02em",
      "case": "sentence case",
      "personality": ["modern", "clean", "professional"],
      "accessibility": {{
        "min_size": "16px",
        "max_line_length": "75ch"
      }},
      "usage_contexts": ["web", "print", "digital"],
      "pairing_rules": ["Never mix with serif body text", "Maintain hierarchy"]
    }}
  ],
  "logos": [
    {{
      "type": "primary",
      "variants": ["full color", "monochrome", "reversed"],
      "min_size": {{
        "print": "0.5 inches",
        "digital": "40px"
      }},
      "clear_space": {{
        "measurement": "height of logo 'E'",
        "minimum": "20px"
      }},
      "allowed_backgrounds": ["white", "cream", "forest green", "photography with overlay"],
      "prohibited_backgrounds": ["busy patterns", "low contrast", "red"],
      "restrictions": [
        "Never stretch or distort",
        "Never rotate",
        "Never add effects or shadows",
        "Never place on busy backgrounds without overlay",
        "Maintain aspect ratio always"
      ],
      "file_formats": ["SVG", "PNG", "EPS"],
      "color_modes": ["RGB for digital", "CMYK for print"],
      "usage_contexts": {{
        "web": "SVG preferred",
        "print": "Vector EPS or high-res PNG",
        "social": "PNG with transparency"
      }}
    }}
  ],
  "voice": {{
    "personality_traits": ["friendly", "professional", "approachable", "authentic", "knowledgeable"],
    "tone_attributes": ["warm", "confident", "helpful", "clear"],
    "values": ["sustainability", "growth", "partnership", "integrity"],
    "messaging_pillars": [
      "We empower sustainable growth",
      "Partnership over transactions",
      "Expertise you can trust"
    ],
    "language_guidelines": {{
      "use": ["active voice", "simple language", "inclusive terms", "positive framing"],
      "avoid": ["jargon", "corporate speak", "passive voice", "negative framing", "exclusionary language"]
    }},
    "sentence_structure": "Clear, concise sentences. Average 15-20 words.",
    "examples": {{
      "good": [
        "We help you grow sustainably",
        "Let's build something great together",
        "Your success is our mission"
      ],
      "bad": [
        "Leveraging synergies for optimal outcomes",
        "It is believed that growth can be achieved",
        "Solutions are provided"
      ]
    }},
    "audience_adaptation": {{
      "B2B": "Professional but warm, focus on ROI and partnership",
      "B2C": "Friendly and accessible, focus on benefits and values",
      "Internal": "Collaborative and empowering, focus on culture"
    }}
  }},
  "imagery": {{
    "style": ["natural", "authentic", "bright", "optimistic"],
    "subjects": ["real people", "nature", "workspaces", "products in use"],
    "avoid": ["stock photos", "staged scenes", "overly corporate", "dark moody"],
    "composition": ["rule of thirds", "natural lighting", "shallow depth of field"],
    "color_treatment": ["vibrant but natural", "warm tones", "avoid heavy filters"],
    "diversity": "Always show diverse representation across age, ethnicity, ability"
  }},
  "layout": {{
    "grid_system": "12-column grid",
    "spacing_scale": ["4px", "8px", "16px", "24px", "32px", "48px", "64px"],
    "white_space": "Generous - minimum 24px between major sections",
    "alignment": "Left-aligned for text, centered for brand elements",
    "hierarchy": "Clear visual hierarchy with size, weight, and spacing"
  }},
  "rules": [
    {{
      "category": "color",
      "rule": "Never use red in brand materials - conflicts with brand values",
      "severity": "critical",
      "rationale": "Red conveys urgency and aggression, opposite of our calm, growth-focused brand",
      "applies_to": ["all channels", "all materials"],
      "exceptions": ["error states in UI only"]
    }},
    {{
      "category": "typography",
      "rule": "Headlines must use sentence case, never all caps",
      "severity": "high",
      "rationale": "Sentence case is more approachable and readable",
      "applies_to": ["web", "print", "social"],
      "exceptions": ["acronyms", "proper nouns"]
    }},
    {{
      "category": "logo",
      "rule": "Minimum clear space must equal height of logo 'E'",
      "severity": "critical",
      "rationale": "Ensures logo visibility and brand recognition",
      "applies_to": ["all placements"],
      "exceptions": ["none"]
    }},
    {{
      "category": "accessibility",
      "rule": "All text must meet WCAG AA contrast requirements (4.5:1)",
      "severity": "critical",
      "rationale": "Legal requirement and inclusive design principle",
      "applies_to": ["all digital materials"],
      "exceptions": ["decorative elements only"]
    }},
    {{
      "category": "voice",
      "rule": "Always use active voice and avoid passive constructions",
      "severity": "medium",
      "rationale": "Active voice is clearer and more engaging",
      "applies_to": ["all copy"],
      "exceptions": ["when subject is truly unknown or unimportant"]
    }}
  ],
  "metadata": {{
    "version": "2.0",
    "last_updated": "2024",
    "brand_values": ["sustainability", "growth", "partnership", "integrity"],
    "target_audiences": ["B2B clients", "eco-conscious consumers", "partners"],
    "competitive_positioning": "Premium sustainable solutions provider",
    "brand_archetype": "The Sage - knowledgeable, trustworthy guide"
  }}
}}

CRITICAL INSTRUCTIONS:
1. Extract ACTUAL values from the document - don't invent examples
2. If information is missing, use empty arrays/null, don't guess
3. Include rationale and context for rules - explain WHY, not just WHAT
4. Think about relationships between elements
5. Consider accessibility and technical constraints
6. Capture emotional and semantic meaning, not just visual specs
7. Include usage contexts and channel-specific adaptations
8. Return ONLY valid JSON, no markdown formatting
"""

    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini's JSON response with robust error handling."""
        import json
        import re

        # Remove markdown code blocks
        cleaned = re.sub(r"```json\s*|\s*```", "", response_text.strip())

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error("json_parse_failed", error=str(e), response=cleaned[:500])
            return self._get_empty_structure()

    def _fallback_extraction(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """
        Fallback extraction using basic pattern matching.
        
        Used when Gemini parsing fails. Extracts what we can from sections.
        """
        logger.warning("using_fallback_extraction")
        
        data = self._get_empty_structure()
        
        # Extract hex codes if available
        if "hex_codes" in sections:
            data["colors"] = [
                {"hex": hex_code, "name": f"Color {i+1}", "usage": "general"}
                for i, hex_code in enumerate(sections["hex_codes"][:10])
            ]
        
        # Extract font names if available
        if "font_names" in sections:
            data["typography"] = [
                {"family": font, "usage": "general"}
                for font in sections["font_names"][:5]
            ]
        
        return data

    def _get_empty_structure(self) -> Dict[str, Any]:
        """Return empty Digital Twin structure."""
        return {
            "colors": [],
            "typography": [],
            "logos": [],
            "voice": None,
            "imagery": None,
            "layout": None,
            "rules": [],
            "metadata": {}
        }

    def _extract_colors(
        self,
        parsed_data: Dict[str, Any],
        sections: Dict[str, str]
    ) -> List[Color]:
        """Extract comprehensive Color objects for Digital Twin."""
        colors = []
        
        # Map Gemini's usage values to our schema
        usage_map = {
            "primary": "primary",
            "secondary": "secondary",
            "accent": "accent",
            "background": "background",
            "text": "primary",  # Map text to primary
            "general": "secondary",
            "neutral": "background",
        }
        
        for i, color_data in enumerate(parsed_data.get("colors", [])):
            try:
                # Get usage and map it
                raw_usage = color_data.get("usage", "").lower() if color_data.get("usage") else ""
                
                # Log what we received
                logger.debug(
                    "color_extraction",
                    index=i,
                    name=color_data.get("name"),
                    raw_usage=raw_usage,
                )
                
                # Map to our schema, with smart defaults based on position
                if raw_usage in usage_map:
                    usage = usage_map[raw_usage]
                else:
                    # Smart defaults: first color is primary, second is secondary, rest are accent/background
                    if i == 0:
                        usage = "primary"
                        logger.debug("color_defaulted_to_primary", name=color_data.get("name"))
                    elif i == 1:
                        usage = "secondary"
                    elif "background" in color_data.get("name", "").lower() or "cream" in color_data.get("name", "").lower() or "white" in color_data.get("name", "").lower():
                        usage = "background"
                    else:
                        usage = "accent"
                
                # Build context from description and emotional attributes
                context_parts = []
                if color_data.get("description"):
                    context_parts.append(color_data["description"])
                if color_data.get("emotional_attributes"):
                    attrs = ", ".join(color_data["emotional_attributes"])
                    context_parts.append(f"Attributes: {attrs}")
                if color_data.get("usage_contexts"):
                    contexts = ", ".join(color_data["usage_contexts"])
                    context_parts.append(f"Use for: {contexts}")
                
                context = " | ".join(context_parts) if context_parts else None
                
                color = Color(
                    hex=color_data.get("hex", "#000000"),
                    name=color_data.get("name", "Unnamed"),
                    usage=usage,
                    context=context,
                )
                colors.append(color)
                
            except Exception as e:
                logger.warning("color_parse_failed", error=str(e), data=color_data)
        
        return colors

    def _extract_typography(
        self,
        parsed_data: Dict[str, Any],
        sections: Dict[str, str]
    ) -> List[Typography]:
        """Extract comprehensive Typography objects for Digital Twin."""
        typography = []
        
        for typo_data in parsed_data.get("typography", []):
            try:
                # Get weights - Gemini returns array, we need array
                weights = typo_data.get("weights", ["Regular"])
                if not isinstance(weights, list):
                    weights = [weights]
                
                # Build comprehensive usage string
                usage_parts = [typo_data.get("usage", "general")]
                
                if typo_data.get("emotional_attributes"):
                    attrs = ", ".join(typo_data["emotional_attributes"])
                    usage_parts.append(f"Style: {attrs}")
                
                if typo_data.get("usage_contexts"):
                    contexts = ", ".join(typo_data["usage_contexts"])
                    usage_parts.append(f"Contexts: {contexts}")
                
                if typo_data.get("hierarchy_rules"):
                    usage_parts.append(f"Hierarchy: {len(typo_data['hierarchy_rules'])} levels defined")
                
                usage = " | ".join(usage_parts)
                
                typo = Typography(
                    family=typo_data.get("family", "Arial"),
                    weights=weights,
                    usage=usage,
                )
                typography.append(typo)
                
            except Exception as e:
                logger.warning("typography_parse_failed", error=str(e), data=typo_data)
        
        return typography

    def _extract_logo_rules(
        self,
        parsed_data: Dict[str, Any],
        sections: Dict[str, str]
    ) -> List[LogoRule]:
        """Extract comprehensive LogoRule objects for Digital Twin."""
        logo_rules = []
        
        for logo_data in parsed_data.get("logos", []):
            try:
                # Extract variant name
                variant_name = logo_data.get("type", "Primary Logo")
                
                # Parse min_size to get pixel width
                min_size = logo_data.get("min_size", {})
                if isinstance(min_size, dict):
                    # Try to extract digital size in pixels
                    digital_size = min_size.get("digital_full") or min_size.get("digital") or "150 pixels"
                    # Extract number from string like "150 pixels" or "150px"
                    import re
                    match = re.search(r'(\d+)', str(digital_size))
                    min_width_px = int(match.group(1)) if match else 150
                else:
                    min_width_px = 150
                
                # Parse clear_space to get ratio
                clear_space = logo_data.get("clear_space", {})
                if isinstance(clear_space, dict):
                    # Default to 0.1 (10% of logo size)
                    clear_space_ratio = 0.1
                else:
                    clear_space_ratio = 0.1
                
                # Extract forbidden backgrounds from restrictions
                forbidden_backgrounds = []
                restrictions = logo_data.get("restrictions", [])
                for restriction in restrictions:
                    if "background" in restriction.lower():
                        # Try to extract color mentions
                        if "red" in restriction.lower():
                            forbidden_backgrounds.append("#FF0000")
                        if "busy" in restriction.lower():
                            forbidden_backgrounds.append("patterns")
                
                # If no forbidden backgrounds found, use empty list
                if not forbidden_backgrounds:
                    forbidden_backgrounds = ["low-contrast", "busy-patterns"]
                
                logo_rule = LogoRule(
                    variant_name=variant_name,
                    url="",  # Will be populated when logo is uploaded
                    min_width_px=min_width_px,
                    clear_space_ratio=clear_space_ratio,
                    forbidden_backgrounds=forbidden_backgrounds,
                )
                logo_rules.append(logo_rule)
                
            except Exception as e:
                logger.warning("logo_rule_parse_failed", error=str(e), data=logo_data)
        
        return logo_rules

    def _extract_voice_tone(
        self,
        parsed_data: Dict[str, Any],
        sections: Dict[str, str]
    ) -> VoiceTone | None:
        """Extract comprehensive VoiceTone object for Digital Twin."""
        voice_data = parsed_data.get("voice")
        if not voice_data:
            logger.warning("voice_data_missing", message="No voice data in Gemini response")
            return None

        logger.debug("extracting_voice_tone", voice_data_keys=list(voice_data.keys()))

        try:
            # Extract adjectives from multiple possible locations
            adjectives = []
            
            # Try personality_traits and tone_attributes (old format)
            if voice_data.get("personality_traits"):
                adjectives.extend(voice_data["personality_traits"])
            if voice_data.get("tone_attributes"):
                adjectives.extend(voice_data["tone_attributes"])
            
            # Try tone_profile (new format from Gemini)
            tone_profile = voice_data.get("tone_profile", {})
            if isinstance(tone_profile, dict):
                if tone_profile.get("adjectives"):
                    adjectives.extend(tone_profile["adjectives"])
                if tone_profile.get("personality"):
                    adjectives.extend(tone_profile["personality"])
                if tone_profile.get("attributes"):
                    adjectives.extend(tone_profile["attributes"])
            elif isinstance(tone_profile, list):
                adjectives.extend(tone_profile)
            
            # Extract forbidden words from multiple possible locations
            forbidden_words = []
            
            # Try language_guidelines (old format)
            lang_guidelines = voice_data.get("language_guidelines", {})
            if isinstance(lang_guidelines, dict):
                avoid_list = lang_guidelines.get("avoid", [])
                forbidden_words.extend(avoid_list)
                
                # Also check vocabulary avoid list
                vocab = lang_guidelines.get("vocabulary", {})
                if isinstance(vocab, dict) and vocab.get("avoid"):
                    forbidden_words.extend(vocab["avoid"])
            
            # Try linguistic_rules (new format from Gemini)
            linguistic_rules = voice_data.get("linguistic_rules", {})
            if isinstance(linguistic_rules, dict):
                if linguistic_rules.get("avoid"):
                    forbidden_words.extend(linguistic_rules["avoid"])
                if linguistic_rules.get("forbidden"):
                    forbidden_words.extend(linguistic_rules["forbidden"])
                if linguistic_rules.get("do_not_use"):
                    forbidden_words.extend(linguistic_rules["do_not_use"])
            
            # Extract example phrases from multiple possible locations
            example_phrases = []
            
            # Try examples (old format)
            examples_data = voice_data.get("examples", {})
            if isinstance(examples_data, dict):
                good_examples = examples_data.get("good", [])
                example_phrases.extend(good_examples)
            elif isinstance(examples_data, list):
                example_phrases.extend(examples_data)
            
            # Try contextual_adaptation (new format from Gemini)
            contextual = voice_data.get("contextual_adaptation", {})
            if isinstance(contextual, dict):
                # Extract example phrases from each context
                for context_name, context_data in contextual.items():
                    if isinstance(context_data, dict) and context_data.get("examples"):
                        example_phrases.extend(context_data["examples"][:2])  # Take 2 from each
                    elif isinstance(context_data, str):
                        example_phrases.append(context_data)
            
            # Try messaging_pillars as fallback
            if not example_phrases and voice_data.get("messaging_pillars"):
                example_phrases = voice_data["messaging_pillars"][:3]
            
            # Try writing_guidelines examples
            if not example_phrases:
                writing_guidelines = voice_data.get("writing_guidelines", {})
                if isinstance(writing_guidelines, dict) and writing_guidelines.get("examples"):
                    example_phrases.extend(writing_guidelines["examples"][:3])
            
            logger.debug(
                "voice_tone_extracted",
                adjectives_count=len(adjectives),
                forbidden_words_count=len(forbidden_words),
                example_phrases_count=len(example_phrases)
            )
            
            voice_tone = VoiceTone(
                adjectives=adjectives if adjectives else ["professional", "friendly"],
                forbidden_words=list(set(forbidden_words)) if forbidden_words else ["jargon"],
                example_phrases=example_phrases if example_phrases else ["Example phrase"],
            )
            
            logger.info("voice_tone_created_successfully")
            return voice_tone
            
        except Exception as e:
            logger.warning("voice_tone_parse_failed", error=str(e), data=voice_data)
            return None

    def _extract_brand_rules(
        self,
        parsed_data: Dict[str, Any],
        sections: Dict[str, str]
    ) -> List[BrandRule]:
        """Extract comprehensive BrandRule objects for Digital Twin."""
        rules = []
        
        # Map Gemini categories to our schema
        category_map = {
            "color": "visual",
            "typography": "visual",
            "logo": "visual",
            "layout": "visual",
            "imagery": "visual",
            "voice": "verbal",
            "tone": "verbal",
            "messaging": "verbal",
            "accessibility": "legal",
            "compliance": "legal",
            "legal": "legal",
        }
        
        # Map severity levels
        severity_map = {
            "critical": "critical",
            "high": "critical",
            "medium": "warning",
            "low": "warning",
        }
        
        for rule_data in parsed_data.get("rules", []):
            try:
                # Map category
                raw_category = rule_data.get("category", "visual").lower()
                category = category_map.get(raw_category, "visual")
                
                # Map severity
                raw_severity = rule_data.get("severity", "warning").lower()
                severity = severity_map.get(raw_severity, "warning")
                
                # Get instruction (use 'rule' field from Gemini)
                instruction = rule_data.get("rule", "")
                
                # Detect if this is a negative constraint (Do Not)
                negative_constraint = any(
                    phrase in instruction.lower()
                    for phrase in ["do not", "don't", "never", "avoid", "prohibited", "forbidden"]
                )
                
                rule = BrandRule(
                    category=category,
                    instruction=instruction,
                    severity=severity,
                    negative_constraint=negative_constraint,
                )
                rules.append(rule)
                
            except Exception as e:
                logger.warning("brand_rule_parse_failed", error=str(e), data=rule_data)
        
        return rules

    def _validate_and_enrich(self, guidelines: BrandGuidelines) -> BrandGuidelines:
        """
        Validate and enrich the Digital Twin with computed properties.
        
        This adds:
        - Accessibility checks
        - Color contrast calculations
        - Relationship mappings
        - Completeness scores
        """
        logger.info("validating_digital_twin")
        
        # Add validation logic here
        # For now, just return as-is
        # Future: Add color contrast checks, completeness scoring, etc.
        
        return guidelines


# Alias for backward compatibility
PDFParser = DigitalTwinPDFParser
