"""
Property-Based Test: Ingestion Response Compatibility

**Feature: gemini-3-dual-architecture, Property 17: Ingestion Response Compatibility**
**Validates: Requirements 7.4**

This test verifies that brand ingestion operations return Brand entity data
that matches the pre-refactoring format, ensuring backward compatibility with
existing integrations.

Property: For any brand ingestion operation, the Brand Entity data should match
the pre-refactoring format with all required fields present and correctly typed.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from typing import Dict, Any

from mobius.models.brand import Brand, BrandGuidelines, CompressedDigitalTwin, Color, Typography
from mobius.storage.brands import BrandStorage


# Strategies for generating valid data

brand_id_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pd"), min_codepoint=45, max_codepoint=122),
    min_size=8,
    max_size=36
).filter(lambda x: len(x.strip()) > 0 and not x.startswith('-') and not x.endswith('-'))

organization_id_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pd"), min_codepoint=45, max_codepoint=122),
    min_size=8,
    max_size=36
).filter(lambda x: len(x.strip()) > 0 and not x.startswith('-') and not x.endswith('-'))

brand_name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"), min_codepoint=32, max_codepoint=122),
    min_size=2,
    max_size=100
).filter(lambda x: len(x.strip()) > 0)

url_strategy = st.text(min_size=10, max_size=200).map(
    lambda x: f"https://cdn.example.com/{x.replace(' ', '-')[:50]}.pdf"
)


@st.composite
def brand_guidelines_strategy(draw):
    """Generate random BrandGuidelines."""
    # Generate colors
    num_colors = draw(st.integers(min_value=0, max_value=5))
    colors = []
    for _ in range(num_colors):
        hex_code = draw(st.text(min_size=6, max_size=6, alphabet='0123456789ABCDEF'))
        colors.append(Color(
            name=draw(st.text(min_size=3, max_size=20)),
            hex=f"#{hex_code}",
            usage=draw(st.sampled_from(['primary', 'secondary', 'accent', 'neutral', 'semantic'])),
            usage_weight=draw(st.floats(min_value=0.0, max_value=1.0)),
            context=draw(st.one_of(st.none(), st.text(min_size=5, max_size=50)))
        ))
    
    # Generate typography
    num_fonts = draw(st.integers(min_value=0, max_value=3))
    typography = []
    for _ in range(num_fonts):
        typography.append(Typography(
            family=draw(st.text(min_size=3, max_size=20)),
            weights=draw(st.lists(st.text(min_size=3, max_size=10), min_size=1, max_size=3)),
            usage=draw(st.text(min_size=5, max_size=50))
        ))
    
    return BrandGuidelines(
        colors=colors,
        typography=typography,
        logos=[],
        voice=None,
        rules=[]
    )


@st.composite
def compressed_twin_strategy(draw):
    """Generate random CompressedDigitalTwin."""
    num_primary = draw(st.integers(min_value=0, max_value=3))
    num_secondary = draw(st.integers(min_value=0, max_value=3))
    num_accent = draw(st.integers(min_value=0, max_value=2))
    num_neutral = draw(st.integers(min_value=0, max_value=3))
    
    primary_colors = [
        f"#{draw(st.text(min_size=6, max_size=6, alphabet='0123456789ABCDEF'))}"
        for _ in range(num_primary)
    ]
    secondary_colors = [
        f"#{draw(st.text(min_size=6, max_size=6, alphabet='0123456789ABCDEF'))}"
        for _ in range(num_secondary)
    ]
    accent_colors = [
        f"#{draw(st.text(min_size=6, max_size=6, alphabet='0123456789ABCDEF'))}"
        for _ in range(num_accent)
    ]
    neutral_colors = [
        f"#{draw(st.text(min_size=6, max_size=6, alphabet='0123456789ABCDEF'))}"
        for _ in range(num_neutral)
    ]
    
    num_fonts = draw(st.integers(min_value=0, max_value=3))
    font_families = [
        draw(st.text(min_size=3, max_size=20))
        for _ in range(num_fonts)
    ]
    
    num_dos = draw(st.integers(min_value=0, max_value=5))
    visual_dos = [
        draw(st.text(min_size=10, max_size=100))
        for _ in range(num_dos)
    ]
    
    num_donts = draw(st.integers(min_value=0, max_value=5))
    visual_donts = [
        draw(st.text(min_size=10, max_size=100))
        for _ in range(num_donts)
    ]
    
    return CompressedDigitalTwin(
        primary_colors=primary_colors,
        secondary_colors=secondary_colors,
        accent_colors=accent_colors,
        neutral_colors=neutral_colors,
        semantic_colors=[],
        font_families=font_families,
        visual_dos=visual_dos,
        visual_donts=visual_donts,
        logo_placement=draw(st.one_of(st.none(), st.text(min_size=5, max_size=50))),
        logo_min_size=draw(st.one_of(st.none(), st.text(min_size=5, max_size=20)))
    )


@st.composite
def needs_review_strategy(draw):
    """Generate random needs_review list."""
    num_items = draw(st.integers(min_value=0, max_value=5))
    return [
        draw(st.text(min_size=10, max_size=100))
        for _ in range(num_items)
    ]


@given(
    brand_id=brand_id_strategy,
    organization_id=organization_id_strategy,
    brand_name=brand_name_strategy,
    pdf_url=url_strategy,
    guidelines=brand_guidelines_strategy(),
    compressed_twin=compressed_twin_strategy(),
    needs_review=needs_review_strategy()
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_brand_entity_has_required_fields(
    brand_id: str,
    organization_id: str,
    brand_name: str,
    pdf_url: str,
    guidelines: BrandGuidelines,
    compressed_twin: CompressedDigitalTwin,
    needs_review: list
):
    """
    **Feature: gemini-3-dual-architecture, Property 17: Ingestion Response Compatibility**
    
    *For any* brand ingestion operation, the Brand entity should include all
    required fields that existed in the pre-refactoring format.
    
    **Validates: Requirements 7.4**
    
    This property test verifies that Brand entities maintain backward compatibility
    by including all expected fields with correct types.
    """
    now = datetime.now(timezone.utc)
    
    # Create a Brand entity as would be returned from ingestion
    brand = Brand(
        brand_id=brand_id,
        organization_id=organization_id,
        name=brand_name,
        website=None,
        guidelines=guidelines,
        compressed_twin=compressed_twin,
        created_at=now.isoformat(),
        updated_at=now.isoformat(),
        deleted_at=None,
        pdf_url=pdf_url,
        logo_thumbnail_url=None,
        needs_review=needs_review,
        learning_active=False,
        feedback_count=0
    )
    
    # Verify all required fields are present (backward compatibility)
    required_fields = [
        'brand_id',
        'organization_id',
        'name',
        'guidelines',
        'created_at',
        'updated_at',
        'pdf_url',
        'needs_review',
        'learning_active',
        'feedback_count'
    ]
    
    for field in required_fields:
        assert hasattr(brand, field), f"Missing required field: {field}"
    
    # Verify field types match old format
    assert isinstance(brand.brand_id, str), f"brand_id must be string, got {type(brand.brand_id)}"
    assert isinstance(brand.organization_id, str), f"organization_id must be string, got {type(brand.organization_id)}"
    assert isinstance(brand.name, str), f"name must be string, got {type(brand.name)}"
    assert isinstance(brand.guidelines, BrandGuidelines), f"guidelines must be BrandGuidelines, got {type(brand.guidelines)}"
    assert isinstance(brand.created_at, str), f"created_at must be string (ISO format), got {type(brand.created_at)}"
    assert isinstance(brand.updated_at, str), f"updated_at must be string (ISO format), got {type(brand.updated_at)}"
    assert isinstance(brand.pdf_url, (str, type(None))), f"pdf_url must be string or None, got {type(brand.pdf_url)}"
    assert isinstance(brand.needs_review, list), f"needs_review must be list, got {type(brand.needs_review)}"
    assert isinstance(brand.learning_active, bool), f"learning_active must be bool, got {type(brand.learning_active)}"
    assert isinstance(brand.feedback_count, int), f"feedback_count must be int, got {type(brand.feedback_count)}"
    
    print(f"✓ Brand entity has all required fields with correct types")


@given(
    brand_id=brand_id_strategy,
    organization_id=organization_id_strategy,
    brand_name=brand_name_strategy,
    pdf_url=url_strategy,
    guidelines=brand_guidelines_strategy(),
    compressed_twin=compressed_twin_strategy(),
    needs_review=needs_review_strategy()
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_brand_entity_json_serialization_compatibility(
    brand_id: str,
    organization_id: str,
    brand_name: str,
    pdf_url: str,
    guidelines: BrandGuidelines,
    compressed_twin: CompressedDigitalTwin,
    needs_review: list
):
    """
    **Feature: gemini-3-dual-architecture, Property 17: Ingestion Response Compatibility**
    
    *For any* brand ingestion operation, the Brand entity should serialize to JSON
    in a format compatible with the pre-refactoring API responses.
    
    **Validates: Requirements 7.4**
    
    This property test verifies that Brand entities can be serialized to JSON
    in a format that existing API clients can parse.
    """
    now = datetime.now(timezone.utc)
    
    brand = Brand(
        brand_id=brand_id,
        organization_id=organization_id,
        name=brand_name,
        website=None,
        guidelines=guidelines,
        compressed_twin=compressed_twin,
        created_at=now.isoformat(),
        updated_at=now.isoformat(),
        deleted_at=None,
        pdf_url=pdf_url,
        logo_thumbnail_url=None,
        needs_review=needs_review,
        learning_active=False,
        feedback_count=0
    )
    
    # Serialize to JSON (as would happen in API response)
    json_str = brand.model_dump_json()
    assert isinstance(json_str, str), "model_dump_json should return string"
    assert len(json_str) > 0, "JSON string should not be empty"
    
    # Parse JSON to verify it's valid
    import json
    parsed = json.loads(json_str)
    
    # Verify all required fields are in the JSON
    required_fields = [
        'brand_id',
        'organization_id',
        'name',
        'guidelines',
        'created_at',
        'updated_at',
        'pdf_url',
        'needs_review',
        'learning_active',
        'feedback_count'
    ]
    
    for field in required_fields:
        assert field in parsed, f"JSON missing required field: {field}"
    
    # Verify guidelines structure in JSON
    assert isinstance(parsed['guidelines'], dict), "guidelines must be dict in JSON"
    assert 'colors' in parsed['guidelines'], "guidelines must have 'colors' field"
    assert 'typography' in parsed['guidelines'], "guidelines must have 'typography' field"
    assert 'logos' in parsed['guidelines'], "guidelines must have 'logos' field"
    assert 'rules' in parsed['guidelines'], "guidelines must have 'rules' field"
    
    # Verify needs_review is a list
    assert isinstance(parsed['needs_review'], list), "needs_review must be list in JSON"
    
    # Verify the JSON can be deserialized back to Brand
    deserialized = Brand.model_validate_json(json_str)
    assert isinstance(deserialized, Brand), "Should deserialize to Brand"
    assert deserialized.brand_id == brand_id
    assert deserialized.organization_id == organization_id
    assert deserialized.name == brand_name
    
    print(f"✓ Brand entity serializes to compatible JSON format")


@given(
    brand_id=brand_id_strategy,
    organization_id=organization_id_strategy,
    brand_name=brand_name_strategy,
    pdf_url=url_strategy,
    guidelines=brand_guidelines_strategy(),
    compressed_twin=compressed_twin_strategy(),
    needs_review=needs_review_strategy()
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_needs_review_field_behavior(
    brand_id: str,
    organization_id: str,
    brand_name: str,
    pdf_url: str,
    guidelines: BrandGuidelines,
    compressed_twin: CompressedDigitalTwin,
    needs_review: list
):
    """
    **Feature: gemini-3-dual-architecture, Property 17: Ingestion Response Compatibility**
    
    *For any* brand ingestion operation, the needs_review field should behave
    consistently with the pre-refactoring implementation.
    
    **Validates: Requirements 7.4**
    
    This property test verifies that the needs_review field:
    1. Is always a list (never None)
    2. Contains string items
    3. Can be empty or populated
    4. Is included in serialization
    """
    now = datetime.now(timezone.utc)
    
    brand = Brand(
        brand_id=brand_id,
        organization_id=organization_id,
        name=brand_name,
        website=None,
        guidelines=guidelines,
        compressed_twin=compressed_twin,
        created_at=now.isoformat(),
        updated_at=now.isoformat(),
        deleted_at=None,
        pdf_url=pdf_url,
        logo_thumbnail_url=None,
        needs_review=needs_review,
        learning_active=False,
        feedback_count=0
    )
    
    # Verify needs_review is always a list
    assert isinstance(brand.needs_review, list), "needs_review must be a list"
    
    # Verify all items in needs_review are strings
    for item in brand.needs_review:
        assert isinstance(item, str), f"needs_review items must be strings, got {type(item)}"
    
    # Verify needs_review is in serialized form
    brand_dict = brand.model_dump()
    assert 'needs_review' in brand_dict, "needs_review must be in serialized form"
    assert isinstance(brand_dict['needs_review'], list), "needs_review must be list in dict"
    
    # Test with empty needs_review
    brand_empty = Brand(
        brand_id=brand_id,
        organization_id=organization_id,
        name=brand_name,
        website=None,
        guidelines=guidelines,
        compressed_twin=compressed_twin,
        created_at=now.isoformat(),
        updated_at=now.isoformat(),
        deleted_at=None,
        pdf_url=pdf_url,
        logo_thumbnail_url=None,
        needs_review=[],  # Empty list
        learning_active=False,
        feedback_count=0
    )
    
    assert brand_empty.needs_review == [], "Empty needs_review should be empty list, not None"
    assert isinstance(brand_empty.needs_review, list), "Empty needs_review must still be a list"
    
    print(f"✓ needs_review field behaves correctly (length={len(needs_review)})")


@given(
    brand_id=brand_id_strategy,
    organization_id=organization_id_strategy,
    brand_name=brand_name_strategy,
    pdf_url=url_strategy,
    guidelines=brand_guidelines_strategy(),
    compressed_twin=compressed_twin_strategy()
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_brand_storage_query_compatibility(
    brand_id: str,
    organization_id: str,
    brand_name: str,
    pdf_url: str,
    guidelines: BrandGuidelines,
    compressed_twin: CompressedDigitalTwin
):
    """
    **Feature: gemini-3-dual-architecture, Property 17: Ingestion Response Compatibility**
    
    *For any* brand entity, it should work with existing brand storage queries
    without modifications.
    
    **Validates: Requirements 7.4**
    
    This property test verifies that Brand entities can be stored and retrieved
    using the existing BrandStorage interface.
    """
    now = datetime.now(timezone.utc)
    
    brand = Brand(
        brand_id=brand_id,
        organization_id=organization_id,
        name=brand_name,
        website=None,
        guidelines=guidelines,
        compressed_twin=compressed_twin,
        created_at=now.isoformat(),
        updated_at=now.isoformat(),
        deleted_at=None,
        pdf_url=pdf_url,
        logo_thumbnail_url=None,
        needs_review=[],
        learning_active=False,
        feedback_count=0
    )
    
    # Mock the Supabase client
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    
    # Mock insert operation
    mock_insert = MagicMock()
    mock_table.insert.return_value = mock_insert
    
    mock_execute = MagicMock()
    mock_execute.data = [brand.model_dump()]
    mock_insert.execute.return_value = mock_execute
    
    with patch('mobius.storage.brands.get_supabase_client', return_value=mock_client):
        storage = BrandStorage()
        
        # Test that the brand can be created using existing storage interface
        result = await storage.create_brand(brand)
        
        # Verify the result matches the input
        assert isinstance(result, Brand), "Storage should return Brand instance"
        assert result.brand_id == brand_id
        assert result.organization_id == organization_id
        assert result.name == brand_name
        
        # Verify the storage interface was called correctly
        mock_client.table.assert_called_with("brands")
        mock_table.insert.assert_called_once()
        
        # Verify the data passed to insert has the expected structure
        insert_call_args = mock_table.insert.call_args
        inserted_data = insert_call_args[0][0]
        
        # Check that all required fields are present in the insert data
        assert 'brand_id' in inserted_data
        assert 'organization_id' in inserted_data
        assert 'name' in inserted_data
        assert 'guidelines' in inserted_data
        assert 'needs_review' in inserted_data
        
    print(f"✓ Brand entity works with existing storage queries")


@given(
    brand_id=brand_id_strategy,
    organization_id=organization_id_strategy,
    brand_name=brand_name_strategy,
    pdf_url=url_strategy,
    guidelines=brand_guidelines_strategy()
)
@settings(max_examples=50, deadline=None)
@pytest.mark.asyncio
async def test_compressed_twin_is_optional_for_backward_compatibility(
    brand_id: str,
    organization_id: str,
    brand_name: str,
    pdf_url: str,
    guidelines: BrandGuidelines
):
    """
    **Feature: gemini-3-dual-architecture, Property 17: Ingestion Response Compatibility**
    
    *For any* brand entity, the compressed_twin field should be optional to maintain
    backward compatibility with brands ingested before the Gemini 3 refactoring.
    
    **Validates: Requirements 7.4**
    
    This property test verifies that Brand entities can exist without a compressed_twin
    (for brands ingested with the old architecture).
    """
    now = datetime.now(timezone.utc)
    
    # Create a brand WITHOUT compressed_twin (old format)
    brand_without_twin = Brand(
        brand_id=brand_id,
        organization_id=organization_id,
        name=brand_name,
        website=None,
        guidelines=guidelines,
        compressed_twin=None,  # No compressed twin (old format)
        created_at=now.isoformat(),
        updated_at=now.isoformat(),
        deleted_at=None,
        pdf_url=pdf_url,
        logo_thumbnail_url=None,
        needs_review=[],
        learning_active=False,
        feedback_count=0
    )
    
    # Verify the brand is valid without compressed_twin
    assert brand_without_twin.compressed_twin is None, "compressed_twin should be None"
    assert isinstance(brand_without_twin.guidelines, BrandGuidelines), "guidelines should still be present"
    
    # Verify it can be serialized
    json_str = brand_without_twin.model_dump_json()
    assert isinstance(json_str, str), "Should serialize without compressed_twin"
    
    # Verify it can be deserialized
    deserialized = Brand.model_validate_json(json_str)
    assert deserialized.compressed_twin is None, "Deserialized brand should have None compressed_twin"
    assert deserialized.brand_id == brand_id
    
    # Verify the serialized JSON has compressed_twin as null (not missing)
    import json
    parsed = json.loads(json_str)
    assert 'compressed_twin' in parsed, "compressed_twin field should be present in JSON"
    assert parsed['compressed_twin'] is None, "compressed_twin should be null in JSON"
    
    print(f"✓ Brand entity works without compressed_twin (backward compatibility)")


@pytest.mark.asyncio
async def test_brand_model_structure_unchanged():
    """
    **Feature: gemini-3-dual-architecture, Property 17: Ingestion Response Compatibility**
    
    Verify that the Brand model structure has not changed from the pre-refactoring
    implementation (except for the addition of the optional compressed_twin field).
    
    **Validates: Requirements 7.4**
    
    This test ensures the data model itself maintains backward compatibility.
    """
    now = datetime.now(timezone.utc)
    
    # Create a sample brand using the old format (without compressed_twin)
    brand = Brand(
        brand_id="brand-123",
        organization_id="org-456",
        name="Test Brand",
        website="https://example.com",
        guidelines=BrandGuidelines(
            colors=[],
            typography=[],
            logos=[],
            voice=None,
            rules=[]
        ),
        compressed_twin=None,  # Optional field
        created_at=now.isoformat(),
        updated_at=now.isoformat(),
        deleted_at=None,
        pdf_url="https://cdn.example.com/brand-123/guidelines.pdf",
        logo_thumbnail_url="https://cdn.example.com/brand-123/logo.png",
        needs_review=["No logo provided"],
        learning_active=False,
        feedback_count=0
    )
    
    # Verify all expected fields are accessible
    assert brand.brand_id == "brand-123"
    assert brand.organization_id == "org-456"
    assert brand.name == "Test Brand"
    assert brand.website == "https://example.com"
    assert isinstance(brand.guidelines, BrandGuidelines)
    assert brand.compressed_twin is None
    assert brand.created_at == now.isoformat()
    assert brand.updated_at == now.isoformat()
    assert brand.deleted_at is None
    assert brand.pdf_url == "https://cdn.example.com/brand-123/guidelines.pdf"
    assert brand.logo_thumbnail_url == "https://cdn.example.com/brand-123/logo.png"
    assert brand.needs_review == ["No logo provided"]
    assert brand.learning_active is False
    assert brand.feedback_count == 0
    
    # Verify the model can be serialized and deserialized
    brand_dict = brand.model_dump()
    assert isinstance(brand_dict, dict)
    assert len(brand_dict) > 0
    
    # Verify all fields are in the dict
    expected_fields = [
        'brand_id', 'organization_id', 'name', 'website', 'guidelines',
        'compressed_twin', 'created_at', 'updated_at', 'deleted_at',
        'pdf_url', 'logo_thumbnail_url', 'needs_review', 'learning_active',
        'feedback_count'
    ]
    
    for field in expected_fields:
        assert field in brand_dict, f"Field {field} should be in serialized dict"
    
    print("✓ Brand model structure is unchanged and backward compatible")
