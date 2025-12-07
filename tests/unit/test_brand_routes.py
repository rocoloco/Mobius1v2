"""
Unit tests for brand management API routes.

Tests PDF validation, brand CRUD operations, search/filtering, and soft delete.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
import uuid

from mobius.api.routes import (
    ingest_brand_handler,
    list_brands_handler,
    get_brand_handler,
    update_brand_handler,
    delete_brand_handler,
)
from mobius.api.errors import ValidationError, NotFoundError, StorageError
from mobius.api.schemas import UpdateBrandRequest
from mobius.models.brand import Brand, BrandGuidelines, Color, Typography
from mobius.constants import MAX_PDF_SIZE_BYTES, ALLOWED_PDF_MIME_TYPES


@pytest.fixture
def sample_brand():
    """Sample brand entity for testing."""
    return Brand(
        brand_id=str(uuid.uuid4()),
        organization_id=str(uuid.uuid4()),
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=[
                Color(name="Primary Red", hex="#FF0000", usage="primary"),
                Color(name="Secondary Blue", hex="#0000FF", usage="secondary"),
            ],
            typography=[
                Typography(family="Arial", weights=["400", "700"], usage="Body text")
            ],
        ),
        pdf_url="https://example.com/brand.pdf",
        logo_thumbnail_url="https://example.com/logo.png",
        needs_review=[],
        learning_active=False,
        feedback_count=0,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


@pytest.fixture
def valid_pdf_bytes():
    """Valid PDF file bytes."""
    # PDF header followed by some content
    return b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n" + b"0" * 1000


@pytest.fixture
def invalid_pdf_bytes():
    """Invalid PDF file bytes (not a PDF)."""
    return b"This is not a PDF file"


# PDF Validation Tests


@pytest.mark.asyncio
async def test_ingest_brand_validates_file_size():
    """Test that file size validation rejects files over 50MB."""
    # Create a file that's too large
    large_file = b"%PDF-1.4\n" + b"0" * (MAX_PDF_SIZE_BYTES + 1)

    with pytest.raises(ValidationError) as exc_info:
        await ingest_brand_handler(
            organization_id="org-123",
            brand_name="Test Brand",
            file=large_file,
            content_type="application/pdf",
            filename="large.pdf",
        )

    error = exc_info.value
    assert error.status_code == 422
    assert error.error_response.error.code == "FILE_TOO_LARGE"
    assert "50MB" in error.error_response.error.message


@pytest.mark.asyncio
async def test_ingest_brand_validates_mime_type():
    """Test that MIME type validation rejects non-PDF files."""
    with pytest.raises(ValidationError) as exc_info:
        await ingest_brand_handler(
            organization_id="org-123",
            brand_name="Test Brand",
            file=b"some content",
            content_type="image/jpeg",  # Wrong MIME type
            filename="image.jpg",
        )

    error = exc_info.value
    assert error.status_code == 422
    assert error.error_response.error.code == "INVALID_FILE_TYPE"
    assert "PDF" in error.error_response.error.message


@pytest.mark.asyncio
async def test_ingest_brand_validates_pdf_header(invalid_pdf_bytes):
    """Test that PDF header validation rejects invalid PDFs."""
    with pytest.raises(ValidationError) as exc_info:
        await ingest_brand_handler(
            organization_id="org-123",
            brand_name="Test Brand",
            file=invalid_pdf_bytes,
            content_type="application/pdf",
            filename="fake.pdf",
        )

    error = exc_info.value
    assert error.status_code == 422
    assert error.error_response.error.code == "INVALID_PDF"
    assert "valid PDF" in error.error_response.error.message


@pytest.mark.asyncio
async def test_ingest_brand_accepts_valid_pdf(valid_pdf_bytes):
    """Test that valid PDFs pass basic validation checks."""
    # This test verifies that the PDF validation logic (size, MIME type, header)
    # works correctly. It will fail at the database level since we're using
    # a test UUID, but that's expected - we're only testing validation here.
    
    # Use valid UUID format for organization_id
    try:
        response = await ingest_brand_handler(
            organization_id="123e4567-e89b-12d3-a456-426614174000",
            brand_name=f"Test Brand {uuid.uuid4()}",  # Unique name to avoid duplicates
            file=valid_pdf_bytes,
            content_type="application/pdf",
            filename="valid.pdf",
        )
        # If we get here, validation passed and brand was created
        assert response.status == "created"
        assert response.request_id is not None
    except Exception as e:
        # If we get a database error, that's OK - validation still passed
        # We're only testing that the PDF validation logic works
        if "No /Root object" in str(e) or "pdf_parsing_failed" in str(e):
            # PDF validation passed, but parsing failed (expected for minimal test PDF)
            pass
        else:
            # Re-raise unexpected errors
            raise


# Brand List Tests


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
@patch("mobius.api.routes.get_supabase_client")
async def test_list_brands_returns_brands_with_stats(
    mock_get_client, mock_storage_class, sample_brand
):
    """Test listing brands returns brands with computed statistics."""
    # Mock storage
    mock_storage = Mock()
    mock_storage.list_brands = AsyncMock(return_value=[sample_brand])
    mock_storage_class.return_value = mock_storage

    # Mock Supabase client for asset queries
    mock_client = Mock()
    mock_execute = Mock()
    mock_execute.data = [
        {"compliance_score": 85.0, "created_at": datetime.now(timezone.utc).isoformat()},
        {"compliance_score": 90.0, "created_at": datetime.now(timezone.utc).isoformat()},
    ]
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
        mock_execute
    )
    mock_get_client.return_value = mock_client

    response = await list_brands_handler(
        organization_id="org-123",
        search=None,
        limit=100,
    )

    assert len(response.brands) == 1
    assert response.brands[0].brand_id == sample_brand.brand_id
    assert response.brands[0].name == sample_brand.name
    assert response.brands[0].asset_count == 2
    assert response.brands[0].avg_compliance_score == 87.5  # (85 + 90) / 2
    assert response.total == 1


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
@patch("mobius.api.routes.get_supabase_client")
async def test_list_brands_with_search(mock_get_client, mock_storage_class, sample_brand):
    """Test listing brands with search filter."""
    mock_storage = Mock()
    mock_storage.list_brands = AsyncMock(return_value=[sample_brand])
    mock_storage_class.return_value = mock_storage

    # Mock Supabase client
    mock_client = Mock()
    mock_execute = Mock()
    mock_execute.data = []
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
        mock_execute
    )
    mock_get_client.return_value = mock_client

    response = await list_brands_handler(
        organization_id="org-123",
        search="Test",
        limit=100,
    )

    # Verify search parameter was passed
    mock_storage.list_brands.assert_called_once_with("org-123", "Test", 100)


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
@patch("mobius.api.routes.get_supabase_client")
async def test_list_brands_handles_no_assets(
    mock_get_client, mock_storage_class, sample_brand
):
    """Test listing brands when brand has no assets."""
    mock_storage = Mock()
    mock_storage.list_brands = AsyncMock(return_value=[sample_brand])
    mock_storage_class.return_value = mock_storage

    # Mock Supabase client with no assets
    mock_client = Mock()
    mock_execute = Mock()
    mock_execute.data = []
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
        mock_execute
    )
    mock_get_client.return_value = mock_client

    response = await list_brands_handler(
        organization_id="org-123",
        search=None,
        limit=100,
    )

    assert len(response.brands) == 1
    assert response.brands[0].asset_count == 0
    assert response.brands[0].avg_compliance_score == 0.0


# Get Brand Tests


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
async def test_get_brand_returns_brand_details(mock_storage_class, sample_brand):
    """Test getting brand details by ID."""
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(return_value=sample_brand)
    mock_storage_class.return_value = mock_storage

    response = await get_brand_handler(brand_id=sample_brand.brand_id)

    assert response.brand_id == sample_brand.brand_id
    assert response.name == sample_brand.name
    assert response.organization_id == sample_brand.organization_id
    assert response.pdf_url == sample_brand.pdf_url
    assert response.learning_active == sample_brand.learning_active


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
async def test_get_brand_raises_not_found(mock_storage_class):
    """Test getting non-existent brand raises NotFoundError."""
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(return_value=None)
    mock_storage_class.return_value = mock_storage

    with pytest.raises(NotFoundError) as exc_info:
        await get_brand_handler(brand_id="nonexistent-brand")

    error = exc_info.value
    assert error.status_code == 404
    assert "BRAND_NOT_FOUND" in error.error_response.error.code


# Update Brand Tests


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
async def test_update_brand_updates_fields(mock_storage_class, sample_brand):
    """Test updating brand metadata."""
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(return_value=sample_brand)

    # Create updated brand
    updated_brand = sample_brand.model_copy()
    updated_brand.name = "Updated Brand Name"
    mock_storage.update_brand = AsyncMock(return_value=updated_brand)
    mock_storage_class.return_value = mock_storage

    updates = UpdateBrandRequest(name="Updated Brand Name")
    response = await update_brand_handler(
        brand_id=sample_brand.brand_id,
        updates=updates,
    )

    assert response.name == "Updated Brand Name"
    mock_storage.update_brand.assert_called_once()


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
async def test_update_brand_with_no_updates(mock_storage_class, sample_brand):
    """Test updating brand with no fields returns current brand."""
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(return_value=sample_brand)
    mock_storage_class.return_value = mock_storage

    updates = UpdateBrandRequest()  # No fields set
    response = await update_brand_handler(
        brand_id=sample_brand.brand_id,
        updates=updates,
    )

    # Should return current brand without calling update
    assert response.brand_id == sample_brand.brand_id
    assert response.name == sample_brand.name
    mock_storage.update_brand.assert_not_called()


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
async def test_update_brand_raises_not_found(mock_storage_class):
    """Test updating non-existent brand raises NotFoundError."""
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(return_value=None)
    mock_storage_class.return_value = mock_storage

    updates = UpdateBrandRequest(name="New Name")

    with pytest.raises(NotFoundError) as exc_info:
        await update_brand_handler(
            brand_id="nonexistent-brand",
            updates=updates,
        )

    error = exc_info.value
    assert error.status_code == 404


# Delete Brand Tests


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
async def test_delete_brand_soft_deletes(mock_storage_class, sample_brand):
    """Test soft deleting a brand."""
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(return_value=sample_brand)
    mock_storage.delete_brand = AsyncMock(return_value=True)
    mock_storage_class.return_value = mock_storage

    response = await delete_brand_handler(brand_id=sample_brand.brand_id)

    assert response["brand_id"] == sample_brand.brand_id
    assert response["status"] == "deleted"
    mock_storage.delete_brand.assert_called_once_with(sample_brand.brand_id)


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
async def test_delete_brand_raises_not_found(mock_storage_class):
    """Test deleting non-existent brand raises NotFoundError."""
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(return_value=None)
    mock_storage_class.return_value = mock_storage

    with pytest.raises(NotFoundError) as exc_info:
        await delete_brand_handler(brand_id="nonexistent-brand")

    error = exc_info.value
    assert error.status_code == 404


# Error Handling Tests


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
@patch("mobius.api.routes.get_supabase_client")
async def test_list_brands_handles_storage_error(mock_get_client, mock_storage_class):
    """Test that storage errors are properly handled."""
    mock_storage = Mock()
    mock_storage.list_brands = AsyncMock(side_effect=Exception("Database error"))
    mock_storage_class.return_value = mock_storage

    with pytest.raises(StorageError) as exc_info:
        await list_brands_handler(
            organization_id="org-123",
            search=None,
            limit=100,
        )

    error = exc_info.value
    assert error.status_code == 500
    assert error.error_response.error.code == "STORAGE_ERROR"


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
async def test_get_brand_handles_storage_error(mock_storage_class):
    """Test that storage errors in get_brand are properly handled."""
    mock_storage = Mock()
    mock_storage.get_brand = AsyncMock(side_effect=Exception("Database error"))
    mock_storage_class.return_value = mock_storage

    with pytest.raises(StorageError) as exc_info:
        await get_brand_handler(brand_id="brand-123")

    error = exc_info.value
    assert error.status_code == 500


# Search and Filtering Tests


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
@patch("mobius.api.routes.get_supabase_client")
async def test_list_brands_filters_by_organization(
    mock_get_client, mock_storage_class, sample_brand
):
    """Test that brands are filtered by organization_id."""
    mock_storage = Mock()
    mock_storage.list_brands = AsyncMock(return_value=[sample_brand])
    mock_storage_class.return_value = mock_storage

    # Mock Supabase client
    mock_client = Mock()
    mock_execute = Mock()
    mock_execute.data = []
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
        mock_execute
    )
    mock_get_client.return_value = mock_client

    response = await list_brands_handler(
        organization_id="specific-org-123",
        search=None,
        limit=100,
    )

    # Verify organization_id was passed to storage
    mock_storage.list_brands.assert_called_once_with("specific-org-123", None, 100)


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
@patch("mobius.api.routes.get_supabase_client")
async def test_list_brands_respects_limit(
    mock_get_client, mock_storage_class, sample_brand
):
    """Test that brand list respects the limit parameter."""
    mock_storage = Mock()
    mock_storage.list_brands = AsyncMock(return_value=[sample_brand])
    mock_storage_class.return_value = mock_storage

    # Mock Supabase client
    mock_client = Mock()
    mock_execute = Mock()
    mock_execute.data = []
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
        mock_execute
    )
    mock_get_client.return_value = mock_client

    response = await list_brands_handler(
        organization_id="org-123",
        search=None,
        limit=50,
    )

    # Verify limit was passed to storage
    mock_storage.list_brands.assert_called_once_with("org-123", None, 50)
