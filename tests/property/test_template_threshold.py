"""
Property-based tests for template threshold enforcement.

**Feature: mobius-phase-2-refactor, Property 7: Template threshold enforcement**
**Validates: Requirements 5.1**
"""

import pytest
from hypothesis import given, strategies as st, settings as hypothesis_settings
from unittest.mock import AsyncMock, Mock, patch
from mobius.api.routes import save_template_handler
from mobius.api.errors import ValidationError, NotFoundError
from mobius.models.asset import Asset
from mobius.config import settings
import uuid


# Strategy for generating compliance scores
compliance_scores = st.floats(min_value=0.0, max_value=100.0)


@given(compliance_score=compliance_scores)
@hypothesis_settings(max_examples=100)
@pytest.mark.asyncio
async def test_template_threshold_enforcement(compliance_score):
    """
    Property 7: Template threshold enforcement
    
    *For any* asset with compliance score below 95 percent, attempting to save it 
    as a template should be rejected.
    
    **Validates: Requirements 5.1**
    """
    # Create a mock asset with the generated compliance score
    asset_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())
    
    mock_asset = Asset(
        asset_id=asset_id,
        brand_id=brand_id,
        job_id=str(uuid.uuid4()),
        prompt="Test prompt",
        image_url="https://example.com/image.png",
        compliance_score=compliance_score,
        compliance_details={},
        generation_params={"prompt": "Test prompt"},
        status="completed",
    )
    
    # Mock the AssetStorage to return our test asset
    with patch("mobius.storage.assets.AssetStorage") as MockAssetStorage:
        mock_storage = AsyncMock()
        mock_storage.get_asset.return_value = mock_asset
        MockAssetStorage.return_value = mock_storage
        
        # Mock TemplateStorage
        with patch("mobius.storage.templates.TemplateStorage") as MockTemplateStorage:
            mock_template_storage = AsyncMock()
            MockTemplateStorage.return_value = mock_template_storage
            
            # Attempt to save as template
            threshold = settings.template_threshold * 100  # 95%
            
            if compliance_score < threshold:
                # Should raise ValidationError for scores below threshold
                with pytest.raises(ValidationError) as exc_info:
                    await save_template_handler(
                        asset_id=asset_id,
                        template_name="Test Template",
                        description="Test Description",
                    )
                
                # Verify the error details
                assert exc_info.value.error_response.error.code == "COMPLIANCE_SCORE_TOO_LOW"
                assert "below the required threshold" in exc_info.value.error_response.error.message
                
                # Verify template was NOT created
                mock_template_storage.create_template.assert_not_called()
            else:
                # Should succeed for scores >= threshold
                from mobius.models.template import Template
                
                mock_template = Template(
                    template_id=str(uuid.uuid4()),
                    brand_id=brand_id,
                    name="Test Template",
                    description="Test Description",
                    generation_params=mock_asset.generation_params,
                    thumbnail_url=mock_asset.image_url,
                    source_asset_id=asset_id,
                )
                mock_template_storage.create_template.return_value = mock_template
                
                result = await save_template_handler(
                    asset_id=asset_id,
                    template_name="Test Template",
                    description="Test Description",
                )
                
                # Verify template was created
                assert result["template_id"] == mock_template.template_id
                assert result["brand_id"] == brand_id
                mock_template_storage.create_template.assert_called_once()


@pytest.mark.asyncio
async def test_template_threshold_with_none_score():
    """
    Edge case: Asset with None compliance score should be rejected.
    """
    asset_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())
    
    mock_asset = Asset(
        asset_id=asset_id,
        brand_id=brand_id,
        job_id=str(uuid.uuid4()),
        prompt="Test prompt",
        image_url="https://example.com/image.png",
        compliance_score=None,  # No score
        compliance_details={},
        generation_params={"prompt": "Test prompt"},
        status="completed",
    )
    
    with patch("mobius.storage.assets.AssetStorage") as MockAssetStorage:
        mock_storage = AsyncMock()
        mock_storage.get_asset.return_value = mock_asset
        MockAssetStorage.return_value = mock_storage
        
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
async def test_template_threshold_with_nonexistent_asset():
    """
    Edge case: Attempting to create template from non-existent asset should fail.
    """
    asset_id = str(uuid.uuid4())
    
    with patch("mobius.storage.assets.AssetStorage") as MockAssetStorage:
        mock_storage = AsyncMock()
        mock_storage.get_asset.return_value = None  # Asset not found
        MockAssetStorage.return_value = mock_storage
        
        # Should raise NotFoundError
        with pytest.raises(NotFoundError) as exc_info:
            await save_template_handler(
                asset_id=asset_id,
                template_name="Test Template",
                description="Test Description",
            )
        
        assert "asset" in exc_info.value.error_response.error.message.lower()
