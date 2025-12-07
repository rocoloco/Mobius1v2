"""
Property-based tests for compressed twin injection in image generation.

**Feature: gemini-3-dual-architecture, Property 7: Compressed Twin Injection**

Tests that the Compressed Digital Twin is properly injected into the system prompt.
"""

from hypothesis import given, strategies as st, settings as hypothesis_settings
import pytest
from unittest.mock import patch, MagicMock, call
from mobius.tools.gemini import GeminiClient
from mobius.config import settings
from mobius.models.brand import CompressedDigitalTwin


# Strategy for generating CompressedDigitalTwin with various content
@st.composite
def compressed_twin_with_content_strategy(draw):
    """Generate CompressedDigitalTwin instances with various content."""
    # Generate color lists
    primary_colors = draw(st.lists(
        st.from_regex(r"#[0-9A-F]{6}", fullmatch=True),
        min_size=1,
        max_size=5
    ))
    secondary_colors = draw(st.lists(
        st.from_regex(r"#[0-9A-F]{6}", fullmatch=True),
        min_size=0,
        max_size=5
    ))
    accent_colors = draw(st.lists(
        st.from_regex(r"#[0-9A-F]{6}", fullmatch=True),
        min_size=0,
        max_size=3
    ))
    neutral_colors = draw(st.lists(
        st.from_regex(r"#[0-9A-F]{6}", fullmatch=True),
        min_size=0,
        max_size=5
    ))
    semantic_colors = draw(st.lists(
        st.from_regex(r"#[0-9A-F]{6}", fullmatch=True),
        min_size=0,
        max_size=3
    ))
    
    # Generate font families
    fonts = ["Arial", "Helvetica", "Georgia", "Times New Roman", "Verdana", "Roboto", "Open Sans"]
    font_families = draw(st.lists(
        st.sampled_from(fonts),
        min_size=0,
        max_size=3,
        unique=True
    ))
    
    # Generate visual rules
    visual_dos = draw(st.lists(
        st.text(min_size=10, max_size=100, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))),
        min_size=0,
        max_size=10
    ))
    visual_donts = draw(st.lists(
        st.text(min_size=10, max_size=100, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))),
        min_size=0,
        max_size=10
    ))
    
    # Generate logo requirements
    logo_placement = draw(st.one_of(
        st.none(),
        st.sampled_from(["top-left", "top-right", "center", "bottom-left", "bottom-right"])
    ))
    logo_min_size = draw(st.one_of(
        st.none(),
        st.sampled_from(["50px", "100px", "150px", "200px"])
    ))
    
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


