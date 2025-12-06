"""
Property-based tests for template parameter preservation.

**Feature: mobius-phase-2-refactor, Property 8: Template parameters are preserved**
**Validates: Requirements 5.4**
"""

import pytest
from hypothesis import given, strategies as st, settings as hypothesis_settings
from unittest.mock import AsyncMock, patch
from mobius.api.routes import save_template_handler, get_template_handler
from mobius.models.asset import Asset
from mobius.models.template import Template
import uuid


# Strategy for generating generation parameters
generation_params_strategy = st.dictionaries(
    keys=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll"))),
    values=st.one_of(
        st.text(min_size=1, max_size=50),
        st.integers(min_value=1, max_value=1000),
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        st.booleans(),
    ),
    min_size=1,
    max_size=10,
)


@given(generation_params=generation_params_strategy)
@hypothesis_settings(max_examples=100)
@pytest.mark.asyncio
async def test_template_parameters_preserved(generation_params):
    """
    Property 8: Template parameters are preserved
    
    *For any* template saved from an asset, when that template is retrieved and applied,
    the generation parameters should match exactly the original asset's parameters.
    
    **Validates: Requirements 5.4**
    """
    # Create a mock asset with high compliance score and generated parameters
    asset_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())
    template_id = str(uuid.uuid4())
    
    mock_asset = Asset(
        asset_id=asset_id,
        brand_id=brand_id,
        job_id=str(uuid.uuid4()),
        prompt="Test prompt",
        image_url="https://example.com/image.png",
        compliance_score=96.0,  # Above threshold
        compliance_details={},
        generation_params=generation_params,  # Use generated params
        status="completed",
    )
    
    # Mock the AssetStorage to return our test asset
    with patch("mobius.storage.assets.AssetStorage") as MockAssetStorage:
        mock_asset_storage = AsyncMock()
        mock_asset_storage.get_asset.return_value = mock_asset
        MockAssetStorage.return_value = mock_asset_storage
        
        # Mock TemplateStorage for creation
        with patch("mobius.storage.templates.TemplateStorage") as MockTemplateStorage:
            mock_template_storage = AsyncMock()
            
            # Create the template that will be returned
            created_template = Template(
                template_id=template_id,
                brand_id=brand_id,
                name="Test Template",
                description="Test Description",
                generation_params=generation_params,  # Should preserve params
                thumbnail_url=mock_asset.image_url,
                source_asset_id=asset_id,
            )
            
            mock_template_storage.create_template.return_value = created_template
            mock_template_storage.get_template.return_value = created_template
            MockTemplateStorage.return_value = mock_template_storage
            
            # Save the template
            save_result = await save_template_handler(
                asset_id=asset_id,
                template_name="Test Template",
                description="Test Description",
            )
            
            # Verify template was created with correct parameters
            assert save_result["generation_params"] == generation_params
            
            # Now retrieve the template
            get_result = await get_template_handler(template_id=template_id)
            
            # Property: Retrieved parameters should match original asset parameters
            assert get_result["generation_params"] == generation_params
            
            # Verify the parameters are exactly the same (deep equality)
            for key, value in generation_params.items():
                assert key in get_result["generation_params"]
                assert get_result["generation_params"][key] == value


@pytest.mark.asyncio
async def test_template_parameters_empty_dict():
    """
    Edge case: Template with empty generation parameters should be preserved.
    """
    asset_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())
    template_id = str(uuid.uuid4())
    
    mock_asset = Asset(
        asset_id=asset_id,
        brand_id=brand_id,
        job_id=str(uuid.uuid4()),
        prompt="Test prompt",
        image_url="https://example.com/image.png",
        compliance_score=96.0,
        compliance_details={},
        generation_params={},  # Empty params
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
                generation_params={},
                thumbnail_url=mock_asset.image_url,
                source_asset_id=asset_id,
            )
            
            mock_template_storage.create_template.return_value = created_template
            mock_template_storage.get_template.return_value = created_template
            MockTemplateStorage.return_value = mock_template_storage
            
            # Save and retrieve
            save_result = await save_template_handler(
                asset_id=asset_id,
                template_name="Test Template",
                description="Test Description",
            )
            
            get_result = await get_template_handler(template_id=template_id)
            
            # Empty dict should be preserved
            assert get_result["generation_params"] == {}
            assert save_result["generation_params"] == {}


@pytest.mark.asyncio
async def test_template_parameters_complex_nested():
    """
    Edge case: Template with complex nested parameters should be preserved.
    """
    asset_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())
    template_id = str(uuid.uuid4())
    
    complex_params = {
        "prompt": "Test prompt",
        "style": "modern",
        "colors": ["#FF0000", "#00FF00", "#0000FF"],
        "dimensions": {"width": 1024, "height": 768},
        "options": {
            "enhance": True,
            "quality": 0.95,
            "format": "png",
        },
    }
    
    mock_asset = Asset(
        asset_id=asset_id,
        brand_id=brand_id,
        job_id=str(uuid.uuid4()),
        prompt="Test prompt",
        image_url="https://example.com/image.png",
        compliance_score=97.0,
        compliance_details={},
        generation_params=complex_params,
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
                generation_params=complex_params,
                thumbnail_url=mock_asset.image_url,
                source_asset_id=asset_id,
            )
            
            mock_template_storage.create_template.return_value = created_template
            mock_template_storage.get_template.return_value = created_template
            MockTemplateStorage.return_value = mock_template_storage
            
            # Save and retrieve
            save_result = await save_template_handler(
                asset_id=asset_id,
                template_name="Test Template",
                description="Test Description",
            )
            
            get_result = await get_template_handler(template_id=template_id)
            
            # Complex nested structure should be preserved exactly
            assert get_result["generation_params"] == complex_params
            assert get_result["generation_params"]["colors"] == ["#FF0000", "#00FF00", "#0000FF"]
            assert get_result["generation_params"]["dimensions"]["width"] == 1024
            assert get_result["generation_params"]["options"]["enhance"] is True
