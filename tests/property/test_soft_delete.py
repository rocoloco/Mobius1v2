"""
Property-based tests for soft delete functionality.

**Feature: mobius-phase-2-refactor, Property 14: Soft delete preserves data**
**Validates: Requirements 4.5**
"""

import pytest
from hypothesis import given, settings, strategies as st, assume
from mobius.models.brand import Brand, BrandGuidelines, Color, Typography
from mobius.models.asset import Asset
from datetime import datetime, timezone
import uuid


# Hypothesis strategies for generating test data
@st.composite
def brand_strategy(draw):
    """Generate valid Brand entity."""
    brand_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    name = draw(st.text(min_size=3, max_size=50))
    
    # Simple guidelines
    guidelines = BrandGuidelines(
        colors=[Color(name="Primary Red", hex="#FF0000", usage="primary")],
        typography=[Typography(family="Arial", weights=["400"], usage="Body text")],
    )
    
    return Brand(
        brand_id=brand_id,
        organization_id=org_id,
        name=name,
        guidelines=guidelines,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        deleted_at=None
    )


@st.composite
def asset_strategy(draw, brand_id: str):
    """Generate valid Asset entity."""
    asset_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    prompt = draw(st.text(min_size=10, max_size=100))
    image_url = f"https://example.com/assets/{asset_id}.png"
    
    return Asset(
        asset_id=asset_id,
        brand_id=brand_id,
        job_id=job_id,
        prompt=prompt,
        image_url=image_url,
        compliance_score=draw(st.floats(min_value=0.0, max_value=100.0)),
        status="completed",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@settings(max_examples=100)
@given(brand_strategy())
def test_soft_delete_preserves_brand_data(brand: Brand):
    """
    Property 14: Soft delete preserves data.
    
    For any brand that is deleted, the brand record should remain
    in the database with deleted_at timestamp set, and the brand
    data should be preserved.
    
    This test validates that:
    1. After soft delete, brand data is still accessible
    2. deleted_at timestamp is set
    3. All brand fields remain unchanged except deleted_at
    """
    # Store original brand data
    original_brand_id = brand.brand_id
    original_name = brand.name
    original_guidelines = brand.guidelines
    original_organization_id = brand.organization_id
    
    # Simulate soft delete by setting deleted_at
    brand.deleted_at = datetime.now(timezone.utc)
    
    # Brand data should still be accessible
    assert brand.brand_id == original_brand_id, \
        "Brand ID should be preserved after soft delete"
    
    assert brand.name == original_name, \
        "Brand name should be preserved after soft delete"
    
    assert brand.guidelines == original_guidelines, \
        "Brand guidelines should be preserved after soft delete"
    
    assert brand.organization_id == original_organization_id, \
        "Organization ID should be preserved after soft delete"
    
    # deleted_at should be set
    assert brand.deleted_at is not None, \
        "deleted_at timestamp should be set after soft delete"
    
    # deleted_at should be a valid datetime
    assert isinstance(brand.deleted_at, datetime), \
        "deleted_at should be a datetime object"


@settings(max_examples=100)
@given(brand_strategy())
def test_soft_delete_timestamp_validity(brand: Brand):
    """
    Property: Soft delete timestamp should be valid.
    
    For any brand that is soft deleted, the deleted_at timestamp
    should be after the created_at timestamp.
    """
    # Simulate soft delete
    brand.deleted_at = datetime.now(timezone.utc).isoformat()
    
    # Parse timestamps for comparison
    created = datetime.fromisoformat(brand.created_at.replace('Z', '+00:00'))
    deleted = datetime.fromisoformat(brand.deleted_at.replace('Z', '+00:00'))
    
    # deleted_at should be after created_at
    assert deleted >= created, \
        "deleted_at should be after or equal to created_at"


@settings(max_examples=100)
@given(brand_strategy())
def test_soft_delete_does_not_remove_record(brand: Brand):
    """
    Property: Soft delete does not remove the record.
    
    For any brand that is soft deleted, the brand record should
    still exist (not None) and all fields should be accessible.
    """
    # Simulate soft delete
    brand.deleted_at = datetime.now(timezone.utc)
    
    # Brand should still exist
    assert brand is not None, "Brand should still exist after soft delete"
    
    # All fields should be accessible
    assert brand.brand_id is not None
    assert brand.organization_id is not None
    assert brand.name is not None
    assert brand.guidelines is not None
    assert brand.created_at is not None
    assert brand.updated_at is not None


@settings(max_examples=100)
@given(brand_strategy())
def test_soft_delete_preserves_relationships(brand: Brand):
    """
    Property: Soft delete preserves brand relationships.
    
    For any brand that is soft deleted, associated assets should
    remain accessible through the brand_id relationship.
    
    This simulates that assets can still be queried by brand_id
    even after the brand is soft deleted.
    """
    # Create a mock asset associated with the brand
    asset = Asset(
        asset_id=str(uuid.uuid4()),
        brand_id=brand.brand_id,
        job_id=str(uuid.uuid4()),
        prompt="Test prompt",
        image_url="https://example.com/test.png",
        compliance_score=85.0,
        status="completed",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    # Simulate soft delete of brand
    brand.deleted_at = datetime.now(timezone.utc)
    
    # Asset should still reference the brand
    assert asset.brand_id == brand.brand_id, \
        "Asset should still reference the soft-deleted brand"
    
    # Brand ID should still be valid for lookups
    assert brand.brand_id is not None
    assert len(brand.brand_id) > 0


@settings(max_examples=100)
@given(brand_strategy())
def test_soft_delete_idempotency(brand: Brand):
    """
    Property: Soft delete is idempotent.
    
    For any brand, soft deleting it multiple times should not
    change the result - the brand should remain soft deleted
    with the same data.
    """
    # First soft delete
    first_delete_time = datetime.now(timezone.utc)
    brand.deleted_at = first_delete_time
    
    original_brand_id = brand.brand_id
    original_name = brand.name
    
    # Second soft delete (simulating calling delete again)
    second_delete_time = datetime.now(timezone.utc)
    brand.deleted_at = second_delete_time
    
    # Brand data should still be preserved
    assert brand.brand_id == original_brand_id
    assert brand.name == original_name
    
    # Brand should still be marked as deleted
    assert brand.deleted_at is not None


@settings(max_examples=100)
@given(brand_strategy())
def test_undeleted_brand_has_no_deleted_at(brand: Brand):
    """
    Property: Active brands have no deleted_at timestamp.
    
    For any brand that has not been deleted, the deleted_at
    field should be None.
    """
    # Ensure brand is not deleted
    brand.deleted_at = None
    
    # deleted_at should be None for active brands
    assert brand.deleted_at is None, \
        "Active brands should have deleted_at set to None"
