"""
Property-based tests for reasoning model usage in PDF processing.

**Feature: gemini-3-dual-architecture, Property 2: Reasoning Model for PDF Processing**

Tests that PDF ingestion uses the reasoning_model instance for extraction.
"""

from hypothesis import given, strategies as st, settings as hypothesis_settings, HealthCheck
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from mobius.tools.gemini import GeminiClient
from mobius.config import settings
from mobius.models.brand import BrandGuidelines, CompressedDigitalTwin


# Strategy for generating PDF bytes
@st.composite
def pdf_bytes_strategy(draw):
    """Generate mock PDF bytes."""
    # Generate random bytes that look like a PDF header
    size = draw(st.integers(min_value=100, max_value=10000))
    return b"%PDF-1.4\n" + bytes([draw(st.integers(min_value=0, max_value=255)) for _ in range(size)])


# Property 2: Reasoning Model for PDF Processing
@given(
    pdf_data=pdf_bytes_strategy()
)
@hypothesis_settings(max_examples=100)
async def test_extract_brand_guidelines_uses_reasoning_model(pdf_data: bytes):
    """
    **Feature: gemini-3-dual-architecture, Property 2: Reasoning Model for PDF Processing**
    
    *For any* PDF ingestion request, the system should use the reasoning_model instance 
    (gemini-3-pro-preview) to extract brand guidelines.
    
    **Validates: Requirements 2.1, 6.2**
    
    This property test verifies that the correct model is used for PDF processing.
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
        
        # Mock the generate_content method to return valid BrandGuidelines
        mock_result = MagicMock()
        mock_result.text = BrandGuidelines().model_dump_json()
        mock_reasoning_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call extract_brand_guidelines
        try:
            await client.extract_brand_guidelines(pdf_data)
        except Exception:
            # We're testing model selection, not full functionality
            pass
        
        # Verify reasoning_model.generate_content was called
        assert mock_reasoning_model.generate_content.called, (
            "reasoning_model.generate_content should be called for PDF processing"
        )
        
        # Verify vision_model was NOT used for PDF processing
        assert not mock_vision_model.generate_content.called, (
            "vision_model should NOT be used for PDF processing"
        )
        
        print(f"✓ extract_brand_guidelines uses reasoning_model for PDF of {len(pdf_data)} bytes")


@given(
    pdf_data=pdf_bytes_strategy()
)
@hypothesis_settings(max_examples=100)
async def test_extract_compressed_guidelines_uses_reasoning_model(pdf_data: bytes):
    """
    **Feature: gemini-3-dual-architecture, Property 2: Reasoning Model for PDF Processing**
    
    *For any* compressed guidelines extraction, the system should use the reasoning_model instance.
    
    **Validates: Requirements 2.1, 6.2**
    
    This property test verifies that compressed extraction uses the correct model.
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
        
        # Mock the generate_content method to return valid CompressedDigitalTwin
        mock_result = MagicMock()
        mock_result.text = CompressedDigitalTwin().model_dump_json()
        mock_reasoning_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call extract_compressed_guidelines
        try:
            await client.extract_compressed_guidelines(pdf_data)
        except Exception:
            # We're testing model selection, not full functionality
            pass
        
        # Verify reasoning_model.generate_content was called
        assert mock_reasoning_model.generate_content.called, (
            "reasoning_model.generate_content should be called for compressed extraction"
        )
        
        # Verify vision_model was NOT used
        assert not mock_vision_model.generate_content.called, (
            "vision_model should NOT be used for compressed extraction"
        )
        
        print(f"✓ extract_compressed_guidelines uses reasoning_model for PDF of {len(pdf_data)} bytes")


