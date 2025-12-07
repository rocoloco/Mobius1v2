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
    logo_file: Optional[bytes] = None,
    logo_filename: Optional[str] = None,
) -> IngestBrandResponse:
    """
    Handle brand guidelines PDF ingestion with optional logo upload.

    Validates file size, MIME type, and PDF header before processing.
    Optionally accepts a logo file (PNG with transparency preferred).

    Args:
        organization_id: Organization ID
        brand_name: Brand name
        file: PDF file bytes
        content_type: MIME type from upload
        filename: Original filename
        logo_file: Optional logo image bytes (PNG with transparency preferred)
        logo_filename: Optional logo filename

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

    # Check for existing brand with same name (deduplication)
    brand_storage = BrandStorage()
    existing_brands = await brand_storage.list_brands(
        organization_id=organization_id,
        search=brand_name,
        limit=10
    )
    
    # Check for exact name match
    existing_brand = next(
        (b for b in existing_brands if b.name.lower() == brand_name.lower()),
        None
    )
    
    if existing_brand:
        logger.warning(
            "duplicate_brand_detected",
            request_id=request_id,
            brand_name=brand_name,
            existing_brand_id=existing_brand.brand_id
        )
        raise ValidationError(
            code="DUPLICATE_BRAND",
            message=f"A brand named '{brand_name}' already exists for this organization",
            request_id=request_id,
            details={
                "existing_brand_id": existing_brand.brand_id,
                "brand_name": brand_name,
            }
        )
    
    # Parse PDF to extract brand guidelines
    from mobius.ingestion.pdf_parser import PDFParser
    from mobius.models.brand import Brand
    from mobius.storage.files import FileStorage
    import uuid
    
    brand_id = str(uuid.uuid4())
    
    # Parse PDF into Digital Twin
    parser = PDFParser()
    logo_images = []
    try:
        guidelines, logo_images = await parser.parse_pdf(file, filename)
        logger.info("pdf_parsed", request_id=request_id, brand_id=brand_id, logo_count=len(logo_images))
        needs_review = []
    except Exception as e:
        logger.error("pdf_parsing_failed", request_id=request_id, error=str(e))
        # Fall back to empty guidelines if parsing fails
        from mobius.models.brand import BrandGuidelines
        guidelines = BrandGuidelines(
            colors=[],
            typography=[],
            logos=[],
            voice=None,
            rules=[],
            source_filename=filename,
        )
        needs_review = [f"PDF parsing failed: {str(e)}"]
    
    # Upload PDF to storage
    file_storage = FileStorage()
    
    try:
        pdf_url = await file_storage.upload_pdf(
            file=file,
            brand_id=brand_id,
            filename=filename,
        )
        logger.info("pdf_uploaded", request_id=request_id, brand_id=brand_id, pdf_url=pdf_url)
    except Exception as e:
        logger.error("pdf_upload_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="upload_pdf",
            request_id=request_id,
            details={"error": str(e)},
        )
    
    # Upload logo - prioritize manually uploaded logo over extracted
    logo_thumbnail_url = None
    
    if logo_file:
        # User provided a logo file - use this (highest quality)
        try:
            # Validate logo file
            if len(logo_file) > 10 * 1024 * 1024:  # 10MB max for logo
                logger.warning("logo_file_too_large", request_id=request_id, size_mb=len(logo_file) / 1024 / 1024)
                needs_review.append("Logo file too large (max 10MB)")
            else:
                # Determine filename
                logo_name = logo_filename or "logo.png"
                
                logo_thumbnail_url = await file_storage.upload_logo(
                    file=logo_file,
                    brand_id=brand_id,
                    filename=logo_name,
                )
                logger.info("manual_logo_uploaded", request_id=request_id, brand_id=brand_id, logo_url=logo_thumbnail_url)
        except Exception as e:
            logger.error("manual_logo_upload_failed", request_id=request_id, error=str(e))
            needs_review.append(f"Logo upload failed: {str(e)}")
    
    elif logo_images:
        # Fallback: Use extracted logo from PDF
        try:
            logo_thumbnail_url = await file_storage.upload_logo(
                file=logo_images[0],
                brand_id=brand_id,
                filename="logo_extracted.png",
            )
            logger.info("extracted_logo_uploaded", request_id=request_id, brand_id=brand_id, logo_url=logo_thumbnail_url)
        except Exception as e:
            logger.warning("extracted_logo_upload_failed", request_id=request_id, error=str(e))
            needs_review.append("Logo extraction/upload failed")
    
    else:
        # No logo provided or extracted
        logger.info("no_logo_available", request_id=request_id, brand_id=brand_id)
        needs_review.append("No logo provided - upload logo for best generation results")
    
    # Update logo URLs in guidelines if logo was uploaded
    if logo_thumbnail_url and guidelines.logos:
        # Update the first logo rule with the actual uploaded URL
        for logo in guidelines.logos:
            if not logo.url or logo.url == "":
                logo.url = logo_thumbnail_url
                logger.info(
                    "logo_url_updated",
                    request_id=request_id,
                    brand_id=brand_id,
                    logo_variant=logo.variant_name,
                    logo_url=logo_thumbnail_url
                )
                break
    elif logo_thumbnail_url and not guidelines.logos:
        # No logos in guidelines, create a default one
        from mobius.models.brand import LogoRule
        default_logo = LogoRule(
            variant_name="Primary Logo",
            url=logo_thumbnail_url,
            min_width_px=150,
            clear_space_ratio=0.1,
            forbidden_backgrounds=["#FFFFFF", "#000000"]
        )
        guidelines.logos.append(default_logo)
        logger.info(
            "default_logo_created",
            request_id=request_id,
            brand_id=brand_id,
            logo_url=logo_thumbnail_url
        )
    
    # Create compressed twin from guidelines for efficient generation
    from mobius.models.brand import CompressedDigitalTwin
    from datetime import datetime, timezone
    
    compressed_twin = CompressedDigitalTwin(
        primary_colors=[c.hex for c in guidelines.colors if c.usage == "primary"],
        secondary_colors=[c.hex for c in guidelines.colors if c.usage == "secondary"],
        accent_colors=[c.hex for c in guidelines.colors if c.usage == "accent"],
        neutral_colors=[c.hex for c in guidelines.colors if c.usage == "neutral"],
        semantic_colors=[c.hex for c in guidelines.colors if c.usage == "semantic"],
        font_families=[t.family for t in guidelines.typography],
        visual_dos=[r.instruction for r in guidelines.rules if r.category == "visual" and not r.negative_constraint][:20],
        visual_donts=[r.instruction for r in guidelines.rules if r.category == "visual" and r.negative_constraint][:20],
    )
    
    logger.info(
        "compressed_twin_created",
        request_id=request_id,
        brand_id=brand_id,
        token_estimate=compressed_twin.estimate_tokens(),
        primary_colors=len(compressed_twin.primary_colors),
        secondary_colors=len(compressed_twin.secondary_colors),
        accent_colors=len(compressed_twin.accent_colors),
    )
    
    now = datetime.now(timezone.utc).isoformat()
    
    brand = Brand(
        brand_id=brand_id,
        organization_id=organization_id,
        name=brand_name,
        guidelines=guidelines,
        compressed_twin=compressed_twin,
        pdf_url=pdf_url,
        logo_thumbnail_url=logo_thumbnail_url,
        needs_review=needs_review,
        learning_active=False,
        feedback_count=0,
        created_at=now,
        updated_at=now,
    )
    
    # Save to database (brand_storage already initialized above for deduplication check)
    try:
        created_brand = await brand_storage.create_brand(brand)
        logger.info("brand_created", request_id=request_id, brand_id=brand_id)
    except Exception as e:
        logger.error("brand_creation_failed", request_id=request_id, error=str(e))
        raise StorageError(
            operation="create_brand",
            request_id=request_id,
            details={"error": str(e)},
        )
    
    return IngestBrandResponse(
        brand_id=brand_id,
        status="created",
        pdf_url=pdf_url,
        needs_review=brand.needs_review,
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

        # If logo_thumbnail_url is being updated, sync it to guidelines.logos
        if "logo_thumbnail_url" in update_dict and update_dict["logo_thumbnail_url"]:
            new_logo_url = update_dict["logo_thumbnail_url"]
            
            # Update existing logo URLs in guidelines
            if brand.guidelines and brand.guidelines.logos:
                for logo in brand.guidelines.logos:
                    if not logo.url or logo.url == "":
                        logo.url = new_logo_url
                        logger.info(
                            "logo_url_synced",
                            request_id=request_id,
                            brand_id=brand_id,
                            logo_variant=logo.variant_name,
                            logo_url=new_logo_url
                        )
                        break
                # Update guidelines in the update dict
                update_dict["guidelines"] = brand.guidelines.model_dump()
            elif brand.guidelines:
                # No logos in guidelines, create a default one
                from mobius.models.brand import LogoRule
                default_logo = LogoRule(
                    variant_name="Primary Logo",
                    url=new_logo_url,
                    min_width_px=150,
                    clear_space_ratio=0.1,
                    forbidden_backgrounds=["#FFFFFF", "#000000"]
                )
                brand.guidelines.logos.append(default_logo)
                update_dict["guidelines"] = brand.guidelines.model_dump()
                logger.info(
                    "default_logo_created_on_update",
                    request_id=request_id,
                    brand_id=brand_id,
                    logo_url=new_logo_url
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
        
        # Execute generation workflow
        from mobius.graphs.generation import run_generation_workflow
        
        if async_mode:
            # TODO: Run in background task
            logger.warning("async_mode_not_implemented", request_id=request_id)
            # For now, run synchronously
            final_state = await run_generation_workflow(
                brand_id=brand_id,
                prompt=prompt,
                job_id=job_id,
            )
        else:
            # Run synchronously
            final_state = await run_generation_workflow(
                brand_id=brand_id,
                prompt=prompt,
                job_id=job_id,
            )
        
        # Update job with final state
        image_url = final_state.get("current_image_url") or final_state.get("image_uri")

        updates = {
            "status": final_state.get("status", "completed"),
            "progress": 100.0,
            "state": {
                "prompt": prompt,
                "generation_params": generation_params,
                "template_id": template_id,
                "compliance_scores": final_state.get("compliance_scores", []),
                "is_approved": final_state.get("is_approved", False),
                "attempt_count": final_state.get("attempt_count", 0),
                "image_uri": image_url,  # Store image in state
            },
        }

        await job_storage.update_job(job_id, updates)

        final_status = updates["status"]

        logger.info(
            "generation_workflow_completed",
            request_id=request_id,
            job_id=job_id,
            final_status=final_status,
        )

        return GenerateResponse(
            job_id=job_id,
            status=final_status,
            message="Generation completed successfully" + (f" using template {template_info['template_name']}" if template_info else ""),
            image_url=image_url,  # Include the image URL in sync response
            compliance_score=final_state.get("compliance_scores", [{}])[-1].get("overall_score") if final_state.get("compliance_scores") else None,
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
        current_image_url = None
        if job.state:
            current_image_url = job.state.get("image_uri") or job.state.get("current_image_url")

        # Extract compliance scores from state
        compliance_scores = job.state.get("compliance_scores", []) if job.state else []
        # Calculate overall score if available
        compliance_score = None
        if compliance_scores:
            compliance_score = compliance_scores[-1].get("overall_score") if compliance_scores[-1] else None
        
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
    
    Returns OpenAPI specification for all API endpoints with comprehensive
    error codes, retry behavior, and rate limiting guidance.
    
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
            "description": """
