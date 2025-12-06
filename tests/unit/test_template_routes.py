"""
Unit tests for template management route handlers.

Tests template creation, retrieval, listing, deletion, and application.
"""

import pytest
from unittest.mock import AsyncMock, patch
from mobius.api.routes import (
    save_template_handler,
    list_templates_handler,
    get_template_handler,
    delete_template_handler,
    apply_template_to_request,
    generate_handler,
)
from mobius.api.errors import ValidationError, NotFoundError
from mobius.models.asset import Asset
from mobius.models.template import Template
from mobius.models.brand import Brand, BrandGuidelines, Color
import uuid


@pytest.mark.asyncio
async def test_save_template_with_threshold_check():
    """Test template creation with compliance score threshold check."""
    asset_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())
    template_id = str(uuid.uuid4())
    
    # Asset with score above threshold (95%)
    mock_asset = Asset(
        asset_id=asset_id,
        brand_id=brand_id,
        job_id=str(uuid.uuid4()),
        prompt="Test prompt",
        image_url="https://example.com/image.png",
        compliance_score=96.0,
        compliance_details={},
        generation_params={"prompt": "Test", "style": "modern"},
        status="completed",
    )
    
    with patch("mobius.storage.assets.AssetStorage") as MockAssetStorage:
        mock_asset_storage = AsyncMock()
        mock_asset_storage.get_asset.return_value = mock_asset
        MockAssetStorage.return_value = mock_asset_storage
        
        with patch("mobius.storage.templates.TemplateStorage") as MockTemplateStorage:
            mock_template_storage = AsyncMock()
            
            created_template = Template(
                template_id=template_id,
                brand_id=brand_id,
                name="Test Template",
                description="Test Description",
                generation_params=mock_asset.generation_params,
                thumbnail_url=mock_asset.image_url,
                source_asset_id=asset_id,
            )
            
            mock_template_storage.create_template.return_value = created_template
            MockTemplateStorage.return_value = mock_template_storage
            
            # Should succeed
            result = await save_template_handler(
                asset_id=asset_id,
                template_name="Test Template",
                description="Test Description",
            )
            
            assert result["template_id"] == template_id
            assert result["brand_id"] == brand_id
            assert result["name"] == "Test Template"
            mock_template_storage.create_template.assert_called_once()


@pytest.mark.asyncio
async def test_save_template_below_threshold():
    """Test template creation fails when compliance score is below threshold."""
    asset_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())
    
    # Asset with score below threshold (< 95%)
    mock_asset = Asset(
        asset_id=asset_id,
        brand_id=brand_id,
        job_id=str(uuid.uuid4()),
        prompt="Test prompt",
        image_url="https://example.com/image.png",
        compliance_score=90.0,  # Below 95%
        compliance_details={},
        generation_params={"prompt": "Test"},
        status="completed",
    )
    
    with patch("mobius.storage.assets.AssetStorage") as MockAssetStorage:
        mock_asset_storage = AsyncMock()
        mock_asset_storage.get_asset.return_value = mock_asset
        MockAssetStorage.return_value = mock_asset_storage
        
        with patch("mobius.storage.templates.TemplateStorage") as MockTemplateStorage:
            mock_template_storage = AsyncMock()
            MockTemplateStorage.return_value = mock_template_storage
            
            # Should raise ValidationError
            with pytest.raises(ValidationError) as exc_info:
                await save_template_handler(
                    asset_id=asset_id,
                    template_name="Test Template",
                    description="Test Description",
                )
            
            assert exc_info.value.error_response.error.code == "COMPLIANCE_SCORE_TOO_LOW"
            mock_template_storage.create_template.assert_not_called()


@pytest.mark.asyncio
async def test_list_templates_by_brand():
    """Test retrieving templates filtered by brand."""
    brand_id = str(uuid.uuid4())
    
    templates = [
        Template(
            template_id=str(uuid.uuid4()),
            brand_id=brand_id,
            name=f"Template {i}",
            description=f"Description {i}",
            generation_params={"prompt": f"Test {i}"},
            thumbnail_url=f"https://example.com/thumb{i}.png",
        )
        for i in range(3)
    ]
    
    with patch("mobius.storage.templates.TemplateStorage") as MockTemplateStorage:
        mock_template_storage = AsyncMock()
        mock_template_storage.list_templates.return_value = templates
        MockTemplateStorage.return_value = mock_template_storage
        
        result = await list_templates_handler(brand_id=brand_id, limit=100)
        
        assert result["total"] == 3
        assert len(result["templates"]) == 3
        assert all(t["brand_id"] == brand_id for t in result["templates"])
        mock_template_storage.list_templates.assert_called_once_with(brand_id, 100)


