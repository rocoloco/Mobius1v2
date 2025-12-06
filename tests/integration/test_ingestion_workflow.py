"""
Integration tests for brand ingestion workflow.

Tests the complete PDF ingestion workflow including:
- Text extraction from PDFs
- Visual element extraction with Gemini
- Brand entity creation
- needs_review flagging for ambiguous data

**Validates: Requirements 2.2, 2.3, 2.4**
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from mobius.graphs.ingestion import run_ingestion_workflow, create_ingestion_workflow
from mobius.models.brand import Brand, BrandGuidelines, Color, Typography, BrandRule
import uuid


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF bytes for testing."""
    # Minimal valid PDF structure
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Brand Guidelines) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000214 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
306
%%EOF"""


@pytest.fixture
def sample_brand_guidelines():
    """Sample BrandGuidelines for testing."""
    return BrandGuidelines(
        colors=[
            Color(name="Primary Blue", hex="#0057B8", usage="primary"),
            Color(name="Secondary Gray", hex="#6C757D", usage="secondary"),
        ],
        typography=[
            Typography(family="Arial", weights=["400", "700"], usage="Body text"),
            Typography(family="Helvetica", weights=["300", "500"], usage="Headers"),
        ],
        logos=[],
        voice=None,
        rules=[
            BrandRule(
                category="visual",
                instruction="Always use primary colors for headers",
                severity="warning",
                negative_constraint=False,
            ),
            BrandRule(
                category="visual",
                instruction="Do not use Comic Sans font",
                severity="critical",
                negative_constraint=True,
            ),
        ],
    )


@pytest.mark.asyncio
@patch("mobius.nodes.structure.BrandStorage")
@patch("mobius.nodes.structure.GeminiClient")
@patch("mobius.nodes.extract_visual.GeminiClient")
@patch("mobius.nodes.extract_text.PDFParser")
@patch("mobius.nodes.extract_text.httpx.AsyncClient")
@patch("mobius.nodes.extract_visual.httpx.AsyncClient")
@patch("mobius.nodes.structure.httpx.AsyncClient")
async def test_complete_ingestion_workflow(
    mock_httpx_structure,
    mock_httpx_visual,
    mock_httpx_text,
    mock_pdf_parser_class,
    mock_gemini_visual_class,
    mock_gemini_structure_class,
    mock_brand_storage_class,
    sample_pdf_bytes,
    sample_brand_guidelines,
):
    """
    Test complete brand ingestion workflow.

    Verifies that the workflow:
    1. Downloads PDF from URL
    2. Extracts text using pdfplumber
    3. Extracts visual elements using Gemini
    4. Structures data into BrandGuidelines
    5. Creates Brand entity in database

    **Validates: Requirements 2.2, 2.3, 2.4**
    """
    brand_id = str(uuid.uuid4())
    organization_id = str(uuid.uuid4())
    brand_name = "Test Brand"
    pdf_url = "https://example.com/guidelines.pdf"

    # Mock httpx client for PDF download (all three nodes)
    mock_response = Mock()
    mock_response.content = sample_pdf_bytes
    mock_response.raise_for_status = Mock()

    mock_http_instance = AsyncMock()
    mock_http_instance.__aenter__ = AsyncMock(return_value=mock_http_instance)
    mock_http_instance.__aexit__ = AsyncMock()
    mock_http_instance.get = AsyncMock(return_value=mock_response)
    
    mock_httpx_text.return_value = mock_http_instance
    mock_httpx_visual.return_value = mock_http_instance
    mock_httpx_structure.return_value = mock_http_instance

    # Mock PDF parser
    mock_parser = Mock()
    mock_parser.extract_text = Mock(return_value="Brand Guidelines\n\nColors: #0057B8, #6C757D\nFonts: Arial, Helvetica")
    mock_parser.extract_hex_codes = Mock(return_value=["#0057B8", "#6C757D"])
    mock_parser.extract_font_names = Mock(return_value=["Arial", "Helvetica"])
    mock_pdf_parser_class.return_value = mock_parser

    # Mock Gemini client for visual extraction
    mock_gemini_visual = Mock()
    mock_gemini_visual.analyze_pdf = AsyncMock(
        return_value={
            "colors": ["#0057B8", "#6C757D"],
            "fonts": ["Arial", "Helvetica"],
            "logo_rules": ["Minimum size 100px"],
            "visual_patterns": ["Clean, modern design"],
        }
    )
    mock_gemini_visual_class.return_value = mock_gemini_visual

    # Mock Gemini client for structure extraction
    mock_gemini_structure = Mock()
    mock_gemini_structure.extract_brand_guidelines = AsyncMock(return_value=sample_brand_guidelines)
    mock_gemini_structure_class.return_value = mock_gemini_structure

    # Mock BrandStorage
    mock_storage = Mock()
    mock_storage.create_brand = AsyncMock(return_value=None)
    mock_brand_storage_class.return_value = mock_storage

    # Run workflow
    final_state = await run_ingestion_workflow(
        brand_id=brand_id,
        organization_id=organization_id,
        brand_name=brand_name,
        pdf_url=pdf_url,
    )

    # Verify workflow completed
    assert final_state["status"] == "completed"
    assert final_state["brand_id"] == brand_id
    assert final_state["organization_id"] == organization_id

    # Verify PDF was downloaded
    mock_http_instance.get.assert_called()

    # Verify text extraction was called
    mock_parser.extract_text.assert_called_once()

    # Verify Gemini analysis was called
    mock_gemini_visual.analyze_pdf.assert_called_once()
    mock_gemini_structure.extract_brand_guidelines.assert_called_once()

    # Verify brand was created in database
    mock_storage.create_brand.assert_called_once()
    created_brand = mock_storage.create_brand.call_args[0][0]
    assert isinstance(created_brand, Brand)
    assert created_brand.brand_id == brand_id
    assert created_brand.organization_id == organization_id
    assert created_brand.name == brand_name
    assert len(created_brand.guidelines.colors) >= 1


@pytest.mark.asyncio
@patch("mobius.nodes.structure.BrandStorage")
@patch("mobius.nodes.structure.GeminiClient")
@patch("mobius.nodes.extract_visual.GeminiClient")
@patch("mobius.nodes.extract_text.PDFParser")
@patch("mobius.nodes.extract_text.httpx.AsyncClient")
@patch("mobius.nodes.extract_visual.httpx.AsyncClient")
@patch("mobius.nodes.structure.httpx.AsyncClient")
async def test_ingestion_with_needs_review(
    mock_httpx_structure,
    mock_httpx_visual,
    mock_httpx_text,
    mock_pdf_parser_class,
    mock_gemini_visual_class,
    mock_gemini_structure_class,
    mock_brand_storage_class,
    sample_pdf_bytes,
):
    """
    Test ingestion workflow with ambiguous data requiring review.

    Verifies that when extraction yields minimal or ambiguous data,
    the workflow flags items for manual review.

    **Validates: Requirements 2.4**
    """
    brand_id = str(uuid.uuid4())
    organization_id = str(uuid.uuid4())
    brand_name = "Test Brand"
    pdf_url = "https://example.com/guidelines.pdf"

    # Mock httpx client
    mock_response = Mock()
    mock_response.content = sample_pdf_bytes
    mock_response.raise_for_status = Mock()

    mock_http_instance = AsyncMock()
    mock_http_instance.__aenter__ = AsyncMock(return_value=mock_http_instance)
    mock_http_instance.__aexit__ = AsyncMock()
    mock_http_instance.get = AsyncMock(return_value=mock_response)
    
    mock_httpx_text.return_value = mock_http_instance
    mock_httpx_visual.return_value = mock_http_instance
    mock_httpx_structure.return_value = mock_http_instance

    # Mock PDF parser with minimal extraction
    mock_parser = Mock()
    mock_parser.extract_text = Mock(return_value="Minimal text")
    mock_parser.extract_hex_codes = Mock(return_value=[])
    mock_parser.extract_font_names = Mock(return_value=[])
    mock_pdf_parser_class.return_value = mock_parser

    # Mock Gemini with minimal data
    mock_gemini_visual = Mock()
    mock_gemini_visual.analyze_pdf = AsyncMock(
        return_value={
            "colors": [],
            "fonts": [],
            "logo_rules": [],
            "visual_patterns": [],
        }
    )
    mock_gemini_visual_class.return_value = mock_gemini_visual
    
    # Return minimal guidelines
    minimal_guidelines = BrandGuidelines(
        colors=[],  # No colors extracted
        typography=[],  # No typography extracted
        logos=[],
        voice=None,
        rules=[],  # No rules extracted
    )
    mock_gemini_structure = Mock()
    mock_gemini_structure.extract_brand_guidelines = AsyncMock(return_value=minimal_guidelines)
    mock_gemini_structure_class.return_value = mock_gemini_structure

    # Mock BrandStorage
    mock_storage = Mock()
    mock_storage.create_brand = AsyncMock(return_value=None)
    mock_brand_storage_class.return_value = mock_storage

    # Run workflow
    final_state = await run_ingestion_workflow(
        brand_id=brand_id,
        organization_id=organization_id,
        brand_name=brand_name,
        pdf_url=pdf_url,
    )

    # Verify workflow completed with needs_review flags
    assert final_state["status"] == "completed"
    assert len(final_state["needs_review"]) > 0

    # Verify specific review flags
    needs_review = final_state["needs_review"]
    assert any("color" in item.lower() for item in needs_review)
    assert any("typography" in item.lower() for item in needs_review)
    assert any("rules" in item.lower() for item in needs_review)


@pytest.mark.asyncio
@patch("mobius.nodes.extract_text.httpx.AsyncClient")
async def test_ingestion_handles_pdf_download_failure(mock_httpx):
    """
    Test ingestion workflow handles PDF download failures gracefully.

    Verifies that when PDF download fails, the workflow:
    1. Catches the error
    2. Sets status to "failed"
    3. Adds error to needs_review

    **Validates: Requirements 2.2**
    """
    brand_id = str(uuid.uuid4())
    organization_id = str(uuid.uuid4())
    brand_name = "Test Brand"
    pdf_url = "https://example.com/nonexistent.pdf"

    # Mock httpx client to raise error
    mock_http_instance = AsyncMock()
    mock_http_instance.__aenter__ = AsyncMock(return_value=mock_http_instance)
    mock_http_instance.__aexit__ = AsyncMock()
    mock_http_instance.get = AsyncMock(side_effect=Exception("404 Not Found"))
    mock_httpx.return_value = mock_http_instance

    # Run workflow
    final_state = await run_ingestion_workflow(
        brand_id=brand_id,
        organization_id=organization_id,
        brand_name=brand_name,
        pdf_url=pdf_url,
    )

    # Verify workflow failed gracefully
    assert final_state["status"] == "failed"
    assert len(final_state["needs_review"]) > 0
    # Check for either "download" or "extraction" in error message
    assert any("download" in item.lower() or "extraction" in item.lower() or "failed" in item.lower() for item in final_state["needs_review"])


@pytest.mark.asyncio
@patch("mobius.nodes.structure.BrandStorage")
@patch("mobius.nodes.structure.GeminiClient")
@patch("mobius.nodes.extract_visual.GeminiClient")
@patch("mobius.nodes.extract_text.PDFParser")
@patch("mobius.nodes.extract_text.httpx.AsyncClient")
@patch("mobius.nodes.extract_visual.httpx.AsyncClient")
@patch("mobius.nodes.structure.httpx.AsyncClient")
async def test_ingestion_extracts_colors_fonts_rules(
    mock_httpx_structure,
    mock_httpx_visual,
    mock_httpx_text,
    mock_pdf_parser_class,
    mock_gemini_visual_class,
    mock_gemini_structure_class,
    mock_brand_storage_class,
    sample_pdf_bytes,
    sample_brand_guidelines,
):
    """
    Test that ingestion extracts colors, fonts, and rules into Digital Twin format.

    Verifies that the workflow correctly extracts and structures:
    - Colors with hex codes and usage
    - Typography with font families and weights
    - Rules with negative_constraint logic

    **Validates: Requirements 2.2, 2.3**
    """
    brand_id = str(uuid.uuid4())
    organization_id = str(uuid.uuid4())
    brand_name = "Test Brand"
    pdf_url = "https://example.com/guidelines.pdf"

    # Mock httpx client
    mock_response = Mock()
    mock_response.content = sample_pdf_bytes
    mock_response.raise_for_status = Mock()

    mock_http_instance = AsyncMock()
    mock_http_instance.__aenter__ = AsyncMock(return_value=mock_http_instance)
    mock_http_instance.__aexit__ = AsyncMock()
    mock_http_instance.get = AsyncMock(return_value=mock_response)
    
    mock_httpx_text.return_value = mock_http_instance
    mock_httpx_visual.return_value = mock_http_instance
    mock_httpx_structure.return_value = mock_http_instance

    # Mock PDF parser
    mock_parser = Mock()
    mock_parser.extract_text = Mock(return_value="Brand Guidelines with colors and fonts")
    mock_parser.extract_hex_codes = Mock(return_value=["#0057B8"])
    mock_parser.extract_font_names = Mock(return_value=["Arial"])
    mock_pdf_parser_class.return_value = mock_parser

    # Mock Gemini
    mock_gemini_visual = Mock()
    mock_gemini_visual.analyze_pdf = AsyncMock(
        return_value={
            "colors": ["#0057B8", "#6C757D"],
            "fonts": ["Arial", "Helvetica"],
            "logo_rules": [],
            "visual_patterns": [],
        }
    )
    mock_gemini_visual_class.return_value = mock_gemini_visual
    
    mock_gemini_structure = Mock()
    mock_gemini_structure.extract_brand_guidelines = AsyncMock(return_value=sample_brand_guidelines)
    mock_gemini_structure_class.return_value = mock_gemini_structure

    # Mock BrandStorage
    mock_storage = Mock()
    mock_storage.create_brand = AsyncMock(return_value=None)
    mock_brand_storage_class.return_value = mock_storage

    # Run workflow
    final_state = await run_ingestion_workflow(
        brand_id=brand_id,
        organization_id=organization_id,
        brand_name=brand_name,
        pdf_url=pdf_url,
    )

    # Verify workflow completed
    assert final_state["status"] == "completed"

    # Verify brand was created with proper structure
    mock_storage.create_brand.assert_called_once()
    created_brand = mock_storage.create_brand.call_args[0][0]

    # Verify colors extracted
    assert len(created_brand.guidelines.colors) >= 2
    for color in created_brand.guidelines.colors:
        assert color.hex.startswith("#")
        assert color.usage in ["primary", "secondary", "accent", "background"]

    # Verify typography extracted
    assert len(created_brand.guidelines.typography) >= 2
    for typo in created_brand.guidelines.typography:
        assert len(typo.family) > 0
        assert len(typo.weights) > 0

    # Verify rules extracted with negative_constraint logic
    assert len(created_brand.guidelines.rules) >= 2
    positive_rules = [r for r in created_brand.guidelines.rules if not r.negative_constraint]
    negative_rules = [r for r in created_brand.guidelines.rules if r.negative_constraint]

    assert len(positive_rules) >= 1  # "Always use primary colors"
    assert len(negative_rules) >= 1  # "Do not use Comic Sans"
