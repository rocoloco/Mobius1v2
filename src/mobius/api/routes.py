"""
Brand management API route handlers.

Implements all brand CRUD operations with validation and error handling.
"""

from mobius.api.utils import generate_request_id, set_request_id, get_request_id
from mobius.api.errors import ValidationError, NotFoundError, StorageError
from mobius.api.schemas import (
    IngestBrandRequest,
    IngestBrandResponse,
    BrandListResponse,
    BrandListItem,
    BrandDetailResponse,
    UpdateBrandRequest,
)
from mobius.constants import MAX_PDF_SIZE_BYTES, ALLOWED_PDF_MIME_TYPES
from mobius.storage.brands import BrandStorage
from mobius.storage.jobs import JobStorage
from mobius.storage.database import get_supabase_client
from typing import Optional
import structlog
from datetime import datetime, timezone
import uuid

logger = structlog.get_logger()


async def ingest_brand_handler(
    organization_id: str,
    brand_name: str,
    file: bytes,
    content_type: str,
    filename: str,
) -> IngestBrandResponse:
    """
    Handle brand guidelines PDF ingestion with validation.

    Validates file size, MIME type, and PDF header before processing.

    Args:
        organization_id: Organization ID
        brand_name: Brand name
        file: PDF file bytes
        content_type: MIME type from upload
        filename: Original filename

    Returns:
        IngestBrandResponse with brand_id and status

    Raises:
        ValidationError: If file validation fails
    """
    request_id = generate_request_id()
    set_request_id(request_id)

    logger.info(
        "ingest_request_received",
        request_id=request_id,
        organization_id=organization_id,
        brand_name=brand_name,
        filename=filename,
        file_size=len(file),
    )

    # Validate file size BEFORE any processing
    if len(file) > MAX_PDF_SIZE_BYTES:
        logger.warning(
            "file_too_large",
            request_id=request_id,
            size_mb=len(file) / 1024 / 1024,
            max_mb=MAX_PDF_SIZE_BYTES / 1024 / 1024,
        )
        raise ValidationError(
            code="FILE_TOO_LARGE",
            message=f"PDF exceeds maximum size of 50MB. Received: {len(file) / 1024 / 1024:.1f}MB",
            request_id=request_id,
        )

    # Validate MIME type
    if content_type not in ALLOWED_PDF_MIME_TYPES:
        logger.warning(
            "invalid_mime_type", request_id=request_id, content_type=content_type
        )
        raise ValidationError(
            code="INVALID_FILE_TYPE",
            message=f"Only PDF files are accepted. Received: {content_type}",
            request_id=request_id,
        )

    # Validate PDF header (basic check)
    if not file[:4] == b"%PDF":
        logger.warning("invalid_pdf_header", request_id=request_id)
        raise ValidationError(
            code="INVALID_PDF",
            message="File does not appear to be a valid PDF",
            request_id=request_id,
        )

    logger.info("pdf_validation_passed", request_id=request_id)

    # TODO: Continue with upload and ingestion workflow
    # For now, return a placeholder response
    return IngestBrandResponse(
        brand_id="brand-placeholder",
        status="validation_passed",
        pdf_url="https://placeholder.com/pdf",
        needs_review=[],
        request_id=request_id,
    )


async def list_brands_handler(
    organization_id: str,
    search: Optional[str] = None,
    limit: int = 100,
) -> BrandListResponse:
    """
    List all brands for an organization with optional search.

    Includes computed statistics: asset_count and avg_compliance_score.

    Args:
        organization_id: Organization ID to filter by
        search: Optional search term for brand name
        limit: Maximum number of brands to return (default 100)

    Returns:
        BrandListResponse with list of brands and total count
    """
    request_id = generate_request_id()
    set_request_id(request_id)

    logger.info(
        "list_brands_request",
        request_id=request_id,
        organization_id=organization_id,
        search=search,
        limit=limit,
    )

    try:
        storage = BrandStorage()
        brands = await storage.list_brands(organization_id, search, limit)

        # Get statistics for each brand
        brand_items = []
        for brand in brands:
            # Get asset count and avg compliance score
            client = get_supabase_client()
            assets_result = (
                client.table("assets")
                .select("compliance_score, created_at")
                .eq("brand_id", brand.brand_id)
                .execute()
            )

            asset_count = len(assets_result.data)
            avg_score = 0.0
            last_activity = brand.updated_at

            if asset_count > 0:
                scores = [
                    a["compliance_score"]
                    for a in assets_result.data
                    if a.get("compliance_score") is not None
                ]
                avg_score = sum(scores) / len(scores) if scores else 0.0

                # Get most recent activity
                if assets_result.data:
                    latest_asset = max(
                        assets_result.data,
                        key=lambda a: a.get("created_at", ""),
                    )
                    last_activity = datetime.fromisoformat(
                        latest_asset["created_at"].replace("Z", "+00:00")
                    )

            brand_items.append(
                BrandListItem(
                    brand_id=brand.brand_id,
                    name=brand.name,
                    logo_thumbnail_url=brand.logo_thumbnail_url,
                    asset_count=asset_count,
                    avg_compliance_score=avg_score,
                    last_activity=last_activity,
                )
            )

        logger.info(
            "list_brands_success",
            request_id=request_id,
            count=len(brand_items),
        )

        return BrandListResponse(
            brands=brand_items,
            total=len(brand_items),
            request_id=request_id,
        )

    except Exception as e:
        logger.error("list_brands_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="list_brands",
            request_id=request_id,
            details={"error": str(e)},
        )


