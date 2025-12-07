"""
Integration tests for the generation node.

These tests verify the generate_node function correctly loads compressed twins
and generates images using the Vision Model.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from mobius.models.state import JobState
from mobius.nodes.generate import generate_node
from mobius.models.brand import Brand, BrandGuidelines, CompressedDigitalTwin


@pytest.fixture
def sample_compressed_twin():
    """Sample compressed digital twin for testing."""
    return CompressedDigitalTwin(
        primary_colors=["#0057B8", "#1E3A8A"],
        secondary_colors=["#FF5733"],
        accent_colors=["#FFC300"],
        neutral_colors=["#FFFFFF", "#333333"],
        semantic_colors=["#10B981", "#EF4444"],
        font_families=["Helvetica Neue", "Georgia"],
        visual_dos=["Use primary colors for headers"],
        visual_donts=["Never distort logo"],
        logo_placement="top-left",
        logo_min_size="100px"
    )


@pytest.fixture
def sample_brand(sample_compressed_twin):
    """Sample brand with compressed twin for testing."""
    return Brand(
        brand_id="test-brand-001",
        organization_id="test-org-001",
        name="Test Brand",
        guidelines=BrandGuidelines(),
        compressed_twin=sample_compressed_twin,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )


@pytest.fixture
def sample_job_state():
    """Sample job state for testing."""
    return JobState(
        job_id="test-job-001",
        brand_id="test-brand-001",
        prompt="Create a modern tech logo",
        brand_hex_codes=["#0057B8"],
        brand_rules="Use primary colors",
        current_image_url=None,
        attempt_count=0,
        audit_history=[],
        compliance_scores=[],
        is_approved=False,
        status="pending",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        webhook_url=None,
        template_id=None,
        generation_params={"temperature": 0.7}
    )


@pytest.mark.asyncio
@patch("mobius.nodes.generate.BrandStorage")
@patch("mobius.nodes.generate.GeminiClient")
async def test_generate_node_success(
    mock_gemini_class, mock_storage_class, sample_brand, sample_job_state
):
    """
    Test successful image generation with compressed twin.
    
    Validates: Requirements 3.1, 3.2, 3.3
    """
    # Setup mocks
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(return_value=sample_brand)
    mock_storage_class.return_value = mock_storage
    
    mock_gemini = Mock()
    mock_gemini.generate_image = AsyncMock(
        return_value="https://example.com/generated-image.png"
    )
    mock_gemini_class.return_value = mock_gemini
    
    # Execute node
    result = await generate_node(sample_job_state)
    
    # Verify brand was loaded
    mock_storage.get_brand.assert_called_once_with("test-brand-001")
    
    # Verify generate_image was called with compressed twin
    mock_gemini.generate_image.assert_called_once()
    call_args = mock_gemini.generate_image.call_args
    assert call_args.kwargs["prompt"] == "Create a modern tech logo"
    assert call_args.kwargs["compressed_twin"] == sample_brand.compressed_twin
    assert call_args.kwargs["temperature"] == 0.7
    
    # Verify result structure
    assert result["current_image_url"] == "https://example.com/generated-image.png"
    assert result["attempt_count"] == 1
    assert result["status"] == "generated"


@pytest.mark.asyncio
@patch("mobius.nodes.generate.BrandStorage")
async def test_generate_node_brand_not_found(mock_storage_class, sample_job_state):
    """
    Test error handling when brand is not found.
    
    Validates: Error handling for missing brands
    """
    # Setup mock to return None (brand not found)
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(return_value=None)
    mock_storage_class.return_value = mock_storage
    
    # Execute node
    result = await generate_node(sample_job_state)
    
    # Verify error state
    assert result["status"] == "generation_error"
    assert result["attempt_count"] == 1
    assert "not found" in result["error"].lower()


@pytest.mark.asyncio
@patch("mobius.nodes.generate.BrandStorage")
async def test_generate_node_missing_compressed_twin(
    mock_storage_class, sample_brand, sample_job_state
):
    """
    Test error handling when compressed twin is missing.
    
    Validates: Error handling for brands without compressed twins
    """
    # Setup brand without compressed twin
    brand_without_twin = Brand(
        brand_id="test-brand-001",
        organization_id="test-org-001",
        name="Test Brand",
        guidelines=BrandGuidelines(),
        compressed_twin=None,  # Missing compressed twin
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(return_value=brand_without_twin)
    mock_storage_class.return_value = mock_storage
    
    # Execute node
    result = await generate_node(sample_job_state)
    
    # Verify error state
    assert result["status"] == "generation_error"
    assert result["attempt_count"] == 1
    assert "compressed twin" in result["error"].lower()


@pytest.mark.asyncio
@patch("mobius.nodes.generate.BrandStorage")
@patch("mobius.nodes.generate.GeminiClient")
async def test_generate_node_generation_failure(
    mock_gemini_class, mock_storage_class, sample_brand, sample_job_state
):
    """
    Test error handling when image generation fails.
    
    Validates: Error handling for generation failures
    """
    # Setup mocks
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(return_value=sample_brand)
    mock_storage_class.return_value = mock_storage
    
    mock_gemini = Mock()
    mock_gemini.generate_image = AsyncMock(
        side_effect=Exception("Generation API error")
    )
    mock_gemini_class.return_value = mock_gemini
    
    # Execute node
    result = await generate_node(sample_job_state)
    
    # Verify error state
    assert result["status"] == "generation_error"
    assert result["attempt_count"] == 1
    assert "error" in result["error"].lower()


@pytest.mark.asyncio
@patch("mobius.nodes.generate.BrandStorage")
@patch("mobius.nodes.generate.GeminiClient")
async def test_generate_node_increments_attempt_count(
    mock_gemini_class, mock_storage_class, sample_brand, sample_job_state
):
    """
    Test that attempt count is properly incremented.
    
    Validates: Attempt count tracking
    """
    # Setup mocks
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(return_value=sample_brand)
    mock_storage_class.return_value = mock_storage
    
    mock_gemini = Mock()
    mock_gemini.generate_image = AsyncMock(
        return_value="https://example.com/image.png"
    )
    mock_gemini_class.return_value = mock_gemini
    
    # Set initial attempt count
    sample_job_state["attempt_count"] = 2
    
    # Execute node
    result = await generate_node(sample_job_state)
    
    # Verify attempt count incremented
    assert result["attempt_count"] == 3


@pytest.mark.asyncio
@patch("mobius.nodes.generate.BrandStorage")
@patch("mobius.nodes.generate.GeminiClient")
async def test_generate_node_passes_generation_params(
    mock_gemini_class, mock_storage_class, sample_brand, sample_job_state
):
    """
    Test that generation parameters are passed to GeminiClient.
    
    Validates: Parameter passing to generation API
    """
    # Setup mocks
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(return_value=sample_brand)
    mock_storage_class.return_value = mock_storage
    
    mock_gemini = Mock()
    mock_gemini.generate_image = AsyncMock(
        return_value="https://example.com/image.png"
    )
    mock_gemini_class.return_value = mock_gemini
    
    # Set custom generation params
    sample_job_state["generation_params"] = {
        "temperature": 0.9,
        "custom_param": "value"
    }
    
    # Execute node
    result = await generate_node(sample_job_state)
    
    # Verify params were passed
    call_kwargs = mock_gemini.generate_image.call_args.kwargs
    assert call_kwargs["temperature"] == 0.9
    assert call_kwargs["custom_param"] == "value"