# Mobius API Documentation

Enterprise brand governance platform with AI-powered compliance using Google's Gemini 3 model family.

## Architecture

Mobius uses a dual-model architecture:
- **Reasoning Model** (gemini-3-pro-preview): PDF parsing and compliance auditing
- **Vision Model** (gemini-3-pro-image-preview): Image generation

## Rate Limiting

API requests are subject to rate limits:
- **Ingestion**: 10 requests/minute per organization
- **Generation**: 30 requests/minute per brand
- **Other endpoints**: 100 requests/minute per API key

When rate limits are exceeded, the API returns HTTP 429 with a `Retry-After` header indicating seconds to wait.

## Retry Behavior

The API implements automatic retries for transient failures:
- **Image Generation**: Up to 3 attempts with exponential backoff (1s, 2s, 4s)
- **Compliance Auditing**: Up to 2 attempts with 2s delay
- **PDF Processing**: Single attempt (large files, no retry)

Clients should implement their own retry logic for 5xx errors with exponential backoff.

## Error Handling

All errors follow a consistent structure with:
- HTTP status code
- Error code (for programmatic handling)
- Human-readable message
- Request ID (for tracing)
- Optional details dictionary

See the Error Codes section below for complete error documentation.

## Authentication

API requests require authentication via API key:
```
Authorization: Bearer YOUR_API_KEY
```