async def get_brand_handler(brand_id: str) -> BrandDetailResponse:
    """
    Get detailed brand information by ID.

    Args:
        brand_id: Brand UUID

    Returns:
        BrandDetailResponse with complete brand details

    Raises:
        NotFoundError: If brand does not exist
    """
    request_id = generate_request_id()
    set_request_id(request_id)

    logger.info("get_brand_request", request_id=request_id, brand_id=brand_id)

    try:
        storage = BrandStorage()
        brand = await storage.get_brand(brand_id)

        if not brand:
            logger.warning("brand_not_found", request_id=request_id, brand_id=brand_id)
            raise NotFoundError(resource="brand", resource_id=brand_id, request_id=request_id)

        logger.info("get_brand_success", request_id=request_id, brand_id=brand_id)

        return BrandDetailResponse(
            brand_id=brand.brand_id,
            organization_id=brand.organization_id,
            name=brand.name,
            guidelines=brand.guidelines.model_dump(),
            pdf_url=brand.pdf_url,
            logo_thumbnail_url=brand.logo_thumbnail_url,
            needs_review=brand.needs_review,
            learning_active=brand.learning_active,
            feedback_count=brand.feedback_count,
            created_at=brand.created_at,
            updated_at=brand.updated_at,
            request_id=request_id,
        )

    except NotFoundError:
        raise
    except Exception as e:
        logger.error("get_brand_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="get_brand",
            request_id=request_id,
            details={"error": str(e)},
        )


async def update_brand_handler(
    brand_id: str,
    updates: UpdateBrandRequest,
) -> BrandDetailResponse:
    """
    Update brand metadata.

    Args:
        brand_id: Brand UUID
        updates: Fields to update

    Returns:
        BrandDetailResponse with updated brand details

    Raises:
        NotFoundError: If brand does not exist
    """
    request_id = generate_request_id()
    set_request_id(request_id)

    logger.info(
        "update_brand_request",
        request_id=request_id,
        brand_id=brand_id,
        updates=updates.model_dump(exclude_none=True),
    )

    try:
        storage = BrandStorage()

        # Check if brand exists
        brand = await storage.get_brand(brand_id)
        if not brand:
            logger.warning("brand_not_found", request_id=request_id, brand_id=brand_id)
            raise NotFoundError(resource="brand", resource_id=brand_id, request_id=request_id)

        # Update brand
        update_dict = updates.model_dump(exclude_none=True)
        if not update_dict:
            # No updates provided, return current brand
            logger.info("no_updates_provided", request_id=request_id, brand_id=brand_id)
            return BrandDetailResponse(
                brand_id=brand.brand_id,
                organization_id=brand.organization_id,
                name=brand.name,
                guidelines=brand.guidelines.model_dump(),
                pdf_url=brand.pdf_url,
                logo_thumbnail_url=brand.logo_thumbnail_url,
                needs_review=brand.needs_review,
                learning_active=brand.learning_active,
                feedback_count=brand.feedback_count,
                created_at=brand.created_at,
                updated_at=brand.updated_at,
                request_id=request_id,
            )

        updated_brand = await storage.update_brand(brand_id, update_dict)

        logger.info("update_brand_success", request_id=request_id, brand_id=brand_id)

        return BrandDetailResponse(
            brand_id=updated_brand.brand_id,
            organization_id=updated_brand.organization_id,
            name=updated_brand.name,
            guidelines=updated_brand.guidelines.model_dump(),
            pdf_url=updated_brand.pdf_url,
            logo_thumbnail_url=updated_brand.logo_thumbnail_url,
            needs_review=updated_brand.needs_review,
            learning_active=updated_brand.learning_active,
            feedback_count=updated_brand.feedback_count,
            created_at=updated_brand.created_at,
            updated_at=updated_brand.updated_at,
            request_id=request_id,
        )

    except NotFoundError:
        raise
    except Exception as e:
        logger.error("update_brand_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="update_brand",
            request_id=request_id,
            details={"error": str(e)},
        )


async def delete_brand_handler(brand_id: str) -> dict:
    """
    Soft delete a brand.

    Sets deleted_at timestamp instead of removing the record.
    Associated assets remain accessible for audit purposes.

    Args:
        brand_id: Brand UUID

    Returns:
        Dictionary with success message

    Raises:
        NotFoundError: If brand does not exist
    """
    request_id = generate_request_id()
    set_request_id(request_id)

    logger.info("delete_brand_request", request_id=request_id, brand_id=brand_id)

    try:
        storage = BrandStorage()

        # Check if brand exists
        brand = await storage.get_brand(brand_id)
        if not brand:
            logger.warning("brand_not_found", request_id=request_id, brand_id=brand_id)
            raise NotFoundError(resource="brand", resource_id=brand_id, request_id=request_id)

        # Soft delete
        await storage.delete_brand(brand_id)

        logger.info("delete_brand_success", request_id=request_id, brand_id=brand_id)

        return {
            "brand_id": brand_id,
            "status": "deleted",
            "message": "Brand soft deleted successfully",
            "request_id": request_id,
        }

    except NotFoundError:
        raise
    except Exception as e:
        logger.error("delete_brand_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="delete_brand",
            request_id=request_id,
            details={"error": str(e)},
        )


# Template Management Handlers

