"""
Modal application with consolidated FastAPI router.

This version uses a single web endpoint with FastAPI routing to work
within Modal's free tier limit of 8 endpoints.
"""

import modal

# Define Modal app
app = modal.App("mobius-v2-final")

# Define image with all dependencies
from pathlib import Path

# Get paths - this file is at src/mobius/api/app_consolidated.py
# So parent.parent.parent gets us to project root
this_file = Path(__file__).resolve()
project_root = this_file.parent.parent.parent.parent

image = (
    modal.Image.debian_slim()
    .apt_install(
        "libcairo2",  # Required for SVG rasterization
        # Chromium dependencies for Playwright
        "libglib2.0-0",
        "libnss3",
        "libnspr4",
        "libatk1.0-0",
        "libatk-bridge2.0-0",
        "libcups2",
        "libdrm2",
        "libxkbcommon0",
        "libxcomposite1",
        "libxdamage1",
        "libxrandr2",
        "libgbm1",
        "libpango-1.0-0",
        "libcairo2",
        "libasound2",
        "libxshmfence1",
        "fonts-liberation",
        "libappindicator3-1",
        "xdg-utils",
    )
    .pip_install(
        "fastapi>=0.104.0",
        "python-multipart>=0.0.6",
        "langgraph>=0.0.20",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "supabase>=2.0.0",
        "google-generativeai>=0.3.0",
        "pdfplumber>=0.10.0",
        "PyMuPDF>=1.23.0",
        "Pillow>=10.0.0",
        "cairosvg>=2.7.0",  # Required for SVG to PNG conversion
        "httpx>=0.25.0",
        "structlog>=23.0.0",
        "tenacity>=8.2.0",
        "tiktoken>=0.5.0",
        "hypothesis>=6.0.0",
        "neo4j>=5.14.0",  # Neo4j Python driver for graph database
        "certifi>=2023.0.0",  # CA bundle for SSL certificate verification
        "pip-system-certs>=5.0",  # Integrate system CA certs for Neo4j SSL
        "playwright==1.48.0",  # For visual scraping
    )
    .run_commands("playwright install chromium")
    .add_local_dir(str(project_root / "src" / "mobius"), "/root/mobius", copy=True)
    .add_local_file(str(project_root / "mobius-dashboard.html"), "/root/mobius-dashboard.html")
)

# Define secrets
secrets = [modal.Secret.from_name("mobius-secrets")]