## Idempotency

Generation requests support idempotency keys to prevent duplicate job creation:
```json
{
  "brand_id": "brand-123",
  "prompt": "Create a social post",
  "idempotency_key": "client-request-456"
}
```

If a job with the same idempotency key exists and is not expired, the API returns the existing job.

## Webhooks

Async jobs support webhook notifications on completion:
```json
{
  "brand_id": "brand-123",
  "prompt": "Create a social post",
  "async_mode": true,
  "webhook_url": "https://your-app.com/webhook"
}
```

Webhook payload includes job status, image URL, and compliance score.
            """,
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
                    "description": """
Upload and ingest brand guidelines PDF.

The system uses the Reasoning Model (gemini-3-pro-preview) to extract:
- Color palette with semantic roles (primary, secondary, accent, neutral, semantic)
- Typography rules
- Logo usage guidelines
- Visual dos and don'ts

The extracted guidelines are stored as both:
1. Full Brand Guidelines (for compliance auditing)
2. Compressed Digital Twin (optimized for image generation, <60k tokens)

**File Requirements:**
- Format: PDF only
- Max size: 50MB
- Must have valid PDF header

**Processing Time:**
- Small PDFs (<5MB): 10-30 seconds
- Large PDFs (>20MB): 60-120 seconds

**Retry Behavior:**
- No automatic retries (large file processing)
- Client should not retry on 5xx errors without investigation
                    """,
                    "operationId": "ingestBrand",
                    "tags": ["Brands"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "organization_id": {
                                            "type": "string",
                                            "description": "Organization ID",
                                            "example": "org-123",
                                        },
                                        "brand_name": {
                                            "type": "string",
                                            "description": "Brand name (must be unique within organization)",
                                            "example": "Acme Corp",
                                        },
                                        "file": {
                                            "type": "string",
                                            "format": "binary",
                                            "description": "Brand guidelines PDF file",
                                        },
                                    },
                                    "required": ["organization_id", "brand_name", "file"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Brand ingestion successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/IngestBrandResponse"
                                    }
                                }
                            },
                        },
                        "400": {"$ref": "#/components/responses/400BadRequest"},
                        "413": {"$ref": "#/components/responses/413PayloadTooLarge"},
                        "422": {"$ref": "#/components/responses/422UnprocessableEntity"},
                        "429": {"$ref": "#/components/responses/429TooManyRequests"},
                        "500": {"$ref": "#/components/responses/500InternalServerError"},
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
                    "summary": "Generate brand-compliant asset",
                    "description": """
