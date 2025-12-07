"""
Modal application definition with all API endpoints.

This module defines the Modal app with all v1 API endpoints and
configures the runtime environment with dependencies and secrets.
"""

import modal
from typing import Optional
from pathlib import Path

# Define Modal app
app = modal.App("mobius-v2")

# Mount the source code so Modal functions can import from mobius package
# This resolves "ModuleNotFoundError: No module named 'mobius'" in scheduled functions
src_mount = modal.Mount.from_local_dir(
    Path(__file__).parent.parent.parent,  # Points to src/ directory
    remote_path="/root/src"
)

# Define image with all dependencies
image = (
    modal.Image.debian_slim()
    .apt_install("libcairo2")  # Required for SVG rasterization
    .pip_install(
        "fastapi>=0.104.0",  # Required for web endpoints
        "langgraph>=0.0.20",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "supabase>=2.0.0",
        "google-generativeai>=0.3.0",
        "pdfplumber>=0.10.0",
        "cairosvg>=2.7.0",  # Required for SVG to PNG conversion
        "rembg>=2.0.50",  # Required for automatic background removal
        "onnxruntime>=1.16.0",  # Required by rembg
        "httpx>=0.25.0",
        "structlog>=23.0.0",
        "tenacity>=8.2.0",
        "hypothesis>=6.0.0",
        "tiktoken>=0.5.0",
    )
)

# Define secrets
secrets = [modal.Secret.from_name("mobius-secrets")]


# Brand Management Endpoints

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST", label="v1-ingest-brand")
async def v1_ingest_brand(request: dict):
    """
    POST /v1/brands/ingest
    
    Upload and ingest brand guidelines PDF.
    """
    from mobius.api.routes import ingest_brand_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        # Extract multipart form data
        organization_id = request.get("organization_id")
        brand_name = request.get("brand_name")
        file_data = request.get("file")  # bytes
        content_type = request.get("content_type", "application/pdf")
        filename = request.get("filename", "guidelines.pdf")
        
        result = await ingest_brand_handler(
            organization_id=organization_id,
            brand_name=brand_name,
            file=file_data,
            content_type=content_type,
            filename=filename,
        )
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="GET", label="v1-list-brands")
async def v1_list_brands(request: dict):
    """
    GET /v1/brands
    
    List all brands for an organization.
    """
    from mobius.api.routes import list_brands_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        organization_id = request.get("organization_id")
        search = request.get("search")
        limit = int(request.get("limit", 100))
        
        result = await list_brands_handler(
            organization_id=organization_id,
            search=search,
            limit=limit,
        )
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="GET", label="v1-get-brand")
async def v1_get_brand(request: dict):
    """
    GET /v1/brands/{brand_id}
    
    Get detailed brand information.
    """
    from mobius.api.routes import get_brand_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        brand_id = request.get("brand_id")
        
        result = await get_brand_handler(brand_id=brand_id)
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="PATCH", label="v1-update-brand")
async def v1_update_brand(request: dict):
    """
    PATCH /v1/brands/{brand_id}
    
    Update brand metadata.
    """
    from mobius.api.routes import update_brand_handler
    from mobius.api.schemas import UpdateBrandRequest
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        brand_id = request.get("brand_id")
        updates = UpdateBrandRequest(**request.get("updates", {}))
        
        result = await update_brand_handler(
            brand_id=brand_id,
            updates=updates,
        )
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="DELETE", label="v1-delete-brand")
async def v1_delete_brand(request: dict):
    """
    DELETE /v1/brands/{brand_id}
    
    Soft delete a brand.
    """
    from mobius.api.routes import delete_brand_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        brand_id = request.get("brand_id")
        
        result = await delete_brand_handler(brand_id=brand_id)
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


