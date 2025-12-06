"""
Property-based tests for file storage bucket correctness.

**Feature: mobius-phase-2-refactor, Property (custom): Files stored in correct buckets**

Tests that files are stored in the correct Supabase Storage buckets based on file type.

**Validates: Requirements 10.1, 10.2**
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from mobius.storage.files import FileStorage
from mobius.constants import BRANDS_BUCKET, ASSETS_BUCKET
from unittest.mock import Mock, patch, AsyncMock
import uuid


@st.composite
def brand_id_strategy(draw):
    """Generate a valid brand ID (UUID format)."""
    return str(uuid.uuid4())


@st.composite
def asset_id_strategy(draw):
    """Generate a valid asset ID (UUID format)."""
    return str(uuid.uuid4())


@st.composite
def pdf_filename_strategy(draw):
    """Generate a valid PDF filename."""
    name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L", "N"))))
    return f"{name}.pdf"


@st.composite
def image_filename_strategy(draw):
    """Generate a valid image filename."""
    name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L", "N"))))
    extension = draw(st.sampled_from([".png", ".jpg", ".jpeg", ".webp"]))
    return f"{name}{extension}"


@given(brand_id=brand_id_strategy(), filename=pdf_filename_strategy())
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
async def test_pdfs_stored_in_brands_bucket(mock_get_client, brand_id, filename):
    """
    Property: PDFs are stored in the brands bucket.

    For any PDF file uploaded through upload_pdf(), the file should be
    stored in the 'brands' bucket, not the 'assets' bucket.

    **Validates: Requirements 10.1**
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_storage = Mock()
    mock_brands_bucket = Mock()
    mock_assets_bucket = Mock()

    # Track which bucket was used
    brands_bucket_called = []
    assets_bucket_called = []

    def mock_from_(bucket_name):
        if bucket_name == BRANDS_BUCKET:
            brands_bucket_called.append(True)
            return mock_brands_bucket
        elif bucket_name == ASSETS_BUCKET:
            assets_bucket_called.append(True)
            return mock_assets_bucket
        return Mock()

    mock_storage.from_ = mock_from_
    mock_client.storage = mock_storage

    # Mock upload and get_public_url
    mock_brands_bucket.upload = Mock(return_value={"path": f"{brand_id}/{filename}"})
    mock_brands_bucket.get_public_url = Mock(
        return_value=f"https://example.supabase.co/storage/v1/object/public/{BRANDS_BUCKET}/{brand_id}/{filename}"
    )

    mock_get_client.return_value = mock_client

    # Create FileStorage instance
    file_storage = FileStorage()

    # Upload a PDF
    pdf_bytes = b"%PDF-1.4 test content"
    url = await file_storage.upload_pdf(pdf_bytes, brand_id, filename)

    # Verify PDF was stored in brands bucket
    assert len(brands_bucket_called) > 0, "PDF should be stored in brands bucket"
    assert len(assets_bucket_called) == 0, "PDF should NOT be stored in assets bucket"

    # Verify URL contains brands bucket
    assert BRANDS_BUCKET in url, f"URL should contain brands bucket, got: {url}"
    assert ASSETS_BUCKET not in url, f"URL should NOT contain assets bucket, got: {url}"