Generate a brand-compliant image using the Vision Model (gemini-3-pro-image-preview).

**Workflow:**
1. Load brand's Compressed Digital Twin (<60k tokens)
2. Inject compressed guidelines into Vision Model system prompt
3. Generate image with brand constraints
4. Audit compliance using Reasoning Model with full guidelines
5. Retry up to 3 times if compliance score < 80%

**Generation Time:**
- Typical: 15-30 seconds
- With retries: 45-90 seconds

**Retry Behavior:**
- Automatic: Up to 3 attempts with exponential backoff (1s, 2s, 4s)
- Client retry: Recommended for 5xx errors with exponential backoff

**Async Mode:**
- Set `async_mode: true` to return immediately with job_id
- Poll `/jobs/{job_id}` for status
- Or provide `webhook_url` for completion notification

**Idempotency:**
- Use `idempotency_key` to prevent duplicate job creation
- If job with same key exists and is not expired, returns existing job
- Keys expire after 24 hours
                    """,
                    "operationId": "generate",
                    "tags": ["Generation"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/GenerateRequest"
                                },
                                "examples": {
                                    "basic": {
                                        "summary": "Basic generation",
                                        "value": {
                                            "brand_id": "brand-123",
                                            "prompt": "Create a social media post announcing our new product launch",
                                        },
                                    },
                                    "with_template": {
                                        "summary": "Using a template",
                                        "value": {
                                            "brand_id": "brand-123",
                                            "prompt": "Announce Q4 earnings with celebratory tone",
                                            "template_id": "template-456",
                                        },
                                    },
                                    "async_with_webhook": {
                                        "summary": "Async with webhook",
                                        "value": {
                                            "brand_id": "brand-123",
                                            "prompt": "Create a hero banner for homepage",
                                            "async_mode": True,
                                            "webhook_url": "https://your-app.com/webhook",
                                            "idempotency_key": "client-request-789",
                                        },
                                    },
                                },
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Generation initiated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/GenerateResponse"
                                    },
                                    "examples": {
                                        "sync_completed": {
                                            "summary": "Synchronous completion",
                                            "value": {
                                                "job_id": "job-789",
                                                "status": "completed",
                                                "message": "Generation completed successfully",
                                                "image_url": "https://cdn.example.com/assets/image-123.png",
                                                "compliance_score": 92.5,
                                                "request_id": "req_gen_123",
                                            },
                                        },
                                        "async_pending": {
                                            "summary": "Async pending",
                                            "value": {
                                                "job_id": "job-789",
                                                "status": "pending",
                                                "message": "Job created successfully. Poll /jobs/{job_id} for status.",
                                                "request_id": "req_gen_123",
                                            },
                                        },
                                    },
                                }
                            },
                        },
                        "404": {"$ref": "#/components/responses/404NotFound"},
                        "422": {"$ref": "#/components/responses/422UnprocessableEntity"},
                        "429": {"$ref": "#/components/responses/429TooManyRequests"},
                        "500": {"$ref": "#/components/responses/500InternalServerError"},
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
                "ErrorResponse": {
                    "type": "object",
                    "description": "Standard error response format",
                    "properties": {
                        "error": {
                            "type": "object",
                            "properties": {
                                "code": {
                                    "type": "string",
                                    "description": "Machine-readable error code",
                                    "enum": [
                                        "FILE_TOO_LARGE",
                                        "INVALID_FILE_TYPE",
                                        "INVALID_PDF",
                                        "DUPLICATE_BRAND",
                                        "BRAND_NOT_FOUND",
                                        "TEMPLATE_NOT_FOUND",
                                        "ASSET_NOT_FOUND",
                                        "JOB_NOT_FOUND",
                                        "COMPLIANCE_SCORE_TOO_LOW",
                                        "STORAGE_ERROR",
                                        "GENERATION_FAILED",
                                        "AUDIT_FAILED",
                                        "RATE_LIMIT_EXCEEDED",
                                        "INVALID_API_KEY",
                                        "INTERNAL_ERROR",
                                    ],
                                },
                                "message": {
                                    "type": "string",
                                    "description": "Human-readable error message",
                                },
                                "details": {
                                    "type": "object",
                                    "description": "Additional error context",
                                    "additionalProperties": True,
                                },
                                "request_id": {
                                    "type": "string",
                                    "description": "Request ID for tracing",
                                },
                            },
                            "required": ["code", "message", "request_id"],
                        }
                    },
                    "required": ["error"],
                    "example": {
                        "error": {
                            "code": "FILE_TOO_LARGE",
                            "message": "PDF exceeds maximum size of 50MB. Received: 75.3MB",
                            "details": {
                                "max_size_mb": 50,
                                "received_size_mb": 75.3,
                            },
                            "request_id": "req_abc123",
                        }
                    },
                },
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
                    "example": {
                        "status": "healthy",
                        "database": "healthy",
                        "storage": "healthy",
                        "api": "healthy",
                        "timestamp": "2025-12-06T10:30:00Z",
                        "request_id": "req_health_123",
                    },
                },
                "GenerateRequest": {
                    "type": "object",
                    "required": ["brand_id", "prompt"],
                    "properties": {
                        "brand_id": {
                            "type": "string",
                            "description": "Brand ID to use for generation",
                            "example": "brand-123",
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Generation prompt describing the desired asset",
                            "example": "Create a social media post announcing our new product launch with vibrant colors",
                        },
                        "template_id": {
                            "type": "string",
                            "description": "Optional template ID to use as a starting point",
                            "example": "template-456",
                        },
                        "webhook_url": {
                            "type": "string",
                            "format": "uri",
                            "description": "Webhook URL for async completion notifications",
                            "example": "https://your-app.com/webhook",
                        },
                        "async_mode": {
                            "type": "boolean",
                            "default": False,
                            "description": "Whether to run asynchronously (returns immediately with job_id)",
                        },
                        "idempotency_key": {
                            "type": "string",
                            "maxLength": 64,
                            "description": "Client-provided key to prevent duplicate job creation",
                            "example": "client-request-456",
                        },
                    },
                },
                "GenerateResponse": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                            "description": "Unique job identifier",
                            "example": "job-789",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "processing", "completed", "failed"],
                            "description": "Current job status",
                        },
                        "message": {
                            "type": "string",
                            "description": "Status message",
                            "example": "Job created successfully",
                        },
                        "image_url": {
                            "type": "string",
                            "format": "uri",
                            "description": "Generated image URL (only present when status=completed)",
                            "example": "https://cdn.example.com/assets/image-123.png",
                        },
                        "compliance_score": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "Brand compliance score (0-100, only present when status=completed)",
                            "example": 92.5,
                        },
                        "request_id": {
                            "type": "string",
                            "description": "Request ID for tracing",
                            "example": "req_gen_123",
                        },
                    },
                    "required": ["job_id", "status", "message", "request_id"],
                },
                "IngestBrandResponse": {
                    "type": "object",
                    "properties": {
                        "brand_id": {
                            "type": "string",
                            "description": "Unique brand identifier",
                            "example": "brand-123",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["created", "processing"],
                            "description": "Ingestion status",
                        },
                        "pdf_url": {
                            "type": "string",
                            "format": "uri",
                            "description": "URL of uploaded PDF",
                            "example": "https://cdn.example.com/brands/brand-123/guidelines.pdf",
                        },
                        "needs_review": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of items requiring manual review",
                            "example": ["No logo provided - upload logo for best generation results"],
                        },
                        "request_id": {
                            "type": "string",
                            "description": "Request ID for tracing",
                            "example": "req_ingest_123",
                        },
                    },
                    "required": ["brand_id", "status", "pdf_url", "needs_review", "request_id"],
                },
                "BrandListResponse": {
                    "type": "object",
                    "properties": {
                        "brands": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/BrandListItem"},
                        },
                        "total": {
                            "type": "integer",
                            "description": "Total number of brands",
                        },
                        "request_id": {"type": "string"},
                    },
                    "required": ["brands", "total", "request_id"],
                },
                "BrandListItem": {
                    "type": "object",
                    "properties": {
                        "brand_id": {"type": "string", "example": "brand-123"},
                        "name": {"type": "string", "example": "Acme Corp"},
                        "logo_thumbnail_url": {
                            "type": "string",
                            "format": "uri",
                            "example": "https://cdn.example.com/logos/brand-123.png",
                        },
                        "asset_count": {
                            "type": "integer",
                            "description": "Number of generated assets",
                            "example": 42,
                        },
                        "avg_compliance_score": {
                            "type": "number",
                            "description": "Average compliance score across all assets",
                            "example": 88.5,
                        },
                        "last_activity": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Timestamp of last activity",
                        },
                    },
                },
                "BrandDetailResponse": {
                    "type": "object",
                    "properties": {
                        "brand_id": {"type": "string"},
                        "organization_id": {"type": "string"},
                        "name": {"type": "string"},
                        "guidelines": {
                            "type": "object",
                            "description": "Structured brand guidelines extracted from PDF",
                            "properties": {
                                "colors": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string", "example": "Primary Blue"},
                                            "hex": {"type": "string", "example": "#0057B8"},
                                            "usage": {
                                                "type": "string",
                                                "enum": ["primary", "secondary", "accent", "neutral", "semantic"],
                                                "description": "Semantic color role",
                                            },
                                        },
                                    },
                                },
                                "typography": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "family": {"type": "string", "example": "Helvetica Neue"},
                                            "usage": {"type": "string", "example": "headings"},
                                        },
                                    },
                                },
                                "logos": {"type": "array", "items": {"type": "object"}},
                                "voice": {"type": "object"},
                                "rules": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                        "pdf_url": {"type": "string", "format": "uri"},
                        "logo_thumbnail_url": {"type": "string", "format": "uri"},
                        "needs_review": {"type": "array", "items": {"type": "string"}},
                        "learning_active": {
                            "type": "boolean",
                            "description": "Whether learning is enabled for this brand",
                        },
                        "feedback_count": {
                            "type": "integer",
                            "description": "Total feedback submissions",
                        },
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"},
                        "request_id": {"type": "string"},
                    },
                },
                "UpdateBrandRequest": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Updated brand name",
                        },
                        "logo_thumbnail_url": {
                            "type": "string",
                            "format": "uri",
                            "description": "Updated logo URL",
                        },
                    },
                },
                "SaveTemplateRequest": {
                    "type": "object",
                    "required": ["asset_id", "template_name", "description"],
                    "properties": {
                        "asset_id": {
                            "type": "string",
                            "description": "Asset ID to create template from (must have compliance score >= 95%)",
                            "example": "asset-789",
                        },
                        "template_name": {
                            "type": "string",
                            "description": "Template name",
                            "example": "Social Media Post - Product Launch",
                        },
                        "description": {
                            "type": "string",
                            "description": "Template description",
                            "example": "High-performing template for product launch announcements",
                        },
                    },
                },
                "TemplateResponse": {
                    "type": "object",
                    "properties": {
                        "template_id": {"type": "string"},
                        "brand_id": {"type": "string"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "generation_params": {
                            "type": "object",
                            "description": "Generation parameters from source asset",
                        },
                        "thumbnail_url": {"type": "string", "format": "uri"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "request_id": {"type": "string"},
                    },
                },
                "TemplateListResponse": {
                    "type": "object",
                    "properties": {
                        "templates": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/TemplateResponse"},
                        },
                        "total": {"type": "integer"},
                        "request_id": {"type": "string"},
                    },
                },
                "SubmitFeedbackRequest": {
                    "type": "object",
                    "required": ["asset_id", "action"],
                    "properties": {
                        "asset_id": {"type": "string"},
                        "action": {
                            "type": "string",
                            "enum": ["approve", "reject"],
                            "description": "Feedback action",
                        },
                        "reason": {
                            "type": "string",
                            "description": "Optional reason for rejection",
                        },
                    },
                },
                "FeedbackResponse": {
                    "type": "object",
                    "properties": {
                        "feedback_id": {"type": "string"},
                        "brand_id": {"type": "string"},
                        "total_feedback_count": {
                            "type": "integer",
                            "description": "Total feedback count for brand",
                        },
                        "learning_active": {
                            "type": "boolean",
                            "description": "Whether learning was activated by this feedback",
                        },
                        "request_id": {"type": "string"},
                    },
                },
                "FeedbackStatsResponse": {
                    "type": "object",
                    "properties": {
                        "brand_id": {"type": "string"},
                        "total_approvals": {"type": "integer"},
                        "total_rejections": {"type": "integer"},
                        "learning_active": {"type": "boolean"},
                        "request_id": {"type": "string"},
                    },
                },
                "JobStatusResponse": {
                    "type": "object",
                    "properties": {
                        "job_id": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["pending", "processing", "completed", "failed", "cancelled"],
                        },
                        "progress": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "Job progress percentage",
                        },
                        "current_image_url": {
                            "type": "string",
                            "format": "uri",
                            "description": "Current generated image URL",
                        },
                        "compliance_score": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "Compliance score (0-100)",
                        },
                        "error": {
                            "type": "string",
                            "description": "Error message if status=failed",
                        },
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"},
                        "request_id": {"type": "string"},
                    },
                },
            },
            "responses": {
                "400BadRequest": {
                    "description": "Bad Request - Invalid input",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            "example": {
                                "error": {
                                    "code": "INVALID_FILE_TYPE",
                                    "message": "Only PDF files are accepted. Received: image/png",
                                    "request_id": "req_abc123",
                                }
                            },
                        }
                    },
                },
                "401Unauthorized": {
                    "description": "Unauthorized - Invalid or missing API key",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            "example": {
                                "error": {
                                    "code": "INVALID_API_KEY",
                                    "message": "API key is invalid or expired",
                                    "request_id": "req_abc123",
                                }
                            },
                        }
                    },
                },
                "404NotFound": {
                    "description": "Not Found - Resource does not exist",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            "example": {
                                "error": {
                                    "code": "BRAND_NOT_FOUND",
                                    "message": "brand with ID brand-123 does not exist",
                                    "request_id": "req_abc123",
                                }
                            },
                        }
                    },
                },
                "413PayloadTooLarge": {
                    "description": "Payload Too Large - File exceeds size limit",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            "example": {
                                "error": {
                                    "code": "FILE_TOO_LARGE",
                                    "message": "PDF exceeds maximum size of 50MB. Received: 75.3MB",
                                    "details": {
                                        "max_size_mb": 50,
                                        "received_size_mb": 75.3,
                                    },
                                    "request_id": "req_abc123",
                                }
                            },
                        }
                    },
                },
                "422UnprocessableEntity": {
                    "description": "Unprocessable Entity - Validation error",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            "example": {
                                "error": {
                                    "code": "COMPLIANCE_SCORE_TOO_LOW",
                                    "message": "Asset compliance score (85%) is below the required threshold (95%) for template creation",
                                    "details": {
                                        "asset_id": "asset-789",
                                        "compliance_score": 85,
                                        "required_threshold": 95,
                                    },
                                    "request_id": "req_abc123",
                                }
                            },
                        }
                    },
                },
                "429TooManyRequests": {
                    "description": "Too Many Requests - Rate limit exceeded",
                    "headers": {
                        "Retry-After": {
                            "description": "Seconds to wait before retrying",
                            "schema": {"type": "integer"},
                        }
                    },
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            "example": {
                                "error": {
                                    "code": "RATE_LIMIT_EXCEEDED",
                                    "message": "Rate limit exceeded. Please retry after 60 seconds.",
                                    "details": {
                                        "retry_after_seconds": 60,
                                        "limit": "30 requests/minute",
                                    },
                                    "request_id": "req_abc123",
                                }
                            },
                        }
                    },
                },
                "500InternalServerError": {
                    "description": "Internal Server Error - Unexpected error occurred",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            "example": {
                                "error": {
                                    "code": "GENERATION_FAILED",
                                    "message": "Image generation failed after 3 retry attempts",
                                    "details": {
                                        "attempts": 3,
                                        "last_error": "Gemini API timeout",
                                    },
                                    "request_id": "req_abc123",
                                }
                            },
                        }
                    },
                },
            },
        },
        "tags": [
            {
                "name": "System",
                "description": "System health and documentation",
            },
            {
                "name": "Brands",
                "description": """
