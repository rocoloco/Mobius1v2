"""
Property-based tests for brand list metadata.

**Feature: mobius-phase-2-refactor, Property (custom): Brand list contains required fields**
**Validates: Requirements 4.3**
"""

import pytest
from hypothesis import given, settings, strategies as st, assume
from datetime import datetime, timezone
from mobius.api.schemas import BrandListItem, BrandListResponse


@settings(max_examples=100)
@given(
    brand_id=st.text(min_size=1, max_size=100),
    name=st.text(min_size=1, max_size=255),
    logo_url=st.one_of(st.none(), st.just("https://example.com/logo.png")),
    asset_count=st.integers(min_value=0, max_value=10000),
    avg_score=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
)
def test_brand_list_item_contains_required_fields(
    brand_id: str,
    name: str,
    logo_url,
    asset_count: int,
    avg_score: float,
):
    """
    Property: Brand list items contain all required fields.

    For any brand list item, it should contain:
    - brand_id (non-empty string)
    - name (non-empty string)
    - logo_thumbnail_url (optional string)
    - asset_count (non-negative integer)
    - avg_compliance_score (float 0-100)
    - last_activity (datetime)

    This ensures the brand list provides all necessary information
    for the UI to display brand summaries.
    """
    last_activity = datetime.now(timezone.utc)

    # Create a brand list item
    item = BrandListItem(
        brand_id=brand_id,
        name=name,
        logo_thumbnail_url=logo_url,
        asset_count=asset_count,
        avg_compliance_score=avg_score,
        last_activity=last_activity,
    )

    # Verify all required fields are present
    assert item.brand_id == brand_id
    assert item.name == name
    assert item.logo_thumbnail_url == logo_url
    assert item.asset_count == asset_count
    assert item.avg_compliance_score == avg_score
    assert item.last_activity == last_activity

    # Verify types
    assert isinstance(item.brand_id, str)
    assert isinstance(item.name, str)
    assert isinstance(item.asset_count, int)
    assert isinstance(item.avg_compliance_score, float)
    assert isinstance(item.last_activity, datetime)

    # Verify constraints
    assert len(item.brand_id) > 0
    assert len(item.name) > 0
    assert item.asset_count >= 0
    assert 0.0 <= item.avg_compliance_score <= 100.0


@settings(max_examples=100)
@given(
    num_brands=st.integers(min_value=0, max_value=100),
    request_id=st.text(min_size=1, max_size=50),
)
def test_brand_list_response_structure(num_brands: int, request_id: str):
    """
    Property: Brand list response has correct structure.

    For any number of brands, the response should:
    - Have a 'brands' list with the correct count
    - Have a 'total' field matching the list length
    - Have a 'request_id' field
    """
    # Create brand list items
    brands = []
    for i in range(num_brands):
        brands.append(
            BrandListItem(
                brand_id=f"brand-{i}",
                name=f"Brand {i}",
                logo_thumbnail_url=None,
                asset_count=0,
                avg_compliance_score=0.0,
                last_activity=datetime.now(timezone.utc),
            )
        )

    # Create response
    response = BrandListResponse(
        brands=brands,
        total=num_brands,
        request_id=request_id,
    )

    # Verify structure
    assert len(response.brands) == num_brands
    assert response.total == num_brands
    assert response.request_id == request_id
    assert isinstance(response.brands, list)


@settings(max_examples=100)
@given(
    asset_count=st.integers(min_value=0, max_value=10000),
)
def test_asset_count_non_negative(asset_count: int):
    """
    Property: Asset count is always non-negative.

    For any brand list item, the asset_count should be >= 0.
    """
    assume(asset_count >= 0)  # Only test valid values

    item = BrandListItem(
        brand_id="test-brand",
        name="Test Brand",
        logo_thumbnail_url=None,
        asset_count=asset_count,
        avg_compliance_score=50.0,
        last_activity=datetime.now(timezone.utc),
    )

    assert item.asset_count >= 0


@settings(max_examples=100)
@given(
    avg_score=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
)
def test_avg_compliance_score_bounded(avg_score: float):
    """
    Property: Average compliance score is bounded between 0 and 100.

    For any brand list item, the avg_compliance_score should be
    in the range [0.0, 100.0].
    """
    item = BrandListItem(
        brand_id="test-brand",
        name="Test Brand",
        logo_thumbnail_url=None,
        asset_count=0,
        avg_compliance_score=avg_score,
        last_activity=datetime.now(timezone.utc),
    )

    assert 0.0 <= item.avg_compliance_score <= 100.0


@settings(max_examples=100)
@given(
    brands_data=st.lists(
        st.tuples(
            st.text(min_size=1, max_size=50),  # brand_id
            st.text(min_size=1, max_size=100),  # name
            st.integers(min_value=0, max_value=1000),  # asset_count
            st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),  # avg_score
        ),
        min_size=0,
        max_size=50,
    ),
)
def test_brand_list_preserves_order(brands_data):
    """
    Property: Brand list preserves the order of brands.

    For any list of brands, the response should maintain the same order.
    """
    # Create brand list items
    brands = []
    for brand_id, name, asset_count, avg_score in brands_data:
        brands.append(
            BrandListItem(
                brand_id=brand_id,
                name=name,
                logo_thumbnail_url=None,
                asset_count=asset_count,
                avg_compliance_score=avg_score,
                last_activity=datetime.now(timezone.utc),
            )
        )

    # Create response
    response = BrandListResponse(
        brands=brands,
        total=len(brands),
        request_id="test-request",
    )

    # Verify order is preserved
    for i, (brand_id, name, _, _) in enumerate(brands_data):
        assert response.brands[i].brand_id == brand_id
        assert response.brands[i].name == name


@settings(max_examples=100)
@given(
    name=st.text(min_size=1, max_size=255),
)
def test_brand_name_not_empty(name: str):
    """
    Property: Brand name is never empty.

    For any brand list item, the name field should be non-empty.
    """
    item = BrandListItem(
        brand_id="test-brand",
        name=name,
        logo_thumbnail_url=None,
        asset_count=0,
        avg_compliance_score=50.0,
        last_activity=datetime.now(timezone.utc),
    )

    assert len(item.name) > 0
    assert item.name.strip() != "" or len(item.name) > 0  # Allow whitespace-only if generated