async def save_template_handler(
    asset_id: str,
    template_name: str,
    description: str,
) -> dict:
    """
    Save an asset as a reusable template.

    Only assets with compliance score >= 95% can be saved as templates.

    Args:
        asset_id: Asset UUID to create template from
        template_name: Name for the template
        description: Template description

    Returns:
        TemplateResponse with created template details

    Raises:
        NotFoundError: If asset does not exist
        ValidationError: If asset compliance score is below 95%
    """
    from mobius.api.schemas import TemplateResponse, SaveTemplateRequest
    from mobius.storage.assets import AssetStorage
    from mobius.storage.templates import TemplateStorage
    from mobius.models.template import Template
    from mobius.config import settings
    import uuid

    request_id = generate_request_id()
    set_request_id(request_id)

    logger.info(
        "save_template_request",
        request_id=request_id,
        asset_id=asset_id,
        template_name=template_name,
    )

    try:
        # Get the asset
        asset_storage = AssetStorage()
        asset = await asset_storage.get_asset(asset_id)

        if not asset:
            logger.warning("asset_not_found", request_id=request_id, asset_id=asset_id)
            raise NotFoundError(resource="asset", resource_id=asset_id, request_id=request_id)

        # Check compliance score threshold (95%)
        if asset.compliance_score is None or asset.compliance_score < settings.template_threshold * 100:
            logger.warning(
                "compliance_score_too_low",
                request_id=request_id,
                asset_id=asset_id,
                score=asset.compliance_score,
                threshold=settings.template_threshold * 100,
            )
            raise ValidationError(
                code="COMPLIANCE_SCORE_TOO_LOW",
                message=f"Asset compliance score ({asset.compliance_score}%) is below the required threshold ({settings.template_threshold * 100}%) for template creation",
                request_id=request_id,
                details={
                    "asset_id": asset_id,
                    "compliance_score": asset.compliance_score,
                    "required_threshold": settings.template_threshold * 100,
                },
            )

        # Create template
        template = Template(
            template_id=str(uuid.uuid4()),
            brand_id=asset.brand_id,
            name=template_name,
            description=description,
            generation_params=asset.generation_params or {},
            thumbnail_url=asset.image_url,
            source_asset_id=asset_id,
        )

        template_storage = TemplateStorage()
        created_template = await template_storage.create_template(template)

        logger.info(
            "save_template_success",
            request_id=request_id,
            template_id=created_template.template_id,
            asset_id=asset_id,
        )

        return TemplateResponse(
            template_id=created_template.template_id,
            brand_id=created_template.brand_id,
            name=created_template.name,
            description=created_template.description,
            generation_params=created_template.generation_params,
            thumbnail_url=created_template.thumbnail_url,
            created_at=created_template.created_at,
            request_id=request_id,
        ).model_dump()

    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error("save_template_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="save_template",
            request_id=request_id,
            details={"error": str(e)},
        )


async def list_templates_handler(
    brand_id: str,
    limit: int = 100,
) -> dict:
    """
    List all templates for a brand.

    Args:
        brand_id: Brand UUID to filter templates
        limit: Maximum number of templates to return (default 100)

    Returns:
        TemplateListResponse with list of templates
    """
    from mobius.api.schemas import TemplateResponse, TemplateListResponse
    from mobius.storage.templates import TemplateStorage

    request_id = generate_request_id()
    set_request_id(request_id)

    logger.info(
        "list_templates_request",
        request_id=request_id,
        brand_id=brand_id,
        limit=limit,
    )

    try:
        template_storage = TemplateStorage()
        templates = await template_storage.list_templates(brand_id, limit)

        template_responses = [
            TemplateResponse(
                template_id=t.template_id,
                brand_id=t.brand_id,
                name=t.name,
                description=t.description,
                generation_params=t.generation_params,
                thumbnail_url=t.thumbnail_url,
                created_at=t.created_at,
                request_id=request_id,
            )
            for t in templates
        ]

        logger.info(
            "list_templates_success",
            request_id=request_id,
            brand_id=brand_id,
            count=len(template_responses),
        )

        return TemplateListResponse(
            templates=template_responses,
            total=len(template_responses),
            request_id=request_id,
        ).model_dump()

    except Exception as e:
        logger.error("list_templates_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="list_templates",
            request_id=request_id,
            details={"error": str(e)},
        )


async def get_template_handler(template_id: str) -> dict:
    """
    Get detailed template information by ID.

    Args:
        template_id: Template UUID

    Returns:
        TemplateResponse with complete template details

    Raises:
        NotFoundError: If template does not exist
    """
    from mobius.api.schemas import TemplateResponse
    from mobius.storage.templates import TemplateStorage

    request_id = generate_request_id()
    set_request_id(request_id)

    logger.info("get_template_request", request_id=request_id, template_id=template_id)

    try:
        template_storage = TemplateStorage()
        template = await template_storage.get_template(template_id)

        if not template:
            logger.warning("template_not_found", request_id=request_id, template_id=template_id)
            raise NotFoundError(resource="template", resource_id=template_id, request_id=request_id)

        logger.info("get_template_success", request_id=request_id, template_id=template_id)

        return TemplateResponse(
            template_id=template.template_id,
            brand_id=template.brand_id,
            name=template.name,
            description=template.description,
            generation_params=template.generation_params,
            thumbnail_url=template.thumbnail_url,
            created_at=template.created_at,
            request_id=request_id,
        ).model_dump()

    except NotFoundError:
        raise
    except Exception as e:
        logger.error("get_template_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="get_template",
            request_id=request_id,
            details={"error": str(e)},
        )