def test_extract_brand_guidelines_uses_correct_model_name():
    """
    **Feature: gemini-3-dual-architecture, Property 2: Reasoning Model for PDF Processing**
    
    Verify that extract_brand_guidelines logs the correct model name.
    
    **Validates: Requirements 2.1, 6.2**
    
    This test ensures proper logging of model usage.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('mobius.tools.gemini.logger') as mock_logger:
        
        # Create mock model instances
        mock_reasoning_model = MagicMock()
        mock_model_class.return_value = mock_reasoning_model
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = BrandGuidelines().model_dump_json()
        mock_reasoning_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Create a simple test
        import asyncio
        pdf_data = b"%PDF-1.4\ntest"
        
        try:
            asyncio.run(client.extract_brand_guidelines(pdf_data))
        except Exception:
            pass
        
        # Verify logger was called with correct model_name
        log_calls = [call for call in mock_logger.info.call_args_list]
        
        # Check that at least one log call includes the reasoning model name
        model_logged = any(
            settings.reasoning_model in str(call)
            for call in log_calls
        )
        
        assert model_logged, (
            f"reasoning_model '{settings.reasoning_model}' should be logged during extraction"
        )
        
        print(f"✓ extract_brand_guidelines logs model_name: {settings.reasoning_model}")


def test_extract_compressed_guidelines_uses_correct_model_name():
    """
    **Feature: gemini-3-dual-architecture, Property 2: Reasoning Model for PDF Processing**
    
    Verify that extract_compressed_guidelines logs the correct model name.
    
    **Validates: Requirements 2.1, 6.2**
    
    This test ensures proper logging of model usage for compressed extraction.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('mobius.tools.gemini.logger') as mock_logger:
        
        # Create mock model instances
        mock_reasoning_model = MagicMock()
        mock_model_class.return_value = mock_reasoning_model
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = CompressedDigitalTwin().model_dump_json()
        mock_reasoning_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Create a simple test
        import asyncio
        pdf_data = b"%PDF-1.4\ntest"
        
        try:
            asyncio.run(client.extract_compressed_guidelines(pdf_data))
        except Exception:
            pass
        
        # Verify logger was called with correct model_name
        log_calls = [call for call in mock_logger.info.call_args_list]
        
        # Check that at least one log call includes the reasoning model name
        model_logged = any(
            settings.reasoning_model in str(call)
            for call in log_calls
        )
        
        assert model_logged, (
            f"reasoning_model '{settings.reasoning_model}' should be logged during compressed extraction"
        )
        
        print(f"✓ extract_compressed_guidelines logs model_name: {settings.reasoning_model}")


@given(
    pdf_data=pdf_bytes_strategy()
)
@hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.data_too_large])
async def test_pdf_processing_never_uses_vision_model(pdf_data: bytes):
    """
    **Feature: gemini-3-dual-architecture, Property 2: Reasoning Model for PDF Processing**
    
    *For any* PDF processing operation, the vision_model should never be used.
    
    **Validates: Requirements 2.1, 6.2**
    
    This property test verifies strict model separation for PDF operations.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances with call tracking
        mock_reasoning_model = MagicMock()
        mock_vision_model = MagicMock()
        
        # Track which model is used
        vision_model_used = False
        
        def create_model(model_name):
            nonlocal vision_model_used
            if model_name == settings.reasoning_model:
                return mock_reasoning_model
            elif model_name == settings.vision_model:
                vision_model_used = True
                return mock_vision_model
            else:
                raise ValueError(f"Unexpected model name: {model_name}")
        
        mock_model_class.side_effect = create_model
        
        # Mock generate_content
        mock_result = MagicMock()
        mock_result.text = BrandGuidelines().model_dump_json()
        mock_reasoning_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Try both PDF processing methods
        try:
            await client.extract_brand_guidelines(pdf_data)
        except Exception:
            pass
        
        try:
            mock_result.text = CompressedDigitalTwin().model_dump_json()
            await client.extract_compressed_guidelines(pdf_data)
        except Exception:
            pass
        
        # Verify vision_model was never called for content generation
        assert not mock_vision_model.generate_content.called, (
            "vision_model should NEVER be used for PDF processing operations"
        )
        
        print(f"✓ PDF processing correctly avoids vision_model for {len(pdf_data)} bytes")
