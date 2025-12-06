"""
Modal application with consolidated FastAPI router.

This version uses a single web endpoint with FastAPI routing to work
within Modal's free tier limit of 8 endpoints.
"""

import modal

# Define Modal app
app = modal.App("mobius-v2")

# Define image with all dependencies
from pathlib import Path

# Get paths - this file is at src/mobius/api/app_consolidated.py
# So parent.parent.parent gets us to project root
this_file = Path(__file__).resolve()
project_root = this_file.parent.parent.parent.parent

image = (
    modal.Image.debian_slim()
    .pip_install(
        "fastapi>=0.104.0",
        "langgraph>=0.0.20",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "supabase>=2.0.0",
        "google-generativeai>=0.3.0",
        "pdfplumber>=0.10.0",
        "httpx>=0.25.0",
        "structlog>=23.0.0",
        "tenacity>=8.2.0",
        "hypothesis>=6.0.0",
    )
    .add_local_file(str(project_root / "pyproject.toml"), "/tmp/mobius-install/pyproject.toml", copy=True)
    .add_local_dir(str(project_root / "src"), "/tmp/mobius-install/src", copy=True)
    .run_commands("pip install /tmp/mobius-install")
)

# Define secrets
secrets = [modal.Secret.from_name("mobius-secrets")]


