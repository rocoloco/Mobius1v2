"""
Property-based tests for image URI multimodal input in auditing.

**Feature: gemini-3-dual-architecture, Property 11: Image URI Multimodal Input**

Tests that audit operations pass image_uri as multimodal input to the Reasoning Model.
"""

from hypothesis import given, strategies as st, settings as hypothesis_settings, HealthCheck
import pytest
from unittest.mock import patch, MagicMock, AsyncMock, call
from mobius.tools.gemini import GeminiClient
from mobius.config import settings
from mobius.models.brand import BrandGuidelines
from mobius.models.compliance import ComplianceScore


# Strategy for generating image URIs
@st.composite
def image_uri_strategy(draw):
    """Generate various image URI formats."""
    uri_type = draw(st.sampled_from(['http', 'https', 'data']))
    
    if uri_type in ['http', 'https']:
        domain = draw(st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Nd')), min_size=5, max_size=20))
        path = draw(st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Nd')), min_size=5, max_size=30))
        return f"{uri_type}://{domain}.com/{path}.jpg"
    else:
        # data URI
        import base64
        data = draw(st.binary(min_size=10, max_size=100))
        encoded = base64.b64encode(data).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded}"


# Property 11: Image URI Multimodal Input
@given(
    image_uri=image_uri_strategy()
)
@hypothesis_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_audit_passes_image_uri_as_multimodal_input(image_uri: str):
    """
    **Feature: gemini-3-dual-architecture, Property 11: Image URI Multimodal Input**
    
    *For any* audit operation, the image_uri from the Generation Node should be passed 
    as multimodal input to the Reasoning Model.
    
    **Validates: Requirements 4.2**
    
    This property test verifies that image data is included in the model input.
    """
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
        
        # Call audit_compliance
        guidelines = BrandGuidelines()
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
        
        # Verify that the call includes multimodal input (list with prompt and image data)
        assert call_args is not None, "generate_content should have been called"
        args, kwargs = call_args
        
        # First argument should be a list containing prompt and image data
        assert len(args) > 0, "generate_content should receive arguments"
        content_list = args[0]
        assert isinstance(content_list, list), "Content should be a list for multimodal input"
        assert len(content_list) >= 2, "Content list should contain prompt and image data"
        
        # Check that one element is a dict with mime_type and data (image)
        has_image_data = any(
            isinstance(item, dict) and 'mime_type' in item and 'data' in item
            for item in content_list
        )
        assert has_image_data, "Multimodal input should include image data with mime_type"
        
        print(f"✓ audit_compliance passes image_uri as multimodal input: {image_uri[:50]}")


@given(
    image_uri=st.sampled_from([
        'https://example.com/image.jpg',
        'http://test.com/photo.png',
    ])
)
@hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_audit_downloads_http_image_uri(image_uri: str):
    """
    **Feature: gemini-3-dual-architecture, Property 11: Image URI Multimodal Input**
    
    *For any* HTTP/HTTPS image URI, the system should download the image before passing 
    it to the Reasoning Model.
    
    **Validates: Requirements 4.2**
    
    This property test verifies that HTTP URIs are properly downloaded.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('httpx.AsyncClient') as mock_httpx:
        
        # Create mock model instance
        mock_reasoning_model = MagicMock()
        mock_model_class.return_value = mock_reasoning_model
        
        # Mock HTTP client
        mock_response = MagicMock()
        mock_response.content = b"downloaded_image_data"
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
        guidelines = BrandGuidelines()
        try:
            await client.audit_compliance(image_uri, guidelines)
        except Exception:
            pass
        
        # Verify HTTP client was used to download the image
        assert mock_client_instance.get.called, (
            "HTTP client should be used to download image from URI"
        )
        
        # Verify the correct URI was requested
        get_call_args = mock_client_instance.get.call_args
        assert get_call_args is not None
        assert image_uri in str(get_call_args), (
            f"HTTP client should request the image URI: {image_uri}"
        )
        
        print(f"✓ audit_compliance downloads HTTP image: {image_uri}")


@given(
    data_size=st.integers(min_value=10, max_value=1000)
)
@hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_audit_decodes_data_uri(data_size: int):
    """
    **Feature: gemini-3-dual-architecture, Property 11: Image URI Multimodal Input**
    
    *For any* data URI, the system should decode the base64 data before passing 
    it to the Reasoning Model.
    
    **Validates: Requirements 4.2**
    
    This property test verifies that data URIs are properly decoded.
    """
    import base64
    
    # Generate random image data
    image_data = bytes([i % 256 for i in range(data_size)])
    encoded_data = base64.b64encode(image_data).decode('utf-8')
    data_uri = f"data:image/jpeg;base64,{encoded_data}"
    
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instance
        mock_reasoning_model = MagicMock()
        mock_model_class.return_value = mock_reasoning_model
        
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
        guidelines = BrandGuidelines()
        try:
            await client.audit_compliance(data_uri, guidelines)
        except Exception:
            pass
        
        # Verify generate_content was called with decoded data
        assert mock_reasoning_model.generate_content.called
        
        call_args = mock_reasoning_model.generate_content.call_args
        args, kwargs = call_args
        content_list = args[0]
        
        # Find the image data in the content list
        image_item = None
        for item in content_list:
            if isinstance(item, dict) and 'data' in item:
                image_item = item
                break
        
        assert image_item is not None, "Image data should be in content list"
        
        # Verify the data was decoded (should be bytes, not base64 string)
        assert isinstance(image_item['data'], bytes), "Image data should be decoded to bytes"
        assert image_item['data'] == image_data, "Decoded data should match original"
        
        print(f"✓ audit_compliance decodes data URI of {data_size} bytes")


def test_audit_multimodal_input_structure():
    """
    **Feature: gemini-3-dual-architecture, Property 11: Image URI Multimodal Input**
    
    Verify that multimodal input has the correct structure for Gemini API.
    
    **Validates: Requirements 4.2**
    
    This test ensures the multimodal input format matches Gemini's expectations.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('httpx.AsyncClient') as mock_httpx:
        
        # Create mock model instance
        mock_reasoning_model = MagicMock()
        mock_model_class.return_value = mock_reasoning_model
        
        # Mock HTTP client
        mock_response = MagicMock()
        mock_response.content = b"test_image_data"
        mock_response.headers = {'content-type': 'image/png'}
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
        import asyncio
        image_uri = "https://example.com/test.png"
        guidelines = BrandGuidelines()
        
        try:
            asyncio.run(client.audit_compliance(image_uri, guidelines))
        except Exception:
            pass
        
        # Verify the structure of the multimodal input
        call_args = mock_reasoning_model.generate_content.call_args
        args, kwargs = call_args
        content_list = args[0]
        
        # Should have at least 2 items: prompt (str) and image (dict)
        assert len(content_list) >= 2
        
        # First item should be the prompt (string)
        assert isinstance(content_list[0], str), "First item should be audit prompt"
        
        # Second item should be image data (dict with mime_type and data)
        image_item = content_list[1]
        assert isinstance(image_item, dict), "Image should be a dict"
        assert 'mime_type' in image_item, "Image dict should have mime_type"
        assert 'data' in image_item, "Image dict should have data"
        assert image_item['mime_type'] == 'image/png', "mime_type should match response"
        assert image_item['data'] == b"test_image_data", "data should be image bytes"
        
        print("✓ Multimodal input has correct structure for Gemini API")