Brand management operations including ingestion, listing, and updates.

**Key Operations:**
- Ingest brand guidelines from PDF
- List brands with statistics
- Get detailed brand information
- Update brand metadata
- Soft delete brands
                """,
            },
            {
                "name": "Generation",
                "description": """
Asset generation operations using Gemini 3 Vision Model.

**Architecture:**
- Vision Model (gemini-3-pro-image-preview) for image generation
- Compressed Digital Twin (<60k tokens) injected into system prompt
- Reasoning Model (gemini-3-pro-preview) for compliance auditing
- Automatic retry with correction loop (up to 3 attempts)

**Performance:**
- Typical generation: 15-30 seconds
- With retries: 45-90 seconds
- Async mode available for long-running jobs
                """,
            },
            {
                "name": "Jobs",
                "description": """
Job management operations for async generation.

**Job Lifecycle:**
1. pending: Job created, waiting to start
2. processing: Generation in progress
3. completed: Generation successful
4. failed: Generation failed after retries
5. cancelled: Job cancelled by user

**Job Expiration:**
- Jobs expire after 24 hours
- Expired jobs are automatically cleaned up
- Use idempotency keys to prevent duplicates
                """,
            },
            {
                "name": "Templates",
                "description": """
Template management operations.

**Requirements:**
- Only assets with compliance score >= 95% can be saved as templates
- Templates capture generation parameters for reuse
- Templates are brand-specific

