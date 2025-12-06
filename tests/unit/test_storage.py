"""
Unit tests for storage operations.

Tests CRUD operations for all storage classes with mocked Supabase client.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone
import uuid

from mobius.storage.brands import BrandStorage
from mobius.storage.assets import AssetStorage
from mobius.storage.templates import TemplateStorage
from mobius.storage.jobs import JobStorage
from mobius.storage.feedback import FeedbackStorage
from mobius.storage.files import FileStorage
from mobius.models.brand import Brand, BrandGuidelines, Color, Typography
from mobius.models.asset import Asset
from mobius.models.template import Template
from mobius.models.job import Job


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    client = Mock()
    client.table = Mock(return_value=Mock())
    client.storage = Mock()
    return client


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
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


@pytest.fixture
def sample_asset():
    """Sample asset entity for testing."""
    return Asset(
        asset_id=str(uuid.uuid4()),
        brand_id=str(uuid.uuid4()),
        job_id=str(uuid.uuid4()),
        prompt="Test prompt",
        image_url="https://example.com/test.png",
        compliance_score=85.0,
        status="completed",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_template():
    """Sample template entity for testing."""
    return Template(
        template_id=str(uuid.uuid4()),
        brand_id=str(uuid.uuid4()),
        name="Test Template",
        description="Test description",
        generation_params={"prompt": "test", "model": "flux"},
        thumbnail_url="https://example.com/thumb.png",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_job():
    """Sample job entity for testing."""
    return Job(
        job_id=str(uuid.uuid4()),
        brand_id=str(uuid.uuid4()),
        status="pending",
        progress=0.0,
        state={"prompt": "test"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
    )


# BrandStorage Tests


@patch("mobius.storage.brands.get_supabase_client")
async def test_brand_storage_create(mock_get_client, mock_supabase_client, sample_brand):
    """Test creating a brand."""
    mock_get_client.return_value = mock_supabase_client

    # Mock the insert response
    mock_execute = Mock()
    mock_execute.data = [sample_brand.model_dump()]
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = (
        mock_execute
    )

    storage = BrandStorage()
    result = await storage.create_brand(sample_brand)

    assert result.brand_id == sample_brand.brand_id
    assert result.name == sample_brand.name
    mock_supabase_client.table.assert_called_with("brands")


@patch("mobius.storage.brands.get_supabase_client")
async def test_brand_storage_get(mock_get_client, mock_supabase_client, sample_brand):
    """Test retrieving a brand by ID."""
    mock_get_client.return_value = mock_supabase_client

    # Mock the select response
    mock_execute = Mock()
    mock_execute.data = [sample_brand.model_dump()]
    (
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.is_.return_value.execute.return_value
    ) = mock_execute

    storage = BrandStorage()
    result = await storage.get_brand(sample_brand.brand_id)

    assert result is not None
    assert result.brand_id == sample_brand.brand_id


@patch("mobius.storage.brands.get_supabase_client")
async def test_brand_storage_soft_delete(
    mock_get_client, mock_supabase_client, sample_brand
):
    """Test soft deleting a brand."""
    mock_get_client.return_value = mock_supabase_client

    # Mock the update response
    mock_execute = Mock()
    mock_execute.data = [sample_brand.model_dump()]
    (
        mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value
    ) = mock_execute

    storage = BrandStorage()
    result = await storage.delete_brand(sample_brand.brand_id)

    assert result is True
    mock_supabase_client.table.return_value.update.assert_called_once()


# AssetStorage Tests


@patch("mobius.storage.assets.get_supabase_client")
async def test_asset_storage_create(mock_get_client, mock_supabase_client, sample_asset):
    """Test creating an asset."""
    mock_get_client.return_value = mock_supabase_client

    # Mock the insert response
    mock_execute = Mock()
    mock_execute.data = [sample_asset.model_dump()]
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = (
        mock_execute
    )

    storage = AssetStorage()
    result = await storage.create_asset(sample_asset)

    assert result.asset_id == sample_asset.asset_id
    assert result.brand_id == sample_asset.brand_id


@patch("mobius.storage.assets.get_supabase_client")
async def test_asset_storage_list_by_brand(
    mock_get_client, mock_supabase_client, sample_asset
):
    """Test listing assets by brand."""
    mock_get_client.return_value = mock_supabase_client

    # Mock the select response
    mock_execute = Mock()
    mock_execute.data = [sample_asset.model_dump()]
    (
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value
    ) = mock_execute

    storage = AssetStorage()
    results = await storage.list_assets(sample_asset.brand_id)

    assert len(results) == 1
    assert results[0].asset_id == sample_asset.asset_id


# TemplateStorage Tests


@patch("mobius.storage.templates.get_supabase_client")
async def test_template_storage_create(
    mock_get_client, mock_supabase_client, sample_template
):
    """Test creating a template."""
    mock_get_client.return_value = mock_supabase_client

    # Mock the insert response
    mock_execute = Mock()
    mock_execute.data = [sample_template.model_dump()]
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = (
        mock_execute
    )

    storage = TemplateStorage()
    result = await storage.create_template(sample_template)

    assert result.template_id == sample_template.template_id
    assert result.name == sample_template.name


@patch("mobius.storage.templates.get_supabase_client")
async def test_template_storage_soft_delete(
    mock_get_client, mock_supabase_client, sample_template
):
    """Test soft deleting a template."""
    mock_get_client.return_value = mock_supabase_client

    # Mock the update response
    mock_execute = Mock()
    mock_execute.data = [sample_template.model_dump()]
    (
        mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value
    ) = mock_execute

    storage = TemplateStorage()
    result = await storage.delete_template(sample_template.template_id)

    assert result is True


# JobStorage Tests


@patch("mobius.storage.jobs.get_supabase_client")
async def test_job_storage_create(mock_get_client, mock_supabase_client, sample_job):
    """Test creating a job."""
    mock_get_client.return_value = mock_supabase_client

    # Mock the insert response
    mock_execute = Mock()
    mock_execute.data = [sample_job.model_dump()]
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = (
        mock_execute
    )

    storage = JobStorage()
    result = await storage.create_job(sample_job)

    assert result.job_id == sample_job.job_id
    assert result.status == sample_job.status


@patch("mobius.storage.jobs.get_supabase_client")
async def test_job_storage_get_by_idempotency_key(
    mock_get_client, mock_supabase_client, sample_job
):
    """Test retrieving a job by idempotency key."""
    mock_get_client.return_value = mock_supabase_client

    # Add idempotency key to sample job
    sample_job.idempotency_key = "test-key-123"

    # Mock the select response
    mock_execute = Mock()
    mock_execute.data = [sample_job.model_dump()]
    (
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.gt.return_value.execute.return_value
    ) = mock_execute

    storage = JobStorage()
    result = await storage.get_by_idempotency_key("test-key-123")

    assert result is not None
    assert result.idempotency_key == "test-key-123"


@patch("mobius.storage.jobs.get_supabase_client")
async def test_job_storage_get_by_idempotency_key_not_found(
    mock_get_client, mock_supabase_client
):
    """Test retrieving a job by idempotency key when not found."""
    mock_get_client.return_value = mock_supabase_client

    # Mock empty response
    mock_execute = Mock()
    mock_execute.data = []
    (
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.gt.return_value.execute.return_value
    ) = mock_execute

    storage = JobStorage()
    result = await storage.get_by_idempotency_key("nonexistent-key")

    assert result is None


# FeedbackStorage Tests


@patch("mobius.storage.feedback.get_supabase_client")
async def test_feedback_storage_create(mock_get_client, mock_supabase_client):
    """Test creating feedback."""
    mock_get_client.return_value = mock_supabase_client

    asset_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())

    # Mock the insert response
    mock_execute = Mock()
    mock_execute.data = [
        {
            "feedback_id": str(uuid.uuid4()),
            "asset_id": asset_id,
            "brand_id": brand_id,
            "action": "approve",
            "reason": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    ]
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = (
        mock_execute
    )

    storage = FeedbackStorage()
    result = await storage.create_feedback(asset_id, brand_id, "approve")

    assert result.asset_id == asset_id
    assert result.brand_id == brand_id
    assert result.action == "approve"


@patch("mobius.storage.feedback.get_supabase_client")
async def test_feedback_storage_get_stats(mock_get_client, mock_supabase_client):
    """Test getting feedback statistics."""
    mock_get_client.return_value = mock_supabase_client

    brand_id = str(uuid.uuid4())

    # Mock feedback query response
    mock_feedback_execute = Mock()
    mock_feedback_execute.data = [
        {"action": "approve"},
        {"action": "approve"},
        {"action": "reject"},
    ]

    # Mock brand query response
    mock_brand_execute = Mock()
    mock_brand_execute.data = [{"learning_active": False}]

    # Create a mock table that returns different results for different queries
    def table_side_effect(table_name):
        mock_table = Mock()
        if table_name == "feedback":
            mock_table.select.return_value.eq.return_value.execute.return_value = (
                mock_feedback_execute
            )
        elif table_name == "brands":
            mock_table.select.return_value.eq.return_value.execute.return_value = (
                mock_brand_execute
            )
        return mock_table

    mock_supabase_client.table.side_effect = table_side_effect

    storage = FeedbackStorage()
    result = await storage.get_feedback_stats(brand_id)

    assert result["total_feedback"] == 3
    assert result["approvals"] == 2
    assert result["rejections"] == 1
    assert result["learning_active"] == False


# FileStorage Tests


@patch("mobius.storage.files.get_supabase_client")
async def test_file_storage_get_file_url(mock_get_client, mock_supabase_client):
    """Test getting a file URL."""
    mock_get_client.return_value = mock_supabase_client

    # Mock storage response
    mock_supabase_client.storage.from_.return_value.get_public_url.return_value = (
        "https://example.com/file.pdf"
    )

    storage = FileStorage()
    url = await storage.get_file_url("brands", "test-brand/guidelines.pdf")

    assert url == "https://example.com/file.pdf"
    mock_supabase_client.storage.from_.assert_called_with("brands")



@patch("mobius.storage.files.get_supabase_client")
async def test_file_storage_list_files(mock_get_client, mock_supabase_client):
    """Test listing files in a bucket."""
    mock_get_client.return_value = mock_supabase_client

    # Mock storage response
    mock_files = [
        {"name": "file1.pdf", "id": "123"},
        {"name": "file2.pdf", "id": "456"}
    ]
    mock_supabase_client.storage.from_.return_value.list.return_value = mock_files

    storage = FileStorage()
    files = await storage.list_files("brands", "test-brand/")

    assert len(files) == 2
    assert files[0]["name"] == "file1.pdf"
    mock_supabase_client.storage.from_.assert_called_with("brands")
    mock_supabase_client.storage.from_.return_value.list.assert_called_with("test-brand/")


@patch("mobius.storage.files.get_supabase_client")
async def test_file_storage_list_files_error(mock_get_client, mock_supabase_client):
    """Test list files error handling."""
    mock_get_client.return_value = mock_supabase_client

    # Mock storage error
    mock_supabase_client.storage.from_.return_value.list.side_effect = Exception("Storage error")

    storage = FileStorage()
    
    with pytest.raises(Exception) as exc_info:
        await storage.list_files("brands", "test-brand/")
    
    assert "Storage error" in str(exc_info.value)