# Visual scraper function (consolidated into main app)
@app.function(image=image, secrets=secrets, timeout=60)
def analyze_brand_visuals(url: str):
    """Analyze a website's visual brand identity using Playwright + Gemini Vision."""
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    import google.generativeai as genai
    import json
    import os
    
    # Extraction schema for Gemini
    EXTRACTION_SCHEMA = {
        "type": "object",
        "properties": {
            "identity_core": {
                "type": "object",
                "properties": {
                    "archetype": {
                        "type": "string",
                        "description": "Jungian brand archetype (e.g., 'The Sage', 'The Hero', 'The Rebel')"
                    },
                    "voice_vectors": {
                        "type": "object",
                        "description": "Voice dimensions as 0.0-1.0 scores",
                        "properties": {
                            "formal": {
                                "type": "number",
                                "description": "0.0 = casual, 1.0 = formal/professional"
                            },
                            "witty": {
                                "type": "number",
                                "description": "0.0 = serious, 1.0 = playful/humorous"
                            },
                            "technical": {
                                "type": "number",
                                "description": "0.0 = accessible, 1.0 = jargon-heavy/expert"
                            },
                            "urgent": {
                                "type": "number",
                                "description": "0.0 = relaxed, 1.0 = time-sensitive/action-oriented"
                            },
                        },
                    },
                },
            },
            "colors": {
                "type": "array",
                "description": "Brand color palette with semantic roles",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Color name (e.g., 'Ocean Blue')"},
                        "hex": {"type": "string", "description": "Hex code (e.g., '#0057B8')"},
                        "usage": {
                            "type": "string",
                            "enum": ["primary", "secondary", "accent", "neutral", "semantic"],
                            "description": "Semantic role: primary (brand identity), secondary (supporting), accent (CTAs), neutral (backgrounds), semantic (status)"
                        },
                        "usage_weight": {
                            "type": "number",
                            "description": "Estimated visual prominence (0.0-1.0)"
                        },
                    },
                },
            },
            "typography": {
                "type": "array",
                "description": "Font families detected",
                "items": {
                    "type": "object",
                    "properties": {
                        "family": {"type": "string", "description": "Font family name"},
                        "usage": {"type": "string", "description": "Usage context (e.g., 'Headlines', 'Body text')"},
                    },
                },
            },
            "visual_style": {
                "type": "object",
                "description": "Overall visual aesthetic",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "3-5 adjectives describing visual style"
                    },
                    "imagery_style": {
                        "type": "string",
                        "description": "Photography/illustration style"
                    },
                },
            },
            "confidence": {
                "type": "number",
                "description": "Confidence score (0.0-1.0)"
            },
        },
        "required": ["identity_core", "colors", "typography", "visual_style", "confidence"],
    }
    
    EXTRACTION_PROMPT = """You are an expert Brand Strategist analyzing a website screenshot.

Your task is to infer the brand's identity by analyzing:
1. **Visual Hierarchy**: What elements dominate? What's emphasized?
2. **Color Psychology**: What emotions do the colors evoke?
3. **Typography**: What does the font choice communicate?
4. **Imagery Style**: What's the photography/illustration aesthetic?
5. **Copy Tone**: Analyze headlines and CTAs for voice characteristics

CRITICAL INSTRUCTIONS:
- Focus on the "above the fold" content (first screen)
- Identify the PRIMARY brand color (used for logos/headers)
- Identify ACCENT colors (used for buttons/CTAs)
- Infer the Jungian archetype based on visual + verbal cues
- Estimate voice vectors by analyzing headline tone and word choice
- Assign usage_weight based on visual prominence (0.0-1.0)

ARCHETYPE GUIDE:
- The Sage: Wisdom, expertise, thought leadership (e.g., universities, consultancies)
- The Hero: Achievement, courage, making an impact (e.g., Nike, sports brands)
- The Rebel: Disruption, revolution, breaking rules (e.g., Harley-Davidson, Tesla)
- The Innocent: Simplicity, purity, nostalgia (e.g., Dove, Coca-Cola)
- The Explorer: Freedom, discovery, adventure (e.g., Patagonia, Jeep)
- The Creator: Innovation, imagination, self-expression (e.g., Adobe, Lego)
- The Ruler: Control, leadership, responsibility (e.g., Mercedes-Benz, Rolex)
- The Magician: Transformation, vision, making dreams reality (e.g., Disney, Apple)
- The Lover: Intimacy, passion, sensuality (e.g., Chanel, Godiva)
- The Caregiver: Service, compassion, nurturing (e.g., Johnson & Johnson, UNICEF)
- The Jester: Joy, humor, living in the moment (e.g., Ben & Jerry's, Old Spice)
- The Everyman: Belonging, authenticity, down-to-earth (e.g., IKEA, Target)

Return strict JSON matching the schema. Be decisive - make your best inference even with limited information."""
    
    # Normalize URL
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    
    # Capture screenshot
    screenshot_bytes = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
            context = browser.new_context(viewport={"width": 1280, "height": 1024})
            page = context.new_page()
            
            try:
                page.goto(url, wait_until="networkidle", timeout=15000)
                page.wait_for_timeout(2000)
                screenshot_bytes = page.screenshot(
                    clip={"x": 0, "y": 0, "width": 1280, "height": 2000},
                    type="jpeg",
                    quality=85,
                )
            finally:
                browser.close()
    except Exception as e:
        return {"error": f"Screenshot failed: {str(e)}", "url": url, "confidence": 0.0}
    
    if not screenshot_bytes:
        return {"error": "Screenshot capture failed", "url": url, "confidence": 0.0}
    
    # Analyze with Gemini
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        response = model.generate_content(
            contents=[
                EXTRACTION_PROMPT,
                {"mime_type": "image/jpeg", "data": screenshot_bytes},
            ],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=EXTRACTION_SCHEMA,
                temperature=0.3,
            ),
        )
        
        result = json.loads(response.text)
        result["url"] = url
        return result
    except Exception as e:
        return {"error": f"Vision analysis failed: {str(e)}", "url": url, "confidence": 0.0}


