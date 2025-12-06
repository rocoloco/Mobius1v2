"""
Minimal Modal application for Mobius - Self-contained version.

This version has all logic inline to avoid import issues.
Once working, we can refactor to use external modules.
"""

import modal
import os

# Define Modal app
app = modal.App("mobius-v2")

# Define image with all dependencies
image = (
    modal.Image.debian_slim()
    .pip_install(
        "fastapi>=0.104.0",
        "pydantic>=2.0.0",
        "supabase>=2.0.0",
        "structlog>=23.0.0",
    )
)

# Define secrets
secrets = [modal.Secret.from_name("mobius-secrets")]


# Mount FastAPI app to Modal
@app.function(image=image, secrets=secrets)
@modal.asgi_app()
def fastapi_app():
    """Main ASGI app with all routes."""
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    web_app = FastAPI(title="Mobius API", version="2.0.0")
    
    @web_app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "Mobius API",
            "version": "2.0.0",
            "docs": "/docs",
            "health": "/v1/health"
        }
    
    @web_app.get("/v1/health")
    async def health():
        """Health check endpoint."""
        health_status = {
            "status": "healthy",
            "api": "v1",
            "environment": "modal",
        }
        
        # Check if secrets are loaded
        if os.getenv("SUPABASE_URL"):
            health_status["database"] = "configured"
            
            # Try to connect to Supabase
            try:
                from supabase import create_client
                supabase_url = os.getenv("SUPABASE_URL")
                supabase_key = os.getenv("SUPABASE_KEY")
                client = create_client(supabase_url, supabase_key)
                # Simple query to test connection
                client.table("brands").select("brand_id").limit(0).execute()
                health_status["database"] = "connected"
            except Exception as e:
                health_status["database"] = f"error: {str(e)[:100]}"
        else:
            health_status["database"] = "not_configured"
            
        if os.getenv("FAL_KEY") and os.getenv("GEMINI_API_KEY"):
            health_status["services"] = "configured"
        else:
            health_status["services"] = "not_configured"
        
        return health_status
    
    @web_app.get("/v1/docs")
    async def docs():
        """API documentation."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Mobius API",
                "version": "2.0.0",
                "description": "Enterprise brand governance platform"
            },
            "endpoints": {
                "health": "GET /v1/health",
                "brands": {
                    "ingest": "POST /v1/brands/ingest",
                    "list": "GET /v1/brands",
                    "get": "GET /v1/brands/{brand_id}",
                    "update": "PATCH /v1/brands/{brand_id}",
                    "delete": "DELETE /v1/brands/{brand_id}"
                },
                "generation": "POST /v1/generate",
                "jobs": {
                    "status": "GET /v1/jobs/{job_id}",
                    "cancel": "POST /v1/jobs/{job_id}/cancel"
                },
                "templates": {
                    "save": "POST /v1/templates",
                    "list": "GET /v1/templates",
                    "get": "GET /v1/templates/{template_id}",
                    "delete": "DELETE /v1/templates/{template_id}"
                },
                "feedback": {
                    "submit": "POST /v1/assets/{asset_id}/feedback",
                    "stats": "GET /v1/brands/{brand_id}/feedback"
                }
            },
            "note": "Full implementation coming soon. This is a minimal working deployment."
        }
    
    @web_app.post("/v1/generate")
    async def generate():
        """Placeholder for generation endpoint."""
        return JSONResponse(
            status_code=501,
            content={
                "error": {
                    "code": "NOT_IMPLEMENTED",
                    "message": "Generation endpoint not yet implemented in minimal version",
                    "details": "Full implementation requires module imports to be fixed"
                }
            }
        )
    
    return web_app


# Simplified cleanup job (no external imports)
@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 * * * *"),  # Run hourly
)
async def cleanup_expired_jobs():
    """Cleanup expired jobs - simplified version."""
    import structlog
    from supabase import create_client
    
    logger = structlog.get_logger()
    logger.info("cleanup_job_started")
    
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.warning("cleanup_job_skipped", reason="no_credentials")
            return
        
        client = create_client(supabase_url, supabase_key)
        
        # Find expired jobs
        expired = (
            client.table("jobs")
            .select("job_id")
            .lt("expires_at", "now()")
            .execute()
        )
        
        deleted_count = 0
        for job in expired.data:
            job_id = job["job_id"]
            client.table("jobs").delete().eq("job_id", job_id).execute()
            deleted_count += 1
        
        logger.info("cleanup_job_completed", deleted_count=deleted_count)
        
    except Exception as e:
        logger.error("cleanup_job_failed", error=str(e))
