"""
Property-based tests for vision model usage in image generation.

**Feature: gemini-3-dual-architecture, Property 6: Vision Model for Generation**

Tests that image generation uses the vision_model instance.
"""

from hypothesis import given, strategies as st, settings as hypothesis_settings
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from mobius.tools.gemini import GeminiClient
from mobius.config import settings
from mobius.models.brand import CompressedDigitalTwin


# Strategy for generating prompts
@st.composite
def prompt_strategy(draw):
    """Generate random image generation prompts."""
    templates = [
        "Create a {adjective} {noun} with {color} background",
        "Design a {style} poster featuring {element}",
        "Generate a {mood} image with {composition}",
        "Make a {format} showing {subject}",
    ]
    
    adjectives = ["modern", "vintage", "minimalist", "bold", "elegant"]
    nouns = ["banner", "card", "flyer", "logo", "illustration"]
    colors = ["blue", "red", "green", "purple", "orange"]
    styles = ["corporate", "playful", "professional", "artistic"]
    elements = ["text", "shapes", "patterns", "gradients"]
    moods = ["energetic", "calm", "dramatic", "friendly"]
    compositions = ["centered layout", "asymmetric design", "grid structure"]
    subjects = ["product", "service", "concept", "brand"]
    formats = ["social media post", "web banner", "print ad"]
    
    template = draw(st.sampled_from(templates))
    
    # Fill in template
    prompt = template.format(
        adjective=draw(st.sampled_from(adjectives)),
        noun=draw(st.sampled_from(nouns)),
        color=draw(st.sampled_from(colors)),
        style=draw(st.sampled_from(styles)),
        element=draw(st.sampled_from(elements)),
        mood=draw(st.sampled_from(moods)),
        composition=draw(st.sampled_from(compositions)),
        subject=draw(st.sampled_from(subjects)),
        format=draw(st.sampled_from(formats))
    )
    
    return prompt


# Strategy for generating CompressedDigitalTwin
@st.composite
def compressed_twin_strategy(draw):
    """Generate random CompressedDigitalTwin instances."""
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
    
    # Generate font families
    fonts = ["Arial", "Helvetica", "Georgia", "Times New Roman", "Verdana"]
    font_families = draw(st.lists(
        st.sampled_from(fonts),
        min_size=0,
        max_size=3,
        unique=True
    ))
    
    # Generate visual rules
    visual_dos = draw(st.lists(
        st.text(min_size=10, max_size=100),
        min_size=0,
        max_size=10
    ))
    visual_donts = draw(st.lists(
        st.text(min_size=10, max_size=100),
        min_size=0,
        max_size=10
    ))
    
    return CompressedDigitalTwin(
        primary_colors=primary_colors,
        secondary_colors=secondary_colors,
        accent_colors=accent_colors,
        neutral_colors=neutral_colors,
        font_families=font_families,
        visual_dos=visual_dos,
        visual_donts=visual_donts
    )