# Mount FastAPI app to Modal
@app.function(image=image, secrets=secrets)
@modal.asgi_app()
def fastapi_app():
    """Main ASGI app with all routes."""
    
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    
    web_app = FastAPI(title="Mobius API", version="2.0.0")
    
    # Brand Management Routes
    
    @web_app.post("/v1/brands/ingest")
    async def ingest_brand(request: Request):
        """Upload and ingest brand guidelines PDF."""
        from mobius.api.routes import ingest_brand_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            data = await request.json()
            result = await ingest_brand_handler(
                organization_id=data.get("organization_id"),
                brand_name=data.get("brand_name"),
                file=data.get("file"),
                content_type=data.get("content_type", "application/pdf"),
                filename=data.get("filename", "guidelines.pdf"),
            )
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    @web_app.get("/v1/brands")
    async def list_brands(
        organization_id: str = None,
        search: str = None,
        limit: int = 100
    ):
        """List all brands for an organization."""
        from mobius.api.routes import list_brands_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            result = await list_brands_handler(
                organization_id=organization_id,
                search=search,
                limit=limit,
            )
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    @web_app.get("/v1/brands/{brand_id}")
    async def get_brand(brand_id: str):
        """Get detailed brand information."""
        from mobius.api.routes import get_brand_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            result = await get_brand_handler(brand_id=brand_id)
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    @web_app.patch("/v1/brands/{brand_id}")
    async def update_brand(brand_id: str, request: Request):
        """Update brand metadata."""
        from mobius.api.routes import update_brand_handler
        from mobius.api.schemas import UpdateBrandRequest
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            data = await request.json()
            updates = UpdateBrandRequest(**data.get("updates", {}))
            result = await update_brand_handler(brand_id=brand_id, updates=updates)
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    @web_app.delete("/v1/brands/{brand_id}")
    async def delete_brand(brand_id: str):
        """Soft delete a brand."""
        from mobius.api.routes import delete_brand_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            result = await delete_brand_handler(brand_id=brand_id)
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    # Generation Routes
    
    @web_app.post("/v1/generate")
    async def generate(request: Request):
        """Generate brand-compliant asset."""
        from mobius.api.routes import generate_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            data = await request.json()
            result = await generate_handler(
                brand_id=data.get("brand_id"),
                prompt=data.get("prompt"),
                template_id=data.get("template_id"),
                webhook_url=data.get("webhook_url"),
                async_mode=data.get("async_mode", False),
                idempotency_key=data.get("idempotency_key"),
            )
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    # Job Management Routes
    
    @web_app.get("/v1/jobs/{job_id}")
    async def get_job_status(job_id: str):
        """Get job status and results."""
        from mobius.api.routes import get_job_status_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            result = await get_job_status_handler(job_id=job_id)
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    @web_app.post("/v1/jobs/{job_id}/cancel")
    async def cancel_job(job_id: str):
        """Cancel a running job."""
        from mobius.api.routes import cancel_job_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            result = await cancel_job_handler(job_id=job_id)
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    # Template Management Routes
    
    @web_app.post("/v1/templates")
    async def save_template(request: Request):
        """Save an asset as a reusable template."""
        from mobius.api.routes import save_template_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            data = await request.json()
            result = await save_template_handler(
                asset_id=data.get("asset_id"),
                template_name=data.get("template_name"),
                description=data.get("description"),
            )
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    @web_app.get("/v1/templates")
    async def list_templates(brand_id: str, limit: int = 100):
        """List all templates for a brand."""
        from mobius.api.routes import list_templates_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            result = await list_templates_handler(brand_id=brand_id, limit=limit)
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    @web_app.get("/v1/templates/{template_id}")
    async def get_template(template_id: str):
        """Get detailed template information."""
        from mobius.api.routes import get_template_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            result = await get_template_handler(template_id=template_id)
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    @web_app.delete("/v1/templates/{template_id}")
    async def delete_template(template_id: str):
        """Delete a template."""
        from mobius.api.routes import delete_template_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            result = await delete_template_handler(template_id=template_id)
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    # Feedback Routes
    
    @web_app.post("/v1/assets/{asset_id}/feedback")
    async def submit_feedback(asset_id: str, request: Request):
        """Submit feedback for an asset."""
        from mobius.api.routes import submit_feedback_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            data = await request.json()
            result = await submit_feedback_handler(
                asset_id=asset_id,
                action=data.get("action"),
                reason=data.get("reason"),
            )
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    @web_app.get("/v1/brands/{brand_id}/feedback")
    async def get_feedback_stats(brand_id: str):
        """Get feedback statistics for a brand."""
        from mobius.api.routes import get_feedback_stats_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            result = await get_feedback_stats_handler(brand_id=brand_id)
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    # System Routes
    
    @web_app.get("/v1/health")
    async def health():
        """Health check endpoint."""
        from mobius.api.routes import health_check_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            result = await health_check_handler()
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    @web_app.get("/v1/docs")
    async def docs():
        """Get OpenAPI documentation."""
        from mobius.api.routes import get_api_docs_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            result = await get_api_docs_handler()
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    # Legacy Phase 1 Endpoint
    
    @web_app.post("/run_mobius_job")
    async def run_mobius_job(request: Request):
        """Legacy Phase 1 endpoint for backward compatibility."""
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
            data = await request.json()
            result = await generate_handler(
                brand_id=data.get("brand_id", "default-legacy-brand"),
                prompt=data.get("prompt"),
                async_mode=False,
            )
            return result
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            logger.error("unexpected_error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": str(e)},
                    }
                }
            )
    
    return web_app


# Background Job Cleanup Scheduler
@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 * * * *"),  # Run hourly
)
async def cleanup_expired_jobs():
    """Cleanup expired jobs and associated temporary files."""
    
    from mobius.storage.database import get_supabase_client
    from mobius.storage.files import FileStorage
    import structlog
    
    logger = structlog.get_logger()
    logger.info("cleanup_job_started")
    
    client = get_supabase_client()
    
    try:
        expired = (
            client.table("jobs")
            .select("job_id, state, status")
            .lt("expires_at", "now()")
            .execute()
        )
        
        deleted_count = 0
        for job in expired.data:
            job_id = job["job_id"]
            
            if job.get("status") == "failed":
                try:
                    file_storage = FileStorage()
                    await file_storage.delete_file("assets", f"temp/{job_id}")
                except Exception:
                    pass
            
            client.table("jobs").delete().eq("job_id", job_id).execute()
            deleted_count += 1
        
        logger.info("cleanup_job_completed", deleted_count=deleted_count)
        
    except Exception as e:
        logger.error("cleanup_job_failed", error=str(e))
        raise