@pytest.mark.asyncio
async def test_get_template_by_id():
    """Test retrieving a specific template by ID."""
    template_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())
    
    mock_template = Template(
        template_id=template_id,
        brand_id=brand_id,
        name="Test Template",
        description="Test Description",
        generation_params={"prompt": "Test", "style": "modern"},
        thumbnail_url="https://example.com/thumb.png",
    )
    
    with patch("mobius.storage.templates.TemplateStorage") as MockTemplateStorage:
        mock_template_storage = AsyncMock()
        mock_template_storage.get_template.return_value = mock_template
        MockTemplateStorage.return_value = mock_template_storage
        
        result = await get_template_handler(template_id=template_id)
        
        assert result["template_id"] == template_id
        assert result["brand_id"] == brand_id
        assert result["name"] == "Test Template"
        assert result["generation_params"]["style"] == "modern"
        mock_template_storage.get_template.assert_called_once_with(template_id)


@pytest.mark.asyncio
async def test_get_template_not_found():
    """Test retrieving non-existent template raises NotFoundError."""
    template_id = str(uuid.uuid4())
    
    with patch("mobius.storage.templates.TemplateStorage") as MockTemplateStorage:
        mock_template_storage = AsyncMock()
        mock_template_storage.get_template.return_value = None
        MockTemplateStorage.return_value = mock_template_storage
        
        with pytest.raises(NotFoundError) as exc_info:
            await get_template_handler(template_id=template_id)
        
        assert "template" in exc_info.value.error_response.error.message.lower()


@pytest.mark.asyncio
async def test_delete_template():
    """Test soft deleting a template."""
    template_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())
    
    mock_template = Template(
        template_id=template_id,
        brand_id=brand_id,
        name="Test Template",
        description="Test Description",
        generation_params={"prompt": "Test"},
        thumbnail_url="https://example.com/thumb.png",
    )
    
    with patch("mobius.storage.templates.TemplateStorage") as MockTemplateStorage:
        mock_template_storage = AsyncMock()
        mock_template_storage.get_template.return_value = mock_template
        mock_template_storage.delete_template.return_value = True
        MockTemplateStorage.return_value = mock_template_storage
        
        result = await delete_template_handler(template_id=template_id)
        
        assert result["template_id"] == template_id
        assert result["status"] == "deleted"
        mock_template_storage.delete_template.assert_called_once_with(template_id)


@pytest.mark.asyncio
async def test_apply_template_to_request():
    """Test applying template parameters with request overrides."""
    template_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())
    
    mock_template = Template(
        template_id=template_id,
        brand_id=brand_id,
        name="Test Template",
        description="Test Description",
        generation_params={
            "prompt": "Template prompt",
            "style": "modern",
            "quality": 0.9,
        },
        thumbnail_url="https://example.com/thumb.png",
    )
    
    with patch("mobius.storage.templates.TemplateStorage") as MockTemplateStorage:
        mock_template_storage = AsyncMock()
        mock_template_storage.get_template.return_value = mock_template
        MockTemplateStorage.return_value = mock_template_storage
        
        # Request overrides prompt but keeps other params
        request_params = {
            "prompt": "Override prompt",
            "extra_param": "new value",
        }
        
        result = await apply_template_to_request(
            template_id=template_id,
            request_params=request_params,
        )
        
        # Should have merged parameters
        assert result["generation_params"]["prompt"] == "Override prompt"  # Overridden
        assert result["generation_params"]["style"] == "modern"  # From template
        assert result["generation_params"]["quality"] == 0.9  # From template
        assert result["generation_params"]["extra_param"] == "new value"  # From request
        assert result["template_brand_id"] == brand_id