# Generation Endpoints

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST", label="v1-generate")
async def v1_generate(request: dict):
    """
    POST /v1/generate
    
    Generate brand-compliant asset.
    """
    from mobius.api.routes import generate_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        brand_id = request.get("brand_id")
        prompt = request.get("prompt")
        template_id = request.get("template_id")
        webhook_url = request.get("webhook_url")
        async_mode = request.get("async_mode", False)
        idempotency_key = request.get("idempotency_key")
        
        # Extract any additional generation parameters
        additional_params = {
            k: v for k, v in request.items()
            if k not in ["brand_id", "prompt", "template_id", "webhook_url", "async_mode", "idempotency_key"]
        }
        
        result = await generate_handler(
            brand_id=brand_id,
            prompt=prompt,
            template_id=template_id,
            webhook_url=webhook_url,
            async_mode=async_mode,
            idempotency_key=idempotency_key,
            **additional_params,
        )
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


# Job Management Endpoints

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="GET", label="v1-get-job-status")
async def v1_get_job_status(request: dict):
    """
    GET /v1/jobs/{job_id}
    
    Get job status and results.
    """
    from mobius.api.routes import get_job_status_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        job_id = request.get("job_id")
        
        result = await get_job_status_handler(job_id=job_id)
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST", label="v1-cancel-job")
async def v1_cancel_job(request: dict):
    """
    POST /v1/jobs/{job_id}/cancel
    
    Cancel a running job.
    """
    from mobius.api.routes import cancel_job_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        job_id = request.get("job_id")
        
        result = await cancel_job_handler(job_id=job_id)
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST", label="v1-review-job")
async def v1_review_job(request: dict):
    """
    POST /v1/jobs/{job_id}/review

    Submit review decision for jobs in needs_review status.
    """
    from mobius.api.routes import review_job_handler
    from mobius.api.errors import MobiusError
    import structlog

    logger = structlog.get_logger()

    try:
        job_id = request.get("job_id")
        decision = request.get("decision")
        tweak_instruction = request.get("tweak_instruction")

        result = await review_job_handler(
            job_id=job_id,
            decision=decision,
            tweak_instruction=tweak_instruction
        )

        return result

    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


# Template Management Endpoints

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST", label="v1-save-template")
async def v1_save_template(request: dict):
    """
    POST /v1/templates
    
    Save an asset as a reusable template.
    """
    from mobius.api.routes import save_template_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        asset_id = request.get("asset_id")
        template_name = request.get("template_name")
        description = request.get("description")
        
        result = await save_template_handler(
            asset_id=asset_id,
            template_name=template_name,
            description=description,
        )
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="GET", label="v1-list-templates")
async def v1_list_templates(request: dict):
    """
    GET /v1/templates
    
    List all templates for a brand.
    """
    from mobius.api.routes import list_templates_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        brand_id = request.get("brand_id")
        limit = int(request.get("limit", 100))
        
        result = await list_templates_handler(
            brand_id=brand_id,
            limit=limit,
        )
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="GET", label="v1-get-template")
async def v1_get_template(request: dict):
    """
    GET /v1/templates/{template_id}
    
    Get detailed template information.
    """
    from mobius.api.routes import get_template_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        template_id = request.get("template_id")
        
        result = await get_template_handler(template_id=template_id)
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="DELETE", label="v1-delete-template")
async def v1_delete_template(request: dict):
    """
    DELETE /v1/templates/{template_id}
    
    Delete a template.
    """
    from mobius.api.routes import delete_template_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        template_id = request.get("template_id")
        
        result = await delete_template_handler(template_id=template_id)
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


# Feedback Endpoints

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST", label="v1-submit-feedback")
async def v1_submit_feedback(request: dict):
    """
    POST /v1/assets/{asset_id}/feedback
    
    Submit feedback for an asset.
    """
    from mobius.api.routes import submit_feedback_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        asset_id = request.get("asset_id")
        action = request.get("action")
        reason = request.get("reason")
        
        result = await submit_feedback_handler(
            asset_id=asset_id,
            action=action,
            reason=reason,
        )
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="GET", label="v1-get-feedback-stats")
async def v1_get_feedback_stats(request: dict):
    """
    GET /v1/brands/{brand_id}/feedback
    
    Get feedback statistics for a brand.
    """
    from mobius.api.routes import get_feedback_stats_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        brand_id = request.get("brand_id")
        
        result = await get_feedback_stats_handler(brand_id=brand_id)
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


