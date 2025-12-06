"""
Property-based tests for file cleanup on deletion.

**Feature: mobius-phase-2-refactor, Property (custom): Files removed on deletion**

Tests that files are properly removed from Supabase Storage when entities are deleted.

**Validates: Requirements 10.4**
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from mobius.storage.files import FileStorage
from mobius.storage.brands import BrandStorage
from mobius.storage.assets import AssetStorage
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
def file_path_strategy(draw):
    """Generate a valid file path."""
    id_part = str(uuid.uuid4())
    filename = draw(st.sampled_from(["guidelines.pdf", "image.png", "logo.jpg", "asset.webp"]))
    return f"{id_part}/{filename}"


@given(brand_id=brand_id_strategy(), filename=st.sampled_from(["guidelines.pdf", "brand.pdf", "rules.pdf"]))
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
async def test_delete_file_removes_from_storage(mock_get_client, brand_id, filename):
    """
    Property: delete_file removes files from storage.

    For any file in Supabase Storage, calling delete_file() should
    remove that file from the storage bucket.

    **Validates: Requirements 10.4**
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_storage = Mock()
    mock_bucket = Mock()

    # Track delete calls
    deleted_files = []

    def mock_remove(paths):
        deleted_files.extend(paths)
        return {"data": paths}

    mock_bucket.remove = mock_remove
    mock_storage.from_ = Mock(return_value=mock_bucket)
    mock_client.storage = mock_storage
    mock_get_client.return_value = mock_client

    # Create FileStorage instance
    file_storage = FileStorage()

    # Delete a file
    path = f"{brand_id}/{filename}"
    result = await file_storage.delete_file(BRANDS_BUCKET, path)

    # Verify file was deleted
    assert result is True, "delete_file should return True on success"
    assert path in deleted_files, f"File {path} should be in deleted files list"
    assert len(deleted_files) == 1, "Exactly one file should be deleted"


@given(
    brand_id=brand_id_strategy(),
    asset_id=asset_id_strategy(),
)
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
async def test_multiple_file_deletions_are_independent(mock_get_client, brand_id, asset_id):
    """
    Property: Multiple file deletions are independent.

    For any sequence of file deletions, each deletion should only
    remove the specified file and not affect other files.

    **Validates: Requirements 10.4**
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_storage = Mock()

    # Track deletions per bucket
    deleted_files = {"brands": [], "assets": []}

    def create_mock_bucket(bucket_name):
        mock_bucket = Mock()

        def mock_remove(paths):
            deleted_files[bucket_name].extend(paths)
            return {"data": paths}

        mock_bucket.remove = mock_remove
        return mock_bucket

    def mock_from_(bucket_name):
        return create_mock_bucket(bucket_name)

    mock_storage.from_ = mock_from_
    mock_client.storage = mock_storage
    mock_get_client.return_value = mock_client

    # Create FileStorage instance
    file_storage = FileStorage()

    # Delete multiple files
    brand_path = f"{brand_id}/guidelines.pdf"
    asset_path = f"{asset_id}/image.png"

    result1 = await file_storage.delete_file(BRANDS_BUCKET, brand_path)
    result2 = await file_storage.delete_file(ASSETS_BUCKET, asset_path)

    # Verify both deletions succeeded
    assert result1 is True
    assert result2 is True

    # Verify correct files were deleted from correct buckets
    assert brand_path in deleted_files["brands"], "Brand file should be deleted from brands bucket"
    assert asset_path in deleted_files["assets"], "Asset file should be deleted from assets bucket"

    # Verify no cross-contamination
    assert brand_path not in deleted_files["assets"], "Brand file should NOT be in assets bucket deletions"
    assert asset_path not in deleted_files["brands"], "Asset file should NOT be in brands bucket deletions"


@given(bucket=st.sampled_from([BRANDS_BUCKET, ASSETS_BUCKET]), path=file_path_strategy())
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
async def test_delete_file_is_idempotent(mock_get_client, bucket, path):
    """
    Property: delete_file is idempotent.

    For any file, calling delete_file() multiple times should not cause
    errors. The first call removes the file, subsequent calls should
    handle the "file not found" case gracefully.

    **Validates: Requirements 10.4**
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_storage = Mock()
    mock_bucket = Mock()

    # Track delete calls
    delete_count = [0]

    def mock_remove(paths):
        delete_count[0] += 1
        # First call succeeds, subsequent calls might fail (file not found)
        # but we handle it gracefully
        if delete_count[0] == 1:
            return {"data": paths}
        else:
            # Simulate "file not found" - but we don't raise error
            return {"data": []}

    mock_bucket.remove = mock_remove
    mock_storage.from_ = Mock(return_value=mock_bucket)
    mock_client.storage = mock_storage
    mock_get_client.return_value = mock_client

    # Create FileStorage instance
    file_storage = FileStorage()

    # Delete file twice
    result1 = await file_storage.delete_file(bucket, path)
    result2 = await file_storage.delete_file(bucket, path)

    # Both should succeed (idempotent)
    assert result1 is True
    assert result2 is True
    assert delete_count[0] == 2, "delete_file should be called twice"