async def delete_template_handler(template_id: str) -> dict:
    """
    Delete a template.

    Soft deletes the template by setting deleted_at timestamp.

    Args:
        template_id: Template UUID

    Returns:
        Dictionary with success message

    Raises:
        NotFoundError: If template does not exist
    """
    from mobius.storage.templates import TemplateStorage

    request_id = generate_request_id()
    set_request_id(request_id)

    logger.info("delete_template_request", request_id=request_id, template_id=template_id)

    try:
        template_storage = TemplateStorage()

        # Check if template exists
        template = await template_storage.get_template(template_id)
        if not template:
            logger.warning("template_not_found", request_id=request_id, template_id=template_id)
            raise NotFoundError(resource="template", resource_id=template_id, request_id=request_id)

        # Soft delete
        await template_storage.delete_template(template_id)

        logger.info("delete_template_success", request_id=request_id, template_id=template_id)

        return {
            "template_id": template_id,
            "status": "deleted",
            "message": "Template deleted successfully",
            "request_id": request_id,
        }

    except NotFoundError:
        raise
    except Exception as e:
        logger.error("delete_template_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="delete_template",
            request_id=request_id,
            details={"error": str(e)},
        )


# Generation Handler with Template Support

async def apply_template_to_request(
    template_id: str,
    request_params: dict,
) -> dict:
    """
    Load a template and merge its parameters with request overrides.
    
    Args:
        template_id: Template UUID to load
        request_params: Request parameters that can override template defaults
        
    Returns:
        Merged generation parameters with request overrides taking precedence
        
    Raises:
        NotFoundError: If template does not exist
    """
    from mobius.storage.templates import TemplateStorage
    
    logger.info("applying_template", template_id=template_id)
    
    template_storage = TemplateStorage()
    template = await template_storage.get_template(template_id)
    
    if not template:
        raise NotFoundError(resource="template", resource_id=template_id, request_id=get_request_id())
    
    # Start with template parameters as base
    merged_params = template.generation_params.copy()
    
    # Override with request parameters (request takes precedence)
    for key, value in request_params.items():
        if value is not None:  # Only override if explicitly provided
            merged_params[key] = value
    
    logger.info(
        "template_applied",
        template_id=template_id,
        template_brand_id=template.brand_id,
        merged_params_count=len(merged_params),
    )
    
    return {
        "generation_params": merged_params,
        "template_brand_id": template.brand_id,
        "template_name": template.name,
    }


async def generate_handler(
    brand_id: str,
    prompt: str,
    template_id: Optional[str] = None,
    webhook_url: Optional[str] = None,
    async_mode: bool = False,
    idempotency_key: Optional[str] = None,
    **additional_params,
) -> dict:
    """
    Handle asset generation with optional template support and idempotency.
    
    If template_id is provided:
    1. Load the template
    2. Pre-fill generation parameters from template
    3. Allow request parameters to override template defaults
    4. Verify brand_id matches template's brand (or use template's brand)
    
    If idempotency_key is provided:
    1. Check for existing non-expired job with same key
    2. Return existing job if found
    3. Create new job if not found
    
    Args:
        brand_id: Brand ID to use for generation
        prompt: Generation prompt (can override template prompt)
        template_id: Optional template ID to use
        webhook_url: Optional webhook URL for async completion
        async_mode: Whether to run asynchronously
        idempotency_key: Optional idempotency key for duplicate prevention
        **additional_params: Additional generation parameters
        
    Returns:
        GenerateResponse with job details
        
    Raises:
        NotFoundError: If template or brand does not exist
        ValidationError: If brand_id doesn't match template's brand
    """
    from mobius.api.schemas import GenerateResponse
    from mobius.models.job import Job
    
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info(
        "generation_request_received",
        request_id=request_id,
        brand_id=brand_id,
        template_id=template_id,
        async_mode=async_mode,
        idempotency_key=idempotency_key,
    )
    
    try:
        # Check for existing job with same idempotency key
        if idempotency_key:
            job_storage = JobStorage()
            existing_job = await job_storage.get_by_idempotency_key(idempotency_key)
            
            if existing_job:
                logger.info(
                    "idempotent_request_matched",
                    request_id=request_id,
                    existing_job_id=existing_job.job_id,
                    idempotency_key=idempotency_key,
                )
                return GenerateResponse(
                    job_id=existing_job.job_id,
                    status=existing_job.status,
                    message="Existing job returned (idempotent request)",
                    request_id=request_id,
                ).model_dump()
        
        generation_params = {"prompt": prompt, **additional_params}
        template_info = None
        
        # If template is provided, load and apply it
        if template_id:
            template_info = await apply_template_to_request(
                template_id=template_id,
                request_params=generation_params,
            )
            
            # Verify brand_id matches template's brand
            if brand_id != template_info["template_brand_id"]:
                logger.warning(
                    "brand_mismatch",
                    request_id=request_id,
                    request_brand_id=brand_id,
                    template_brand_id=template_info["template_brand_id"],
                )
                raise ValidationError(
                    code="BRAND_MISMATCH",
                    message=f"Brand ID {brand_id} does not match template's brand {template_info['template_brand_id']}",
                    request_id=request_id,
                    details={
                        "request_brand_id": brand_id,
                        "template_brand_id": template_info["template_brand_id"],
                        "template_id": template_id,
                    },
                )
            
            # Use merged parameters from template
            generation_params = template_info["generation_params"]
            logger.info(
                "template_parameters_applied",
                request_id=request_id,
                template_name=template_info["template_name"],
            )
        
        # Verify brand exists
        brand_storage = BrandStorage()
        brand = await brand_storage.get_brand(brand_id)
        if not brand:
            logger.warning("brand_not_found", request_id=request_id, brand_id=brand_id)
            raise NotFoundError(resource="brand", resource_id=brand_id, request_id=request_id)
        
        # Create new job
        job_id = str(uuid.uuid4())
        job = Job(
            job_id=job_id,
            brand_id=brand_id,
            status="pending" if async_mode else "processing",
            progress=0.0,
            state={
                "prompt": prompt,
                "generation_params": generation_params,
                "template_id": template_id,
            },
            webhook_url=webhook_url,
            idempotency_key=idempotency_key,
        )
        
        # Store job in database
        job_storage = JobStorage()
        await job_storage.create_job(job)
        
        logger.info(
            "generation_job_created",
            request_id=request_id,
            job_id=job_id,
            brand_id=brand_id,
            template_used=template_id is not None,
            idempotency_key=idempotency_key,
        )
        
        # TODO: Execute generation workflow in background if async_mode
        
        return GenerateResponse(
            job_id=job_id,
            status=job.status,
            message="Generation job created successfully" + (f" using template {template_info['template_name']}" if template_info else ""),
            request_id=request_id,
        ).model_dump()
        
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error("generation_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="generate",
            request_id=request_id,
            details={"error": str(e)},
        )



