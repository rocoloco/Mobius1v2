"""
Property-based tests for file storage CDN URL format.

**Feature: mobius-phase-2-refactor, Property 13: File storage returns CDN URL**

Tests that file storage operations return valid HTTPS CDN URLs.

**Validates: Requirements 10.3**
"""

import pytest
from hypothesis import given, strategies as st, settings
from mobius.storage.files import FileStorage
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
def filename_strategy(draw):
    """Generate a valid filename."""
    name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L", "N"))))
    extension = draw(st.sampled_from([".pdf", ".png", ".jpg", ".jpeg", ".webp"]))
    return f"{name}{extension}"


@given(brand_id=brand_id_strategy(), filename=filename_strategy())
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
async def test_upload_pdf_returns_cdn_url(mock_get_client, brand_id, filename):
    """
    Property 13: File storage returns CDN URL.

    For any PDF uploaded to Supabase Storage, the returned URL should be
    a valid HTTPS URL pointing to the Supabase CDN.

    **Validates: Requirements 10.3**
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_storage = Mock()
    mock_bucket = Mock()

    # Mock the upload and get_public_url methods
    mock_bucket.upload = Mock(return_value={"path": f"{brand_id}/{filename}"})
    mock_bucket.get_public_url = Mock(
        return_value=f"https://example.supabase.co/storage/v1/object/public/brands/{brand_id}/{filename}"
    )

    mock_storage.from_ = Mock(return_value=mock_bucket)
    mock_client.storage = mock_storage
    mock_get_client.return_value = mock_client

    # Create FileStorage instance
    file_storage = FileStorage()

    # Upload a PDF
    pdf_bytes = b"%PDF-1.4 test content"
    url = await file_storage.upload_pdf(pdf_bytes, brand_id, filename)

    # Verify URL format
    assert isinstance(url, str)
    assert url.startswith("https://"), f"URL should start with https://, got: {url}"
    assert "supabase" in url.lower(), f"URL should contain 'supabase', got: {url}"
    assert brand_id in url, f"URL should contain brand_id, got: {url}"
    assert filename in url, f"URL should contain filename, got: {url}"


@given(asset_id=asset_id_strategy())
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
@patch("httpx.AsyncClient")
async def test_upload_image_returns_cdn_url(mock_httpx_client, mock_get_client, asset_id):
    """
    Property 13: File storage returns CDN URL for images.

    For any image uploaded to Supabase Storage, the returned URL should be
    a valid HTTPS URL pointing to the Supabase CDN.

    **Validates: Requirements 10.3**
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_storage = Mock()
    mock_bucket = Mock()

    filename = "image.png"
    mock_bucket.upload = Mock(return_value={"path": f"{asset_id}/{filename}"})
    mock_bucket.get_public_url = Mock(
        return_value=f"https://example.supabase.co/storage/v1/object/public/assets/{asset_id}/{filename}"
    )

    mock_storage.from_ = Mock(return_value=mock_bucket)
    mock_client.storage = mock_storage
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

    # Verify URL format
    assert isinstance(url, str)
    assert url.startswith("https://"), f"URL should start with https://, got: {url}"
    assert "supabase" in url.lower(), f"URL should contain 'supabase', got: {url}"
    assert asset_id in url, f"URL should contain asset_id, got: {url}"


@given(brand_id=brand_id_strategy())
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
async def test_get_file_url_returns_cdn_url(mock_get_client, brand_id):
    """
    Property 13: get_file_url returns CDN URL.

    For any file path in Supabase Storage, get_file_url should return
    a valid HTTPS CDN URL.

    **Validates: Requirements 10.3**
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_storage = Mock()
    mock_bucket = Mock()

    path = f"{brand_id}/guidelines.pdf"
    mock_bucket.get_public_url = Mock(
        return_value=f"https://example.supabase.co/storage/v1/object/public/brands/{path}"
    )

    mock_storage.from_ = Mock(return_value=mock_bucket)
    mock_client.storage = mock_storage
    mock_get_client.return_value = mock_client

    # Create FileStorage instance
    file_storage = FileStorage()

    # Get file URL
    url = await file_storage.get_file_url("brands", path)

    # Verify URL format
    assert isinstance(url, str)
    assert url.startswith("https://"), f"URL should start with https://, got: {url}"
    assert "supabase" in url.lower(), f"URL should contain 'supabase', got: {url}"
    assert path in url, f"URL should contain file path, got: {url}"


def test_cdn_url_format_validation():
    """
    Property 13: CDN URLs must follow specific format.

    All CDN URLs returned by file storage should:
    - Start with https://
    - Contain the Supabase domain
    - Include the storage path
    - Be publicly accessible

    **Validates: Requirements 10.3**
    """
    # Test valid CDN URL formats
    valid_urls = [
        "https://example.supabase.co/storage/v1/object/public/brands/123/guidelines.pdf",
        "https://project.supabase.co/storage/v1/object/public/assets/456/image.png",
        "https://abc123.supabase.co/storage/v1/object/public/brands/test/file.pdf",
    ]

    for url in valid_urls:
        assert url.startswith("https://")
        assert "supabase" in url.lower()
        assert "/storage/" in url
        assert "/public/" in url

    # Test invalid URL formats (should not be returned)
    invalid_urls = [
        "http://example.com/file.pdf",  # Not HTTPS
        "https://example.com/file.pdf",  # Not Supabase
        "ftp://example.supabase.co/file.pdf",  # Wrong protocol
        "/local/path/file.pdf",  # Local path
    ]

    for url in invalid_urls:
        # These should fail at least one validation
        is_valid = (
            url.startswith("https://")
            and "supabase" in url.lower()
            and "/storage/" in url
            and "/public/" in url
        )
        assert not is_valid, f"Invalid URL passed validation: {url}"


@given(
    bucket=st.sampled_from(["brands", "assets"]),
    path=st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=("L", "N", "P"))),
)
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
async def test_cdn_url_contains_bucket_and_path(mock_get_client, bucket, path):
    """
    Property 13: CDN URLs contain bucket and path information.

    For any bucket and path combination, the returned CDN URL should
    include both the bucket name and the file path.

    **Validates: Requirements 10.3**
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_storage = Mock()
    mock_bucket_obj = Mock()

    expected_url = f"https://example.supabase.co/storage/v1/object/public/{bucket}/{path}"
    mock_bucket_obj.get_public_url = Mock(return_value=expected_url)

    mock_storage.from_ = Mock(return_value=mock_bucket_obj)
    mock_client.storage = mock_storage
    mock_get_client.return_value = mock_client

    # Create FileStorage instance
    file_storage = FileStorage()

    # Get file URL
    url = await file_storage.get_file_url(bucket, path)

    # Verify URL contains bucket and path
    assert bucket in url, f"URL should contain bucket '{bucket}', got: {url}"
    assert path in url, f"URL should contain path '{path}', got: {url}"
    assert url.startswith("https://")