@given(asset_id=asset_id_strategy(), filename=image_filename_strategy())
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
@patch("httpx.AsyncClient")
async def test_images_stored_in_assets_bucket(mock_httpx_client, mock_get_client, asset_id, filename):
    """
    Property: Images are stored in the assets bucket.

    For any image file uploaded through upload_image(), the file should be
    stored in the 'assets' bucket, not the 'brands' bucket.

    **Validates: Requirements 10.2**
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_storage = Mock()
    mock_brands_bucket = Mock()
    mock_assets_bucket = Mock()

    # Track which bucket was used
    brands_bucket_called = []
    assets_bucket_called = []

    def mock_from_(bucket_name):
        if bucket_name == BRANDS_BUCKET:
            brands_bucket_called.append(True)
            return mock_brands_bucket
        elif bucket_name == ASSETS_BUCKET:
            assets_bucket_called.append(True)
            return mock_assets_bucket
        return Mock()

    mock_storage.from_ = mock_from_
    mock_client.storage = mock_storage

    # Mock upload and get_public_url
    mock_assets_bucket.upload = Mock(return_value={"path": f"{asset_id}/{filename}"})
    mock_assets_bucket.get_public_url = Mock(
        return_value=f"https://example.supabase.co/storage/v1/object/public/{ASSETS_BUCKET}/{asset_id}/{filename}"
    )

    mock_get_client.return_value = mock_client

    # Mock httpx client for downloading image
    mock_response = Mock()
    mock_response.content = b"fake image data"
    mock_response.raise_for_status = Mock()

    mock_http_instance = AsyncMock()
    mock_http_instance.__aenter__ = AsyncMock(return_value=mock_http_instance)
    mock_http_instance.__aexit__ = AsyncMock()
    mock_http_instance.get = AsyncMock(return_value=mock_response)

    mock_httpx_client.return_value = mock_http_instance

    # Create FileStorage instance
    file_storage = FileStorage()

    # Upload an image
    source_url = "https://example.com/generated-image.png"
    url = await file_storage.upload_image(source_url, asset_id, filename)

    # Verify image was stored in assets bucket
    assert len(assets_bucket_called) > 0, "Image should be stored in assets bucket"
    assert len(brands_bucket_called) == 0, "Image should NOT be stored in brands bucket"

    # Verify URL contains assets bucket
    assert ASSETS_BUCKET in url, f"URL should contain assets bucket, got: {url}"
    assert BRANDS_BUCKET not in url, f"URL should NOT contain brands bucket, got: {url}"


@given(
    brand_id=brand_id_strategy(),
    asset_id=asset_id_strategy(),
    pdf_filename=pdf_filename_strategy(),
    image_filename=image_filename_strategy(),
)
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
@patch("httpx.AsyncClient")
async def test_bucket_separation_maintained(
    mock_httpx_client, mock_get_client, brand_id, asset_id, pdf_filename, image_filename
):
    """
    Property: Bucket separation is maintained across operations.

    For any sequence of PDF and image uploads, PDFs should always go to
    the brands bucket and images should always go to the assets bucket.
    There should be no cross-contamination.

    **Validates: Requirements 10.1, 10.2**
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_storage = Mock()
    mock_brands_bucket = Mock()
    mock_assets_bucket = Mock()

    # Track bucket usage
    bucket_usage = {"brands": [], "assets": []}

    def mock_from_(bucket_name):
        if bucket_name == BRANDS_BUCKET:
            bucket_usage["brands"].append(bucket_name)
            return mock_brands_bucket
        elif bucket_name == ASSETS_BUCKET:
            bucket_usage["assets"].append(bucket_name)
            return mock_assets_bucket
        return Mock()

    mock_storage.from_ = mock_from_
    mock_client.storage = mock_storage

    # Mock brands bucket
    mock_brands_bucket.upload = Mock(return_value={"path": f"{brand_id}/{pdf_filename}"})
    mock_brands_bucket.get_public_url = Mock(
        return_value=f"https://example.supabase.co/storage/v1/object/public/{BRANDS_BUCKET}/{brand_id}/{pdf_filename}"
    )

    # Mock assets bucket
    mock_assets_bucket.upload = Mock(return_value={"path": f"{asset_id}/{image_filename}"})
    mock_assets_bucket.get_public_url = Mock(
        return_value=f"https://example.supabase.co/storage/v1/object/public/{ASSETS_BUCKET}/{asset_id}/{image_filename}"
    )

    mock_get_client.return_value = mock_client

    # Mock httpx client
    mock_response = Mock()
    mock_response.content = b"fake image data"
    mock_response.raise_for_status = Mock()

    mock_http_instance = AsyncMock()
    mock_http_instance.__aenter__ = AsyncMock(return_value=mock_http_instance)
    mock_http_instance.__aexit__ = AsyncMock()
    mock_http_instance.get = AsyncMock(return_value=mock_response)

    mock_httpx_client.return_value = mock_http_instance

    # Create FileStorage instance
    file_storage = FileStorage()

    # Upload PDF
    pdf_bytes = b"%PDF-1.4 test content"
    pdf_url = await file_storage.upload_pdf(pdf_bytes, brand_id, pdf_filename)

    # Upload image
    source_url = "https://example.com/generated-image.png"
    image_url = await file_storage.upload_image(source_url, asset_id, image_filename)

    # Verify bucket separation
    assert len(bucket_usage["brands"]) > 0, "Brands bucket should be used for PDFs"
    assert len(bucket_usage["assets"]) > 0, "Assets bucket should be used for images"

    # Verify URLs contain correct buckets by checking the bucket path segment
    # URL format: https://example.supabase.co/storage/v1/object/public/{bucket}/{path}
    # Extract bucket from URL (it's the 7th segment after splitting by '/')
    pdf_url_parts = pdf_url.split('/')
    pdf_bucket = pdf_url_parts[7] if len(pdf_url_parts) > 7 else ""
    
    image_url_parts = image_url.split('/')
    image_bucket = image_url_parts[7] if len(image_url_parts) > 7 else ""
    
    assert pdf_bucket == BRANDS_BUCKET, f"PDF should be in brands bucket, got {pdf_bucket}"
    assert image_bucket == ASSETS_BUCKET, f"Image should be in assets bucket, got {image_bucket}"


