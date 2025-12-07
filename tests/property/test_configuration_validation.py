"""
Property-based tests for configuration validation.

**Feature: gemini-3-dual-architecture, Property 21: Configuration Validation**

Tests that configuration properly validates gemini_api_key presence.
"""

from hypothesis import given, strategies as st, settings
import pytest
from pydantic import ValidationError
from mobius.config import Settings


# Property 21: Configuration Validation
@given(
    gemini_key=st.one_of(
        st.just(""),
        st.just("   "),
        st.just("\t"),
        st.just("\n"),
    )
)
@settings(max_examples=100)
def test_empty_gemini_api_key_raises_validation_error(gemini_key: str):
    """
    **Feature: gemini-3-dual-architecture, Property 21: Configuration Validation**
    
    *For any* empty or whitespace-only gemini_api_key, configuration loading should raise a ValidationError.
    
    **Validates: Requirements 1.4**
    
    This property test verifies that the system properly validates the presence of gemini_api_key.
    """
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            gemini_api_key=gemini_key,
            supabase_url="https://test.supabase.co",
            supabase_key="test_key"
        )
    
    # Verify the error message mentions gemini_api_key
    error_str = str(exc_info.value)
    assert "gemini_api_key" in error_str.lower(), (
        f"ValidationError should mention gemini_api_key, got: {error_str}"
    )


@given(
    gemini_key=st.text(min_size=1).filter(lambda x: x.strip() != "")
)
@settings(max_examples=100)
def test_valid_gemini_api_key_succeeds(gemini_key: str):
    """
    **Feature: gemini-3-dual-architecture, Property 21: Configuration Validation**
    
    *For any* non-empty gemini_api_key, configuration loading should succeed.
    
    **Validates: Requirements 1.4**
    
    This property test verifies that valid API keys are accepted.
    """
    settings = Settings(
        gemini_api_key=gemini_key,
        supabase_url="https://test.supabase.co",
        supabase_key="test_key"
    )
    
    assert settings.gemini_api_key == gemini_key
    assert settings.reasoning_model == "gemini-3-pro-preview"
    assert settings.vision_model == "gemini-3-pro-image-preview"


def test_model_constants_are_defined():
    """
    **Feature: gemini-3-dual-architecture, Property 21: Configuration Validation**
    
    Verify that reasoning_model and vision_model constants are properly defined.
    
    **Validates: Requirements 1.1, 1.2**
    
    This test ensures the dual-model architecture constants are present.
    """
    settings = Settings(
        gemini_api_key="test_key",
        supabase_url="https://test.supabase.co",
        supabase_key="test_key"
    )
    
    # Verify reasoning model constant
    assert hasattr(settings, "reasoning_model"), "reasoning_model constant not found"
    assert settings.reasoning_model == "gemini-3-pro-preview", (
        f"Expected reasoning_model to be 'gemini-3-pro-preview', got '{settings.reasoning_model}'"
    )
    
    # Verify vision model constant
    assert hasattr(settings, "vision_model"), "vision_model constant not found"
    assert settings.vision_model == "gemini-3-pro-image-preview", (
        f"Expected vision_model to be 'gemini-3-pro-image-preview', got '{settings.vision_model}'"
    )
    
    print("✓ Both reasoning_model and vision_model constants are properly defined")


def test_fal_api_key_removed():
    """
    **Feature: gemini-3-dual-architecture, Property 21: Configuration Validation**
    
    Verify that fal_api_key field has been removed from Settings.
    
    **Validates: Requirements 1.5**
    
    This test ensures Fal.ai dependencies are removed from configuration.
    """
    settings = Settings(
        gemini_api_key="test_key",
        supabase_url="https://test.supabase.co",
        supabase_key="test_key"
    )
    
    # Verify fal_api_key is not present
    assert not hasattr(settings, "fal_api_key"), (
        "fal_api_key field should be removed from Settings class"
    )
    
    print("✓ fal_api_key field has been removed from Settings")


@given(
    reasoning_model=st.text(min_size=1),
    vision_model=st.text(min_size=1)
)
@settings(max_examples=100)
def test_model_constants_can_be_overridden(reasoning_model: str, vision_model: str):
    """
    **Feature: gemini-3-dual-architecture, Property 21: Configuration Validation**
    
    *For any* valid model names, the system should allow overriding default model constants.
    
    **Validates: Requirements 1.1, 1.2**
    
    This property test verifies that model constants can be configured via environment.
    """
    settings = Settings(
        gemini_api_key="test_key",
        supabase_url="https://test.supabase.co",
        supabase_key="test_key",
        reasoning_model=reasoning_model,
        vision_model=vision_model
    )
    
    assert settings.reasoning_model == reasoning_model
    assert settings.vision_model == vision_model
