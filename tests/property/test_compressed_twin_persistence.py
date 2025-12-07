"""
Property-based tests for compressed twin persistence.

**Feature: gemini-3-dual-architecture, Property 5: Compressed Twin Persistence**

Tests that CompressedDigitalTwin is stored in the Brand Entity database record.
"""

from hypothesis import given, strategies as st, settings as hypothesis_settings, assume
import pytest
from mobius.models.brand import CompressedDigitalTwin, Brand, BrandGuidelines
from mobius.storage.brands import BrandStorage
from datetime import datetime, timezone
import uuid


# Strategy for generating hex color codes
@st.composite
def hex_colors(draw):
    """Generate valid hex color codes."""
    r = draw(st.integers(min_value=0, max_value=255))
    g = draw(st.integers(min_value=0, max_value=255))
    b = draw(st.integers(min_value=0, max_value=255))
    return f"#{r:02X}{g:02X}{b:02X}"


# Strategy for generating CompressedDigitalTwin
@st.composite
def compressed_twins(draw):
    """Generate valid CompressedDigitalTwin instances."""
    return CompressedDigitalTwin(
        primary_colors=draw(st.lists(hex_colors(), min_size=0, max_size=5)),
        secondary_colors=draw(st.lists(hex_colors(), min_size=0, max_size=5)),
        accent_colors=draw(st.lists(hex_colors(), min_size=0, max_size=3)),
        neutral_colors=draw(st.lists(hex_colors(), min_size=0, max_size=5)),
        semantic_colors=draw(st.lists(hex_colors(), min_size=0, max_size=3)),
        font_families=draw(st.lists(st.text(min_size=3, max_size=30), min_size=0, max_size=5)),
        visual_dos=draw(st.lists(st.text(min_size=10, max_size=100), min_size=0, max_size=10)),
        visual_donts=draw(st.lists(st.text(min_size=10, max_size=100), min_size=0, max_size=10)),
        logo_placement=draw(st.one_of(st.none(), st.text(min_size=5, max_size=50))),
        logo_min_size=draw(st.one_of(st.none(), st.text(min_size=5, max_size=30)))
    )


# Property 5: Compressed Twin Persistence
@given(
    compressed_twin=compressed_twins(),
    brand_name=st.text(min_size=3, max_size=50)
)
@hypothesis_settings(max_examples=100)
@pytest.mark.asyncio
async def test_compressed_twin_persisted_to_database(compressed_twin, brand_name):
    """
    **Feature: gemini-3-dual-architecture, Property 5: Compressed Twin Persistence**
    
    *For any* successful brand extraction, the Compressed Digital Twin should be 
    stored in the Brand Entity database record.
    
    **Validates: Requirements 2.5**
    
    This property test verifies that compressed twins are persisted to the database.
    """
    # Generate unique IDs for this test
    brand_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    
    # Create a minimal BrandGuidelines
    guidelines = BrandGuidelines(
        colors=[],
        typography=[],
        logos=[],
        rules=[]
    )
    
    # Create Brand entity with compressed twin
    brand = Brand(
        brand_id=brand_id,
        organization_id=org_id,
        name=brand_name,
        website=None,
        guidelines=guidelines,
        compressed_twin=compressed_twin,
        pdf_url="https://example.com/test.pdf",
        logo_thumbnail_url=None,
        needs_review=[],
        learning_active=False,
        feedback_count=0,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        deleted_at=None,
    )
    
    # Persist to database
    storage = BrandStorage()
    try:
        created_brand = await storage.create_brand(brand)
        
        # Verify compressed_twin was persisted
        assert created_brand.compressed_twin is not None, (
            "Compressed twin should be persisted to database"
        )
        
        # Verify the persisted compressed twin matches the original
        assert created_brand.compressed_twin.primary_colors == compressed_twin.primary_colors
        assert created_brand.compressed_twin.secondary_colors == compressed_twin.secondary_colors
        assert created_brand.compressed_twin.accent_colors == compressed_twin.accent_colors
        assert created_brand.compressed_twin.neutral_colors == compressed_twin.neutral_colors
        assert created_brand.compressed_twin.semantic_colors == compressed_twin.semantic_colors
        assert created_brand.compressed_twin.font_families == compressed_twin.font_families
        assert created_brand.compressed_twin.visual_dos == compressed_twin.visual_dos
        assert created_brand.compressed_twin.visual_donts == compressed_twin.visual_donts
        assert created_brand.compressed_twin.logo_placement == compressed_twin.logo_placement
        assert created_brand.compressed_twin.logo_min_size == compressed_twin.logo_min_size
        
        # Retrieve from database to verify persistence
        retrieved_brand = await storage.get_brand(brand_id)
        assert retrieved_brand is not None, "Brand should be retrievable from database"
        assert retrieved_brand.compressed_twin is not None, (
            "Compressed twin should be retrievable from database"
        )
        
        # Verify retrieved compressed twin matches original
        assert retrieved_brand.compressed_twin.primary_colors == compressed_twin.primary_colors
        assert retrieved_brand.compressed_twin.font_families == compressed_twin.font_families
        
        print(f"✓ CompressedDigitalTwin persisted and retrieved for brand '{brand_name}'")
        
    finally:
        # Cleanup: delete the test brand
        try:
            await storage.delete_brand(brand_id)
        except Exception:
            pass  # Ignore cleanup errors