@given(brand_id=brand_id_strategy())
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
async def test_get_file_url_respects_bucket_parameter(mock_get_client, brand_id):
    """
    Property: get_file_url respects the bucket parameter.

    For any bucket parameter passed to get_file_url(), the returned URL
    should reference that specific bucket.

    **Validates: Requirements 10.1, 10.2**
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_storage = Mock()

    # Track which bucket was accessed
    accessed_buckets = []

    def mock_from_(bucket_name):
        accessed_buckets.append(bucket_name)
        mock_bucket = Mock()
        mock_bucket.get_public_url = Mock(
            return_value=f"https://example.supabase.co/storage/v1/object/public/{bucket_name}/test/file.pdf"
        )
        return mock_bucket

    mock_storage.from_ = mock_from_
    mock_client.storage = mock_storage
    mock_get_client.return_value = mock_client

    # Create FileStorage instance
    file_storage = FileStorage()

    # Test brands bucket
    brands_url = await file_storage.get_file_url(BRANDS_BUCKET, f"{brand_id}/guidelines.pdf")
    assert BRANDS_BUCKET in accessed_buckets, "Brands bucket should be accessed"
    assert BRANDS_BUCKET in brands_url, "URL should contain brands bucket"

    # Reset tracking
    accessed_buckets.clear()

    # Test assets bucket
    assets_url = await file_storage.get_file_url(ASSETS_BUCKET, f"{brand_id}/image.png")
    assert ASSETS_BUCKET in accessed_buckets, "Assets bucket should be accessed"
    assert ASSETS_BUCKET in assets_url, "URL should contain assets bucket"


def test_bucket_constants_are_different():
    """
    Property: Bucket constants are distinct.

    The BRANDS_BUCKET and ASSETS_BUCKET constants should be different
    to ensure proper separation of file types.

    **Validates: Requirements 10.1, 10.2**
    """
    assert BRANDS_BUCKET != ASSETS_BUCKET, "Bucket constants should be different"
    assert isinstance(BRANDS_BUCKET, str), "BRANDS_BUCKET should be a string"
    assert isinstance(ASSETS_BUCKET, str), "ASSETS_BUCKET should be a string"
    assert len(BRANDS_BUCKET) > 0, "BRANDS_BUCKET should not be empty"
    assert len(ASSETS_BUCKET) > 0, "ASSETS_BUCKET should not be empty"
