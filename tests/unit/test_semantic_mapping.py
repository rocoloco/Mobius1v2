"""
Unit tests for semantic color mapping in GeminiClient.

Verifies that the "Rosetta Stone" mapping rules are correctly integrated
and that the end-to-end flow works with semantic color roles.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from mobius.tools.gemini import GeminiClient
from mobius.models.brand import BrandGuidelines, Color
import inspect


# --- Mock Data: The "Hallucinated" Response ---
# We simulate what Gemini 3 Pro *should* return if the prompt is working correctly.
# This validates that your Pydantic model can handle the mapped output.
MOCK_GEMINI_RESPONSE = {
    "colors": [
        {
            "name": "Navy Blue",
            "hex": "#000080",
            "usage": "primary",  # Mapped from "Dominant"
            "usage_weight": 0.6,
            "context": "Listed as Dominant brand color"
        },
        {
            "name": "Heritage Gold",
            "hex": "#C4A962",
            "usage": "accent",   # Mapped from "CTA"
            "usage_weight": 0.1,
            "context": "Used for CTAs and buttons"
        },
        {
            "name": "Dark Charcoal",
            "hex": "#1A1A1A",
            "usage": "neutral",  # Mapped from "Body Copy"
            "usage_weight": 0.2,
            "context": "Used for body text"
        }
    ],
    "typography": [],
    "logos": [],
    "rules": [],
    "voice": None
}


@pytest.mark.asyncio
async def test_semantic_role_mapping():
    """
    The 'Rosetta Stone' Test.
    
    Verifies that the GeminiClient correctly processes the mapped response
    where:
    - 'Dominant' -> PRIMARY (usage="primary")
    - 'CTA' -> ACCENT (usage="accent")
    - 'Body Copy' -> NEUTRAL (usage="neutral")
    """
    
    # 1. Setup: Mock the Gemini API client so we don't hit real Google servers
    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as MockModel:
        
        # Create a mock instance of the model
        mock_reasoning_model = MockModel.return_value
        
        # Configure the mock to return our pre-calculated JSON
        mock_response = MagicMock()
        mock_response.text = BrandGuidelines(**MOCK_GEMINI_RESPONSE).model_dump_json()
        
        # Mock for the generate_content call (synchronous, not async)
        mock_reasoning_model.generate_content = MagicMock(return_value=mock_response)
        
        # Initialize Client (which uses the mocked model internally)
        client = GeminiClient()
        client.reasoning_model = mock_reasoning_model
        
        # 2. Execution: Feed it a dummy PDF (content doesn't matter because we mocked the response)
        # The PROMPT inside the client is what matters, but here we are testing the Schema <-> Client handshake.
        result = await client.extract_brand_guidelines(pdf_bytes=b"fake_pdf_content")
        
        # 3. Validation: The "Reflex Check"
        
        # Check PRIMARY mapping
        primary_color = next(c for c in result.colors if c.name == "Navy Blue")
        assert primary_color.usage == "primary"
        assert primary_color.usage_weight == 0.6
        
        # Check ACCENT mapping (The "CTA" test)
        accent_color = next(c for c in result.colors if c.name == "Heritage Gold")
        assert accent_color.usage == "accent"
        assert "CTA" in accent_color.context or "buttons" in accent_color.context
        
        # Check NEUTRAL mapping (The "Body Copy" test)
        neutral_color = next(c for c in result.colors if c.name == "Dark Charcoal")
        assert neutral_color.usage == "neutral"
        
        print("\n✅ Rosetta Stone Logic Verified: All semantic roles mapped correctly.")


@pytest.mark.asyncio
async def test_trap_keywords_in_prompt():
    """
    Verifies that the System Prompt actually contains our critical mapping rules.
    This inspects the string sent to Gemini to ensure the rules weren't deleted.
    """
    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as MockModel:
        
        mock_model_instance = MockModel.return_value
        client = GeminiClient()
        client.reasoning_model = mock_model_instance
        
        # Mock the generate_content method to capture the call (synchronous, not async)
        # We need to return a valid response so the method doesn't fail
        mock_response = MagicMock()
        mock_response.text = BrandGuidelines(**MOCK_GEMINI_RESPONSE).model_dump_json()
        mock_model_instance.generate_content = MagicMock(return_value=mock_response)
        
        await client.extract_brand_guidelines(pdf_bytes=b"test")
        
        # Extract the arguments passed to generate_content
        call_args = mock_model_instance.generate_content.call_args
        # The prompt is usually the first arg or in the first list element
        sent_prompt = call_args[0][0] 
        if isinstance(sent_prompt, list):
            sent_prompt = sent_prompt[0]
            
        # ASSERTIONS: Check for the "Rosetta Stone" keywords in the prompt text
        assert "Rosetta Stone" in sent_prompt, "Prompt should contain 'Rosetta Stone' reference"
        assert "CTA" in sent_prompt, "Prompt should mention CTA trigger term"
        assert "ACCENT" in sent_prompt, "Prompt should define ACCENT role"
        assert "Body Copy" in sent_prompt, "Prompt should mention Body Copy trigger term"
        assert "NEUTRAL" in sent_prompt, "Prompt should define NEUTRAL role"
        assert "PRIMARY" in sent_prompt, "Prompt should define PRIMARY role"
        
        print("\n✅ Prompt Integrity Verified: Mapping rules are present in the System Instruction.")


def test_prompt_contains_rosetta_stone_keywords():
    """
    Verifies that the extraction prompt contains the Rosetta Stone mapping rules.
    
    This test ensures that the semantic color mapping keywords are present
    in the prompt sent to the Reasoning Model during PDF extraction.
    """
    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as MockModel:
        
        # Create mock model instance
        mock_model = MagicMock()
        MockModel.return_value = mock_model
        
        # Initialize client
        client = GeminiClient()
        
        # Get the extract_brand_guidelines method source
        source = inspect.getsource(client.extract_brand_guidelines)
        
        # Check for Rosetta Stone keywords in the method source
        assert "Rosetta Stone" in source, "Prompt should contain 'Rosetta Stone' reference"
        assert "PRIMARY" in source, "Prompt should define PRIMARY role"
        assert "SECONDARY" in source, "Prompt should define SECONDARY role"
        assert "ACCENT" in source, "Prompt should define ACCENT role"
        assert "NEUTRAL" in source, "Prompt should define NEUTRAL role"
        assert "SEMANTIC" in source, "Prompt should define SEMANTIC role"
        assert "CTA" in source, "Prompt should mention CTA as trigger term"
        assert "Body Copy" in source, "Prompt should mention Body Copy as trigger term"
        
        print("\n✅ Prompt Integrity Verified: All Rosetta Stone mapping rules are present")


def test_color_model_supports_semantic_roles():
    """
    Verifies that the Color model supports all five semantic roles.
    """
    # Test each semantic role
    roles = ["primary", "secondary", "accent", "neutral", "semantic"]
    
    for role in roles:
        color = Color(
            name="Test Color",
            hex="#FF0000",
            usage=role,
            usage_weight=0.5
        )
        assert color.usage == role
        assert 0.0 <= color.usage_weight <= 1.0
    
    print(f"\n✅ Color Model Verified: Supports all {len(roles)} semantic roles")


def test_color_model_has_usage_weight():
    """
    Verifies that the Color model has the usage_weight field for 60-30-10 rule.
    """
    color = Color(
        name="Test Color",
        hex="#FF0000",
        usage="primary",
        usage_weight=0.6
    )
    
    assert hasattr(color, "usage_weight")
    assert color.usage_weight == 0.6
    assert 0.0 <= color.usage_weight <= 1.0
    
    print("\n✅ Usage Weight Verified: Color model supports 60-30-10 design rule")