# Job Management Handlers

async def get_job_status_handler(job_id: str) -> dict:
    """
    Get job status and results.
    
    Returns current job state including status, progress, and partial results.
    
    Args:
        job_id: Job UUID
        
    Returns:
        JobStatusResponse with job details
        
    Raises:
        NotFoundError: If job does not exist
    """
    from mobius.api.schemas import JobStatusResponse
    
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info("get_job_status_request", request_id=request_id, job_id=job_id)
    
    try:
        job_storage = JobStorage()
        job = await job_storage.get_job(job_id)
        
        if not job:
            logger.warning("job_not_found", request_id=request_id, job_id=job_id)
            raise NotFoundError(resource="job", resource_id=job_id, request_id=request_id)
        
        logger.info("get_job_status_success", request_id=request_id, job_id=job_id, status=job.status)
        
        # Extract current image URL from state if available
        current_image_url = job.state.get("current_image_url") if job.state else None
        compliance_score = job.state.get("compliance_score") if job.state else None
        
        return JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            progress=job.progress,
            current_image_url=current_image_url,
            compliance_score=compliance_score,
            error=job.error,
            created_at=job.created_at,
            updated_at=job.updated_at,
            request_id=request_id,
        ).model_dump()
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("get_job_status_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="get_job_status",
            request_id=request_id,
            details={"error": str(e)},
        )


