"""
Property-based tests for image URI return format.

**Feature: gemini-3-dual-architecture, Property 8: Image URI Return Format**

Tests that generate_image returns a valid image_uri string.
"""

from hypothesis import given, strategies as st, settings as hypothesis_settings
import pytest
from unittest.mock import patch, MagicMock
from mobius.tools.gemini import GeminiClient
from mobius.config import settings
from mobius.models.brand import CompressedDigitalTwin
import re


# Strategy for generating mock image URIs
@st.composite
def image_uri_strategy(draw):
    """Generate various valid image URI formats."""
    uri_type = draw(st.sampled_from(["data_uri", "http_url", "https_url"]))
    
    if uri_type == "data_uri":
        # Data URI format: data:image/png;base64,<base64_data>
        mime_types = ["image/png", "image/jpeg", "image/jpg", "image/webp"]
        mime_type = draw(st.sampled_from(mime_types))
        # Generate random base64-like string
        base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        base64_data = ''.join(draw(st.lists(
            st.sampled_from(list(base64_chars)),
            min_size=20,
            max_size=100
        )))
        return f"data:{mime_type};base64,{base64_data}"
    
    elif uri_type == "http_url":
        # HTTP URL format
        domains = ["example.com", "images.example.com", "cdn.example.com"]
        domain = draw(st.sampled_from(domains))
        path = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))))
        extensions = [".png", ".jpg", ".jpeg", ".webp"]
        ext = draw(st.sampled_from(extensions))
        return f"http://{domain}/{path}{ext}"
    
    else:  # https_url
        # HTTPS URL format
        domains = ["example.com", "images.example.com", "cdn.example.com", "storage.googleapis.com"]
        domain = draw(st.sampled_from(domains))
        path = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))))
        extensions = [".png", ".jpg", ".jpeg", ".webp"]
        ext = draw(st.sampled_from(extensions))
        return f"https://{domain}/{path}{ext}"


# Strategy for generating CompressedDigitalTwin
@st.composite
def compressed_twin_strategy(draw):
    """Generate random CompressedDigitalTwin instances."""
    return CompressedDigitalTwin(
        primary_colors=draw(st.lists(
            st.from_regex(r"#[0-9A-F]{6}", fullmatch=True),
            min_size=1,
            max_size=3
        ))
    )


# Property 8: Image URI Return Format
@given(
    prompt=st.text(min_size=10, max_size=200),
    compressed_twin=compressed_twin_strategy(),
    mock_uri=image_uri_strategy()
)
@hypothesis_settings(max_examples=100)
async def test_generate_image_returns_image_uri(
    prompt: str,
    compressed_twin: CompressedDigitalTwin,
    mock_uri: str
):
    """
    **Feature: gemini-3-dual-architecture, Property 8: Image URI Return Format**
    
    *For any* successful image generation, the system should return an image_uri string 
    that references the generated image.
    
    **Validates: Requirements 3.3**
    
    This property test verifies that the return value is a valid image URI.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock the generate_content method to return the mock URI
        mock_result = MagicMock()
        mock_result.text = mock_uri
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image
        result = await client.generate_image(prompt, compressed_twin)
        
        # Verify result is a string
        assert isinstance(result, str), (
            f"generate_image should return a string, got {type(result)}"
        )
        
        # Verify result is not empty
        assert len(result) > 0, (
            "generate_image should return a non-empty string"
        )
        
        # Verify result is a valid URI format
        is_data_uri = result.startswith("data:")
        is_http_url = result.startswith("http://") or result.startswith("https://")
        
        assert is_data_uri or is_http_url, (
            f"Result should be a valid URI (data: or http(s)://), got: {result[:50]}"
        )
        
        print(f"✓ generate_image returns valid image_uri: {result[:50]}...")


@given(
    compressed_twin=compressed_twin_strategy(),
    mock_uri=image_uri_strategy()
)
@hypothesis_settings(max_examples=100)
async def test_image_uri_is_string_type(
    compressed_twin: CompressedDigitalTwin,
    mock_uri: str
):
    """
    **Feature: gemini-3-dual-architecture, Property 8: Image URI Return Format**
    
    *For any* successful generation, the return value should be of type str.
    
    **Validates: Requirements 3.3**
    
    This property test verifies the return type is always a string.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = mock_uri
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image
        result = await client.generate_image("test prompt", compressed_twin)
        
        # Verify result is exactly a string type
        assert type(result) == str, (
            f"generate_image must return str type, got {type(result)}"
        )
        
        print(f"✓ generate_image returns str type")