# Mount FastAPI app to Modal
@app.function(image=image, secrets=secrets, timeout=180)  # 3min timeout for long-running generation workflows
@modal.asgi_app()
def fastapi_app():
    """Main ASGI app with all routes."""
    
    import sys
    sys.path.insert(0, "/root")
    
    from fastapi import FastAPI, Request, WebSocket
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    
    web_app = FastAPI(title="Mobius API", version="2.0.0")
    
    # CORS middleware - allow all origins including file:// and localhost for testing
    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Must be False when using allow_origins=["*"]
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    # Brand Management Routes
    
    @web_app.post("/v1/brands/ingest")
    async def ingest_brand(request: Request):
        """Upload and ingest brand guidelines PDF."""
        from mobius.api.routes import ingest_brand_handler
        from mobius.api.errors import MobiusError, ValidationError
        from fastapi import UploadFile, File, Form
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            # Check content type to determine how to parse the request
            content_type = request.headers.get("content-type", "")
            
            if "multipart/form-data" in content_type:
                # Handle multipart form data (standard file upload)
                form = await request.form()
                
                file_upload = form.get("file")
                if not file_upload:
                    raise ValidationError(
                        code="MISSING_FILE",
                        message="file is required in form data",
                        request_id="",
                    )
                
                # Read file bytes
                file_bytes = await file_upload.read()
                filename = file_upload.filename or "guidelines.pdf"
                content_type_file = file_upload.content_type or "application/pdf"
                
                # Get other form fields
                organization_id = form.get("organization_id") or "00000000-0000-0000-0000-000000000000"
                brand_name = form.get("brand_name") or filename.replace(".pdf", "")
                
                # Check for optional logo upload
                logo_file_upload = form.get("logo")
                logo_file_bytes = None
                logo_filename = None
                if logo_file_upload:
                    logo_file_bytes = await logo_file_upload.read()
                    logo_filename = logo_file_upload.filename or "logo.png"
                    logger.info("logo_file_received", 
                               logo_size=len(logo_file_bytes), 
                               logo_filename=logo_filename)
                
                # Check for optional visual scan data (MOAT enrichment)
                visual_scan_data = form.get("visual_scan_data")
                if visual_scan_data:
                    logger.info("visual_scan_data_received", 
                               data_length=len(visual_scan_data))
                
                logger.info("multipart_upload_received", 
                           file_size=len(file_bytes), 
                           filename=filename,
                           brand_name=brand_name,
                           has_logo=logo_file_bytes is not None,
                           has_visual_scan=visual_scan_data is not None)
                
            else:
                # Handle JSON with base64-encoded file (legacy support)
                try:
                    data = await request.json()
                except UnicodeDecodeError as e:
                    logger.error("json_decode_error", error=str(e))
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": {
                                "code": "INVALID_REQUEST",
                                "message": "Use multipart/form-data for file uploads",
                                "details": {"error": str(e)},
                            }
                        }
                    )
                
                import base64
                organization_id = data.get("organization_id") or "00000000-0000-0000-0000-000000000000"
                brand_name = data.get("brand_name")
                
                if not brand_name:
                    raise ValidationError(
                        code="MISSING_BRAND_NAME",
                        message="brand_name is required",
                        request_id="",
                    )
                
                file_data = data.get("file")
                if not file_data:
                    raise ValidationError(
                        code="MISSING_FILE",
                        message="file data is required",
                        request_id="",
                    )
                
                # Decode base64
                if isinstance(file_data, str):
                    if file_data.startswith("data:"):
                        file_data = file_data.split(",", 1)[1]
                    file_bytes = base64.b64decode(file_data)
                else:
                    file_bytes = file_data
                
                filename = data.get("filename", "guidelines.pdf")
                content_type_file = data.get("content_type", "application/pdf")
                
                logger.info("json_upload_received", 
                           file_size=len(file_bytes),
                           brand_name=brand_name)
            
            # Call handler with processed data
            result = await ingest_brand_handler(
                organization_id=organization_id,
                brand_name=brand_name,
                file=file_bytes,
                content_type=content_type_file,
                filename=filename,
                logo_file=logo_file_bytes,
                logo_filename=logo_filename,
                visual_scan_data=visual_scan_data if 'visual_scan_data' in locals() else None,
            )
            
            return result.model_dump() if hasattr(result, 'model_dump') else result
            
        except MobiusError as e:
            logger.error("endpoint_error", error=str(e))
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.error_response.model_dump()}
            )
        except Exception as e:
            error_msg = str(e)
            logger.error("unexpected_error", error=error_msg, error_type=type(e).__name__)
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {"error": error_msg},
                    }
                }
            )
    
    @web_app.post("/v1/brands/scan")
    async def scan_brand_from_url(request: Request):
        """Scan a website URL to extract brand identity using vision AI."""
        from mobius.api.errors import MobiusError, ValidationError
        import structlog
        import modal
        
        logger = structlog.get_logger()
        
        try:
            data = await request.json()
            url = data.get("url")
            
            if not url:
                raise ValidationError(
                    code="MISSING_URL",
                    message="url is required",
                    request_id="",
                )
            
            logger.info("visual_scan_started", url=url)
            
            # Call the visual scraper function using spawn (async execution within same app)
            # We use .spawn() to run it in a separate container, then get the result
            call = analyze_brand_visuals.spawn(url)
            result = call.get()
            
            logger.info("visual_scan_completed", url=url, has_error="error" in result)
            
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
                        "message": "An unexpected error occurred during visual scan",
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
        from mobius.api.errors import MobiusError, ValidationError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            # For now, use a default organization_id if not provided
            # TODO: Implement proper multi-tenant organization management
            if not organization_id:
                # Use a consistent UUID for default organization
                organization_id = "00000000-0000-0000-0000-000000000000"
            
            result = await list_brands_handler(
                organization_id=organization_id,
                search=search,
                limit=limit,
            )
            # Ensure proper JSON serialization of Pydantic model
            return result.model_dump() if hasattr(result, 'model_dump') else result
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
    
    @web_app.post("/v1/jobs/{job_id}/review")
    async def review_job(job_id: str, request: Request):
        """Submit review decision for jobs in needs_review status."""
        from mobius.api.routes import review_job_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            body = await request.json()
            decision = body.get("decision")
            tweak_instruction = body.get("tweak_instruction")
            
            result = await review_job_handler(
                job_id=job_id,
                decision=decision,
                tweak_instruction=tweak_instruction
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
    
    @web_app.post("/v1/jobs/{job_id}/tweak")
    async def tweak_job(job_id: str, request: Request):
        """Apply multi-turn tweak to a completed or needs_review job."""
        from mobius.api.routes import tweak_completed_job_handler
        from mobius.api.errors import MobiusError
        import structlog
        
        logger = structlog.get_logger()
        
        try:
            body = await request.json()
            tweak_instruction = body.get("tweak_instruction")
            
            result = await tweak_completed_job_handler(
                job_id=job_id,
                tweak_instruction=tweak_instruction
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

    # Graph Database Routes

    @web_app.get("/v1/health/graph")
    async def graph_health():
        """Graph database health check endpoint."""
        from mobius.api.routes import graph_health_check_handler
        from mobius.api.errors import MobiusError
        import structlog

        logger = structlog.get_logger()

        try:
            result = await graph_health_check_handler()
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

    @web_app.get("/v1/brands/{brand_id}/graph")
    async def brand_graph(brand_id: str):
        """Get graph relationships for a brand."""
        from mobius.api.routes import get_brand_graph_handler
        from mobius.api.errors import MobiusError
        import structlog

        logger = structlog.get_logger()

        try:
            result = await get_brand_graph_handler(brand_id=brand_id)
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

    @web_app.get("/v1/brands/{brand_id}/similar")
    async def similar_brands(brand_id: str, min_shared_colors: int = 3):
        """Find brands with similar color palettes."""
        from mobius.api.routes import find_similar_brands_handler
        from mobius.api.errors import MobiusError
        import structlog

        logger = structlog.get_logger()

        try:
            result = await find_similar_brands_handler(
                brand_id=brand_id,
                min_shared_colors=min_shared_colors
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

    @web_app.get("/v1/colors/{hex}/brands")
    async def color_relationships(hex: str):
        """Find all brands using a specific color."""
        from mobius.api.routes import find_color_relationships_handler
        from mobius.api.errors import MobiusError
        import structlog

        logger = structlog.get_logger()

        try:
            result = await find_color_relationships_handler(hex=hex)
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

    @web_app.get("/v1/colors/{hex}/pairings")
    async def color_pairings(hex: str, min_samples: int = 5):
        """Find colors that pair well with a given color (MOAT feature)."""
        from mobius.api.routes import find_color_pairings_handler
        from mobius.api.errors import MobiusError
        import structlog

        logger = structlog.get_logger()

        try:
            result = await find_color_pairings_handler(hex=hex, min_samples=min_samples)
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

    # WebSocket Routes for Real-Time Monitoring

    @web_app.websocket("/ws/monitoring/{job_id}")
    async def websocket_monitoring(websocket: WebSocket, job_id: str):
        """WebSocket endpoint for real-time job monitoring."""
        from mobius.api.websocket_handlers import websocket_monitoring_endpoint
        await websocket_monitoring_endpoint(websocket, job_id)

    # Dashboard UI

    @web_app.get("/")
    async def serve_dashboard():
        """Serve the Mobius dashboard HTML."""
        from fastapi.responses import HTMLResponse

        # Read the dashboard HTML file from Modal container
        dashboard_path = Path("/root/mobius-dashboard.html")
        if dashboard_path.exists():
            html_content = dashboard_path.read_text(encoding='utf-8')
            # Update API URL in the HTML to use relative path
            html_content = html_content.replace(
                'https://rocoloco--mobius-v2-final-fastapi-app.modal.run/v1',
                '/v1'
            )
            return HTMLResponse(content=html_content)
        else:
            return HTMLResponse(content="<h1>Mobius API</h1><p>Dashboard not found. Use /v1/docs for API documentation.</p>")

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
    import sys
    sys.path.insert(0, "/root")  # Add mounted source to Python path
    
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
