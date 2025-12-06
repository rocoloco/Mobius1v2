"""
Comprehensive tests for storage modules.

Tests CRUD operations for brands, jobs, assets, and templates storage.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, MagicMock, patch
from mobius.storage.brands import BrandStorage
from mobius.storage.jobs import JobStorage
from mobius.storage.assets import AssetStorage
from mobius.storage.templates import TemplateStorage
from mobius.models.brand import Brand, BrandGuidelines, Color, Typography, LogoRule
from mobius.models.job import Job
from mobius.models.asset import Asset
from mobius.models.template import Template


# Fixtures

@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client."""
    client = Mock()
    client.table = Mock(return_value=client)
    client.select = Mock(return_value=client)
    client.insert = Mock(return_value=client)
    client.update = Mock(return_value=client)
    client.delete = Mock(return_value=client)
    client.eq = Mock(return_value=client)
    client.is_ = Mock(return_value=client)
    client.ilike = Mock(return_value=client)
    client.gt = Mock(return_value=client)
    client.lt = Mock(return_value=client)
    client.limit = Mock(return_value=client)
    client.order = Mock(return_value=client)
    client.range = Mock(return_value=client)
    client.execute = Mock()
    return client


@pytest.fixture
def sample_brand():
    """Sample brand for testing."""
    return Brand(
        brand_id="brand-123",
        organization_id="org-456",
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=[Color(name="Red", hex="#FF0000", usage="primary")],
            typography=[Typography(family="Arial", weights=["400", "700"], usage="body")],
            logos=[],
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


@pytest.fixture
def sample_job():
    """Sample job for testing."""
    return Job(
        job_id="job-123",
        brand_id="brand-123",
        status="pending",
        state={"attempt_count": 0},
        idempotency_key="idem-123",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )


@pytest.fixture
def sample_asset():
    """Sample asset for testing."""
    return Asset(
        asset_id="asset-123",
        brand_id="brand-123",
        job_id="job-123",
        prompt="Test prompt",
        image_url="https://example.com/image.png",
        compliance_score=85.5,
        status="approved",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_template():
    """Sample template for testing."""
    return Template(
        template_id="template-123",
        brand_id="brand-123",
        name="Test Template",
        description="A test template",
        generation_params={"prompt": "test"},
        thumbnail_url="https://example.com/thumb.png",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


# BrandStorage Tests

@pytest.mark.asyncio
@patch("mobius.storage.brands.get_supabase_client")
async def test_brand_storage_create(mock_get_client, mock_supabase_client, sample_brand):
    """Test creating a brand."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_brand.model_dump()])
    
    storage = BrandStorage()
    result = await storage.create_brand(sample_brand)
    
    assert result.brand_id == sample_brand.brand_id
    mock_supabase_client.table.assert_called_with("brands")
    mock_supabase_client.insert.assert_called_once()


@pytest.mark.asyncio
@patch("mobius.storage.brands.get_supabase_client")
async def test_brand_storage_get(mock_get_client, mock_supabase_client, sample_brand):
    """Test retrieving a brand."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_brand.model_dump()])
    
    storage = BrandStorage()
    result = await storage.get_brand("brand-123")
    
    assert result is not None
    assert result.brand_id == "brand-123"
    mock_supabase_client.eq.assert_called_with("brand_id", "brand-123")


@pytest.mark.asyncio
@patch("mobius.storage.brands.get_supabase_client")
async def test_brand_storage_get_not_found(mock_get_client, mock_supabase_client):
    """Test retrieving a non-existent brand."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[])
    
    storage = BrandStorage()
    result = await storage.get_brand("nonexistent")
    
    assert result is None


@pytest.mark.asyncio
@patch("mobius.storage.brands.get_supabase_client")
async def test_brand_storage_list(mock_get_client, mock_supabase_client, sample_brand):
    """Test listing brands."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_brand.model_dump()])
    
    storage = BrandStorage()
    result = await storage.list_brands("org-456")
    
    assert len(result) == 1
    assert result[0].brand_id == "brand-123"
    mock_supabase_client.eq.assert_called_with("organization_id", "org-456")


@pytest.mark.asyncio
@patch("mobius.storage.brands.get_supabase_client")
async def test_brand_storage_list_with_search(mock_get_client, mock_supabase_client, sample_brand):
    """Test listing brands with search."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_brand.model_dump()])
    
    storage = BrandStorage()
    result = await storage.list_brands("org-456", search="Test")
    
    assert len(result) == 1
    mock_supabase_client.ilike.assert_called_with("name", "%Test%")


@pytest.mark.asyncio
@patch("mobius.storage.brands.get_supabase_client")
async def test_brand_storage_update(mock_get_client, mock_supabase_client, sample_brand):
    """Test updating a brand."""
    mock_get_client.return_value = mock_supabase_client
    updated_brand = sample_brand.model_copy()
    updated_brand.name = "Updated Brand"
    mock_supabase_client.execute.return_value = Mock(data=[updated_brand.model_dump()])
    
    storage = BrandStorage()
    result = await storage.update_brand("brand-123", {"name": "Updated Brand"})
    
    assert result.name == "Updated Brand"
    mock_supabase_client.update.assert_called_once()


@pytest.mark.asyncio
@patch("mobius.storage.brands.get_supabase_client")
async def test_brand_storage_update_not_found(mock_get_client, mock_supabase_client):
    """Test updating a non-existent brand."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[])
    
    storage = BrandStorage()
    
    with pytest.raises(ValueError, match="Brand .* not found"):
        await storage.update_brand("nonexistent", {"name": "Updated"})


@pytest.mark.asyncio
@patch("mobius.storage.brands.get_supabase_client")
async def test_brand_storage_delete(mock_get_client, mock_supabase_client, sample_brand):
    """Test soft deleting a brand."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_brand.model_dump()])
    
    storage = BrandStorage()
    result = await storage.delete_brand("brand-123")
    
    assert result is True
    mock_supabase_client.update.assert_called_once()


@pytest.mark.asyncio
@patch("mobius.storage.brands.get_supabase_client")
async def test_brand_storage_delete_not_found(mock_get_client, mock_supabase_client):
    """Test deleting a non-existent brand."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[])
    
    storage = BrandStorage()
    
    with pytest.raises(ValueError, match="Brand .* not found"):
        await storage.delete_brand("nonexistent")


@pytest.mark.asyncio
@patch("mobius.storage.brands.get_supabase_client")
async def test_brand_storage_get_with_stats(mock_get_client, mock_supabase_client, sample_brand):
    """Test getting brand with statistics."""
    mock_get_client.return_value = mock_supabase_client
    
    # Mock brand fetch
    brand_response = Mock(data=[sample_brand.model_dump()])
    
    # Mock assets fetch
    assets_response = Mock(data=[
        {"compliance_score": 85.0},
        {"compliance_score": 90.0},
    ])
    
    mock_supabase_client.execute.side_effect = [brand_response, assets_response]
    
    storage = BrandStorage()
    result = await storage.get_brand_with_stats("brand-123")
    
    assert result is not None
    assert result["brand_id"] == "brand-123"
    assert result["asset_count"] == 2
    assert result["avg_compliance_score"] == 87.5


# JobStorage Tests

@pytest.mark.asyncio
@patch("mobius.storage.jobs.get_supabase_client")
async def test_job_storage_create(mock_get_client, mock_supabase_client, sample_job):
    """Test creating a job."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_job.model_dump()])
    
    storage = JobStorage()
    result = await storage.create_job(sample_job)
    
    assert result.job_id == sample_job.job_id
    mock_supabase_client.table.assert_called_with("jobs")


@pytest.mark.asyncio
@patch("mobius.storage.jobs.get_supabase_client")
async def test_job_storage_get(mock_get_client, mock_supabase_client, sample_job):
    """Test retrieving a job."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_job.model_dump()])
    
    storage = JobStorage()
    result = await storage.get_job("job-123")
    
    assert result is not None
    assert result.job_id == "job-123"


@pytest.mark.asyncio
@patch("mobius.storage.jobs.get_supabase_client")
async def test_job_storage_get_by_idempotency_key(mock_get_client, mock_supabase_client, sample_job):
    """Test retrieving a job by idempotency key."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_job.model_dump()])
    
    storage = JobStorage()
    result = await storage.get_by_idempotency_key("idem-123")
    
    assert result is not None
    assert result.idempotency_key == "idem-123"
    mock_supabase_client.eq.assert_called_with("idempotency_key", "idem-123")


@pytest.mark.asyncio
@patch("mobius.storage.jobs.get_supabase_client")
async def test_job_storage_get_by_idempotency_key_not_found(mock_get_client, mock_supabase_client):
    """Test retrieving a non-existent job by idempotency key."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[])
    
    storage = JobStorage()
    result = await storage.get_by_idempotency_key("nonexistent")
    
    assert result is None


@pytest.mark.asyncio
@patch("mobius.storage.jobs.get_supabase_client")
async def test_job_storage_list(mock_get_client, mock_supabase_client, sample_job):
    """Test listing jobs."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_job.model_dump()])
    
    storage = JobStorage()
    result = await storage.list_jobs(brand_id="brand-123")
    
    assert len(result) == 1
    assert result[0].job_id == "job-123"


@pytest.mark.asyncio
@patch("mobius.storage.jobs.get_supabase_client")
async def test_job_storage_list_with_status(mock_get_client, mock_supabase_client, sample_job):
    """Test listing jobs with status filter."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_job.model_dump()])
    
    storage = JobStorage()
    result = await storage.list_jobs(status="pending")
    
    assert len(result) == 1
    mock_supabase_client.eq.assert_any_call("status", "pending")


@pytest.mark.asyncio
@patch("mobius.storage.jobs.get_supabase_client")
async def test_job_storage_update(mock_get_client, mock_supabase_client, sample_job):
    """Test updating a job."""
    mock_get_client.return_value = mock_supabase_client
    updated_job = sample_job.model_copy()
    updated_job.status = "completed"
    mock_supabase_client.execute.return_value = Mock(data=[updated_job.model_dump()])
    
    storage = JobStorage()
    result = await storage.update_job("job-123", {"status": "completed"})
    
    assert result.status == "completed"


@pytest.mark.asyncio
@patch("mobius.storage.jobs.get_supabase_client")
async def test_job_storage_delete(mock_get_client, mock_supabase_client, sample_job):
    """Test deleting a job."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_job.model_dump()])
    
    storage = JobStorage()
    result = await storage.delete_job("job-123")
    
    assert result is True


@pytest.mark.asyncio
@patch("mobius.storage.jobs.get_supabase_client")
async def test_job_storage_list_expired(mock_get_client, mock_supabase_client, sample_job):
    """Test listing expired jobs."""
    mock_get_client.return_value = mock_supabase_client
    expired_job = sample_job.model_copy()
    expired_job.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    mock_supabase_client.execute.return_value = Mock(data=[expired_job.model_dump()])
    
    storage = JobStorage()
    result = await storage.list_expired_jobs()
    
    assert len(result) == 1
    mock_supabase_client.lt.assert_called_once()


# AssetStorage Tests

@pytest.mark.asyncio
@patch("mobius.storage.assets.get_supabase_client")
async def test_asset_storage_create(mock_get_client, mock_supabase_client, sample_asset):
    """Test creating an asset."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_asset.model_dump()])
    
    storage = AssetStorage()
    result = await storage.create_asset(sample_asset)
    
    assert result.asset_id == sample_asset.asset_id
    mock_supabase_client.table.assert_called_with("assets")


@pytest.mark.asyncio
@patch("mobius.storage.assets.get_supabase_client")
async def test_asset_storage_get(mock_get_client, mock_supabase_client, sample_asset):
    """Test retrieving an asset."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_asset.model_dump()])
    
    storage = AssetStorage()
    result = await storage.get_asset("asset-123")
    
    assert result is not None
    assert result.asset_id == "asset-123"


@pytest.mark.asyncio
@patch("mobius.storage.assets.get_supabase_client")
async def test_asset_storage_list(mock_get_client, mock_supabase_client, sample_asset):
    """Test listing assets."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_asset.model_dump()])
    
    storage = AssetStorage()
    result = await storage.list_assets("brand-123")
    
    assert len(result) == 1
    assert result[0].asset_id == "asset-123"


@pytest.mark.asyncio
@patch("mobius.storage.assets.get_supabase_client")
async def test_asset_storage_list_by_job(mock_get_client, mock_supabase_client, sample_asset):
    """Test listing assets by job."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_asset.model_dump()])
    
    storage = AssetStorage()
    result = await storage.list_assets_by_job("job-123")
    
    assert len(result) == 1
    mock_supabase_client.eq.assert_called_with("job_id", "job-123")


@pytest.mark.asyncio
@patch("mobius.storage.assets.get_supabase_client")
async def test_asset_storage_update(mock_get_client, mock_supabase_client, sample_asset):
    """Test updating an asset."""
    mock_get_client.return_value = mock_supabase_client
    updated_asset = sample_asset.model_copy()
    updated_asset.compliance_score = 95.0
    mock_supabase_client.execute.return_value = Mock(data=[updated_asset.model_dump()])
    
    storage = AssetStorage()
    result = await storage.update_asset("asset-123", {"compliance_score": 95.0})
    
    assert result.compliance_score == 95.0


@pytest.mark.asyncio
@patch("mobius.storage.assets.get_supabase_client")
async def test_asset_storage_delete(mock_get_client, mock_supabase_client, sample_asset):
    """Test deleting an asset."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_asset.model_dump()])
    
    storage = AssetStorage()
    result = await storage.delete_asset("asset-123")
    
    assert result is True


# TemplateStorage Tests

@pytest.mark.asyncio
@patch("mobius.storage.templates.get_supabase_client")
async def test_template_storage_create(mock_get_client, mock_supabase_client, sample_template):
    """Test creating a template."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_template.model_dump()])
    
    storage = TemplateStorage()
    result = await storage.create_template(sample_template)
    
    assert result.template_id == sample_template.template_id
    mock_supabase_client.table.assert_called_with("templates")


@pytest.mark.asyncio
@patch("mobius.storage.templates.get_supabase_client")
async def test_template_storage_get(mock_get_client, mock_supabase_client, sample_template):
    """Test retrieving a template."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_template.model_dump()])
    
    storage = TemplateStorage()
    result = await storage.get_template("template-123")
    
    assert result is not None
    assert result.template_id == "template-123"


@pytest.mark.asyncio
@patch("mobius.storage.templates.get_supabase_client")
async def test_template_storage_list(mock_get_client, mock_supabase_client, sample_template):
    """Test listing templates."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_template.model_dump()])
    
    storage = TemplateStorage()
    result = await storage.list_templates("brand-123")
    
    assert len(result) == 1
    assert result[0].template_id == "template-123"


@pytest.mark.asyncio
@patch("mobius.storage.templates.get_supabase_client")
async def test_template_storage_update(mock_get_client, mock_supabase_client, sample_template):
    """Test updating a template."""
    mock_get_client.return_value = mock_supabase_client
    updated_template = sample_template.model_copy()
    updated_template.name = "Updated Template"
    mock_supabase_client.execute.return_value = Mock(data=[updated_template.model_dump()])
    
    storage = TemplateStorage()
    result = await storage.update_template("template-123", {"name": "Updated Template"})
    
    assert result.name == "Updated Template"


@pytest.mark.asyncio
@patch("mobius.storage.templates.get_supabase_client")
async def test_template_storage_delete(mock_get_client, mock_supabase_client, sample_template):
    """Test soft deleting a template."""
    mock_get_client.return_value = mock_supabase_client
    mock_supabase_client.execute.return_value = Mock(data=[sample_template.model_dump()])
    
    storage = TemplateStorage()
    result = await storage.delete_template("template-123")
    
    assert result is True
    mock_supabase_client.update.assert_called_once()