async def cancel_job_handler(job_id: str) -> dict:
    """
    Cancel a running job.
    
    Sets job status to 'cancelled' and stops further processing.
    
    Args:
        job_id: Job UUID
        
    Returns:
        Dictionary with success message
        
    Raises:
        NotFoundError: If job does not exist
        ValidationError: If job is already completed or failed
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info("cancel_job_request", request_id=request_id, job_id=job_id)
    
    try:
        job_storage = JobStorage()
        job = await job_storage.get_job(job_id)
        
        if not job:
            logger.warning("job_not_found", request_id=request_id, job_id=job_id)
            raise NotFoundError(resource="job", resource_id=job_id, request_id=request_id)
        
        # Check if job can be cancelled
        if job.status in ["completed", "failed", "cancelled"]:
            logger.warning(
                "job_cannot_be_cancelled",
                request_id=request_id,
                job_id=job_id,
                current_status=job.status,
            )
            raise ValidationError(
                code="JOB_CANNOT_BE_CANCELLED",
                message=f"Job with status '{job.status}' cannot be cancelled",
                request_id=request_id,
                details={
                    "job_id": job_id,
                    "current_status": job.status,
                },
            )
        
        # Update job status to cancelled
        await job_storage.update_job(job_id, {"status": "cancelled"})
        
        logger.info("cancel_job_success", request_id=request_id, job_id=job_id)
        
        return {
            "job_id": job_id,
            "status": "cancelled",
            "message": "Job cancelled successfully",
            "request_id": request_id,
        }
        
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error("cancel_job_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="cancel_job",
            request_id=request_id,
            details={"error": str(e)},
        )


# Feedback Handlers

async def submit_feedback_handler(
    asset_id: str,
    action: str,
    reason: Optional[str] = None,
) -> dict:
    """
    Submit feedback for an asset.
    
    Stores feedback event with action (approve/reject) and optional reason.
    The database trigger automatically updates the brand's feedback_count
    and learning_active flag.
    
    Args:
        asset_id: Asset UUID
        action: 'approve' or 'reject'
        reason: Optional reason for rejection
        
    Returns:
        FeedbackResponse with feedback details and updated statistics
        
    Raises:
        NotFoundError: If asset does not exist
        ValidationError: If action is invalid
    """
    from mobius.api.schemas import FeedbackResponse
    from mobius.storage.feedback import FeedbackStorage
    from mobius.storage.assets import AssetStorage
    
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info(
        "submit_feedback_request",
        request_id=request_id,
        asset_id=asset_id,
        action=action,
    )
    
    try:
        # Validate action
        if action not in ["approve", "reject"]:
            logger.warning(
                "invalid_feedback_action",
                request_id=request_id,
                action=action,
            )
            raise ValidationError(
                code="INVALID_ACTION",
                message=f"Action must be 'approve' or 'reject', got '{action}'",
                request_id=request_id,
                details={"action": action},
            )
        
        # Verify asset exists and get brand_id
        asset_storage = AssetStorage()
        asset = await asset_storage.get_asset(asset_id)
        
        if not asset:
            logger.warning("asset_not_found", request_id=request_id, asset_id=asset_id)
            raise NotFoundError(resource="asset", resource_id=asset_id, request_id=request_id)
        
        brand_id = asset.brand_id
        
        # Create feedback
        feedback_storage = FeedbackStorage()
        feedback = await feedback_storage.create_feedback(
            asset_id=asset_id,
            brand_id=brand_id,
            action=action,
            reason=reason,
        )
        
        # Get updated feedback statistics
        stats = await feedback_storage.get_feedback_stats(brand_id)
        
        logger.info(
            "submit_feedback_success",
            request_id=request_id,
            feedback_id=feedback.feedback_id,
            brand_id=brand_id,
            total_feedback=stats["total_feedback"],
            learning_active=stats["learning_active"],
        )
        
        return FeedbackResponse(
            feedback_id=feedback.feedback_id,
            brand_id=brand_id,
            total_feedback_count=stats["total_feedback"],
            learning_active=stats["learning_active"],
            request_id=request_id,
        ).model_dump()
        
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error("submit_feedback_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="submit_feedback",
            request_id=request_id,
            details={"error": str(e)},
        )


async def get_feedback_stats_handler(brand_id: str) -> dict:
    """
    Get feedback statistics for a brand.
    
    Returns total approvals, rejections, and learning_active status.
    
    Args:
        brand_id: Brand UUID
        
    Returns:
        FeedbackStatsResponse with statistics
        
    Raises:
        NotFoundError: If brand does not exist
    """
    from mobius.api.schemas import FeedbackStatsResponse
    from mobius.storage.feedback import FeedbackStorage
    from mobius.storage.brands import BrandStorage
    
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info(
        "get_feedback_stats_request",
        request_id=request_id,
        brand_id=brand_id,
    )
    
    try:
        # Verify brand exists
        brand_storage = BrandStorage()
        brand = await brand_storage.get_brand(brand_id)
        
        if not brand:
            logger.warning("brand_not_found", request_id=request_id, brand_id=brand_id)
            raise NotFoundError(resource="brand", resource_id=brand_id, request_id=request_id)
        
        # Get feedback statistics
        feedback_storage = FeedbackStorage()
        stats = await feedback_storage.get_feedback_stats(brand_id)
        
        logger.info(
            "get_feedback_stats_success",
            request_id=request_id,
            brand_id=brand_id,
            total_feedback=stats["total_feedback"],
            approvals=stats["approvals"],
            rejections=stats["rejections"],
            learning_active=stats["learning_active"],
        )
        
        return FeedbackStatsResponse(
            brand_id=brand_id,
            total_feedback=stats["total_feedback"],
            approvals=stats["approvals"],
            rejections=stats["rejections"],
            learning_active=stats["learning_active"],
            request_id=request_id,
        ).model_dump()
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("get_feedback_stats_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="get_feedback_stats",
            request_id=request_id,
            details={"error": str(e)},
        )



# System Endpoints

async def health_check_handler() -> dict:
    """
    Health check endpoint.
    
    Checks the health of all system components:
    - Database connectivity
    - Storage accessibility
    - API responsiveness
    
    Returns:
        HealthCheckResponse with component statuses
    """
    from mobius.api.schemas import HealthCheckResponse
    from mobius.storage.database import get_supabase_client
    from mobius.constants import BRANDS_BUCKET, ASSETS_BUCKET
    
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info("health_check_request", request_id=request_id)
    
    # Overall status
    overall_status = "healthy"
    
    # Check database
    database_status = "healthy"
    try:
        client = get_supabase_client()
        # Simple query to test database connectivity
        result = client.table("brands").select("brand_id").limit(1).execute()
        logger.debug("database_check_passed", request_id=request_id)
    except Exception as e:
        database_status = "unhealthy"
        overall_status = "degraded"
        logger.error("database_check_failed", request_id=request_id, error=str(e))
    
    # Check storage
    storage_status = "healthy"
    try:
        client = get_supabase_client()
        # Test storage bucket accessibility (list() doesn't take limit parameter)
        client.storage.from_(BRANDS_BUCKET).list()
        client.storage.from_(ASSETS_BUCKET).list()
        logger.debug("storage_check_passed", request_id=request_id)
    except Exception as e:
        storage_status = "unhealthy"
        overall_status = "degraded"
        logger.error("storage_check_failed", request_id=request_id, error=str(e))
    
    # API is healthy if we got here
    api_status = "healthy"
    
    logger.info(
        "health_check_complete",
        request_id=request_id,
        overall_status=overall_status,
        database=database_status,
        storage=storage_status,
        api=api_status,
    )
    
    return HealthCheckResponse(
        status=overall_status,
        database=database_status,
        storage=storage_status,
        api=api_status,
        timestamp=datetime.now(timezone.utc),
        request_id=request_id,
    ).model_dump()


async def get_api_docs_handler() -> dict:
    """
    Get OpenAPI documentation.
    
    Returns OpenAPI specification for all API endpoints.
    
    Returns:
        Dictionary with OpenAPI specification
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info("api_docs_request", request_id=request_id)
    
    # OpenAPI 3.0 specification
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Mobius API",
            "version": "1.0.0",
            "description": "Enterprise brand governance platform with AI-powered compliance",
            "contact": {
                "name": "Mobius Support",
                "url": "https://mobius.example.com/support",
            },
        },
        "servers": [
            {
                "url": "/v1",
                "description": "Version 1 API",
            }
        ],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health check",
                    "description": "Check the health of all system components",
                    "operationId": "healthCheck",
                    "tags": ["System"],
                    "responses": {
                        "200": {
                            "description": "Health check response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HealthCheckResponse"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/docs": {
                "get": {
                    "summary": "API documentation",
                    "description": "Get OpenAPI specification",
                    "operationId": "getApiDocs",
                    "tags": ["System"],
                    "responses": {
                        "200": {
                            "description": "OpenAPI specification",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/brands/ingest": {
                "post": {
                    "summary": "Ingest brand guidelines",
                    "description": "Upload and ingest brand guidelines PDF",
                    "operationId": "ingestBrand",
                    "tags": ["Brands"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "organization_id": {"type": "string"},
                                        "brand_name": {"type": "string"},
                                        "file": {
                                            "type": "string",
                                            "format": "binary",
                                        },
                                    },
                                    "required": ["organization_id", "brand_name", "file"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Brand ingestion response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/IngestBrandResponse"
                                    }
                                }
                            },
                        },
                        "400": {"description": "Invalid PDF file"},
                        "413": {"description": "File too large"},
                        "422": {"description": "Validation error"},
                    },
                }
            },
            "/brands": {
                "get": {
                    "summary": "List brands",
                    "description": "List all brands for an organization",
                    "operationId": "listBrands",
                    "tags": ["Brands"],
                    "parameters": [
                        {
                            "name": "organization_id",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "search",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 100},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Brand list response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/BrandListResponse"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/brands/{brand_id}": {
                "get": {
                    "summary": "Get brand details",
                    "description": "Get detailed brand information",
                    "operationId": "getBrand",
                    "tags": ["Brands"],
                    "parameters": [
                        {
                            "name": "brand_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Brand details",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/BrandDetailResponse"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Brand not found"},
                    },
                },
                "patch": {
                    "summary": "Update brand",
                    "description": "Update brand metadata",
                    "operationId": "updateBrand",
                    "tags": ["Brands"],
                    "parameters": [
                        {
                            "name": "brand_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/UpdateBrandRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Updated brand details",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/BrandDetailResponse"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Brand not found"},
                    },
                },
                "delete": {
                    "summary": "Delete brand",
                    "description": "Soft delete a brand",
                    "operationId": "deleteBrand",
                    "tags": ["Brands"],
                    "parameters": [
                        {
                            "name": "brand_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Brand deleted successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "brand_id": {"type": "string"},
                                            "status": {"type": "string"},
                                            "message": {"type": "string"},
                                            "request_id": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        },
                        "404": {"description": "Brand not found"},
                    },
                },
            },
            "/generate": {
                "post": {
                    "summary": "Generate asset",
                    "description": "Generate brand-compliant asset",
                    "operationId": "generate",
                    "tags": ["Generation"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/GenerateRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Generation response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/GenerateResponse"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Brand or template not found"},
                        "422": {"description": "Validation error"},
                    },
                }
            },
            "/jobs/{job_id}": {
                "get": {
                    "summary": "Get job status",
                    "description": "Get job status and results",
                    "operationId": "getJobStatus",
                    "tags": ["Jobs"],
                    "parameters": [
                        {
                            "name": "job_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Job status",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/JobStatusResponse"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Job not found"},
                    },
                }
            },
            "/jobs/{job_id}/cancel": {
                "post": {
                    "summary": "Cancel job",
                    "description": "Cancel a running job",
                    "operationId": "cancelJob",
                    "tags": ["Jobs"],
                    "parameters": [
                        {
                            "name": "job_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Job cancelled successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "job_id": {"type": "string"},
                                            "status": {"type": "string"},
                                            "message": {"type": "string"},
                                            "request_id": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        },
                        "404": {"description": "Job not found"},
                        "422": {"description": "Job cannot be cancelled"},
                    },
                }
            },
            "/templates": {
                "post": {
                    "summary": "Save template",
                    "description": "Save an asset as a reusable template",
                    "operationId": "saveTemplate",
                    "tags": ["Templates"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SaveTemplateRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Template created",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TemplateResponse"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Asset not found"},
                        "422": {"description": "Compliance score too low"},
                    },
                },
                "get": {
                    "summary": "List templates",
                    "description": "List all templates for a brand",
                    "operationId": "listTemplates",
                    "tags": ["Templates"],
                    "parameters": [
                        {
                            "name": "brand_id",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 100},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Template list",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TemplateListResponse"
                                    }
                                }
                            },
                        }
                    },
                },
            },
            "/templates/{template_id}": {
                "get": {
                    "summary": "Get template",
                    "description": "Get template details",
                    "operationId": "getTemplate",
                    "tags": ["Templates"],
                    "parameters": [
                        {
                            "name": "template_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Template details",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TemplateResponse"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Template not found"},
                    },
                },
                "delete": {
                    "summary": "Delete template",
                    "description": "Delete a template",
                    "operationId": "deleteTemplate",
                    "tags": ["Templates"],
                    "parameters": [
                        {
                            "name": "template_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Template deleted successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "template_id": {"type": "string"},
                                            "status": {"type": "string"},
                                            "message": {"type": "string"},
                                            "request_id": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        },
                        "404": {"description": "Template not found"},
                    },
                },
            },
            "/assets/{asset_id}/feedback": {
                "post": {
                    "summary": "Submit feedback",
                    "description": "Submit approval or rejection feedback for an asset",
                    "operationId": "submitFeedback",
                    "tags": ["Feedback"],
                    "parameters": [
                        {
                            "name": "asset_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SubmitFeedbackRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Feedback submitted",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/FeedbackResponse"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Asset not found"},
                        "422": {"description": "Invalid action"},
                    },
                }
            },
            "/brands/{brand_id}/feedback": {
                "get": {
                    "summary": "Get feedback statistics",
                    "description": "Get feedback statistics for a brand",
                    "operationId": "getFeedbackStats",
                    "tags": ["Feedback"],
                    "parameters": [
                        {
                            "name": "brand_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Feedback statistics",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/FeedbackStatsResponse"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Brand not found"},
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "HealthCheckResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["healthy", "degraded", "unhealthy"]},
                        "database": {"type": "string", "enum": ["healthy", "unhealthy"]},
                        "storage": {"type": "string", "enum": ["healthy", "unhealthy"]},
                        "api": {"type": "string", "enum": ["healthy", "unhealthy"]},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "request_id": {"type": "string"},
                    },
                    "required": ["status", "database", "storage", "api", "timestamp", "request_id"],
                },
                # Additional schemas would be defined here
                # For brevity, referencing the Pydantic models
            },
        },
        "tags": [
            {"name": "System", "description": "System health and documentation"},
            {"name": "Brands", "description": "Brand management operations"},
            {"name": "Generation", "description": "Asset generation operations"},
            {"name": "Jobs", "description": "Job management operations"},
            {"name": "Templates", "description": "Template management operations"},
            {"name": "Feedback", "description": "Feedback operations"},
        ],
    }
    
    logger.info("api_docs_generated", request_id=request_id)
    
    return openapi_spec


