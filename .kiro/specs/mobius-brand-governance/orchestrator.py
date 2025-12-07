"""
Mobius Brand Governance Engine - Orchestrator (Ruby Edition v2.0)

Production-hardened version with:
- Exponential backoff with jitter for rate limiting
- HTTPX with connection pooling (replacing requests)
- Updated Gemini 2.5 Flash model
- Structured logging
- Secret validation at startup
- PostgreSQL checkpointing support
- Async-ready architecture
- Cost tracking
- Webhook support for long-running jobs
"""

import os
import json
import time
import random
import logging
import hashlib
from datetime import datetime
from typing import TypedDict, List, Optional, Literal, Callable, Any
from functools import wraps
from dataclasses import dataclass

import httpx
from pydantic import BaseModel, Field

import modal
from langgraph.graph import StateGraph, END

# Optional PostgreSQL checkpointing - only import if available
try:
    from langgraph_checkpoint_postgres import PostgresSaver
    CHECKPOINTING_AVAILABLE = True
except ImportError:
    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        CHECKPOINTING_AVAILABLE = True
    except ImportError:
        PostgresSaver = None
        CHECKPOINTING_AVAILABLE = False
from google import genai
from google.genai import types
from supabase import create_client, Client

# ============================================================================
# 1. CONFIGURATION & LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("mobius")


@dataclass
class MobiusConfig:
    """Centralized configuration for Mobius engine."""
    max_retries: int = 3
    base_retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    http_timeout: float = 30.0
    gemini_model: str = "gemini-2.5-flash"
    gemini_temperature: float = 0.1
    max_generation_attempts: int = 3
    enable_checkpointing: bool = False
    postgres_uri: Optional[str] = None


CONFIG = MobiusConfig()


# ============================================================================
# 2. INFRASTRUCTURE & DEPENDENCIES
# ============================================================================

image = modal.Image.debian_slim().pip_install(
    "langgraph>=0.2.0",
    "langgraph-checkpoint-postgres>=2.0.0",
    "google-genai>=1.0.0",
    "supabase>=2.0.0",
    "httpx>=0.27.0",
    "fastapi>=0.110.0",
    "psycopg[binary]>=3.1.0",
)

app = modal.App(
    name="mobius-worker",
    image=image,
    secrets=[modal.Secret.from_name("mobius-secrets")]
)


# ============================================================================
# 3. SECRET VALIDATION
# ============================================================================

REQUIRED_SECRETS = [
    "GEMINI_API_KEY",
]

OPTIONAL_SECRETS = [
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "POSTGRES_URI",
]


def validate_secrets() -> dict[str, bool]:
    """
    Validate required secrets exist at startup.
    Returns dict of secret availability.
    Raises RuntimeError if required secrets are missing.
    """
    status = {}
    missing_required = []
    
    for secret in REQUIRED_SECRETS:
        present = bool(os.environ.get(secret))
        status[secret] = present
        if not present:
            missing_required.append(secret)
    
    for secret in OPTIONAL_SECRETS:
        status[secret] = bool(os.environ.get(secret))
    
    if missing_required:
        raise RuntimeError(
            f"Missing required secrets: {missing_required}. "
            "Please configure these in Modal secrets."
        )
    
    logger.info(f"Secret validation passed. Available: {[k for k, v in status.items() if v]}")
    return status


# ============================================================================
# 4. HTTP CLIENT WITH CONNECTION POOLING
# ============================================================================

_http_client: Optional[httpx.Client] = None