@pytest.mark.asyncio
async def test_compressed_twin_persistence_with_none():
    """
    **Feature: gemini-3-dual-architecture, Property 5: Compressed Twin Persistence**
    
    Verify that brands can be created without a compressed twin (None value).
    
    **Validates: Requirements 2.5**
    
    This test ensures the compressed_twin field is optional.
    """
    brand_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    
    guidelines = BrandGuidelines(
        colors=[],
        typography=[],
        logos=[],
        rules=[]
    )
    
    # Create Brand entity WITHOUT compressed twin
    brand = Brand(
        brand_id=brand_id,
        organization_id=org_id,
        name="Test Brand Without Twin",
        website=None,
        guidelines=guidelines,
        compressed_twin=None,  # Explicitly None
        pdf_url="https://example.com/test.pdf",
        logo_thumbnail_url=None,
        needs_review=[],
        learning_active=False,
        feedback_count=0,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        deleted_at=None,
    )
    
    storage = BrandStorage()
    try:
        created_brand = await storage.create_brand(brand)
        
        # Verify brand was created successfully even without compressed twin
        assert created_brand.brand_id == brand_id
        assert created_brand.compressed_twin is None
        
        # Retrieve from database
        retrieved_brand = await storage.get_brand(brand_id)
        assert retrieved_brand is not None
        assert retrieved_brand.compressed_twin is None
        
        print("✓ Brand can be persisted without compressed twin (None value)")
        
    finally:
        try:
            await storage.delete_brand(brand_id)
        except Exception:
            pass


@given(
    compressed_twin=compressed_twins()
)
@hypothesis_settings(max_examples=100)
@pytest.mark.asyncio
async def test_compressed_twin_roundtrip_preserves_data(compressed_twin):
    """
    **Feature: gemini-3-dual-architecture, Property 5: Compressed Twin Persistence**
    
    *For any* CompressedDigitalTwin, persisting and retrieving should preserve all data.
    
    **Validates: Requirements 2.5**
    
    This property test verifies data integrity through database roundtrip.
    """
    brand_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    
    guidelines = BrandGuidelines(
        colors=[],
        typography=[],
        logos=[],
        rules=[]
    )
    
    brand = Brand(
        brand_id=brand_id,
        organization_id=org_id,
        name="Roundtrip Test Brand",
        website=None,
        guidelines=guidelines,
        compressed_twin=compressed_twin,
        pdf_url="https://example.com/test.pdf",
        logo_thumbnail_url=None,
        needs_review=[],
        learning_active=False,
        feedback_count=0,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        deleted_at=None,
    )
    
    storage = BrandStorage()
    try:
        # Persist
        await storage.create_brand(brand)
        
        # Retrieve
        retrieved_brand = await storage.get_brand(brand_id)
        assert retrieved_brand is not None
        assert retrieved_brand.compressed_twin is not None
        
        # Verify all fields match exactly
        original_dict = compressed_twin.model_dump()
        retrieved_dict = retrieved_brand.compressed_twin.model_dump()
        
        assert original_dict == retrieved_dict, (
            "Roundtrip should preserve all compressed twin data"
        )
        
        print(f"✓ CompressedDigitalTwin roundtrip preserves all data")
        
    finally:
        try:
            await storage.delete_brand(brand_id)
        except Exception:
            pass


@pytest.mark.asyncio
async def test_compressed_twin_update_persistence():
    """
    **Feature: gemini-3-dual-architecture, Property 5: Compressed Twin Persistence**
    
    Verify that compressed twin can be updated after initial creation.
    
    **Validates: Requirements 2.5**
    
    This test ensures compressed twins can be modified and re-persisted.
    """
    brand_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    
    guidelines = BrandGuidelines(
        colors=[],
        typography=[],
        logos=[],
        rules=[]
    )
    
    # Create initial compressed twin
    initial_twin = CompressedDigitalTwin(
        primary_colors=["#FF0000"],
        font_families=["Arial"]
    )
    
    brand = Brand(
        brand_id=brand_id,
        organization_id=org_id,
        name="Update Test Brand",
        website=None,
        guidelines=guidelines,
        compressed_twin=initial_twin,
        pdf_url="https://example.com/test.pdf",
        logo_thumbnail_url=None,
        needs_review=[],
        learning_active=False,
        feedback_count=0,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        deleted_at=None,
    )
    
    storage = BrandStorage()
    try:
        # Create brand
        await storage.create_brand(brand)
        
        # Update with new compressed twin
        updated_twin = CompressedDigitalTwin(
            primary_colors=["#00FF00", "#0000FF"],
            font_families=["Helvetica", "Georgia"],
            visual_dos=["Use primary colors for headers"]
        )
        
        await storage.update_brand(
            brand_id,
            {"compressed_twin": updated_twin.model_dump()}
        )
        
        # Retrieve and verify update
        retrieved_brand = await storage.get_brand(brand_id)
        assert retrieved_brand is not None
        assert retrieved_brand.compressed_twin is not None
        
        # Verify updated values
        assert len(retrieved_brand.compressed_twin.primary_colors) == 2
        assert "#00FF00" in retrieved_brand.compressed_twin.primary_colors
        assert "#0000FF" in retrieved_brand.compressed_twin.primary_colors
        assert "Helvetica" in retrieved_brand.compressed_twin.font_families
        assert "Georgia" in retrieved_brand.compressed_twin.font_families
        assert len(retrieved_brand.compressed_twin.visual_dos) == 1
        
        print("✓ CompressedDigitalTwin can be updated and re-persisted")
        
    finally:
        try:
            await storage.delete_brand(brand_id)
        except Exception:
            pass