# Background Job Cleanup

async def cleanup_expired_jobs() -> dict:
    """
    Cleanup expired jobs and associated temporary files.
    
    This function is designed to be called by a scheduled task (e.g., Modal cron).
    It runs hourly to:
    1. Find all jobs that have expired (> 24 hours old)
    2. Delete temporary files for failed jobs
    3. Remove job records from the database
    
    Returns:
        Dictionary with cleanup statistics
    """
    from mobius.storage.files import FileStorage
    
    logger.info("cleanup_job_started")
    
    try:
        job_storage = JobStorage()
        file_storage = FileStorage()
        
        # Find expired jobs
        expired_jobs = await job_storage.list_expired_jobs(limit=1000)
        
        deleted_count = 0
        files_deleted = 0
        errors = []
        
        for job in expired_jobs:
            job_id = job.job_id
            
            try:
                # Delete any temporary files associated with failed jobs
                # (Successful jobs have assets moved to permanent storage)
                if job.status == "failed":
                    try:
                        await file_storage.delete_file("assets", f"temp/{job_id}")
                        files_deleted += 1
                        logger.debug("temp_file_deleted", job_id=job_id)
                    except Exception as e:
                        # Ignore if file doesn't exist
                        logger.debug("temp_file_not_found", job_id=job_id, error=str(e))
                
                # Delete job record
                await job_storage.delete_job(job_id)
                deleted_count += 1
                logger.debug("job_deleted", job_id=job_id)
                
            except Exception as e:
                error_msg = f"Failed to delete job {job_id}: {str(e)}"
                errors.append(error_msg)
                logger.error("job_deletion_failed", job_id=job_id, error=str(e))
        
        logger.info(
            "cleanup_job_completed",
            deleted_count=deleted_count,
            files_deleted=files_deleted,
            errors_count=len(errors),
        )
        
        return {
            "status": "completed",
            "jobs_deleted": deleted_count,
            "files_deleted": files_deleted,
            "errors": errors,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
    except Exception as e:
        logger.error("cleanup_job_failed", error=str(e))
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Legacy Phase 1 Compatibility Handler

async def legacy_generate_handler(
    prompt: str,
    webhook_url: Optional[str] = None,
) -> dict:
    """
    Legacy Phase 1 endpoint for backward compatibility.
    
    Redirects to v1 API using a default brand.
    
    Args:
        prompt: Generation prompt
        webhook_url: Optional webhook URL
        
    Returns:
        GenerateResponse compatible with Phase 1 format
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.warning(
        "legacy_endpoint_used",
        request_id=request_id,
        message="Please migrate to /v1/generate endpoint",
    )
    
    # Use default brand for legacy requests
    default_brand_id = "default-brand"
    
    # Call the new generate_handler with default brand
    response = await generate_handler(
        brand_id=default_brand_id,
        prompt=prompt,
        webhook_url=webhook_url,
        async_mode=False,
        idempotency_key=None,
    )
    
    logger.info(
        "legacy_request_redirected",
        request_id=request_id,
        job_id=response.get("job_id"),
    )
    
    return response
