"""
Property-Based Test: Generation Request Compatibility

**Feature: gemini-3-dual-architecture, Property 15: Generation Request Compatibility**
**Validates: Requirements 7.2**

This test verifies that generation requests using the pre-refactoring format
are processed successfully using the new Gemini architecture without requiring
client changes.

Property: For any generation request in the old format, the system should
process it successfully using the new Gemini architecture and return a valid
response with the expected structure.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from mobius.graphs.generation import run_generation_workflow


# Strategy for generating valid brand IDs
brand_id_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=48, max_codepoint=122),
    min_size=8,
    max_size=36
).filter(lambda x: len(x.strip()) > 0)

# Strategy for generating valid prompts
prompt_strategy = st.text(min_size=10, max_size=500).filter(lambda x: len(x.strip()) > 0)

# Strategy for generation parameters
generation_params_strategy = st.fixed_dictionaries({
    "temperature": st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    "aspect_ratio": st.sampled_from(["1:1", "16:9", "9:16", "4:3", "3:4"]),
})


@given(
    brand_id=brand_id_strategy,
    prompt=prompt_strategy,
    generation_params=generation_params_strategy
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_generation_request_compatibility(brand_id, prompt, generation_params):
    """
    Property 15: Generation Request Compatibility
    
    For any generation request using the pre-refactoring format (brand_id, prompt,
    optional generation_params), the system should:
    1. Accept the request without errors
    2. Process it using the new Gemini architecture
    3. Return a response with the expected structure
    4. Include all required fields in the response
    
    This ensures backward compatibility - existing API clients can continue
    to use the same request format without modifications.
    """
    # Mock the brand storage to return a valid brand with compressed twin
    mock_brand = MagicMock()
    mock_brand.compressed_twin = MagicMock()
    mock_brand.compressed_twin.estimate_tokens.return_value = 5000
    mock_brand.compressed_twin.primary_colors = ["#FF0000"]
    mock_brand.compressed_twin.secondary_colors = ["#00FF00"]
    mock_brand.compressed_twin.accent_colors = ["#0000FF"]
    mock_brand.compressed_twin.neutral_colors = ["#FFFFFF"]
    mock_brand.compressed_twin.semantic_colors = []
    mock_brand.compressed_twin.font_families = ["Arial"]
    mock_brand.compressed_twin.visual_dos = ["Use primary colors"]
    mock_brand.compressed_twin.visual_donts = ["Don't use Comic Sans"]
    mock_brand.compressed_twin.logo_placement = "top-left"
    mock_brand.compressed_twin.logo_min_size = "100px"
    
    mock_brand.guidelines = MagicMock()
    mock_brand.guidelines.colors = []
    mock_brand.guidelines.typography = MagicMock()
    mock_brand.guidelines.typography.fonts = []
    mock_brand.guidelines.logo_usage = MagicMock()
    mock_brand.guidelines.governance = MagicMock()
    
    # Mock the GeminiClient
    mock_image_uri = f"https://generativelanguage.googleapis.com/v1beta/files/{brand_id[:8]}"
    
    mock_compliance = MagicMock()
    mock_compliance.overall_score = 85.0
    mock_compliance.approved = True
    mock_compliance.categories = []
    mock_compliance.summary = "Compliant"
    mock_compliance.model_dump.return_value = {
        "overall_score": 85.0,
        "approved": True,
        "categories": [],
        "summary": "Compliant"
    }
    
    with patch('mobius.nodes.generate.BrandStorage') as MockBrandStorage, \
         patch('mobius.nodes.generate.GeminiClient') as MockGeminiClient, \
         patch('mobius.nodes.audit.BrandStorage') as MockAuditBrandStorage, \
         patch('mobius.nodes.audit.GeminiClient') as MockAuditGeminiClient:
        
        # Setup generate node mocks
        mock_brand_storage = MockBrandStorage.return_value
        mock_brand_storage.get_brand = AsyncMock(return_value=mock_brand)
        
        mock_gemini_client = MockGeminiClient.return_value
        mock_gemini_client.generate_image = AsyncMock(return_value=mock_image_uri)
        
        # Setup audit node mocks
        mock_audit_brand_storage = MockAuditBrandStorage.return_value
        mock_audit_brand_storage.get_brand = AsyncMock(return_value=mock_brand)
        
        mock_audit_gemini_client = MockAuditGeminiClient.return_value
        mock_audit_gemini_client.audit_compliance = AsyncMock(return_value=mock_compliance)
        
        # Execute the workflow with the old format request
        result = await run_generation_workflow(
            brand_id=brand_id,
            prompt=prompt,
            **generation_params
        )
        
        # Verify the response structure matches the expected format
        assert isinstance(result, dict), "Result should be a dictionary"
        
        # Required fields that must be present in the response
        required_fields = [
            "job_id",
            "brand_id",
            "status",
            "current_image_url",
            "is_approved",
            "compliance_scores",
            "attempt_count",
            "prompt"
        ]
        
        for field in required_fields:
            assert field in result, f"Response must include '{field}' field for backward compatibility"
        
        # Verify field types
        assert isinstance(result["job_id"], str), "job_id should be a string"
        assert isinstance(result["brand_id"], str), "brand_id should be a string"
        assert isinstance(result["status"], str), "status should be a string"
        assert isinstance(result["is_approved"], bool), "is_approved should be a boolean"
        assert isinstance(result["compliance_scores"], list), "compliance_scores should be a list"
        assert isinstance(result["attempt_count"], int), "attempt_count should be an integer"
        assert isinstance(result["prompt"], str), "prompt should be a string"
        
        # Verify the brand_id matches the input
        assert result["brand_id"] == brand_id, "Response brand_id should match request brand_id"
        
        # Verify status is valid
        valid_statuses = ["completed", "failed", "pending", "generating", "auditing", "correcting"]
        assert result["status"] in valid_statuses, f"Status should be one of {valid_statuses}"
        
        # Verify attempt_count is reasonable
        assert result["attempt_count"] >= 0, "attempt_count should be non-negative"
        assert result["attempt_count"] <= 10, "attempt_count should not exceed reasonable limits"
        
        # If the workflow completed successfully, verify image_uri is present
        if result["status"] == "completed" and result["is_approved"]:
            assert result["current_image_url"] is not None, \
                "Successful generation should include current_image_url (image_uri)"
            assert isinstance(result["current_image_url"], str), \
                "current_image_url should be a string"
        
        # Verify compliance_scores structure if present
        if result["compliance_scores"]:
            for score in result["compliance_scores"]:
                assert isinstance(score, dict), "Each compliance score should be a dictionary"
                # The score should have the expected structure from ComplianceScore model
                assert "overall_score" in score or "approved" in score, \
                    "Compliance score should have expected fields"


@pytest.mark.asyncio
async def test_generation_request_with_optional_params():
    """
    Test that optional parameters (webhook_url, template_id) are handled correctly.
    
    This ensures backward compatibility for clients that use these optional fields.
    """
    brand_id = "test-brand-123"
    prompt = "Generate a professional banner"
    webhook_url = "https://example.com/webhook"
    template_id = "template-456"
    
    # Mock setup (same as above)
    mock_brand = MagicMock()
    mock_brand.compressed_twin = MagicMock()
    mock_brand.compressed_twin.estimate_tokens.return_value = 5000
    mock_brand.compressed_twin.primary_colors = ["#FF0000"]
    mock_brand.compressed_twin.secondary_colors = ["#00FF00"]
    mock_brand.compressed_twin.accent_colors = ["#0000FF"]
    mock_brand.compressed_twin.neutral_colors = ["#FFFFFF"]
    mock_brand.compressed_twin.semantic_colors = []
    mock_brand.compressed_twin.font_families = ["Arial"]
    mock_brand.compressed_twin.visual_dos = ["Use primary colors"]
    mock_brand.compressed_twin.visual_donts = ["Don't use Comic Sans"]
    mock_brand.compressed_twin.logo_placement = "top-left"
    mock_brand.compressed_twin.logo_min_size = "100px"
    
    mock_brand.guidelines = MagicMock()
    mock_brand.guidelines.colors = []
    mock_brand.guidelines.typography = MagicMock()
    mock_brand.guidelines.typography.fonts = []
    mock_brand.guidelines.logo_usage = MagicMock()
    mock_brand.guidelines.governance = MagicMock()
    
    mock_image_uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
    
    mock_compliance = MagicMock()
    mock_compliance.overall_score = 85.0
    mock_compliance.approved = True
    mock_compliance.categories = []
    mock_compliance.summary = "Compliant"
    mock_compliance.model_dump.return_value = {
        "overall_score": 85.0,
        "approved": True,
        "categories": [],
        "summary": "Compliant"
    }
    
    with patch('mobius.nodes.generate.BrandStorage') as MockBrandStorage, \
         patch('mobius.nodes.generate.GeminiClient') as MockGeminiClient, \
         patch('mobius.nodes.audit.BrandStorage') as MockAuditBrandStorage, \
         patch('mobius.nodes.audit.GeminiClient') as MockAuditGeminiClient:
        
        mock_brand_storage = MockBrandStorage.return_value
        mock_brand_storage.get_brand = AsyncMock(return_value=mock_brand)
        
        mock_gemini_client = MockGeminiClient.return_value
        mock_gemini_client.generate_image = AsyncMock(return_value=mock_image_uri)
        
        mock_audit_brand_storage = MockAuditBrandStorage.return_value
        mock_audit_brand_storage.get_brand = AsyncMock(return_value=mock_brand)
        
        mock_audit_gemini_client = MockAuditGeminiClient.return_value
        mock_audit_gemini_client.audit_compliance = AsyncMock(return_value=mock_compliance)
        
        # Execute with optional parameters
        result = await run_generation_workflow(
            brand_id=brand_id,
            prompt=prompt,
            webhook_url=webhook_url,
            template_id=template_id
        )
        
        # Verify optional parameters are preserved in the response
        assert result["template_id"] == template_id, \
            "template_id should be preserved in response"
        
        # Verify the workflow executed successfully
        assert "job_id" in result
        assert result["brand_id"] == brand_id