@given(brand_id=brand_id_strategy())
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
async def test_brand_file_cleanup_workflow(mock_file_client, brand_id):
    """
    Property: Brand file cleanup workflow.

    For any brand with associated files, the file cleanup workflow should
    properly remove the PDF file from storage when requested.

    This tests the file cleanup mechanism in isolation, which would be
    triggered by brand deletion logic.

    **Validates: Requirements 10.4**
    """
    # Mock Supabase client for file operations
    mock_file_supabase = Mock()
    mock_storage = Mock()
    mock_bucket = Mock()

    deleted_files = []

    def mock_remove(paths):
        deleted_files.extend(paths)
        return {"data": paths}

    mock_bucket.remove = mock_remove
    mock_storage.from_ = Mock(return_value=mock_bucket)
    mock_file_supabase.storage = mock_storage
    mock_file_client.return_value = mock_file_supabase

    # Create file storage instance
    file_storage = FileStorage()

    # Simulate brand deletion file cleanup
    pdf_path = f"{brand_id}/guidelines.pdf"
    result = await file_storage.delete_file(BRANDS_BUCKET, pdf_path)

    # Verify file was deleted
    assert result is True, "File deletion should succeed"
    assert len(deleted_files) > 0, "File should be deleted"
    assert pdf_path in deleted_files, f"PDF path {pdf_path} should be in deleted files"
    assert brand_id in deleted_files[0], "Deleted file path should contain brand_id"


@given(asset_id=asset_id_strategy())
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
async def test_asset_file_cleanup_workflow(mock_file_client, asset_id):
    """
    Property: Asset file cleanup workflow.

    For any asset with associated image files, the file cleanup workflow
    should properly remove the image file from storage when requested.

    This tests the file cleanup mechanism in isolation, which would be
    triggered by asset deletion logic.

    **Validates: Requirements 10.4**
    """
    # Mock Supabase client for file operations
    mock_file_supabase = Mock()
    mock_storage = Mock()
    mock_bucket = Mock()

    deleted_files = []

    def mock_remove(paths):
        deleted_files.extend(paths)
        return {"data": paths}

    mock_bucket.remove = mock_remove
    mock_storage.from_ = Mock(return_value=mock_bucket)
    mock_file_supabase.storage = mock_storage
    mock_file_client.return_value = mock_file_supabase

    # Create file storage instance
    file_storage = FileStorage()

    # Simulate asset deletion file cleanup
    image_path = f"{asset_id}/image.png"
    result = await file_storage.delete_file(ASSETS_BUCKET, image_path)

    # Verify file was deleted
    assert result is True, "File deletion should succeed"
    assert len(deleted_files) > 0, "File should be deleted"
    assert image_path in deleted_files, f"Image path {image_path} should be in deleted files"
    assert asset_id in deleted_files[0], "Deleted file path should contain asset_id"


@given(
    bucket=st.sampled_from([BRANDS_BUCKET, ASSETS_BUCKET]),
    paths=st.lists(file_path_strategy(), min_size=1, max_size=10),
)
@settings(max_examples=100)
@patch("mobius.storage.files.get_supabase_client")
async def test_batch_file_deletion(mock_get_client, bucket, paths):
    """
    Property: Batch file deletion removes all specified files.

    For any list of file paths, calling delete_file() for each path
    should remove all files from storage.

    **Validates: Requirements 10.4**
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_storage = Mock()
    mock_bucket = Mock()

    deleted_files = []

    def mock_remove(file_paths):
        deleted_files.extend(file_paths)
        return {"data": file_paths}

    mock_bucket.remove = mock_remove
    mock_storage.from_ = Mock(return_value=mock_bucket)
    mock_client.storage = mock_storage
    mock_get_client.return_value = mock_client

    # Create FileStorage instance
    file_storage = FileStorage()

    # Delete all files
    for path in paths:
        result = await file_storage.delete_file(bucket, path)
        assert result is True, f"Deletion of {path} should succeed"

    # Verify all files were deleted
    assert len(deleted_files) == len(paths), "All files should be deleted"
    for path in paths:
        assert path in deleted_files, f"File {path} should be in deleted files list"


def test_file_cleanup_requirement_exists():
    """
    Property: File cleanup is a documented requirement.

    The system should have explicit requirements for file cleanup
    when entities are deleted.

    **Validates: Requirements 10.4**
    """
    # Mock Supabase client
    with patch("mobius.storage.files.get_supabase_client") as mock_get_client:
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # This test verifies that the FileStorage class has a delete_file method
        file_storage = FileStorage()
        assert hasattr(file_storage, "delete_file"), "FileStorage should have delete_file method"

        # Verify the method signature
        import inspect

        sig = inspect.signature(file_storage.delete_file)
        params = list(sig.parameters.keys())

        assert "bucket" in params, "delete_file should accept bucket parameter"
        assert "path" in params, "delete_file should accept path parameter"