# Property 7: Compressed Twin Injection
@given(
    prompt=st.text(min_size=10, max_size=200),
    compressed_twin=compressed_twin_with_content_strategy()
)
@hypothesis_settings(max_examples=100)
async def test_compressed_twin_injected_into_prompt(
    prompt: str,
    compressed_twin: CompressedDigitalTwin
):
    """
    **Feature: gemini-3-dual-architecture, Property 7: Compressed Twin Injection**
    
    *For any* image generation, the Compressed Digital Twin should be present in the 
    system prompt sent to the Vision Model.
    
    **Validates: Requirements 3.2**
    
    This property test verifies that brand context is properly injected.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = "data:image/png;base64,test"
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image
        try:
            await client.generate_image(prompt, compressed_twin)
        except Exception:
            pass
        
        # Verify generate_content was called
        assert mock_vision_model.generate_content.called, (
            "generate_content should be called"
        )
        
        # Get the prompt that was sent to the model
        call_args = mock_vision_model.generate_content.call_args
        sent_prompt = call_args[0][0][0] if call_args and call_args[0] else ""
        
        # Verify compressed twin colors are in the prompt
        if compressed_twin.primary_colors:
            for color in compressed_twin.primary_colors:
                assert color in sent_prompt, (
                    f"Primary color {color} should be in the system prompt"
                )
        
        # Verify font families are in the prompt if present
        if compressed_twin.font_families:
            for font in compressed_twin.font_families:
                assert font in sent_prompt, (
                    f"Font family {font} should be in the system prompt"
                )
        
        # Verify the user prompt is also included
        assert prompt in sent_prompt, (
            "User prompt should be included in the full prompt"
        )
        
        print(f"✓ Compressed twin properly injected for prompt: '{prompt[:50]}...'")


@given(
    compressed_twin=compressed_twin_with_content_strategy()
)
@hypothesis_settings(max_examples=100)
async def test_all_color_categories_injected(
    compressed_twin: CompressedDigitalTwin
):
    """
    **Feature: gemini-3-dual-architecture, Property 7: Compressed Twin Injection**
    
    *For any* compressed twin with colors, all color categories should be represented 
    in the system prompt.
    
    **Validates: Requirements 3.2**
    
    This property test verifies complete color hierarchy injection.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = "data:image/png;base64,test"
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image
        try:
            await client.generate_image("test prompt", compressed_twin)
        except Exception:
            pass
        
        # Get the prompt that was sent
        call_args = mock_vision_model.generate_content.call_args
        sent_prompt = call_args[0][0][0] if call_args and call_args[0] else ""
        
        # Verify all non-empty color categories are represented
        if compressed_twin.primary_colors:
            assert any(color in sent_prompt for color in compressed_twin.primary_colors), (
                "At least one primary color should be in prompt"
            )
        
        if compressed_twin.secondary_colors:
            assert any(color in sent_prompt for color in compressed_twin.secondary_colors), (
                "At least one secondary color should be in prompt"
            )
        
        if compressed_twin.accent_colors:
            assert any(color in sent_prompt for color in compressed_twin.accent_colors), (
                "At least one accent color should be in prompt"
            )
        
        if compressed_twin.neutral_colors:
            assert any(color in sent_prompt for color in compressed_twin.neutral_colors), (
                "At least one neutral color should be in prompt"
            )
        
        if compressed_twin.semantic_colors:
            assert any(color in sent_prompt for color in compressed_twin.semantic_colors), (
                "At least one semantic color should be in prompt"
            )
        
        print(f"✓ All color categories properly injected")


@given(
    compressed_twin=compressed_twin_with_content_strategy()
)
@hypothesis_settings(max_examples=100)
async def test_visual_rules_injected(
    compressed_twin: CompressedDigitalTwin
):
    """
    **Feature: gemini-3-dual-architecture, Property 7: Compressed Twin Injection**
    
    *For any* compressed twin with visual rules, those rules should be present in 
    the system prompt.
    
    **Validates: Requirements 3.2**
    
    This property test verifies that visual guidelines are injected.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = "data:image/png;base64,test"
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image
        try:
            await client.generate_image("test prompt", compressed_twin)
        except Exception:
            pass
        
        # Get the prompt that was sent
        call_args = mock_vision_model.generate_content.call_args
        sent_prompt = call_args[0][0][0] if call_args and call_args[0] else ""
        
        # Verify visual dos are in the prompt
        if compressed_twin.visual_dos:
            for rule in compressed_twin.visual_dos:
                if rule.strip():  # Only check non-empty rules
                    assert rule in sent_prompt, (
                        f"Visual do rule '{rule[:50]}...' should be in prompt"
                    )
        
        # Verify visual donts are in the prompt
        if compressed_twin.visual_donts:
            for rule in compressed_twin.visual_donts:
                if rule.strip():  # Only check non-empty rules
                    assert rule in sent_prompt, (
                        f"Visual dont rule '{rule[:50]}...' should be in prompt"
                    )
        
        print(f"✓ Visual rules properly injected")


@given(
    compressed_twin=compressed_twin_with_content_strategy()
)
@hypothesis_settings(max_examples=100)
async def test_logo_requirements_injected(
    compressed_twin: CompressedDigitalTwin
):
    """
    **Feature: gemini-3-dual-architecture, Property 7: Compressed Twin Injection**
    
    *For any* compressed twin with logo requirements, those requirements should be 
    present in the system prompt.
    
    **Validates: Requirements 3.2**
    
    This property test verifies that logo guidelines are injected.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = "data:image/png;base64,test"
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image
        try:
            await client.generate_image("test prompt", compressed_twin)
        except Exception:
            pass
        
        # Get the prompt that was sent
        call_args = mock_vision_model.generate_content.call_args
        sent_prompt = call_args[0][0][0] if call_args and call_args[0] else ""
        
        # Verify logo placement is in the prompt if present
        if compressed_twin.logo_placement:
            assert compressed_twin.logo_placement in sent_prompt, (
                f"Logo placement '{compressed_twin.logo_placement}' should be in prompt"
            )
        
        # Verify logo min size is in the prompt if present
        if compressed_twin.logo_min_size:
            assert compressed_twin.logo_min_size in sent_prompt, (
                f"Logo min size '{compressed_twin.logo_min_size}' should be in prompt"
            )
        
        print(f"✓ Logo requirements properly injected")


