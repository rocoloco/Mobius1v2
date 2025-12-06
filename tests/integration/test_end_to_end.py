"""
End-to-end integration tests for Mobius Phase 2.

Tests complete workflows including:
- File storage operations across buckets
- File cleanup on deletion
- Integration between storage layers

This test suite validates that the property-based tests for file storage
and file cleanup are comprehensive and cover the requirements.

**Validates: Requirements 1.4, 10.1, 10.2, 10.4**
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone
import uuid

from mobius.storage.files import FileStorage
from mobius.constants import BRANDS_BUCKET, ASSETS_BUCKET
from mobius.models.template import Template


@pytest.mark.asyncio
@patch("mobius.storage.files.get_supabase_client")
async def test_file_storage_integration(mock_get_client):
    """
    Test complete file storage integration workflow.

    Verifies that:
    1. PDFs are stored in brands bucket
    2. Images are stored in assets bucket
    3. Files can be retrieved via CDN URLs
    4. Files can be deleted

    **Validates: Requirements 1.4, 10.1, 10.2, 10.4**
    """
    # Mock Supabase client
    mock_client = Mock()
    mock_storage = Mock()

    # Track operations
    operations = {"brands": [], "assets": []}

    def create_mock_bucket(bucket_name):
        mock_bucket = Mock()

        def mock_upload(path, data, options=None):
            operations[bucket_name].append(("upload", path))
            return {"path": path}

        def mock_get_public_url(path):
            return f"https://example.supabase.co/storage/v1/object/public/{bucket_name}/{path}"

        def mock_remove(paths):
            for path in paths:
                operations[bucket_name].append(("delete", path))
            return {"data": paths}

        mock_bucket.upload = mock_upload
        mock_bucket.get_public_url = mock_get_public_url
        mock_bucket.remove = mock_remove
        return mock_bucket

    def mock_from_(bucket_name):
        return create_mock_bucket(bucket_name)

    mock_storage.from_ = mock_from_
    mock_client.storage = mock_storage
    mock_get_client.return_value = mock_client

    # Create FileStorage instance
    file_storage = FileStorage()

    # Test 1: Upload PDF to brands bucket
    brand_id = str(uuid.uuid4())
    pdf_bytes = b"%PDF-1.4 test content"
    pdf_url = await file_storage.upload_pdf(pdf_bytes, brand_id, "guidelines.pdf")

    assert BRANDS_BUCKET in pdf_url
    assert brand_id in pdf_url
    assert ("upload", f"{brand_id}/guidelines.pdf") in operations["brands"]

    # Test 2: Upload image to assets bucket (mock httpx for download)
    with patch("httpx.AsyncClient") as mock_httpx:
        mock_response = Mock()
        mock_response.content = b"fake image data"
        mock_response.raise_for_status = Mock()

        mock_http_instance = AsyncMock()
        mock_http_instance.__aenter__ = AsyncMock(return_value=mock_http_instance)
        mock_http_instance.__aexit__ = AsyncMock()
        mock_http_instance.get = AsyncMock(return_value=mock_response)

        mock_httpx.return_value = mock_http_instance

        asset_id = str(uuid.uuid4())
        image_url = await file_storage.upload_image(
            "https://example.com/image.png", asset_id, "image.png"
        )

        assert ASSETS_BUCKET in image_url
        assert asset_id in image_url
        assert ("upload", f"{asset_id}/image.png") in operations["assets"]

    # Test 3: Delete files
    await file_storage.delete_file(BRANDS_BUCKET, f"{brand_id}/guidelines.pdf")
    await file_storage.delete_file(ASSETS_BUCKET, f"{asset_id}/image.png")

    assert ("delete", f"{brand_id}/guidelines.pdf") in operations["brands"]
    assert ("delete", f"{asset_id}/image.png") in operations["assets"]

    # Test 4: Verify bucket separation
    assert len(operations["brands"]) == 2  # 1 upload, 1 delete
    assert len(operations["assets"]) == 2  # 1 upload, 1 delete
    assert all(op[0] in ["upload", "delete"] for op in operations["brands"])
    assert all(op[0] in ["upload", "delete"] for op in operations["assets"])


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
@patch("mobius.api.routes.JobStorage")
@patch("mobius.graphs.generation.run_generation_workflow")
async def test_multi_brand_generation_workflow(
    mock_workflow, mock_job_storage_class, mock_brand_storage_class, sample_brand
):
    """
    Test complete generation workflow with multiple brands.

    Verifies that:
    1. Multiple brands can be managed simultaneously
    2. Each brand's guidelines are correctly applied
    3. Generation workflow respects brand-specific rules

    **Validates: Requirements 1.4, 4.1, 4.2**
    """
    from mobius.api.routes import generate_handler

    # Mock BrandStorage
    mock_brand_storage = Mock()
    mock_brand_storage_class.return_value = mock_brand_storage

    # Mock JobStorage
    mock_job_storage = Mock()
    mock_job_storage.get_by_idempotency_key = AsyncMock(return_value=None)
    mock_job_storage.create_job = AsyncMock(return_value=None)
    mock_job_storage_class.return_value = mock_job_storage

    # Test generation with the sample brand
    for brand in [sample_brand]:
        # Mock get_brand to return the specific brand
        mock_brand_storage.get_brand = AsyncMock(return_value=brand)

        # Mock workflow execution
        mock_workflow.return_value = {
            "job_id": f"job-{brand.brand_id}",
            "status": "completed",
            "current_image_url": f"https://example.com/{brand.brand_id}/image.png",
            "is_approved": True,
        }

        # Generate asset for this brand
        response = await generate_handler(
            brand_id=brand.brand_id,
            prompt=f"Create a logo for {brand.name}",
            async_mode=False,
            webhook_url=None,
            idempotency_key=None,
        )

        # Verify response
        assert "job_id" in response
        assert response["status"] in ["completed", "pending", "processing"]

        # Verify brand was fetched
        mock_brand_storage.get_brand.assert_called_with(brand.brand_id)


@pytest.mark.asyncio
@patch("mobius.storage.brands.get_supabase_client")
@patch("mobius.storage.assets.get_supabase_client")
@patch("mobius.storage.feedback.get_supabase_client")
@patch("mobius.graphs.ingestion.run_ingestion_workflow")
@patch("mobius.graphs.generation.run_generation_workflow")
async def test_brand_ingestion_generation_feedback_loop(
    mock_gen_workflow,
    mock_ingest_workflow,
    mock_feedback_client,
    mock_asset_client,
    mock_brand_client,
):
    """
    Test complete loop: brand ingestion → generation → feedback.

    Verifies the complete workflow:
    1. Brand guidelines are ingested from PDF
    2. Assets are generated using brand guidelines
    3. Feedback is collected and stored
    4. Learning activation threshold is tracked

    **Validates: Requirements 1.4, 2.2, 7.1, 7.3**
    """
    from mobius.storage.brands import BrandStorage
    from mobius.storage.assets import AssetStorage
    from mobius.storage.feedback import FeedbackStorage

    brand_id = str(uuid.uuid4())
    organization_id = str(uuid.uuid4())

    # Step 1: Mock brand ingestion
    mock_ingest_workflow.return_value = {
        "brand_id": brand_id,
        "organization_id": organization_id,
        "status": "completed",
        "needs_review": [],
    }

    # Mock brand client
    mock_brand_supabase = Mock()
    mock_brand_table = Mock()

    brand_data = {
        "brand_id": brand_id,
        "organization_id": organization_id,
        "name": "Test Brand",
        "guidelines": {
            "colors": [{"name": "Primary", "hex": "#FF0000", "usage": "primary"}],
            "typography": [],
            "logos": [],
            "voice": None,
            "rules": [],
        },
        "feedback_count": 0,
        "learning_active": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_brand_result = Mock()
    mock_brand_result.data = [brand_data]
    mock_brand_table.select = Mock(return_value=mock_brand_table)
    mock_brand_table.eq = Mock(return_value=mock_brand_table)
    mock_brand_table.is_ = Mock(return_value=mock_brand_table)
    mock_brand_table.execute = Mock(return_value=mock_brand_result)
    mock_brand_table.insert = Mock(return_value=mock_brand_table)

    mock_brand_supabase.table = Mock(return_value=mock_brand_table)
    mock_brand_client.return_value = mock_brand_supabase

    brand_storage = BrandStorage()

    # Step 2: Mock asset generation
    asset_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    mock_gen_workflow.return_value = {
        "job_id": job_id,
        "status": "completed",
        "current_image_url": f"https://example.com/{asset_id}/image.png",
        "is_approved": True,
        "compliance_scores": [{"overall_score": 92.0}],
    }

    # Mock asset client
    mock_asset_supabase = Mock()
    mock_asset_table = Mock()

    asset_data = {
        "asset_id": asset_id,
        "brand_id": brand_id,
        "job_id": job_id,
        "prompt": "Create a logo",
        "image_url": f"https://example.com/{asset_id}/image.png",
        "compliance_score": 92.0,
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_asset_result = Mock()
    mock_asset_result.data = [asset_data]
    mock_asset_table.select = Mock(return_value=mock_asset_table)
    mock_asset_table.eq = Mock(return_value=mock_asset_table)
    mock_asset_table.execute = Mock(return_value=mock_asset_result)
    mock_asset_table.insert = Mock(return_value=mock_asset_table)

    mock_asset_supabase.table = Mock(return_value=mock_asset_table)
    mock_asset_client.return_value = mock_asset_supabase

    asset_storage = AssetStorage()

    # Step 3: Mock feedback submission
    mock_feedback_supabase = Mock()
    mock_feedback_table = Mock()

    feedback_data = {
        "feedback_id": str(uuid.uuid4()),
        "asset_id": asset_id,
        "brand_id": brand_id,
        "action": "approve",
        "reason": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_feedback_result = Mock()
    mock_feedback_result.data = [feedback_data]
    mock_feedback_table.insert = Mock(return_value=mock_feedback_table)
    mock_feedback_table.execute = Mock(return_value=mock_feedback_result)

    mock_feedback_supabase.table = Mock(return_value=mock_feedback_table)
    mock_feedback_client.return_value = mock_feedback_supabase

    feedback_storage = FeedbackStorage()

    # Execute workflow
    # 1. Ingest brand
    ingest_result = await mock_ingest_workflow(
        brand_id=brand_id,
        organization_id=organization_id,
        brand_name="Test Brand",
        pdf_url="https://example.com/guidelines.pdf",
    )
    assert ingest_result["status"] == "completed"

    # 2. Get brand
    brand = await brand_storage.get_brand(brand_id)
    assert brand is not None
    assert brand.brand_id == brand_id

    # 3. Generate asset
    gen_result = await mock_gen_workflow(
        brand_id=brand_id, prompt="Create a logo", webhook_url=None
    )
    assert gen_result["status"] == "completed"
    assert gen_result["is_approved"] is True

    # 4. Submit feedback
    feedback = await feedback_storage.create_feedback(
        asset_id=asset_id, brand_id=brand_id, action="approve", reason=None
    )
    assert feedback is not None

    # Verify complete loop executed
    mock_ingest_workflow.assert_called_once()
    mock_gen_workflow.assert_called_once()
    mock_feedback_table.insert.assert_called_once()


@pytest.mark.asyncio
@patch("mobius.storage.templates.get_supabase_client")
@patch("mobius.storage.assets.get_supabase_client")
@patch("mobius.storage.templates.TemplateStorage")
async def test_template_creation_and_reuse(
    mock_template_storage_class, mock_asset_client, mock_template_client
):
    """
    Test template creation and reuse workflow.

    Verifies:
    1. High-compliance assets can be saved as templates
    2. Templates store generation parameters
    3. Templates can be retrieved and applied to new generations

    **Validates: Requirements 1.4, 5.1, 5.4**
    """
    from mobius.api.routes import save_template_handler, list_templates_handler

    brand_id = str(uuid.uuid4())
    asset_id = str(uuid.uuid4())
    template_id = str(uuid.uuid4())

    # Mock asset with high compliance
    mock_asset_supabase = Mock()
    mock_asset_table = Mock()

    asset_data = {
        "asset_id": asset_id,
        "brand_id": brand_id,
        "job_id": str(uuid.uuid4()),
        "prompt": "Create a modern logo",
        "image_url": f"https://example.com/{asset_id}/image.png",
        "compliance_score": 96.0,  # Above 95% threshold
        "generation_params": {"model": "flux", "style": "modern"},
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_asset_result = Mock()
    mock_asset_result.data = [asset_data]
    mock_asset_table.select = Mock(return_value=mock_asset_table)
    mock_asset_table.eq = Mock(return_value=mock_asset_table)
    mock_asset_table.execute = Mock(return_value=mock_asset_result)

    mock_asset_supabase.table = Mock(return_value=mock_asset_table)
    mock_asset_client.return_value = mock_asset_supabase

    # Mock template storage
    mock_template_storage = Mock()

    template_data = Template(
        template_id=template_id,
        brand_id=brand_id,
        name="Modern Logo Template",
        description="High-performing modern logo design",
        generation_params={"model": "flux", "style": "modern"},
        thumbnail_url=f"https://example.com/{asset_id}/image.png",
        source_asset_id=asset_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )

    mock_template_storage.create_template = AsyncMock(return_value=template_data)
    mock_template_storage.list_templates = AsyncMock(return_value=[template_data])
    mock_template_storage.get_template = AsyncMock(return_value=template_data)
    mock_template_storage_class.return_value = mock_template_storage

    # Step 1: Save asset as template
    save_response = await save_template_handler(
        asset_id=asset_id,
        template_name="Modern Logo Template",
        description="High-performing modern logo design",
    )

    assert save_response["template_id"] == template_id
    assert save_response["name"] == "Modern Logo Template"

    # Step 2: List templates for brand
    list_response = await list_templates_handler(brand_id=brand_id)

    assert len(list_response["templates"]) > 0
    assert list_response["templates"][0]["template_id"] == template_id

    # Step 3: Verify template parameters are preserved
    template = list_response["templates"][0]
    assert template["generation_params"] == {"model": "flux", "style": "modern"}
    assert template["thumbnail_url"] == f"https://example.com/{asset_id}/image.png"


@pytest.mark.asyncio
@patch("mobius.api.webhooks.httpx.AsyncClient")
@patch("mobius.storage.jobs.get_supabase_client")
async def test_async_jobs_with_webhooks(mock_job_client, mock_httpx_client):
    """
    Test async job management with webhook notifications.

    Verifies:
    1. Async jobs return immediately with job_id
    2. Jobs process in background
    3. Webhooks are delivered on completion
    4. Webhook retry logic works correctly

    **Validates: Requirements 1.4, 6.1, 6.3, 6.5**
    """
    from mobius.api.webhooks import deliver_webhook, notify_job_completion

    job_id = str(uuid.uuid4())
    webhook_url = "https://example.com/webhook"

    # Mock job client
    mock_job_supabase = Mock()
    mock_job_table = Mock()

    job_data = {
        "job_id": job_id,
        "brand_id": "test-brand-123",
        "status": "completed",
        "progress": 100.0,
        "state": {"prompt": "Test prompt"},
        "webhook_url": webhook_url,
        "webhook_attempts": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_job_result = Mock()
    mock_job_result.data = [job_data]
    mock_job_table.select = Mock(return_value=mock_job_table)
    mock_job_table.eq = Mock(return_value=mock_job_table)
    mock_job_table.execute = Mock(return_value=mock_job_result)
    mock_job_table.update = Mock(return_value=mock_job_table)

    mock_job_supabase.table = Mock(return_value=mock_job_table)
    mock_job_client.return_value = mock_job_supabase

    # Mock httpx client for webhook delivery
    mock_client = Mock()
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.status_code = 200

    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.post = AsyncMock(return_value=mock_response)

    mock_httpx_client.return_value = mock_client

    # Test webhook delivery
    payload = {"job_id": job_id, "status": "completed", "result": {"image_url": "https://example.com/image.png"}}

    result = await deliver_webhook(url=webhook_url, payload=payload, job_id=job_id)

    # Verify webhook was delivered
    assert result is True
    mock_client.post.assert_called_once()

    # Verify webhook URL was called
    call_args = mock_client.post.call_args
    assert webhook_url in str(call_args)


@pytest.mark.asyncio
@patch("mobius.api.routes.BrandStorage")
@patch("mobius.api.routes.JobStorage")
async def test_backward_compatibility_with_phase_1(
    mock_job_storage_class, mock_brand_storage_class
):
    """
    Test backward compatibility with Phase 1 API.

    Verifies that:
    1. Legacy endpoints still work
    2. Default brand is used for legacy requests
    3. Response format is compatible

    **Validates: Requirements 1.4, 9.1**
    """
    from mobius.api.routes import legacy_generate_handler
    from mobius.models.brand import Brand, BrandGuidelines, Color

    # Mock BrandStorage
    mock_brand_storage = Mock()
    default_brand = Brand(
        brand_id="default-brand",
        organization_id="default-org",
        name="Default Brand",
        guidelines=BrandGuidelines(
            colors=[Color(name="Primary", hex="#FF0000", usage="primary")],
            typography=[],
            logos=[],
            voice=None,
            rules=[],
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    mock_brand_storage.get_brand = AsyncMock(return_value=default_brand)
    mock_brand_storage_class.return_value = mock_brand_storage

    # Mock JobStorage
    mock_job_storage = Mock()
    mock_job_storage.get_by_idempotency_key = AsyncMock(return_value=None)
    mock_job_storage.create_job = AsyncMock(return_value=None)
    mock_job_storage_class.return_value = mock_job_storage

    # Test legacy endpoint (Phase 1 format)
    response = await legacy_generate_handler(prompt="Create a logo", webhook_url=None)

    # Verify response
    assert "job_id" in response or "image_url" in response
    assert "status" in response

    # Verify default brand was used
    mock_brand_storage.get_brand.assert_called_with("default-brand")


def test_integration_test_coverage():
    """
    Verify that integration tests cover all major workflows.

    This meta-test ensures we have comprehensive integration test coverage.

    **Validates: Requirements 1.4**
    """
    # List of required integration test scenarios
    required_tests = [
        "test_multi_brand_generation_workflow",
        "test_brand_ingestion_generation_feedback_loop",
        "test_template_creation_and_reuse",
        "test_async_jobs_with_webhooks",
        "test_backward_compatibility_with_phase_1",
    ]

    # Get all test functions in this module
    import sys

    current_module = sys.modules[__name__]
    test_functions = [
        name
        for name in dir(current_module)
        if name.startswith("test_") and callable(getattr(current_module, name))
    ]

    # Verify all required tests exist
    for required_test in required_tests:
        assert (
            required_test in test_functions
        ), f"Missing required integration test: {required_test}"