@pytest.mark.asyncio
async def test_generate_with_template():
    """Test generation handler with template application."""
    brand_id = str(uuid.uuid4())
    template_id = str(uuid.uuid4())
    
    mock_template = Template(
        template_id=template_id,
        brand_id=brand_id,
        name="Test Template",
        description="Test Description",
        generation_params={
            "prompt": "Template prompt",
            "style": "modern",
        },
        thumbnail_url="https://example.com/thumb.png",
    )
    
    mock_brand = Brand(
        brand_id=brand_id,
        organization_id=str(uuid.uuid4()),
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=[Color(name="Red", hex="#FF0000", usage="primary")],
            typography=[],
            logos=[],
        ),
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )
    
    # Mock Supabase client
    from unittest.mock import Mock
    mock_client = Mock()
    
    with patch("mobius.storage.brands.get_supabase_client", return_value=mock_client):
        with patch("mobius.storage.templates.get_supabase_client", return_value=mock_client):
            with patch("mobius.storage.jobs.get_supabase_client", return_value=mock_client):
                with patch("mobius.storage.templates.TemplateStorage.get_template", new_callable=AsyncMock, return_value=mock_template):
                    with patch("mobius.storage.brands.BrandStorage.get_brand", new_callable=AsyncMock, return_value=mock_brand):
                        with patch("mobius.storage.jobs.JobStorage.create_job", new_callable=AsyncMock) as mock_create_job:
                            # Mock the job creation to return a job
                            from mobius.models.job import Job
                            mock_job = Job(
                                job_id=str(uuid.uuid4()),
                                brand_id=brand_id,
                                status="pending",
                                progress=0.0,
                                state={},
                                webhook_url=None,
                                idempotency_key=None,
                            )
                            mock_create_job.return_value = mock_job
                            
                            result = await generate_handler(
                                brand_id=brand_id,
                                prompt="Override prompt",
                                template_id=template_id,
                                async_mode=False,
                            )
                            
                            assert result["status"] in ["pending", "processing"]
                            assert "template" in result["message"].lower()
                            assert "job_id" in result


@pytest.mark.asyncio
async def test_generate_with_template_brand_mismatch():
    """Test generation fails when brand_id doesn't match template's brand."""
    brand_id = str(uuid.uuid4())
    different_brand_id = str(uuid.uuid4())
    template_id = str(uuid.uuid4())
    
    mock_template = Template(
        template_id=template_id,
        brand_id=different_brand_id,  # Different brand
        name="Test Template",
        description="Test Description",
        generation_params={"prompt": "Template prompt"},
        thumbnail_url="https://example.com/thumb.png",
    )
    
    with patch("mobius.storage.templates.TemplateStorage") as MockTemplateStorage:
        mock_template_storage = AsyncMock()
        mock_template_storage.get_template.return_value = mock_template
        MockTemplateStorage.return_value = mock_template_storage
        
        # Should raise ValidationError for brand mismatch
        with pytest.raises(ValidationError) as exc_info:
            await generate_handler(
                brand_id=brand_id,
                prompt="Test prompt",
                template_id=template_id,
            )
        
        assert exc_info.value.error_response.error.code == "BRAND_MISMATCH"


@pytest.mark.asyncio
async def test_generate_without_template():
    """Test generation handler without template (direct parameters)."""
    brand_id = str(uuid.uuid4())
    
    mock_brand = Brand(
        brand_id=brand_id,
        organization_id=str(uuid.uuid4()),
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=[Color(name="Red", hex="#FF0000", usage="primary")],
            typography=[],
            logos=[],
        ),
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )
    
    # Mock Supabase client
    from unittest.mock import Mock
    mock_client = Mock()
    
    with patch("mobius.storage.brands.get_supabase_client", return_value=mock_client):
        with patch("mobius.storage.jobs.get_supabase_client", return_value=mock_client):
            with patch("mobius.storage.brands.BrandStorage.get_brand", new_callable=AsyncMock, return_value=mock_brand):
                with patch("mobius.storage.jobs.JobStorage.create_job", new_callable=AsyncMock) as mock_create_job:
                    # Mock the job creation to return a job
                    from mobius.models.job import Job
                    mock_job = Job(
                        job_id=str(uuid.uuid4()),
                        brand_id=brand_id,
                        status="pending",
                        progress=0.0,
                        state={},
                        webhook_url=None,
                        idempotency_key=None,
                    )
                    mock_create_job.return_value = mock_job
                    
                    result = await generate_handler(
                        brand_id=brand_id,
                        prompt="Direct prompt",
                        async_mode=False,
                    )
                    
                    assert result["status"] in ["pending", "processing"]
                    assert "job_id" in result
                    # Should not mention template
                    assert "template" not in result["message"].lower() or "using template" not in result["message"].lower()