def test_compressed_twin_injection_includes_60_30_10_rule():
    """
    **Feature: gemini-3-dual-architecture, Property 7: Compressed Twin Injection**
    
    Verify that the system prompt includes the 60-30-10 design rule.
    
    **Validates: Requirements 3.2**
    
    This test ensures proper design guidance is provided to the Vision Model.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = "data:image/png;base64,test"
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Create a simple compressed twin
        compressed_twin = CompressedDigitalTwin(
            primary_colors=["#FF0000"],
            neutral_colors=["#FFFFFF"]
        )
        
        # Call generate_image
        import asyncio
        try:
            asyncio.run(client.generate_image("test prompt", compressed_twin))
        except Exception:
            pass
        
        # Get the prompt that was sent
        call_args = mock_vision_model.generate_content.call_args
        sent_prompt = call_args[0][0][0] if call_args and call_args[0] else ""
        
        # Verify 60-30-10 rule is mentioned
        assert "60-30-10" in sent_prompt or "60%" in sent_prompt, (
            "System prompt should include the 60-30-10 design rule"
        )
        
        print(f"✓ System prompt includes 60-30-10 design rule")


def test_compressed_twin_injection_structure():
    """
    **Feature: gemini-3-dual-architecture, Property 7: Compressed Twin Injection**
    
    Verify that the system prompt has proper structure with sections.
    
    **Validates: Requirements 3.2**
    
    This test ensures the prompt is well-organized for the Vision Model.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = "data:image/png;base64,test"
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Create a comprehensive compressed twin
        compressed_twin = CompressedDigitalTwin(
            primary_colors=["#FF0000"],
            secondary_colors=["#00FF00"],
            accent_colors=["#0000FF"],
            neutral_colors=["#FFFFFF"],
            font_families=["Arial", "Helvetica"],
            visual_dos=["Use primary colors for headers"],
            visual_donts=["Never use Comic Sans"],
            logo_placement="top-left",
            logo_min_size="100px"
        )
        
        # Call generate_image
        import asyncio
        try:
            asyncio.run(client.generate_image("test prompt", compressed_twin))
        except Exception:
            pass
        
        # Get the prompt that was sent
        call_args = mock_vision_model.generate_content.call_args
        sent_prompt = call_args[0][0][0] if call_args and call_args[0] else ""
        
        # Verify prompt has structured sections
        assert "Brand Colors" in sent_prompt or "Colors" in sent_prompt, (
            "System prompt should have a colors section"
        )
        assert "Typography" in sent_prompt or "fonts" in sent_prompt.lower(), (
            "System prompt should have a typography section"
        )
        assert "Guidelines" in sent_prompt or "DO" in sent_prompt, (
            "System prompt should have a guidelines section"
        )
        
        print(f"✓ System prompt has proper structure with sections")