def get_http_client() -> httpx.Client:
    """Get or create a reusable HTTP client with connection pooling."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.Client(
            timeout=httpx.Timeout(CONFIG.http_timeout),
            limits=httpx.Limits(
                max_keepalive_connections=10,
                max_connections=100,
                keepalive_expiry=30.0
            ),
            follow_redirects=True
        )
    return _http_client


def close_http_client():
    """Close the HTTP client (call on shutdown)."""
    global _http_client
    if _http_client is not None:
        _http_client.close()
        _http_client = None


# ============================================================================
# 5. RETRY LOGIC WITH EXPONENTIAL BACKOFF
# ============================================================================

class RetryableError(Exception):
    """Exception that indicates the operation should be retried."""
    pass


class RateLimitError(RetryableError):
    """Specific error for rate limiting (HTTP 429)."""
    pass


def retry_with_backoff(
    max_retries: int = None,
    base_delay: float = None,
    max_delay: float = None,
    retryable_exceptions: tuple = (RetryableError, httpx.TimeoutException, httpx.NetworkError)
):
    """
    Decorator for retry logic with exponential backoff and jitter.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        retryable_exceptions: Tuple of exceptions that trigger retry
    """
    max_retries = max_retries or CONFIG.max_retries
    base_delay = base_delay or CONFIG.base_retry_delay
    max_delay = max_delay or CONFIG.max_retry_delay
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}: {e}"
                        )
                        raise
                    
                    # Calculate delay with exponential backoff + jitter
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0, delay * 0.1)
                    total_delay = delay + jitter
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {total_delay:.2f}s..."
                    )
                    time.sleep(total_delay)
                    
                except Exception as e:
                    # Non-retryable exception, raise immediately
                    logger.error(f"Non-retryable error in {func.__name__}: {e}")
                    raise
            
            raise last_exception
        return wrapper
    return decorator


def check_rate_limit_error(exception: Exception) -> bool:
    """Check if an exception indicates a rate limit error."""
    error_str = str(exception).lower()
    return any(indicator in error_str for indicator in ["429", "rate limit", "quota", "resource_exhausted"])


# ============================================================================
# 6. DATA MODELS
# ============================================================================

class JobState(TypedDict):
    """State object for the LangGraph workflow."""
    # Core fields
    prompt: str
    brand_hex_codes: List[str]
    brand_rules: str
    
    # Processing state
    current_image_url: Optional[str]
    attempt_count: int
    audit_history: List[dict]
    is_approved: bool
    used_model: str
    
    # Metadata
    job_id: str
    created_at: str
    
    # Cost tracking
    estimated_cost_usd: float
    
    # Error tracking
    last_error: Optional[str]


class MobiusJobRequest(BaseModel):
    """Request model for Mobius job submission."""
    prompt: str = Field(..., description="Image generation prompt")
    brand_hex_codes: List[str] = Field(..., description="List of brand hex color codes")
    brand_rules: str = Field(..., description="Brand visual style rules")
    webhook_url: Optional[str] = Field(None, description="Optional webhook for async results")
    job_id: Optional[str] = Field(None, description="Optional custom job ID")


class MobiusJobResponse(BaseModel):
    """Response model for Mobius job results."""
    status: Literal["success", "failed", "error", "pending"]
    job_id: str
    final_image_url: Optional[str] = None
    attempts: int = 0
    is_approved: bool = False
    audit_history: List[dict] = []
    estimated_cost_usd: float = 0.0
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = None


# ============================================================================
# 7. COST TRACKING
# ============================================================================

# Approximate costs per operation (USD)
COST_ESTIMATES = {
    "gemini_vision_generation": 0.03,
    "gemini_audit": 0.001,
}


def estimate_cost(model_id: str, operation: str = "generation") -> float:
    """Estimate cost for an operation."""
    if "image" in model_id.lower() or "vision" in model_id.lower():
        return COST_ESTIMATES.get("gemini_vision_generation", 0.03)
    elif "gemini" in model_id.lower():
        return COST_ESTIMATES.get("gemini_audit", 0.001)
    return 0.0


# ============================================================================
# 8. WORKFLOW NODES
# ============================================================================

@retry_with_backoff(retryable_exceptions=(RetryableError, httpx.TimeoutException))
def generate_node(state: JobState) -> JobState:
    """
    Generation Node: Gemini 3 Vision Model for Image Generation
    
    Uses Gemini 3 Pro Image Preview model with compressed brand guidelines.
    """
    attempt = state["attempt_count"] + 1
    logger.info(f"🎨 Generation Node | Job: {state['job_id']} | Attempt: {attempt}")
    
    hex_string = ", ".join(state["brand_hex_codes"])
    combined_prompt = (
        f"{state['prompt']}. "
        f"Strict Visual Style Rules: {state['brand_rules']}. "
        f"Mandatory Brand Colors: {hex_string}"
    )
    
    model_id = "gemini-3-pro-image-preview"
    logger.info(f"🔀 Using {model_id} for image generation")
    
    try:
        # Call Gemini Vision Model for image generation
        gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        response = gemini_client.models.generate_content(
            model=model_id,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=combined_prompt)]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.7
            )
        )
        
        # Extract image URI from response
        # Note: This is a placeholder - actual implementation depends on Gemini API response format
        image_url = response.text if hasattr(response, 'text') else None
        
        if not image_url:
            raise RetryableError("No image URL in response")
        
        logger.info(f"✅ Generated: {image_url[:80]}...")
        
        cost = estimate_cost(model_id)
        
        new_state = {
            **state,
            "current_image_url": image_url,
            "attempt_count": attempt,
            "used_model": model_id,
            "estimated_cost_usd": state.get("estimated_cost_usd", 0) + cost,
            "last_error": None
        }
        persist_state(new_state, "GENERATED")
        return new_state
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Generation error: {error_msg}")
        
        if check_rate_limit_error(e):
            raise RateLimitError(f"Rate limit hit: {error_msg}")
        
        new_state = {
            **state,
            "current_image_url": None,
            "attempt_count": attempt,
            "used_model": model_id,
            "last_error": error_msg
        }
        persist_state(new_state, "GENERATION_FAILED")
        return new_state


@retry_with_backoff(retryable_exceptions=(RetryableError, RateLimitError, httpx.TimeoutException))
def audit_node(state: JobState) -> JobState:
    """
    Audit Node: Gemini 2.5 Flash with byte transfer.
    
    Downloads image and sends bytes directly to Gemini for brand compliance audit.
    """
    logger.info(f"🔍 Audit Node | Job: {state['job_id']} | Model: {CONFIG.gemini_model}")
    
    if state["current_image_url"] is None:
        return _fail_audit(state, "No image generated")
    
    audit_prompt = f"""You are a strict Brand Compliance Officer.
    