# System Endpoints

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="GET", label="v1-health")
async def v1_health(request: dict):
    """
    GET /v1/health
    
    Health check endpoint.
    """
    from mobius.api.routes import health_check_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        result = await health_check_handler()
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="GET", label="v1-docs")
async def v1_docs(request: dict):
    """
    GET /v1/docs
    
    Get OpenAPI documentation.
    """
    from mobius.api.routes import get_api_docs_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        result = await get_api_docs_handler()
        
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


# Legacy Phase 1 Endpoint for Backward Compatibility

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST", label="run-mobius-job")
async def run_mobius_job(request: dict):
    """
    POST /run_mobius_job (Legacy Phase 1 endpoint)
    
    Maintained for backward compatibility. Redirects to v1 API.
    
    This endpoint will be deprecated in a future release.
    Please migrate to POST /v1/generate.
    """
    from mobius.api.routes import generate_handler
    from mobius.api.errors import MobiusError
    import structlog
    
    logger = structlog.get_logger()
    logger.warning(
        "legacy_endpoint_used",
        message="Please migrate to /v1/generate",
        endpoint="run_mobius_job",
    )
    
    try:
        # Transform legacy request to v1 format
        # Legacy format: {"prompt": "...", ...}
        # v1 format: {"brand_id": "...", "prompt": "...", ...}
        
        prompt = request.get("prompt")
        
        # Use a default brand for legacy requests
        # In production, this should be configured per client
        brand_id = request.get("brand_id", "default-legacy-brand")
        
        result = await generate_handler(
            brand_id=brand_id,
            prompt=prompt,
            async_mode=False,
        )
        
        # Transform v1 response to legacy format if needed
        return result
        
    except MobiusError as e:
        logger.error("endpoint_error", error=str(e))
        return {"error": e.error_response.model_dump()}, e.status_code
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            }
        }, 500


# Background Job Cleanup Scheduler

@app.function(
    image=image,
    secrets=secrets,
    mounts=[src_mount],
    schedule=modal.Cron("0 * * * *"),  # Run hourly
)
async def cleanup_expired_jobs():
    """
    Cleanup expired jobs and associated temporary files.
    
    Runs hourly via Modal cron schedule.
    Deletes jobs older than 24 hours and cleans up temporary files.
    """
    import sys
    sys.path.insert(0, "/root/src")  # Add mounted source to Python path
    
    from mobius.storage.database import get_supabase_client
    from mobius.storage.files import FileStorage
    import structlog
    
    logger = structlog.get_logger()
    logger.info("cleanup_job_started")
    
    client = get_supabase_client()
    
    try:
        # Find expired jobs
        expired = (
            client.table("jobs")
            .select("job_id, state, status")
            .lt("expires_at", "now()")
            .execute()
        )
        
        deleted_count = 0
        for job in expired.data:
            job_id = job["job_id"]
            
            # Delete any temporary files associated with failed jobs
            # (Successful jobs have assets moved to permanent storage)
            if job.get("status") == "failed":
                try:
                    file_storage = FileStorage()
                    await file_storage.delete_file("assets", f"temp/{job_id}")
                except Exception:
                    pass  # Ignore if file doesn't exist
            
            # Delete job record
            client.table("jobs").delete().eq("job_id", job_id).execute()
            deleted_count += 1
        
        logger.info("cleanup_job_completed", deleted_count=deleted_count)
        
    except Exception as e:
        logger.error("cleanup_job_failed", error=str(e))
        raise