@given(
    compressed_twin=compressed_twin_strategy()
)
@hypothesis_settings(max_examples=100)
async def test_data_uri_format_is_valid(
    compressed_twin: CompressedDigitalTwin
):
    """
    **Feature: gemini-3-dual-architecture, Property 8: Image URI Return Format**
    
    *For any* generation that returns a data URI, it should follow the standard format.
    
    **Validates: Requirements 3.3**
    
    This property test verifies data URI format compliance.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock the generate_content method to return a data URI
        mock_result = MagicMock()
        mock_result.text = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image
        result = await client.generate_image("test prompt", compressed_twin)
        
        # If result is a data URI, verify format
        if result.startswith("data:"):
            # Data URI format: data:[<mediatype>][;base64],<data>
            data_uri_pattern = r"^data:([a-zA-Z0-9]+/[a-zA-Z0-9\-\+\.]+)(;base64)?,(.+)$"
            match = re.match(data_uri_pattern, result)
            
            assert match is not None, (
                f"Data URI should follow standard format: data:[mediatype][;base64],<data>"
            )
            
            mime_type = match.group(1)
            encoding = match.group(2)
            data = match.group(3)
            
            # Verify mime type is image-related
            assert mime_type.startswith("image/"), (
                f"Data URI mime type should be image/*, got {mime_type}"
            )
            
            # Verify data is not empty
            assert len(data) > 0, (
                "Data URI data section should not be empty"
            )
            
            print(f"✓ Data URI format is valid: {mime_type}")


@given(
    compressed_twin=compressed_twin_strategy()
)
@hypothesis_settings(max_examples=100)
async def test_http_url_format_is_valid(
    compressed_twin: CompressedDigitalTwin
):
    """
    **Feature: gemini-3-dual-architecture, Property 8: Image URI Return Format**
    
    *For any* generation that returns an HTTP(S) URL, it should be a valid URL.
    
    **Validates: Requirements 3.3**
    
    This property test verifies HTTP URL format compliance.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock the generate_content method to return an HTTP URL
        mock_result = MagicMock()
        mock_result.text = "https://storage.googleapis.com/generated-images/test-image.png"
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image
        result = await client.generate_image("test prompt", compressed_twin)
        
        # If result is an HTTP URL, verify format
        if result.startswith("http://") or result.startswith("https://"):
            # Basic URL pattern
            url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
            match = re.match(url_pattern, result)
            
            assert match is not None, (
                f"HTTP URL should be a valid URL format"
            )
            
            print(f"✓ HTTP URL format is valid: {result[:50]}...")


def test_generate_image_returns_non_empty_uri():
    """
    **Feature: gemini-3-dual-architecture, Property 8: Image URI Return Format**
    
    Verify that generate_image never returns an empty string.
    
    **Validates: Requirements 3.3**
    
    This test ensures the return value is always meaningful.
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
        
        # Create a simple test
        import asyncio
        compressed_twin = CompressedDigitalTwin(primary_colors=["#FF0000"])
        
        result = asyncio.run(client.generate_image("test prompt", compressed_twin))
        
        # Verify result is not empty
        assert result, "generate_image should not return an empty string"
        assert len(result) > 0, "generate_image should return a non-empty URI"
        
        print(f"✓ generate_image returns non-empty URI")


def test_generate_image_uri_is_usable_reference():
    """
    **Feature: gemini-3-dual-architecture, Property 8: Image URI Return Format**
    
    Verify that the returned URI can be used as a reference to the image.
    
    **Validates: Requirements 3.3**
    
    This test ensures the URI is a usable reference format.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = "https://example.com/image.png"
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Create a simple test
        import asyncio
        compressed_twin = CompressedDigitalTwin(primary_colors=["#FF0000"])
        
        result = asyncio.run(client.generate_image("test prompt", compressed_twin))
        
        # Verify result can be used as a reference
        # It should be a string that can be stored, logged, or passed to other functions
        assert isinstance(result, str), "URI should be a string"
        assert result.strip() == result, "URI should not have leading/trailing whitespace"
        
        # Verify it's a valid URI format (data: or http(s)://)
        is_valid_uri = (
            result.startswith("data:") or 
            result.startswith("http://") or 
            result.startswith("https://")
        )
        assert is_valid_uri, "URI should be in a standard format"
        
        print(f"✓ Returned URI is a usable reference: {result}")


@given(
    compressed_twin=compressed_twin_strategy()
)
@hypothesis_settings(max_examples=50)
async def test_image_uri_contains_no_control_characters(
    compressed_twin: CompressedDigitalTwin
):
    """
    **Feature: gemini-3-dual-architecture, Property 8: Image URI Return Format**
    
    *For any* returned URI, it should not contain control characters.
    
    **Validates: Requirements 3.3**
    
    This property test verifies URI cleanliness.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        # Create mock model instances
        mock_vision_model = MagicMock()
        mock_model_class.return_value = mock_vision_model
        
        # Mock the generate_content method
        mock_result = MagicMock()
        mock_result.text = "data:image/png;base64,testdata123"
        mock_result.parts = []
        mock_vision_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call generate_image
        result = await client.generate_image("test prompt", compressed_twin)
        
        # Verify no control characters (ASCII 0-31 except space)
        for char in result:
            char_code = ord(char)
            assert char_code >= 32 or char_code == 9, (  # Allow tab (9) and printable chars
                f"URI should not contain control characters, found char code {char_code}"
            )
        
        print(f"✓ Image URI contains no control characters")
