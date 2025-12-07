"""
Property-based tests for dual model initialization.

**Feature: gemini-3-dual-architecture, Property 1: Dual Model Initialization**

Tests that GeminiClient properly initializes both reasoning and vision models.
"""

from hypothesis import given, strategies as st, settings as hypothesis_settings
import pytest
from unittest.mock import patch, MagicMock
from mobius.tools.gemini import GeminiClient
from mobius.config import settings


# Property 1: Dual Model Initialization
def test_gemini_client_initializes_both_models():
    """
    **Feature: gemini-3-dual-architecture, Property 1: Dual Model Initialization**
    
    *For any* GeminiClient instantiation, both reasoning_model and vision_model 
    attributes should be initialized and non-null.
    
    **Validates: Requirements 1.3, 6.1**
    
    This property test verifies that the dual-model architecture is properly initialized.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_reasoning_model = MagicMock()
        mock_vision_model = MagicMock()
        
        # Configure the mock to return different instances for different model names
        def create_model(model_name):
            if model_name == settings.reasoning_model:
                return mock_reasoning_model
            elif model_name == settings.vision_model:
                return mock_vision_model
            else:
                raise ValueError(f"Unexpected model name: {model_name}")
        
        mock_model_class.side_effect = create_model
        
        # Initialize client
        client = GeminiClient()
        
        # Verify both models are initialized
        assert hasattr(client, 'reasoning_model'), "reasoning_model attribute not found"
        assert hasattr(client, 'vision_model'), "vision_model attribute not found"
        
        # Verify models are non-null
        assert client.reasoning_model is not None, "reasoning_model should not be None"
        assert client.vision_model is not None, "vision_model should not be None"
        
        # Verify they are different instances
        assert client.reasoning_model is not client.vision_model, (
            "reasoning_model and vision_model should be separate instances"
        )
        
        # Verify correct model names were used
        assert mock_model_class.call_count == 2, (
            f"Expected 2 model instantiations, got {mock_model_class.call_count}"
        )
        
        # Verify the models were created with correct names
        call_args = [call[0][0] for call in mock_model_class.call_args_list]
        assert settings.reasoning_model in call_args, (
            f"reasoning_model '{settings.reasoning_model}' not instantiated"
        )
        assert settings.vision_model in call_args, (
            f"vision_model '{settings.vision_model}' not instantiated"
        )
        
        print("✓ GeminiClient properly initializes both reasoning_model and vision_model")


@given(
    api_key=st.text(min_size=10, max_size=100)
)
@hypothesis_settings(max_examples=100)
def test_gemini_client_configures_api_with_key(api_key: str):
    """
    **Feature: gemini-3-dual-architecture, Property 1: Dual Model Initialization**
    
    *For any* valid API key, GeminiClient should configure the Gemini API.
    
    **Validates: Requirements 1.3, 6.1**
    
    This property test verifies that API configuration happens during initialization.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('mobius.tools.gemini.settings') as mock_settings:
        
        # Set up mock settings
        mock_settings.gemini_api_key = api_key
        mock_settings.reasoning_model = "gemini-3-pro-preview"
        mock_settings.vision_model = "gemini-3-pro-image-preview"
        
        # Create mock model instances
        mock_model_class.return_value = MagicMock()
        
        # Initialize client
        client = GeminiClient()
        
        # Verify API was configured with the key
        mock_configure.assert_called_once_with(api_key=api_key)
        
        print(f"✓ GeminiClient properly configures API with key: {api_key[:10]}...")


def test_gemini_client_uses_settings_model_names():
    """
    **Feature: gemini-3-dual-architecture, Property 1: Dual Model Initialization**
    
    Verify that GeminiClient uses model names from settings configuration.
    
    **Validates: Requirements 1.3, 6.1**
    
    This test ensures the client respects configuration for model selection.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_model_class.return_value = MagicMock()
        
        # Initialize client
        client = GeminiClient()
        
        # Verify models were created with names from settings
        calls = mock_model_class.call_args_list
        assert len(calls) == 2, f"Expected 2 model creations, got {len(calls)}"
        
        model_names_used = [call[0][0] for call in calls]
        
        assert settings.reasoning_model in model_names_used, (
            f"reasoning_model '{settings.reasoning_model}' not used"
        )
        assert settings.vision_model in model_names_used, (
            f"vision_model '{settings.vision_model}' not used"
        )
        
        print(f"✓ GeminiClient uses reasoning_model: {settings.reasoning_model}")
        print(f"✓ GeminiClient uses vision_model: {settings.vision_model}")


@given(
    reasoning_model_name=st.text(min_size=5, max_size=50),
    vision_model_name=st.text(min_size=5, max_size=50)
)
@hypothesis_settings(max_examples=100)
def test_gemini_client_respects_custom_model_names(
    reasoning_model_name: str,
    vision_model_name: str
):
    """
    **Feature: gemini-3-dual-architecture, Property 1: Dual Model Initialization**
    
    *For any* valid model names in settings, GeminiClient should use those names.
    
    **Validates: Requirements 1.3, 6.1**
    
    This property test verifies that custom model names are respected.
    """
    # Skip if model names are the same (we want to test different models)
    if reasoning_model_name == vision_model_name:
        return
    
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('mobius.tools.gemini.settings') as mock_settings:
        
        # Set up mock settings with custom model names
        mock_settings.gemini_api_key = "test_key"
        mock_settings.reasoning_model = reasoning_model_name
        mock_settings.vision_model = vision_model_name
        
        # Create mock model instances
        mock_model_class.return_value = MagicMock()
        
        # Initialize client
        client = GeminiClient()
        
        # Verify both custom model names were used
        calls = mock_model_class.call_args_list
        model_names_used = [call[0][0] for call in calls]
        
        assert reasoning_model_name in model_names_used, (
            f"Custom reasoning_model '{reasoning_model_name}' not used"
        )
        assert vision_model_name in model_names_used, (
            f"Custom vision_model '{vision_model_name}' not used"
        )


def test_gemini_client_model_attributes_are_accessible():
    """
    **Feature: gemini-3-dual-architecture, Property 1: Dual Model Initialization**
    
    Verify that model attributes can be accessed after initialization.
    
    **Validates: Requirements 1.3, 6.1**
    
    This test ensures the models are properly stored as instance attributes.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create distinct mock model instances
        mock_reasoning = MagicMock(name="reasoning_model")
        mock_vision = MagicMock(name="vision_model")
        
        # Return different mocks based on model name
        def create_model(model_name):
            if "preview" in model_name and "image" not in model_name:
                return mock_reasoning
            else:
                return mock_vision
        
        mock_model_class.side_effect = create_model
        
        # Initialize client
        client = GeminiClient()
        
        # Verify we can access both model attributes
        reasoning = client.reasoning_model
        vision = client.vision_model
        
        assert reasoning is not None, "reasoning_model should be accessible"
        assert vision is not None, "vision_model should be accessible"
        
        # Verify they are the expected mock objects
        assert reasoning is mock_reasoning or vision is mock_vision, (
            "Model attributes should reference the created model instances"
        )
        
        print("✓ Both model attributes are accessible after initialization")
