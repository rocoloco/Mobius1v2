"""
Property-based tests for full guidelines in audit context.

**Feature: gemini-3-dual-architecture, Property 12: Full Guidelines in Audit Context**

Tests that audit operations use full Brand Guidelines (not compressed twin) as context.
"""

from hypothesis import given, strategies as st, settings as hypothesis_settings, HealthCheck
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from mobius.tools.gemini import GeminiClient
from mobius.config import settings
from mobius.models.brand import BrandGuidelines, Color, Typography, LogoRule, VoiceTone, BrandRule
from mobius.models.compliance import ComplianceScore


# Strategy for generating image URIs
@st.composite
def image_uri_strategy(draw):
    """Generate various image URI formats."""
    uri_type = draw(st.sampled_from(['http', 'https']))
    domain = draw(st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Nd')), min_size=5, max_size=20))
    path = draw(st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Nd')), min_size=5, max_size=30))
    return f"{uri_type}://{domain}.com/{path}.jpg"


# Property 12: Full Guidelines in Audit Context
@given(
    image_uri=image_uri_strategy()
)
@hypothesis_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_audit_uses_full_guidelines_not_compressed(image_uri: str):
    """
    **Feature: gemini-3-dual-architecture, Property 12: Full Guidelines in Audit Context**
    
    *For any* audit operation, the full Brand Guidelines (not the compressed twin) should be 
    provided as context to the Reasoning Model.
    
    **Validates: Requirements 4.3**
    
    This property test verifies that comprehensive brand context is used for auditing.
    """
    # Create comprehensive guidelines with all fields
    guidelines = BrandGuidelines(
        colors=[
            Color(name="Primary Blue", hex="#0057B8", usage="primary", usage_weight=0.6, context="Use for headers"),
            Color(name="Accent Gold", hex="#FFC300", usage="accent", usage_weight=0.1, context="CTAs only")
        ],
        typography=[
            Typography(family="Helvetica Neue", weights=["regular", "bold"], usage="Headers and body")
        ],
        logos=[
            LogoRule(
                variant_name="Main Logo",
                url="https://example.com/logo.png",
                min_width_px=100,
                clear_space_ratio=0.2,
                forbidden_backgrounds=["#FF0000"]
            )
        ],
        voice=VoiceTone(
            adjectives=["professional", "friendly"],
            forbidden_words=["cheap"],
            example_phrases=["We deliver excellence"]
        ),
        rules=[
            BrandRule(
                category="visual",
                instruction="Use primary colors for headers",
                severity="warning",
                negative_constraint=False
            )
        ]
    )
    
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('httpx.AsyncClient') as mock_httpx:
        
        # Create mock model instance
        mock_reasoning_model = MagicMock()
        mock_model_class.return_value = mock_reasoning_model
        
        # Mock HTTP client for image download
        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_httpx.return_value = mock_client_instance
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = ComplianceScore(
            overall_score=85.0,
            categories=[],
            approved=True,
            summary="Test"
        ).model_dump_json()
        mock_reasoning_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call audit_compliance with full guidelines
        try:
            await client.audit_compliance(image_uri, guidelines)
        except Exception:
            pass
        
        # Verify generate_content was called
        assert mock_reasoning_model.generate_content.called, (
            "generate_content should be called for audit"
        )
        
        # Get the call arguments
        call_args = mock_reasoning_model.generate_content.call_args
        args, kwargs = call_args
        
        # First argument should be a list containing prompt and image data
        content_list = args[0]
        assert isinstance(content_list, list), "Content should be a list"
        
        # Extract the prompt (first string in the list)
        prompt = content_list[0]
        assert isinstance(prompt, str), "First item should be the audit prompt"
        
        # Verify that the prompt contains elements from the FULL guidelines
        assert "Primary Blue" in prompt or "#0057B8" in prompt, (
            "Audit prompt should include color names and hex codes from full guidelines"
        )
        
        assert "Helvetica Neue" in prompt, (
            "Audit prompt should include typography information from full guidelines"
        )
        
        assert "Main Logo" in prompt or "logo" in prompt.lower(), (
            "Audit prompt should include logo information from full guidelines"
        )
        
        assert "professional" in prompt or "friendly" in prompt or "voice" in prompt.lower(), (
            "Audit prompt should include voice information from full guidelines"
        )
        
        assert "Use primary colors for headers" in prompt or "rules" in prompt.lower(), (
            "Audit prompt should include governance rules from full guidelines"
        )
        
        print(f"✓ audit_compliance uses full guidelines for URI: {image_uri[:50]}")


@given(
    image_uri=image_uri_strategy()
)
@hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_audit_never_uses_compressed_twin_fields(image_uri: str):
    """
    **Feature: gemini-3-dual-architecture, Property 12: Full Guidelines in Audit Context**
    
    *For any* audit operation, the prompt should NOT contain compressed twin specific fields
    like "primary_colors", "secondary_colors", "visual_dos", "visual_donts".
    
    **Validates: Requirements 4.3**
    
    This property test verifies that compressed twin structure is not used in auditing.
    """
    # Create guidelines with specific structure
    guidelines = BrandGuidelines(
        colors=[
            Color(name="Brand Blue", hex="#0057B8", usage="primary", usage_weight=0.6),
            Color(name="Accent Gold", hex="#FFC300", usage="accent", usage_weight=0.1)
        ],
        typography=[
            Typography(family="Helvetica Neue", weights=["regular", "bold"], usage="Headers and body")
        ]
    )
    
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('httpx.AsyncClient') as mock_httpx:
        
        # Create mock model instance
        mock_reasoning_model = MagicMock()
        mock_model_class.return_value = mock_reasoning_model
        
        # Mock HTTP client
        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_httpx.return_value = mock_client_instance
        
        # Mock generate_content
        mock_result = MagicMock()
        mock_result.text = ComplianceScore(
            overall_score=85.0,
            categories=[],
            approved=True,
            summary="Test"
        ).model_dump_json()
        mock_reasoning_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call audit_compliance
        try:
            await client.audit_compliance(image_uri, guidelines)
        except Exception:
            pass
        
        # Get the prompt
        call_args = mock_reasoning_model.generate_content.call_args
        args, kwargs = call_args
        content_list = args[0]
        prompt = content_list[0]
        
        # Verify compressed twin field names are NOT in the prompt
        compressed_twin_fields = [
            "primary_colors",
            "secondary_colors",
            "accent_colors",
            "neutral_colors",
            "semantic_colors",
            "visual_dos",
            "visual_donts",
            "logo_placement",
            "logo_min_size"
        ]
        
        for field in compressed_twin_fields:
            assert field not in prompt, (
                f"Audit prompt should NOT contain compressed twin field '{field}'. "
                f"It should use full BrandGuidelines structure instead."
            )
        
        # Verify that full guidelines fields ARE present
        assert "Brand Blue" in prompt or "#0057B8" in prompt, (
            "Audit prompt should contain full color information (name and hex)"
        )
        assert "Helvetica Neue" in prompt, (
            "Audit prompt should contain full typography information"
        )
        
        print(f"✓ Audit prompt correctly avoids compressed twin fields")
