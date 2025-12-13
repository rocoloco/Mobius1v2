#!/usr/bin/env python3
"""
Local development version of the Mobius API.

This version extracts just the FastAPI app from app_consolidated.py
for local development with uvicorn, without Modal dependencies.
"""

import sys
import os

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the FastAPI app creation logic from app_consolidated
# We'll extract just the FastAPI parts, not the Modal parts
def create_local_app() -> FastAPI:
    """Create FastAPI app for local development."""
    
    app = FastAPI(
        title="Mobius V2 API (Local)",
        description="Brand governance platform with AI-powered compliance (Local Development)",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware for local development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import and include all the routes
    from mobius.api.routes import (
        ingest_brand_handler,
        list_brands_handler,
        get_brand_handler,
        update_brand_handler,
        delete_brand_handler,
        generate_asset_handler,
        get_job_handler,
        list_jobs_handler,
        cancel_job_handler,
        review_job_handler,
        tweak_completed_job_handler,
        health_check_handler,
    )
    
    # Add all the routes manually (since we can't use the Modal web_app)
    @app.get("/v1/health")
    async def health():
        return await health_check_handler()
    
    @app.post("/v1/brands/ingest")
    async def ingest_brand(request):
        # This would need proper request handling for local development
        # For now, just return a placeholder
        return {"message": "Local development - ingest not fully implemented"}
    
    @app.get("/v1/brands")
    async def list_brands():
        return await list_brands_handler()
    
    @app.get("/v1/brands/{brand_id}")
    async def get_brand(brand_id: str):
        return await get_brand_handler(brand_id)
    
    # Add other routes as needed...
    
    return app

# Create the app instance
app = create_local_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)