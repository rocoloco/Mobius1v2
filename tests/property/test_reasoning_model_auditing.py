"""
Property-based tests for reasoning model usage in auditing.

**Feature: gemini-3-dual-architecture, Property 10: Reasoning Model for Auditing**

Tests that compliance auditing uses the reasoning_model instance.
"""

from hypothesis import given, strategies as st, settings as hypothesis_settings, HealthCheck
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
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


# Strategy for generating BrandGuidelines
@st.composite
def brand_guidelines_strategy(draw):
    """Generate random BrandGuidelines."""
    # For simplicity, create minimal guidelines
    return BrandGuidelines()


# Property 10: Reasoning Model for Auditing
@given(
    image_uri=image_uri_strategy(),
    guidelines=brand_guidelines_strategy()
)
@hypothesis_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_audit_compliance_uses_reasoning_model(image_uri: str, guidelines: BrandGuidelines):
    """
    **Feature: gemini-3-dual-architecture, Property 10: Reasoning Model for Auditing**
    
    *For any* compliance audit request, the system should use the reasoning_model instance 
    (gemini-3-pro-preview) to evaluate compliance.
    
    **Validates: Requirements 4.1, 6.4**
    
    This property test verifies that the correct model is used for auditing.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('httpx.AsyncClient') as mock_httpx:
        
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
        
        # Mock the generate_content method to return valid ComplianceScore
        mock_result = MagicMock()
        mock_result.text = ComplianceScore(
            overall_score=85.0,
            categories=[],
            approved=True,
            summary="Test compliance"
        ).model_dump_json()
        mock_reasoning_model.generate_content = MagicMock(return_value=mock_result)
        
        # Initialize client
        client = GeminiClient()
        
        # Call audit_compliance
        try:
            await client.audit_compliance(image_uri, guidelines)
        except Exception as e:
            # We're testing model selection, not full functionality
            pass
        
        # Verify reasoning_model.generate_content was called
        assert mock_reasoning_model.generate_content.called, (
            "reasoning_model.generate_content should be called for compliance auditing"
        )
        
        # Verify vision_model was NOT used for auditing
        assert not mock_vision_model.generate_content.called, (
            "vision_model should NOT be used for compliance auditing"
        )
        
        print(f"✓ audit_compliance uses reasoning_model for URI: {image_uri[:50]}")


@given(
    image_uri=image_uri_strategy(),
    guidelines=brand_guidelines_strategy()
)
@hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_audit_never_uses_vision_model(image_uri: str, guidelines: BrandGuidelines):
    """
    **Feature: gemini-3-dual-architecture, Property 10: Reasoning Model for Auditing**
    
    *For any* audit operation, the vision_model should never be used.
    
    **Validates: Requirements 4.1, 6.4**
    
    This property test verifies strict model separation for audit operations.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('httpx.AsyncClient') as mock_httpx:
        
        # Create mock model instances
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
        
        # Verify vision_model was never called for content generation
        assert not mock_vision_model.generate_content.called, (
            "vision_model should NEVER be used for audit operations"
        )
        
        print(f"✓ Audit correctly avoids vision_model for URI: {image_uri[:50]}")


def test_audit_compliance_logs_correct_model_name():
    """
    **Feature: gemini-3-dual-architecture, Property 10: Reasoning Model for Auditing**
    
    Verify that audit_compliance logs the correct model name.
    
    **Validates: Requirements 4.1, 6.4**
    
    This test ensures proper logging of model usage.
    """
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('mobius.tools.gemini.logger') as mock_logger, \
         patch('httpx.AsyncClient') as mock_httpx:
        
        # Create mock model instances
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
        
        # Create a simple test
        import asyncio
        image_uri = "https://example.com/image.jpg"
        guidelines = BrandGuidelines()
        
        try:
            asyncio.run(client.audit_compliance(image_uri, guidelines))
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
            f"reasoning_model '{settings.reasoning_model}' should be logged during audit"
        )
        
        print(f"✓ audit_compliance logs model_name: {settings.reasoning_model}")