# Property 6: Vision Model for Generation
@given(
    prompt=prompt_strategy(),
    compressed_twin=compressed_twin_strategy()
)
@hypothesis_settings(max_examples=100)
async def test_generate_image_uses_vision_model(
    prompt: str,
    compressed_twin: CompressedDigitalTwin
):
    """
    **Feature: gemini-3-dual-architecture, Property 6: Vision Model for Generation**
    
    *For any* image generation request, the system should use the vision_model instance 
    (gemini-3-pro-image-preview) to generate images.
    
    **Validates: Requirements 3.1, 6.3**
    
    This property test verifies that the correct model is used for image generation.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_reasoning_model = MagicMock()
        mock_vision_model = MagicMock()
        
        # Configure mock to return different instances
        def create_model(model_name):
            if model_name == settings.reasoning_model:
                return mock_reasoning_model
            elif model_name == settings.vision_model:
                return mock_vision_model
            else:
                raise ValueError(f"Unexpected model name: {model_name}")
        
        mock_model_class.side_effect = create_model
        
        # Mock the generate_content method to return a valid result with image URI
        mock_result = MagicMock()
        mock_result.text = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image
        try:
            await client.generate_image(prompt, compressed_twin)
        except Exception as e:
            # We're testing model selection, not full functionality
            pass
        
        # Verify vision_model.generate_content was called
        assert mock_vision_model.generate_content.called, (
            "vision_model.generate_content should be called for image generation"
        )
        
        # Verify reasoning_model was NOT used for image generation
        assert not mock_reasoning_model.generate_content.called, (
            "reasoning_model should NOT be used for image generation"
        )
        
        print(f"✓ generate_image uses vision_model for prompt: '{prompt[:50]}...'")


@given(
    prompt=prompt_strategy(),
    compressed_twin=compressed_twin_strategy()
)
@hypothesis_settings(max_examples=50)
async def test_image_generation_never_uses_reasoning_model(
    prompt: str,
    compressed_twin: CompressedDigitalTwin
):
    """
    **Feature: gemini-3-dual-architecture, Property 6: Vision Model for Generation**
    
    *For any* image generation operation, the reasoning_model should never be used.
    
    **Validates: Requirements 3.1, 6.3**
    
    This property test verifies strict model separation for generation operations.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_reasoning_model = MagicMock()
        mock_vision_model = MagicMock()
        
        # Configure mock to return different instances
        def create_model(model_name):
            if model_name == settings.reasoning_model:
                return mock_reasoning_model
            elif model_name == settings.vision_model:
                return mock_vision_model
            else:
                raise ValueError(f"Unexpected model name: {model_name}")
        
        mock_model_class.side_effect = create_model
        
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
        
        # Verify reasoning_model was never called for content generation
        assert not mock_reasoning_model.generate_content.called, (
            "reasoning_model should NEVER be used for image generation operations"
        )
        
        print(f"✓ Image generation correctly avoids reasoning_model for prompt: '{prompt[:50]}...'")


def test_generate_image_uses_correct_model_name():
    """
    **Feature: gemini-3-dual-architecture, Property 6: Vision Model for Generation**
    
    Verify that generate_image logs the correct model name.
    
    **Validates: Requirements 3.1, 6.3**
    
    This test ensures proper logging of model usage.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('mobius.tools.gemini.logger') as mock_logger:
        
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
        
        # Create a simple test
        import asyncio
        prompt = "Create a test image"
        compressed_twin = CompressedDigitalTwin(primary_colors=["#FF0000"])
        
        try:
            asyncio.run(client.generate_image(prompt, compressed_twin))
        except Exception:
            pass
        
        # Verify logger was called with correct model_name
        log_calls = [call for call in mock_logger.info.call_args_list]
        
        # Check that at least one log call includes the vision model name
        model_logged = any(
            settings.vision_model in str(call)
            for call in log_calls
        )
        
        assert model_logged, (
            f"vision_model '{settings.vision_model}' should be logged during generation"
        )
        
        print(f"✓ generate_image logs model_name: {settings.vision_model}")


@given(
    prompt=prompt_strategy(),
    compressed_twin=compressed_twin_strategy()
)
@hypothesis_settings(max_examples=100)
async def test_generate_image_uses_vision_model_instance(
    prompt: str,
    compressed_twin: CompressedDigitalTwin
):
    """
    **Feature: gemini-3-dual-architecture, Property 6: Vision Model for Generation**
    
    *For any* generation request, the client.vision_model instance should be used.
    
    **Validates: Requirements 3.1, 6.3**
    
    This property test verifies that the correct instance attribute is accessed.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_reasoning_model = MagicMock()
        mock_vision_model = MagicMock()
        
        # Configure mock to return different instances
        def create_model(model_name):
            if model_name == settings.reasoning_model:
                return mock_reasoning_model
            elif model_name == settings.vision_model:
                return mock_vision_model
            else:
                raise ValueError(f"Unexpected model name: {model_name}")
        
        mock_model_class.side_effect = create_model
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = "data:image/png;base64,test"
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Verify the vision_model attribute exists
        assert hasattr(client, 'vision_model'), "Client should have vision_model attribute"
        assert client.vision_model is mock_vision_model, "vision_model should be the correct instance"
        
        # Call generate_image
        try:
            await client.generate_image(prompt, compressed_twin)
        except Exception:
            pass
        
        # Verify the correct instance was used
        assert mock_vision_model.generate_content.called, (
            "client.vision_model instance should be used for generation"
        )
        
        print(f"✓ generate_image uses client.vision_model instance")