**Use Cases:**
- Save high-performing assets as templates
- Reuse successful generation patterns
- Maintain consistency across campaigns
                """,
            },
            {
                "name": "Feedback",
                "description": """
Feedback operations for learning system.

**Learning Activation:**
- Requires 10+ feedback submissions
- Enables privacy-preserving pattern learning
- Improves future generation quality

**Privacy Tiers:**
- off: No learning
- private: Brand-specific learning only
- shared: Anonymized cross-brand learning
                """,
            },
        ],
        "x-error-codes": {
            "description": "Complete error code reference",
            "codes": {
                "FILE_TOO_LARGE": {
                    "http_status": 413,
                    "description": "PDF exceeds 50MB size limit",
                    "retry": "No - reduce file size",
                    "example": "PDF exceeds maximum size of 50MB. Received: 75.3MB",
                },
                "INVALID_FILE_TYPE": {
                    "http_status": 400,
                    "description": "File is not a PDF",
                    "retry": "No - upload PDF file",
                    "example": "Only PDF files are accepted. Received: image/png",
                },
                "INVALID_PDF": {
                    "http_status": 400,
                    "description": "File does not have valid PDF header",
                    "retry": "No - upload valid PDF",
                    "example": "File does not appear to be a valid PDF",
                },
                "DUPLICATE_BRAND": {
                    "http_status": 422,
                    "description": "Brand name already exists in organization",
                    "retry": "No - use different name or update existing brand",
                    "example": "A brand named 'Acme Corp' already exists for this organization",
                },
                "BRAND_NOT_FOUND": {
                    "http_status": 404,
                    "description": "Brand does not exist",
                    "retry": "No - verify brand_id",
                    "example": "brand with ID brand-123 does not exist",
                },
                "TEMPLATE_NOT_FOUND": {
                    "http_status": 404,
                    "description": "Template does not exist",
                    "retry": "No - verify template_id",
                    "example": "template with ID template-456 does not exist",
                },
                "ASSET_NOT_FOUND": {
                    "http_status": 404,
                    "description": "Asset does not exist",
                    "retry": "No - verify asset_id",
                    "example": "asset with ID asset-789 does not exist",
                },
                "JOB_NOT_FOUND": {
                    "http_status": 404,
                    "description": "Job does not exist or has expired",
                    "retry": "No - verify job_id or create new job",
                    "example": "job with ID job-123 does not exist",
                },
                "COMPLIANCE_SCORE_TOO_LOW": {
                    "http_status": 422,
                    "description": "Asset compliance score below required threshold for template creation (95%)",
                    "retry": "No - improve asset quality or use different asset",
                    "example": "Asset compliance score (85%) is below the required threshold (95%) for template creation",
                },
                "STORAGE_ERROR": {
                    "http_status": 500,
                    "description": "File storage or database operation failed",
                    "retry": "Yes - exponential backoff recommended",
                    "example": "Storage operation failed: upload_pdf",
                },
                "GENERATION_FAILED": {
                    "http_status": 500,
                    "description": "Image generation failed after automatic retries",
                    "retry": "Yes - after delay, or adjust prompt",
                    "example": "Image generation failed after 3 retry attempts",
                },
                "AUDIT_FAILED": {
                    "http_status": 500,
                    "description": "Compliance audit failed",
                    "retry": "Yes - exponential backoff recommended",
                    "example": "Compliance audit failed: Gemini API timeout",
                },
                "RATE_LIMIT_EXCEEDED": {
                    "http_status": 429,
                    "description": "API rate limit exceeded",
                    "retry": "Yes - wait for Retry-After seconds",
                    "example": "Rate limit exceeded. Please retry after 60 seconds.",
                },
                "INVALID_API_KEY": {
                    "http_status": 401,
                    "description": "API key is invalid or expired",
                    "retry": "No - verify API key",
                    "example": "API key is invalid or expired",
                },
                "INTERNAL_ERROR": {
                    "http_status": 500,
                    "description": "Unexpected internal error",
                    "retry": "Yes - exponential backoff recommended",
                    "example": "An unexpected error occurred",
                },
            },
        },
        "x-retry-guidance": {
            "description": "Retry behavior guidance for API clients",
            "automatic_retries": {
                "image_generation": {
                    "max_attempts": 3,
                    "backoff": "exponential (1s, 2s, 4s)",
                    "description": "Automatic retries for transient generation failures",
                },
                "compliance_audit": {
                    "max_attempts": 2,
                    "backoff": "fixed (2s)",
                    "description": "Automatic retries for audit failures",
                },
                "pdf_processing": {
                    "max_attempts": 1,
                    "backoff": "none",
                    "description": "No automatic retries for large file processing",
                },
            },
            "client_retries": {
                "5xx_errors": {
                    "recommended": True,
                    "strategy": "exponential backoff",
                    "initial_delay": "1s",
                    "max_delay": "60s",
                    "max_attempts": 5,
                },
                "429_rate_limit": {
                    "recommended": True,
                    "strategy": "respect Retry-After header",
                    "description": "Wait for Retry-After seconds before retrying",
                },
                "4xx_errors": {
                    "recommended": False,
                    "description": "Client errors require fixing the request, not retrying",
                },
            },
        },
        "x-rate-limits": {
            "description": "API rate limits by endpoint category",
            "limits": {
                "ingestion": {
                    "limit": "10 requests/minute",
                    "scope": "per organization_id",
                    "description": "Brand PDF ingestion rate limit",
                },
                "generation": {
                    "limit": "30 requests/minute",
                    "scope": "per brand_id",
                    "description": "Asset generation rate limit",
                },
                "other_endpoints": {
                    "limit": "100 requests/minute",
                    "scope": "per API key",
                    "description": "All other endpoints (list, get, update, etc.)",
                },
            },
            "headers": {
                "X-RateLimit-Limit": "Maximum requests per window",
                "X-RateLimit-Remaining": "Remaining requests in current window",
                "X-RateLimit-Reset": "Unix timestamp when limit resets",
                "Retry-After": "Seconds to wait before retrying (on 429 response)",
            },
        },
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