**Brand Guidelines:**
{state['brand_rules']}

**Required Colors:**
{", ".join(state['brand_hex_codes'])}

Analyze the attached image carefully.

1. Does the image adhere to the visual style rules?
2. Are the brand colors correctly represented and prominent?
3. Is the overall composition professional and on-brand?

Return JSON ONLY (no markdown, no explanation):
{{
  "approved": boolean,
  "confidence": number between 0 and 1,
  "reason": "concise explanation",
  "color_compliance": "pass" | "partial" | "fail",
  "style_compliance": "pass" | "partial" | "fail",
  "fix_suggestion": "specific prompt modification to fix the issue, or null if approved"
}}"""

    try:
        # Download image bytes using connection-pooled client
        client = get_http_client()
        logger.info("⬇️ Downloading image bytes...")
        img_response = client.get(state["current_image_url"])
        img_response.raise_for_status()
        
        # Determine mime type from response or URL
        content_type = img_response.headers.get("content-type", "image/jpeg")
        if "png" in content_type or state["current_image_url"].endswith(".png"):
            mime_type = "image/png"
        elif "webp" in content_type or state["current_image_url"].endswith(".webp"):
            mime_type = "image/webp"
        else:
            mime_type = "image/jpeg"
        
        # Call Gemini API
        gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        response = gemini_client.models.generate_content(
            model=CONFIG.gemini_model,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(
                            data=img_response.content,
                            mime_type=mime_type
                        ),
                        types.Part.from_text(text=audit_prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=CONFIG.gemini_temperature
            )
        )
        
        # Parse audit result
        audit_result = json.loads(response.text)
        is_approved = audit_result.get("approved", False)
        
        logger.info(
            f"✅ Audit: {'APPROVED' if is_approved else 'REJECTED'} | "
            f"Confidence: {audit_result.get('confidence', 'N/A')} | "
            f"Colors: {audit_result.get('color_compliance', 'N/A')} | "
            f"Style: {audit_result.get('style_compliance', 'N/A')}"
        )
        
        cost = estimate_cost("gemini")
        
        new_state = {
            **state,
            "audit_history": state["audit_history"] + [audit_result],
            "is_approved": is_approved,
            "estimated_cost_usd": state.get("estimated_cost_usd", 0) + cost,
            "last_error": None
        }
        persist_state(new_state, "AUDITED")
        return new_state
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse Gemini response as JSON: {e}")
        return _fail_audit(state, f"JSON parse error: {e}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Gemini Error: {error_msg}")
        
        if check_rate_limit_error(e):
            logger.warning("💰 Rate limit hit. Will retry with backoff.")
            raise RateLimitError(f"Gemini rate limit: {error_msg}")
        
        return _fail_audit(state, f"Audit Error: {error_msg}")


def _fail_audit(state: JobState, reason: str) -> JobState:
    """Helper to create a failed audit state."""
    result = {
        "approved": False,
        "confidence": 0,
        "reason": reason,
        "color_compliance": "unknown",
        "style_compliance": "unknown",
        "fix_suggestion": "Retry with adjusted prompt"
    }
    return {
        **state,
        "audit_history": state["audit_history"] + [result],
        "is_approved": False,
        "last_error": reason
    }


def correct_node(state: JobState) -> JobState:
    """
    Correction Node: Apply fixes from audit feedback to the prompt.
    """
    logger.info(f"🔧 Correction Node | Job: {state['job_id']}")
    
    if not state["audit_history"]:
        logger.warning("No audit history to correct from")
        return state
    
    last_audit = state["audit_history"][-1]
    fix_suggestion = last_audit.get("fix_suggestion")
    
    if fix_suggestion and fix_suggestion.lower() not in ["null", "none", "retry"]:
        # Apply the fix to the prompt
        enhanced_prompt = f"{state['prompt']}. IMPORTANT CORRECTION: {fix_suggestion}"
        logger.info(f"   Applying fix: {fix_suggestion[:100]}...")
        
        new_state = {
            **state,
            "prompt": enhanced_prompt
        }
        persist_state(new_state, "CORRECTED")
        return new_state
    else:
        logger.info("   No specific fix suggested, retrying with original prompt...")
        return state


# ============================================================================
# 9. PERSISTENCE
# ============================================================================

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """Get or create Supabase client (cached)."""
    global _supabase_client
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        return None
    
    if _supabase_client is None:
        _supabase_client = create_client(url, key)
    
    return _supabase_client


def persist_state(state: JobState, status: str) -> None:
    """Persist job state to Supabase for tracking/auditing."""
    client = get_supabase_client()
    if client is None:
        logger.debug("Supabase not configured, skipping persistence")
        return
    
    try:
        client.table("job_logs").insert({
            "job_id": state.get("job_id"),
            "status": status,
            "prompt": state["prompt"][:500],  # Truncate for storage
            "image_url": state.get("current_image_url"),
            "attempt": state["attempt_count"],
            "approved": state["is_approved"],
            "used_model": state.get("used_model"),
            "estimated_cost_usd": state.get("estimated_cost_usd", 0),
            "last_error": state.get("last_error"),
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
        logger.debug(f"✅ DB Saved: {status}")
        
    except Exception as e:
        logger.warning(f"⚠️ DB persistence error (non-fatal): {e}")


# ============================================================================
# 10. WEBHOOK SUPPORT
# ============================================================================

def send_webhook(url: str, payload: dict) -> bool:
    """Send webhook notification for async job completion."""
    if not url:
        return False
    
    try:
        client = get_http_client()
        response = client.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        logger.info(f"✅ Webhook sent to {url[:50]}...")
        return True
        
    except Exception as e:
        logger.error(f"❌ Webhook failed: {e}")
        return False


# ============================================================================
# 11. ORCHESTRATION
# ============================================================================

def route_decision(state: JobState) -> Literal["__end__", "correct"]:
    """
    Routing decision after audit.
    
    Returns END if approved or max attempts reached, otherwise routes to correction.
    """
    if state["is_approved"]:
        logger.info(f"✅ Job {state['job_id']} approved after {state['attempt_count']} attempts")
        return END
    
    if state["attempt_count"] >= CONFIG.max_generation_attempts:
        logger.warning(
            f"⚠️ Job {state['job_id']} hit max attempts ({CONFIG.max_generation_attempts})"
        )
        return END
    
    return "correct"


def create_workflow(checkpointer=None) -> StateGraph:
    """Create and compile the LangGraph workflow."""
    workflow = StateGraph(JobState)
    
    # Add nodes
    workflow.add_node("generate", generate_node)
    workflow.add_node("audit", audit_node)
    workflow.add_node("correct", correct_node)
    
    # Define edges
    workflow.set_entry_point("generate")
    workflow.add_edge("generate", "audit")
    workflow.add_conditional_edges("audit", route_decision)
    workflow.add_edge("correct", "generate")
    
    # Compile with optional checkpointer
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()


def generate_job_id(request: MobiusJobRequest) -> str:
    """Generate a unique job ID based on request content."""
    content = f"{request.prompt}{request.brand_rules}{datetime.utcnow().isoformat()}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _run_mobius_job_impl(request: MobiusJobRequest) -> MobiusJobResponse:
    """
    Core implementation of Mobius job execution.
    
    Creates workflow, initializes state, runs to completion, and returns results.
    """
    start_time = time.time()
    job_id = request.job_id or generate_job_id(request)
    
    logger.info(f"🚀 Starting Mobius Job: {job_id}")
    logger.info(f"   Prompt: {request.prompt[:100]}...")
    logger.info(f"   Brand colors: {request.brand_hex_codes}")
    
    try:
        # Validate secrets
        validate_secrets()
        
        # Create checkpointer if configured and available
        checkpointer = None
        if CONFIG.enable_checkpointing and CONFIG.postgres_uri and CHECKPOINTING_AVAILABLE:
            try:
                checkpointer = PostgresSaver.from_conn_string(CONFIG.postgres_uri)
                checkpointer.setup()
                logger.info("✅ PostgreSQL checkpointer initialized")
            except Exception as e:
                logger.warning(f"⚠️ Checkpointer setup failed (continuing without): {e}")
        elif CONFIG.enable_checkpointing and not CHECKPOINTING_AVAILABLE:
            logger.warning("⚠️ Checkpointing requested but langgraph-checkpoint-postgres not installed")
        
        # Create and run workflow
        app_graph = create_workflow(checkpointer)
        
        initial_state: JobState = {
            "prompt": request.prompt,
            "brand_hex_codes": request.brand_hex_codes,
            "brand_rules": request.brand_rules,
            "current_image_url": None,
            "attempt_count": 0,
            "audit_history": [],
            "is_approved": False,
            "used_model": "pending",
            "job_id": job_id,
            "created_at": datetime.utcnow().isoformat(),
            "estimated_cost_usd": 0.0,
            "last_error": None
        }
        
        # Execute workflow
        config = {"configurable": {"thread_id": job_id}} if checkpointer else {}
        final_state = app_graph.invoke(initial_state, config)
        
        processing_time = time.time() - start_time
        
        # Build response
        response = MobiusJobResponse(
            status="success" if final_state["is_approved"] else "failed",
            job_id=job_id,
            final_image_url=final_state.get("current_image_url"),
            attempts=final_state["attempt_count"],
            is_approved=final_state["is_approved"],
            audit_history=final_state["audit_history"],
            estimated_cost_usd=final_state.get("estimated_cost_usd", 0),
            error_message=final_state.get("last_error"),
            processing_time_seconds=round(processing_time, 2)
        )
        
        logger.info(
            f"🏁 Job {job_id} completed | Status: {response.status} | "
            f"Attempts: {response.attempts} | Time: {processing_time:.2f}s | "
            f"Est. Cost: ${response.estimated_cost_usd:.4f}"
        )
        
        # Send webhook if configured
        if request.webhook_url:
            send_webhook(request.webhook_url, response.model_dump())
        
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = str(e)
        logger.error(f"❌ Workflow Fatal Error for job {job_id}: {error_msg}")
        
        response = MobiusJobResponse(
            status="error",
            job_id=job_id,
            error_message=error_msg,
            processing_time_seconds=round(processing_time, 2)
        )
        
        if request.webhook_url:
            send_webhook(request.webhook_url, response.model_dump())
        
        return response
    
    finally:
        # Cleanup (optional - keep client alive for connection reuse)
        pass


# ============================================================================
# 12. MODAL ENDPOINTS
# ============================================================================

@app.function(timeout=600)
@modal.fastapi_endpoint(method="POST")
def run_mobius_job(request: MobiusJobRequest) -> dict:
    """
    Main API endpoint for synchronous job execution.
    
    POST /run_mobius_job
    
    Request body:
        - prompt: str - Image generation prompt
        - brand_hex_codes: list[str] - Brand colors
        - brand_rules: str - Visual style guidelines
        - webhook_url: str (optional) - Async notification URL
        - job_id: str (optional) - Custom job ID
    
    Returns:
        MobiusJobResponse with status, image URL, audit history, etc.
    """
    response = _run_mobius_job_impl(request)
    return response.model_dump()


@app.function(timeout=600)
@modal.fastapi_endpoint(method="POST")
def submit_mobius_job(request: MobiusJobRequest) -> dict:
    """
    Async job submission endpoint.
    
    Returns immediately with job_id. Results sent to webhook_url.
    Requires webhook_url in request.
    """
    if not request.webhook_url:
        return {
            "status": "error",
            "error_message": "webhook_url is required for async submission"
        }
    
    job_id = request.job_id or generate_job_id(request)
    
    # Spawn the job asynchronously
    run_mobius_job.spawn(request)
    
    return {
        "status": "pending",
        "job_id": job_id,
        "message": f"Job submitted. Results will be sent to {request.webhook_url}"
    }


@app.function()
@modal.fastapi_endpoint(method="GET")
def health_check() -> dict:
    """Health check endpoint."""
    try:
        secrets_status = validate_secrets()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "config": {
                "gemini_model": CONFIG.gemini_model,
                "max_attempts": CONFIG.max_generation_attempts,
                "checkpointing_enabled": CONFIG.enable_checkpointing
            },
            "secrets": {k: "configured" if v else "missing" for k, v in secrets_status.items()}
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# 13. LOCAL TESTING
# ============================================================================

if __name__ == "__main__":
    # For local testing
    import sys
    
    logging.getLogger().setLevel(logging.DEBUG)
    
    test_request = MobiusJobRequest(
        prompt="A modern tech startup logo with the letter M",
        brand_hex_codes=["#2563EB", "#1E40AF", "#FFFFFF"],
        brand_rules="Minimalist design, clean lines, professional appearance, blue color scheme"
    )
    
    print("\n" + "=" * 60)
    print("MOBIUS BRAND GOVERNANCE ENGINE - Local Test")
    print("=" * 60 + "\n")
    
    try:
        result = _run_mobius_job_impl(test_request)
        print("\n" + "=" * 60)
        print("RESULT:")
        print("=" * 60)
        print(json.dumps(result.model_dump(), indent=2))
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)