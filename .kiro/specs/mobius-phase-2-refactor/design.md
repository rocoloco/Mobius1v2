# Design Document: Mobius Phase 2 - Enterprise Features & Refactoring

## Overview

Mobius Phase 2 transforms the monolithic MVP into an enterprise-ready brand governance platform. This phase refactors the single-file orchestrator.py into a modular architecture following 2025 Python best practices, while adding six major feature sets that position Mobius competitively against Adobe GenStudio, Typeface, and Bynder.

The refactored system maintains the core closed-loop auto-correction workflow (Generate → Audit → Correct) while adding:
- **Brand Guidelines Ingestion**: AI-powered PDF parsing to extract structured brand rules
- **Detailed Compliance Scoring**: Category-level breakdowns with specific violation reporting
- **Multi-Brand Management**: Agency-scale portfolio management for 10-50+ brands
- **Reusable Templates**: Save and reuse successful generation configurations
- **Enhanced Async Jobs**: Webhook notifications with retry logic and job status tracking
- **Learning Foundation**: Feedback collection infrastructure for future ML training

All new features are built on LangGraph workflows, deployed on Modal serverless infrastructure, and persist to Supabase (PostgreSQL + Storage).

## Architecture

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Client[API Clients]
        Webhook[Webhook Receivers]
    end
    
    subgraph "API Layer - Modal"
        V1[/v1/* Endpoints]
        Auth[Request Validation]
        Routes[Route Handlers]
    end
    
    subgraph "Orchestration Layer - LangGraph"
        GenGraph[Generation Workflow]
        IngestGraph[Ingestion Workflow]
        GenNode[Generate Node]
        AuditNode[Audit Node]
        CorrectNode[Correct Node]
        ExtractNode[Extract Node]
        StructureNode[Structure Node]
    end
    
    subgraph "Integration Layer - Tools"
        Flux[Flux API]
        Ideogram[Ideogram API]
        Gemini[Gemini Vision]
        PDFParser[PDF Parser]
    end
    
    subgraph "Persistence Layer - Supabase"
        DB[(PostgreSQL)]
        Storage[Supabase Storage]
        Brands[brands table]
        Assets[assets table]
        Templates[templates table]
        Jobs[jobs table]
        Feedback[feedback table]
    end
    
    Client --> V1
    V1 --> Auth
    Auth --> Routes
    Routes --> GenGraph
    Routes --> IngestGraph
    GenGraph --> GenNode
    GenGraph --> AuditNode
    GenGraph --> CorrectNode
    IngestGraph --> ExtractNode
    IngestGraph --> StructureNode
    GenNode --> Flux
    GenNode --> Ideogram
    AuditNode --> Gemini
    ExtractNode --> PDFParser
    ExtractNode --> Gemini
    GenNode --> DB
    AuditNode --> DB
    IngestGraph --> DB
    Routes --> DB
    GenNode --> Storage
    IngestGraph --> Storage
    GenGraph -.webhook.-> Webhook
```

### Technology Stack

- **Language**: Python 3.11+ with type hints and async/await
- **Infrastructure**: Modal (serverless Python runtime with GPU support)
- **Orchestration**: LangGraph (state machine workflows)
- **API Framework**: Modal web endpoints with Pydantic v2 validation
- **Database**: Supabase PostgreSQL with migrations
- **File Storage**: Supabase Storage with CDN URLs
- **Image Generation**: Fal.ai (Flux.2 Pro) and Ideogram
- **Visual AI**: Google Gemini 1.5 Pro for auditing and PDF extraction
- **PDF Processing**: pdfplumber for text extraction
- **Testing**: pytest with Hypothesis for property-based tests
- **Logging**: structlog for structured JSON logging


### Project Structure

```
mobius/
├── pyproject.toml              # PEP 621 project configuration
├── .env.example                # Environment variables template
├── README.md                   # Project documentation
├── alembic.ini                 # Database migration config (if using Alembic)
├── supabase/
│   └── migrations/             # Supabase migration SQL files
│       ├── 001_initial_schema.sql
│       ├── 002_add_templates.sql
│       └── 003_add_feedback.sql
├── src/
│   └── mobius/
│       ├── __init__.py
│       ├── config.py           # Centralized configuration and secrets
│       ├── constants.py        # Application constants
│       ├── models/             # Data models and state definitions
│       │   ├── __init__.py
│       │   ├── state.py        # LangGraph state TypedDicts
│       │   ├── brand.py        # Brand entity Pydantic models
│       │   ├── asset.py        # Asset entity Pydantic models
│       │   ├── template.py     # Template entity models
│       │   ├── job.py          # Job state models
│       │   └── compliance.py   # Compliance scoring models
│       ├── nodes/              # LangGraph workflow nodes
│       │   ├── __init__.py
│       │   ├── generate.py     # Image generation node
│       │   ├── audit.py        # Compliance audit node
│       │   ├── correct.py      # Auto-correction node
│       │   ├── extract_text.py # PDF text extraction node
│       │   ├── extract_visual.py # PDF visual extraction node
│       │   └── structure.py    # Brand data structuring node
│       ├── tools/              # External service integrations
│       │   ├── __init__.py
│       │   ├── flux.py         # Flux API client
│       │   ├── ideogram.py     # Ideogram API client
│       │   ├── gemini.py       # Gemini vision client
│       │   └── pdf_parser.py   # PDF parsing utilities
│       ├── graphs/             # LangGraph workflow definitions
│       │   ├── __init__.py
│       │   ├── generation.py   # Main generation workflow
│       │   └── ingestion.py    # Brand ingestion workflow
│       ├── api/                # HTTP API endpoints
│       │   ├── __init__.py
│       │   ├── app.py          # Modal app definition
│       │   ├── routes.py       # Endpoint route handlers
│       │   ├── schemas.py      # Pydantic request/response schemas
│       │   ├── errors.py       # Error handling utilities
│       │   ├── utils.py        # Request ID and helpers
│       │   └── dependencies.py # Auth dependencies (mock for Phase 2)
│       └── storage/            # Persistence layer
│           ├── __init__.py
│           ├── database.py     # Supabase client setup with pooling
│           ├── brands.py       # Brand CRUD operations
│           ├── assets.py       # Asset CRUD operations
│           ├── templates.py    # Template CRUD operations
│           ├── jobs.py         # Job tracking operations
│           ├── feedback.py     # Feedback storage operations
│           └── files.py        # Supabase Storage operations
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/                   # Unit tests for nodes and tools
│   │   ├── test_nodes.py
│   │   ├── test_tools.py
│   │   └── test_storage.py
│   ├── integration/            # Integration tests for workflows
│   │   ├── test_generation_workflow.py
│   │   └── test_ingestion_workflow.py
│   └── property/               # Property-based tests
│       └── test_properties.py
└── scripts/
    ├── deploy.py               # Modal deployment script
    └── migrate.py              # Database migration runner
```


## Components and Interfaces

### 0. Application Constants (constants.py)

Centralized constants and default values:

```python
# src/mobius/constants.py
"""
Application constants and default values.

These are compile-time constants. For runtime configuration, see config.py.
"""

# File size limits
MAX_PDF_SIZE_BYTES = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

# Allowed MIME types
ALLOWED_PDF_MIME_TYPES = ["application/pdf"]
ALLOWED_IMAGE_MIME_TYPES = ["image/png", "image/jpeg", "image/webp"]

# Compliance scoring
DEFAULT_COMPLIANCE_THRESHOLD = 0.80  # 80%
DEFAULT_TEMPLATE_THRESHOLD = 0.95    # 95%
CATEGORY_WEIGHTS = {
    "colors": 0.30,      # Color compliance is critical for brand recognition
    "typography": 0.25,  # Typography affects readability and brand voice
    "layout": 0.25,      # Layout/composition impacts visual hierarchy
    "logo_usage": 0.20   # Logo rules (when applicable)
}

# Job management
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_JOB_EXPIRY_HOURS = 24
DEFAULT_WEBHOOK_RETRY_MAX = 5

# Learning activation
LEARNING_ACTIVATION_THRESHOLD = 50  # feedback count to activate learning

# API
API_VERSION = "v1"
REQUEST_ID_PREFIX = "req_"

# Storage buckets
BRANDS_BUCKET = "brands"
ASSETS_BUCKET = "assets"
```

### 1. Configuration Management (config.py)

Centralized configuration using Pydantic Settings with validation:

```python
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import warnings
import os

class Settings(BaseSettings):
    # Modal Secrets
    fal_api_key: str = os.getenv("FAL_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    
    # Configuration
    max_generation_attempts: int = 3
    compliance_threshold: float = 0.80
    template_threshold: float = 0.95
    job_expiry_hours: int = 24
    webhook_retry_max: int = 5
    
    # Storage buckets
    brands_bucket: str = "brands"
    assets_bucket: str = "assets"
    
    @field_validator('supabase_url')
    @classmethod
    def validate_pooler_url(cls, v: str) -> str:
        """Warn if not using pooler URL for serverless compatibility."""
        if 'pooler.supabase.com' not in v and ':6543' not in v:
            warnings.warn(
                "Consider using Supabase pooler URL (port 6543) for serverless. "
                "Direct connections may exhaust connection limits under load."
            )
        return v
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. Data Models

#### Brand Entity (models/brand.py)

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BrandColors(BaseModel):
    primary: List[str] = Field(description="Primary brand hex codes")
    secondary: List[str] = Field(description="Secondary brand hex codes")

class BrandTypography(BaseModel):
    font_families: List[str]
    sizes: Optional[dict] = None
    weights: Optional[List[str]] = None

class BrandLogo(BaseModel):
    clear_space: Optional[str] = None
    minimum_size: Optional[str] = None
    prohibited_modifications: List[str] = []

class BrandGuidelines(BaseModel):
    colors: BrandColors
    typography: BrandTypography
    logo: BrandLogo
    tone_of_voice: List[str] = []
    visual_rules: List[str] = []
    dos_and_donts: dict = {}

class Brand(BaseModel):
    brand_id: str
    organization_id: str
    name: str
    guidelines: BrandGuidelines
    pdf_url: Optional[str] = None
    logo_thumbnail_url: Optional[str] = None
    needs_review: List[str] = []
    learning_active: bool = False
    created_at: datetime
    updated_at: datetime
```


#### Compliance Scoring Models (models/compliance.py)

```python
from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Violation(BaseModel):
    category: str
    description: str
    severity: Severity
    fix_suggestion: str

class CategoryScore(BaseModel):
    category: str
    score: float = Field(ge=0, le=100)
    passed: bool
    violations: List[Violation] = []

class ComplianceScore(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    categories: List[CategoryScore]
    approved: bool
    summary: str
```

#### Job State (models/state.py)

```python
from typing import TypedDict, List, Optional
from datetime import datetime

class JobState(TypedDict):
    job_id: str
    brand_id: str
    prompt: str
    brand_hex_codes: List[str]
    brand_rules: str
    current_image_url: Optional[str]
    attempt_count: int
    audit_history: List[dict]
    compliance_scores: List[dict]
    is_approved: bool
    status: str  # "pending", "generating", "auditing", "correcting", "completed", "failed"
    created_at: datetime
    updated_at: datetime
    webhook_url: Optional[str]
    template_id: Optional[str]

class IngestionState(TypedDict):
    brand_id: str
    organization_id: str
    pdf_url: str
    extracted_text: Optional[str]
    extracted_colors: List[str]
    extracted_fonts: List[str]
    extracted_rules: List[str]
    needs_review: List[str]
    status: str  # "uploading", "extracting_text", "extracting_visual", "structuring", "completed", "failed"
```


### 3. API Utilities

#### Request ID Management (api/utils.py)

```python
# src/mobius/api/utils.py
import uuid
from contextvars import ContextVar

# Context variable for request tracking across async calls
_request_id: ContextVar[str] = ContextVar('request_id', default='')

def generate_request_id() -> str:
    """Generate unique request ID for tracing."""
    return f"req_{uuid.uuid4().hex[:12]}"

def get_request_id() -> str:
    """Get current request ID from context."""
    return _request_id.get()

def set_request_id(request_id: str) -> None:
    """Set request ID in context for current request."""
    _request_id.set(request_id)
```

#### Auth Dependencies (api/dependencies.py)

Mock authentication dependency for Phase 3 readiness:

```python
# src/mobius/api/dependencies.py
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    """User model for dependency injection."""
    user_id: str
    organization_id: str
    email: Optional[str] = None

async def get_current_user(x_user_id: Optional[str] = None) -> User:
    """
    Mock authentication dependency for Phase 2.
    
    In Phase 2: Returns user from x-user-id header or test user.
    In Phase 3: Will validate JWT token and return authenticated user.
    
    This pattern allows all route handlers to use Depends(get_current_user)
    without code changes when real auth is added in Phase 3.
    """
    if x_user_id:
        return User(
            user_id=x_user_id,
            organization_id=f"org-{x_user_id[:8]}"
        )
    
    # Default test user for development
    return User(
        user_id="test-user-123",
        organization_id="test-org-456",
        email="test@example.com"
    )

# Phase 3 implementation will look like:
# async def get_current_user(authorization: str = Header(...)) -> User:
#     token = authorization.replace("Bearer ", "")
#     payload = verify_jwt(token)
#     return User(**payload)
```

**Usage in route handlers:**

```python
from mobius.api.dependencies import get_current_user, User
from fastapi import Depends

async def generate_handler(
    request: GenerateRequest,
    user: User = Depends(get_current_user)
) -> GenerateResponse:
    """Generate asset with user context."""
    # user.user_id and user.organization_id available
    # No code changes needed when auth is added in Phase 3
    pass
```

#### Error Handling (api/errors.py)

```python
# src/mobius/api/errors.py
from pydantic import BaseModel
from typing import Optional, Any
from fastapi import HTTPException

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict[str, Any]] = None
    request_id: str

class ErrorResponse(BaseModel):
    error: ErrorDetail

class MobiusError(HTTPException):
    """Base exception for Mobius API errors."""
    
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        request_id: str,
        details: Optional[dict] = None
    ):
        self.error_response = ErrorResponse(
            error=ErrorDetail(
                code=code,
                message=message,
                details=details or {},
                request_id=request_id
            )
        )
        super().__init__(
            status_code=status_code,
            detail=self.error_response.model_dump()
        )

class ValidationError(MobiusError):
    def __init__(self, code: str, message: str, request_id: str, details: Optional[dict] = None):
        super().__init__(422, code, message, request_id, details)

class NotFoundError(MobiusError):
    def __init__(self, resource: str, resource_id: str, request_id: str):
        super().__init__(
            404,
            f"{resource.upper()}_NOT_FOUND",
            f"{resource} with ID {resource_id} does not exist",
            request_id
        )

class StorageError(MobiusError):
    def __init__(self, operation: str, request_id: str, details: Optional[dict] = None):
        super().__init__(
            500,
            "STORAGE_ERROR",
            f"Storage operation failed: {operation}",
            request_id,
            details
        )
```

### 4. API Schemas (api/schemas.py)

```python
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

# Generation API
class GenerateRequest(BaseModel):
    brand_id: str
    prompt: str
    template_id: Optional[str] = None
    webhook_url: Optional[HttpUrl] = None
    async_mode: bool = False
    idempotency_key: Optional[str] = Field(
        None,
        description="Client-provided key to prevent duplicate job creation. "
                    "If a job with this key exists and is not expired, "
                    "returns the existing job instead of creating a new one.",
        max_length=64
    )

class GenerateResponse(BaseModel):
    job_id: str
    status: str
    message: str
    image_url: Optional[str] = None
    compliance_score: Optional[float] = None
    request_id: str

# Brand Ingestion API
class IngestBrandRequest(BaseModel):
    organization_id: str
    brand_name: str
    # PDF file uploaded as multipart/form-data

class IngestBrandResponse(BaseModel):
    brand_id: str
    status: str
    pdf_url: str
    needs_review: List[str] = []
    request_id: str

# Brand Management API
class BrandListItem(BaseModel):
    brand_id: str
    name: str
    logo_thumbnail_url: Optional[str]
    asset_count: int
    avg_compliance_score: float
    last_activity: datetime

class BrandListResponse(BaseModel):
    brands: List[BrandListItem]
    total: int
    request_id: str

# Template API
class SaveTemplateRequest(BaseModel):
    asset_id: str
    template_name: str
    description: str

class TemplateResponse(BaseModel):
    template_id: str
    brand_id: str
    name: str
    description: str
    generation_params: dict
    thumbnail_url: str
    created_at: datetime

# Feedback API
class SubmitFeedbackRequest(BaseModel):
    asset_id: str
    action: str = Field(pattern="^(approve|reject)$")
    reason: Optional[str] = None

class FeedbackResponse(BaseModel):
    feedback_id: str
    brand_id: str
    total_feedback_count: int
    learning_active: bool
    request_id: str

# Job Status API
class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float = Field(ge=0, le=100)
    current_image_url: Optional[str]
    compliance_score: Optional[float]
    error: Optional[str]
    created_at: datetime
    updated_at: datetime
```


### 5. Database Client with Connection Pooling (storage/database.py)

**CRITICAL**: Supabase connection pooling is essential for serverless deployments.

```python
# src/mobius/storage/database.py
from supabase import create_client, Client
from mobius.config import settings
import structlog

logger = structlog.get_logger()

_client: Client | None = None

def get_supabase_client() -> Client:
    """
    Get Supabase client configured for serverless.
    
    IMPORTANT: Use the pooler URL (port 6543), not direct connection (port 5432).
    Format: postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
    
    This is critical for Modal's serverless architecture where many function instances
    may run concurrently. Direct connections will exhaust connection limits under load.
    """
    global _client
    if _client is None:
        _client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        logger.info("supabase_client_initialized", pooler_enabled=":6543" in settings.supabase_url)
    return _client
```

### 6. LangGraph Workflows

#### Generation Workflow (graphs/generation.py)

Enhanced version of Phase 1 workflow with compliance scoring:

```python
from langgraph.graph import StateGraph, END
from mobius.models.state import JobState
from mobius.nodes import generate, audit, correct

def create_generation_workflow():
    workflow = StateGraph(JobState)
    
    # Add nodes
    workflow.add_node("generate", generate.generate_node)
    workflow.add_node("audit", audit.audit_node)
    workflow.add_node("correct", correct.correct_node)
    
    # Set entry point
    workflow.set_entry_point("generate")
    
    # Add edges
    workflow.add_edge("generate", "audit")
    workflow.add_conditional_edges(
        "audit",
        route_after_audit,
        {
            "correct": "correct",
            "complete": END,
            "failed": END
        }
    )
    workflow.add_edge("correct", "generate")
    
    return workflow.compile()

def route_after_audit(state: JobState) -> str:
    if state["is_approved"]:
        return "complete"
    if state["attempt_count"] >= 3:
        return "failed"
    return "correct"
```

#### Brand Ingestion Workflow (graphs/ingestion.py)

New workflow for PDF processing:

```python
from langgraph.graph import StateGraph, END
from mobius.models.state import IngestionState
from mobius.nodes import extract_text, extract_visual, structure

def create_ingestion_workflow():
    workflow = StateGraph(IngestionState)
    
    # Add nodes
    workflow.add_node("extract_text", extract_text.extract_text_node)
    workflow.add_node("extract_visual", extract_visual.extract_visual_node)
    workflow.add_node("structure", structure.structure_node)
    
    # Set entry point
    workflow.set_entry_point("extract_text")
    
    # Add edges
    workflow.add_edge("extract_text", "extract_visual")
    workflow.add_edge("extract_visual", "structure")
    workflow.add_edge("structure", END)
    
    return workflow.compile()
```


### 7. Workflow Nodes

#### Enhanced Audit Node (nodes/audit.py)

Updated to return detailed compliance scoring with weighted categories:

```python
from mobius.models.state import JobState
from mobius.models.compliance import ComplianceScore, CategoryScore, Violation
from mobius.tools.gemini import GeminiClient
from mobius.constants import CATEGORY_WEIGHTS
from mobius.config import settings
import structlog

logger = structlog.get_logger()

def calculate_overall_score(categories: List[CategoryScore]) -> float:
    """
    Calculate weighted average compliance score.
    
    Categories not in CATEGORY_WEIGHTS default to equal weight
    among remaining weight allocation.
    """
    total_score = 0.0
    total_weight = 0.0
    
    for cat in categories:
        weight = CATEGORY_WEIGHTS.get(cat.category, 0.25)
        total_score += cat.score * weight
        total_weight += weight
    
    # Normalize if weights don't sum to 1.0
    if total_weight > 0:
        return total_score / total_weight
    return 0.0

async def audit_node(state: JobState) -> dict:
    """Audit image for brand compliance with detailed scoring."""
    logger.info("audit_node_start", job_id=state["job_id"])
    
    gemini = GeminiClient()
    
    # Construct detailed audit prompt
    prompt = f"""
    Analyze this image for brand compliance. Provide detailed scoring.
    
    Brand Rules: {state['brand_rules']}
    Required Colors: {', '.join(state['brand_hex_codes'])}
    
    Evaluate these categories (0-100 score each):
    1. Colors: Are brand colors used correctly?
    2. Typography: Do fonts match brand guidelines?
    3. Layout: Is composition aligned with brand standards?
    4. Logo Usage: If logo present, does it follow guidelines?
    
    Return JSON with this exact structure:
    {{
      "overall_score": <0-100>,
      "categories": [
        {{
          "category": "colors",
          "score": <0-100>,
          "passed": <true/false>,
          "violations": [
            {{
              "category": "colors",
              "description": "specific issue",
              "severity": "low|medium|high|critical",
              "fix_suggestion": "how to fix"
            }}
          ]
        }},
        // ... other categories
      ],
      "approved": <true/false>,
      "summary": "overall assessment"
    }}
    """
    
    try:
        result = await gemini.analyze_image(
            image_url=state["current_image_url"],
            prompt=prompt,
            response_format="json"
        )
        
        compliance = ComplianceScore.model_validate(result)
        
        # Recalculate overall score with proper weighting
        compliance.overall_score = calculate_overall_score(compliance.categories)
        compliance.approved = compliance.overall_score >= settings.compliance_threshold * 100
        
        return {
            "audit_history": state["audit_history"] + [compliance.model_dump()],
            "compliance_scores": state.get("compliance_scores", []) + [compliance.model_dump()],
            "is_approved": compliance.approved,
            "status": "audited"
        }
    except Exception as e:
        logger.error("audit_failed", error=str(e), job_id=state["job_id"])
        # Fail-safe: reject with generic feedback
        return {
            "audit_history": state["audit_history"] + [{
                "overall_score": 0,
                "approved": False,
                "summary": f"Audit error: {str(e)}"
            }],
            "is_approved": False,
            "status": "audit_error"
        }
```


#### PDF Text Extraction Node (nodes/extract_text.py)

```python
from mobius.models.state import IngestionState
from mobius.tools.pdf_parser import PDFParser
import structlog

logger = structlog.get_logger()

async def extract_text_node(state: IngestionState) -> dict:
    """Extract text content from brand guidelines PDF."""
    logger.info("extract_text_start", brand_id=state["brand_id"])
    
    parser = PDFParser()
    
    try:
        # Download PDF from Supabase Storage
        pdf_bytes = await download_from_storage(state["pdf_url"])
        
        # Extract text using pdfplumber
        text = parser.extract_text(pdf_bytes)
        
        # Extract structured sections
        colors_section = parser.find_section(text, ["color", "palette", "hex"])
        fonts_section = parser.find_section(text, ["typography", "font", "typeface"])
        rules_section = parser.find_section(text, ["guidelines", "rules", "standards"])
        
        return {
            "extracted_text": text,
            "status": "text_extracted"
        }
    except Exception as e:
        logger.error("text_extraction_failed", error=str(e))
        return {
            "status": "failed",
            "needs_review": state.get("needs_review", []) + ["Text extraction failed"]
        }
```

#### PDF Visual Extraction Node (nodes/extract_visual.py)

```python
from mobius.models.state import IngestionState
from mobius.tools.gemini import GeminiClient
import structlog

logger = structlog.get_logger()

async def extract_visual_node(state: IngestionState) -> dict:
    """Extract visual elements (colors, logos) from PDF using Gemini vision."""
    logger.info("extract_visual_start", brand_id=state["brand_id"])
    
    gemini = GeminiClient()
    
    prompt = """
    Analyze this brand guidelines PDF and extract:
    1. All color swatches (return hex codes)
    2. Logo variations and their usage rules
    3. Typography examples (font names if visible)
    4. Visual style patterns
    
    Return JSON:
    {
      "colors": ["#HEX1", "#HEX2", ...],
      "fonts": ["Font Name 1", ...],
      "logo_rules": ["rule 1", "rule 2", ...],
      "visual_patterns": ["pattern 1", ...]
    }
    """
    
    try:
        result = await gemini.analyze_pdf(
            pdf_url=state["pdf_url"],
            prompt=prompt,
            response_format="json"
        )
        
        return {
            "extracted_colors": result.get("colors", []),
            "extracted_fonts": result.get("fonts", []),
            "status": "visual_extracted"
        }
    except Exception as e:
        logger.error("visual_extraction_failed", error=str(e))
        return {
            "needs_review": state.get("needs_review", []) + ["Visual extraction incomplete"],
            "status": "partial_extraction"
        }
```


#### Brand Structuring Node (nodes/structure.py)

```python
from mobius.models.state import IngestionState
from mobius.models.brand import Brand, BrandGuidelines, BrandColors
from mobius.storage.brands import BrandStorage
import structlog

logger = structlog.get_logger()

async def structure_node(state: IngestionState) -> dict:
    """Structure extracted data into Brand entity and persist."""
    logger.info("structure_start", brand_id=state["brand_id"])
    
    try:
        # Combine text and visual extraction results
        guidelines = BrandGuidelines(
            colors=BrandColors(
                primary=state["extracted_colors"][:3],
                secondary=state["extracted_colors"][3:]
            ),
            typography={
                "font_families": state["extracted_fonts"]
            },
            logo={},
            visual_rules=[]
        )
        
        brand = Brand(
            brand_id=state["brand_id"],
            organization_id=state["organization_id"],
            name=f"Brand {state['brand_id'][:8]}",
            guidelines=guidelines,
            pdf_url=state["pdf_url"],
            needs_review=state.get("needs_review", [])
        )
        
        # Persist to database
        storage = BrandStorage()
        await storage.create_brand(brand)
        
        return {
            "status": "completed"
        }
    except Exception as e:
        logger.error("structuring_failed", error=str(e))
        return {
            "status": "failed",
            "needs_review": state.get("needs_review", []) + ["Structuring failed"]
        }
```

### 8. Storage Layer

#### Brand Storage (storage/brands.py)

```python
from mobius.models.brand import Brand
from mobius.storage.database import get_supabase_client
from typing import List, Optional
import structlog

logger = structlog.get_logger()

class BrandStorage:
    def __init__(self):
        self.client = get_supabase_client()
    
    async def create_brand(self, brand: Brand) -> Brand:
        """Create a new brand in the database."""
        data = brand.model_dump()
        result = self.client.table("brands").insert(data).execute()
        return Brand.model_validate(result.data[0])
    
    async def get_brand(self, brand_id: str) -> Optional[Brand]:
        """Retrieve a brand by ID."""
        result = self.client.table("brands").select("*").eq("brand_id", brand_id).execute()
        if result.data:
            return Brand.model_validate(result.data[0])
        return None
    
    async def list_brands(self, organization_id: str, limit: int = 100) -> List[Brand]:
        """List all brands for an organization."""
        result = self.client.table("brands").select("*").eq("organization_id", organization_id).limit(limit).execute()
        return [Brand.model_validate(b) for b in result.data]
    
    async def update_brand(self, brand_id: str, updates: dict) -> Brand:
        """Update brand fields."""
        result = self.client.table("brands").update(updates).eq("brand_id", brand_id).execute()
        return Brand.model_validate(result.data[0])
    
    async def delete_brand(self, brand_id: str) -> bool:
        """Soft delete a brand."""
        self.client.table("brands").update({"deleted_at": "now()"}).eq("brand_id", brand_id).execute()
        return True
```


#### File Storage (storage/files.py)

```python
from mobius.storage.database import get_supabase_client
from typing import BinaryIO
import structlog

logger = structlog.get_logger()

class FileStorage:
    def __init__(self):
        self.client = get_supabase_client()
    
    async def upload_pdf(self, file: BinaryIO, brand_id: str) -> str:
        """Upload brand guidelines PDF to Supabase Storage."""
        bucket = "brands"
        path = f"{brand_id}/guidelines.pdf"
        
        result = self.client.storage.from_(bucket).upload(path, file)
        
        # Get public URL
        url = self.client.storage.from_(bucket).get_public_url(path)
        return url
    
    async def upload_image(self, image_url: str, asset_id: str) -> str:
        """Download image from generation service and upload to Supabase Storage."""
        import httpx
        
        # Download from generation service
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            image_bytes = response.content
        
        # Upload to Supabase
        bucket = "assets"
        path = f"{asset_id}/image.png"
        
        self.client.storage.from_(bucket).upload(path, image_bytes)
        
        # Get public CDN URL
        url = self.client.storage.from_(bucket).get_public_url(path)
        return url
    
    async def delete_file(self, bucket: str, path: str) -> bool:
        """Delete a file from Supabase Storage."""
        self.client.storage.from_(bucket).remove([path])
        return True
```


## Data Models

### Database Schema (Supabase PostgreSQL)

#### Migration 001: Initial Schema

```sql
-- brands table
CREATE TABLE brands (
    brand_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    guidelines JSONB NOT NULL,
    pdf_url TEXT,
    logo_thumbnail_url TEXT,
    needs_review TEXT[] DEFAULT '{}',
    learning_active BOOLEAN DEFAULT FALSE,
    feedback_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_brands_org ON brands(organization_id) WHERE deleted_at IS NULL;

-- assets table
CREATE TABLE assets (
    asset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(brand_id),
    job_id UUID NOT NULL,
    prompt TEXT NOT NULL,
    image_url TEXT NOT NULL,
    compliance_score FLOAT,
    compliance_details JSONB,
    generation_params JSONB,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_assets_brand ON assets(brand_id);
CREATE INDEX idx_assets_job ON assets(job_id);

-- jobs table
CREATE TABLE jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(brand_id),
    status VARCHAR(50) NOT NULL,
    progress FLOAT DEFAULT 0,
    state JSONB NOT NULL,
    webhook_url TEXT,
    webhook_attempts INT DEFAULT 0,
    idempotency_key VARCHAR(64),
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours'
);

CREATE INDEX idx_jobs_brand ON jobs(brand_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_expires ON jobs(expires_at) WHERE expires_at IS NOT NULL;
CREATE UNIQUE INDEX idx_jobs_idempotency ON jobs(idempotency_key) 
    WHERE idempotency_key IS NOT NULL AND expires_at > NOW();
```

#### Migration 002: Templates

```sql
-- templates table
CREATE TABLE templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(brand_id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    generation_params JSONB NOT NULL,
    thumbnail_url TEXT,
    source_asset_id UUID REFERENCES assets(asset_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_templates_brand ON templates(brand_id) WHERE deleted_at IS NULL;
```

#### Migration 003: Feedback

```sql
-- feedback table
CREATE TABLE feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES assets(asset_id),
    brand_id UUID NOT NULL REFERENCES brands(brand_id),
    action VARCHAR(20) NOT NULL CHECK (action IN ('approve', 'reject')),
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_feedback_brand ON feedback(brand_id);
CREATE INDEX idx_feedback_asset ON feedback(asset_id);

-- Trigger to update learning_active flag
CREATE OR REPLACE FUNCTION update_learning_active()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE brands
    SET 
        feedback_count = (SELECT COUNT(*) FROM feedback WHERE brand_id = NEW.brand_id),
        learning_active = (SELECT COUNT(*) FROM feedback WHERE brand_id = NEW.brand_id) >= 50
    WHERE brand_id = NEW.brand_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER feedback_learning_trigger
AFTER INSERT ON feedback
FOR EACH ROW
EXECUTE FUNCTION update_learning_active();
```


### Supabase Storage Buckets

```sql
-- Create storage buckets
INSERT INTO storage.buckets (id, name, public) VALUES
    ('brands', 'brands', true),
    ('assets', 'assets', true);

-- Set size limits
UPDATE storage.buckets SET file_size_limit = 52428800 WHERE id = 'brands';  -- 50MB
UPDATE storage.buckets SET file_size_limit = 10485760 WHERE id = 'assets';  -- 10MB

-- Set allowed MIME types
UPDATE storage.buckets SET allowed_mime_types = ARRAY['application/pdf'] WHERE id = 'brands';
UPDATE storage.buckets SET allowed_mime_types = ARRAY['image/png', 'image/jpeg', 'image/webp'] WHERE id = 'assets';
```

## Background Jobs

### Job Cleanup Scheduler

Automated cleanup of expired jobs runs hourly via Modal cron:

```python
# src/mobius/api/app.py

@app.function(
    image=image, 
    secrets=secrets,
    schedule=modal.Cron("0 * * * *")  # Run hourly
)
async def cleanup_expired_jobs():
    """
    Cleanup expired jobs and associated temporary files.
    
    Runs hourly via Modal cron schedule.
    """
    logger = structlog.get_logger()
    logger.info("cleanup_job_started")
    
    client = get_supabase_client()
    
    try:
        # Find expired jobs
        expired = client.table("jobs").select("job_id, state").lt(
            "expires_at", "now()"
        ).execute()
        
        deleted_count = 0
        for job in expired.data:
            job_id = job["job_id"]
            
            # Delete any temporary files associated with failed jobs
            # (Successful jobs have assets moved to permanent storage)
            if job.get("state", {}).get("status") == "failed":
                try:
                    await FileStorage().delete_file("assets", f"temp/{job_id}")
                except Exception:
                    pass  # Ignore if file doesn't exist
            
            # Delete job record
            client.table("jobs").delete().eq("job_id", job_id).execute()
            deleted_count += 1
        
        logger.info("cleanup_job_completed", deleted_count=deleted_count)
        
    except Exception as e:
        logger.error("cleanup_job_failed", error=str(e))
        raise
```

## API Endpoints

### Version 1 API Routes

All endpoints prefixed with `/v1/`:

#### Route Handler Examples

```python
# src/mobius/api/routes.py
from mobius.api.utils import generate_request_id, set_request_id, get_request_id
from mobius.api.errors import ValidationError, NotFoundError
from mobius.api.schemas import GenerateRequest, GenerateResponse
from mobius.constants import MAX_PDF_SIZE_BYTES, ALLOWED_PDF_MIME_TYPES
from mobius.storage.jobs import JobStorage
import structlog

logger = structlog.get_logger()

async def generate_handler(request: GenerateRequest) -> GenerateResponse:
    """Handle asset generation with idempotency support."""
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info("generation_request_received", 
        request_id=request_id,
        brand_id=request.brand_id,
        async_mode=request.async_mode
    )
    
    try:
        # Check for existing job with same idempotency key
        if request.idempotency_key:
            existing_job = await JobStorage().get_by_idempotency_key(
                request.idempotency_key
            )
            if existing_job:
                logger.info("idempotent_request_matched",
                    request_id=request_id,
                    existing_job_id=existing_job.job_id,
                    idempotency_key=request.idempotency_key
                )
                return GenerateResponse(
                    job_id=existing_job.job_id,
                    status=existing_job.status,
                    message="Existing job returned (idempotent request)",
                    request_id=request_id
                )
        
        # Create new job and execute workflow
        # ... implementation
        
    except Exception as e:
        logger.error("generation_failed", request_id=request_id, error=str(e))
        raise

async def ingest_brand_handler(
    organization_id: str,
    brand_name: str,
    file: bytes,
    content_type: str,
    filename: str
) -> IngestBrandResponse:
    """Handle brand guidelines PDF ingestion with validation."""
    request_id = generate_request_id()
    set_request_id(request_id)
    
    logger.info("ingest_request_received", 
        request_id=request_id,
        organization_id=organization_id,
        filename=filename
    )
    
    # Validate file size BEFORE any processing
    if len(file) > MAX_PDF_SIZE_BYTES:
        raise ValidationError(
            code="FILE_TOO_LARGE",
            message=f"PDF exceeds maximum size of 50MB. Received: {len(file) / 1024 / 1024:.1f}MB",
            request_id=request_id
        )
    
    # Validate MIME type
    if content_type not in ALLOWED_PDF_MIME_TYPES:
        raise ValidationError(
            code="INVALID_FILE_TYPE",
            message=f"Only PDF files are accepted. Received: {content_type}",
            request_id=request_id
        )
    
    # Validate PDF is readable (basic header check)
    if not file[:4] == b'%PDF':
        raise ValidationError(
            code="INVALID_PDF",
            message="File does not appear to be a valid PDF",
            request_id=request_id
        )
    
    # Continue with upload and ingestion workflow
    # ... implementation
```

#### Brand Management

```
POST   /v1/brands/ingest          - Upload and ingest brand guidelines PDF
GET    /v1/brands                 - List all brands for organization
GET    /v1/brands/{brand_id}      - Get brand details
PATCH  /v1/brands/{brand_id}      - Update brand metadata
DELETE /v1/brands/{brand_id}      - Soft delete brand
```

#### Asset Generation

```
POST   /v1/generate               - Generate brand-compliant asset (sync or async)
GET    /v1/jobs/{job_id}          - Get job status and results
POST   /v1/jobs/{job_id}/cancel   - Cancel running job
```

#### Templates

```
POST   /v1/templates              - Save asset as template
GET    /v1/templates              - List templates for brand
GET    /v1/templates/{template_id} - Get template details
DELETE /v1/templates/{template_id} - Delete template
```

#### Feedback

```
POST   /v1/assets/{asset_id}/feedback - Submit approval/rejection feedback
GET    /v1/brands/{brand_id}/feedback - Get feedback statistics
```

#### System

```
GET    /v1/health                 - Health check
GET    /v1/docs                   - OpenAPI documentation
```


## Error Handling

### Error Response Format

All errors follow a consistent structure:

```json
{
  "error": {
    "code": "BRAND_NOT_FOUND",
    "message": "Brand with ID abc123 does not exist",
    "details": {},
    "request_id": "req_xyz789"
  }
}
```

### Error Codes

- `VALIDATION_ERROR` (422): Request validation failed
- `BRAND_NOT_FOUND` (404): Brand ID does not exist
- `ASSET_NOT_FOUND` (404): Asset ID does not exist
- `TEMPLATE_NOT_FOUND` (404): Template ID does not exist
- `JOB_NOT_FOUND` (404): Job ID does not exist
- `PDF_PARSE_ERROR` (400): PDF file could not be parsed
- `FILE_TOO_LARGE` (413): Uploaded file exceeds size limit
- `GENERATION_FAILED` (500): Image generation service error
- `AUDIT_FAILED` (500): Compliance audit service error
- `STORAGE_ERROR` (500): File storage operation failed
- `DATABASE_ERROR` (500): Database operation failed
- `WEBHOOK_FAILED` (500): Webhook delivery failed after retries

### Retry Logic

#### Webhook Retries

```python
import httpx
import asyncio
from typing import Optional

async def deliver_webhook(url: str, payload: dict, attempt: int = 1, max_attempts: int = 5) -> bool:
    """Deliver webhook with exponential backoff."""
    backoff_seconds = 2 ** attempt  # 2, 4, 8, 16, 32 seconds
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return True
    except Exception as e:
        logger.warning("webhook_failed", attempt=attempt, error=str(e))
        
        if attempt < max_attempts:
            await asyncio.sleep(backoff_seconds)
            return await deliver_webhook(url, payload, attempt + 1, max_attempts)
        
        logger.error("webhook_exhausted", url=url)
        return False
```

#### External API Retries

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_generation_api(prompt: str) -> str:
    """Call image generation API with automatic retries."""
    # Implementation
    pass
```


## Testing Strategy

### Testing Approach

The system uses a dual testing strategy combining unit tests for specific scenarios and property-based tests for universal correctness guarantees.

**Unit Tests** will cover:
- Individual node functions with mocked dependencies
- Storage layer CRUD operations
- API endpoint request/response handling
- Error handling and edge cases
- Webhook delivery logic

**Integration Tests** will verify:
- Complete workflow execution (generation and ingestion)
- Database transactions and rollbacks
- File upload and storage operations
- Multi-step API interactions

**Property-Based Tests** will verify:
- Universal properties that hold across all valid inputs
- State transitions in workflows
- Data structure invariants
- Compliance scoring consistency

**Property-Based Testing Library**: We will use **Hypothesis** for Python, which provides robust property-based testing with automatic test case generation and shrinking.

**Test Configuration**: Each property-based test will run a minimum of 100 iterations to ensure thorough coverage of the input space.

### Test Infrastructure

```python
# tests/conftest.py
import pytest
from mobius.storage.database import get_supabase_client
from unittest.mock import Mock

@pytest.fixture
def mock_supabase():
    """Mock Supabase client for unit tests."""
    return Mock()

@pytest.fixture
def mock_gemini():
    """Mock Gemini API client."""
    mock = Mock()
    mock.analyze_image.return_value = {
        "overall_score": 85,
        "approved": True,
        "categories": []
    }
    return mock

@pytest.fixture
def sample_brand():
    """Sample brand entity for testing."""
    from mobius.models.brand import Brand, BrandGuidelines, BrandColors
    return Brand(
        brand_id="test-brand-123",
        organization_id="test-org-456",
        name="Test Brand",
        guidelines=BrandGuidelines(
            colors=BrandColors(
                primary=["#FF0000", "#00FF00"],
                secondary=["#0000FF"]
            ),
            typography={"font_families": ["Arial"]},
            logo={},
            visual_rules=[]
        )
    )
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Brand ingestion creates valid entity

*For any* valid PDF file uploaded through the ingestion workflow, when the workflow completes successfully, the resulting Brand entity should contain non-empty guidelines with at least one color extracted.

**Validates: Requirements 2.2, 2.3**

### Property 2: Compliance score is bounded

*For any* audit result returned by the audit node, the overall compliance score should be between 0 and 100 inclusive, and each category score should also be between 0 and 100 inclusive.

**Validates: Requirements 3.1**

### Property 3: Category scores aggregate correctly

*For any* compliance result with multiple category scores, the overall score should be the weighted average of all category scores.

**Validates: Requirements 3.2**

### Property 4: Low compliance triggers correction

*For any* job state where the compliance score is below 80 percent and attempt count is less than 3, the routing function should direct to the correction node.

**Validates: Requirements 3.4**

### Property 5: High compliance approves asset

*For any* job state where all category scores are above 90 percent, the is_approved flag should be set to true.

**Validates: Requirements 3.5**

### Property 6: Brand ID is required for generation

*For any* generation request, if the brand_id parameter is missing or invalid, the system should return a 422 validation error.

**Validates: Requirements 4.2**

### Property 7: Template threshold enforcement

*For any* asset with compliance score below 95 percent, attempting to save it as a template should be rejected.

**Validates: Requirements 5.1**

### Property 8: Template parameters are preserved

*For any* template saved from an asset, when that template is retrieved and applied, the generation parameters should match exactly the original asset's parameters.

**Validates: Requirements 5.4**

### Property 9: Async job returns immediately

*For any* generation request with async_mode set to true, the API should return a job_id within 500 milliseconds.

**Validates: Requirements 6.1**

### Property 10: Webhook retry exhaustion

*For any* webhook URL that fails delivery, after 5 retry attempts with exponential backoff, the system should mark the webhook as failed and stop retrying.

**Validates: Requirements 6.5**

### Property 11: Feedback increments count

*For any* brand, when a feedback event is submitted for an asset belonging to that brand, the brand's feedback_count should increase by exactly one.

**Validates: Requirements 7.1, 7.2**

### Property 12: Learning activation threshold

*For any* brand, when the feedback_count reaches 50, the learning_active flag should be automatically set to true.

**Validates: Requirements 7.3**

### Property 13: File storage returns CDN URL

*For any* file uploaded to Supabase Storage, the returned URL should be a valid HTTPS URL pointing to the Supabase CDN.

**Validates: Requirements 10.3**

### Property 14: Soft delete preserves data

*For any* brand that is deleted, the brand record should remain in the database with deleted_at timestamp set, and associated assets should remain accessible.

**Validates: Requirements 4.5**

### Property 15: API versioning consistency

*For any* API endpoint, the URL path should start with the version prefix v1.

**Validates: Requirements 9.1**

### Property 16: Idempotency key prevents duplicates

*For any* two generation requests with the same non-null idempotency_key submitted within the job expiry window, the system should return the same job_id for both requests.

**Validates: Requirements 6.1 (enhanced)**


## Implementation Notes

### Modal Deployment

The refactored system maintains Modal deployment but with modular organization:

```python
# src/mobius/api/app.py
import modal

# Define Modal app
app = modal.App("mobius-v2")

# Define image with dependencies
image = modal.Image.debian_slim().pip_install(
    "langgraph",
    "pydantic",
    "pydantic-settings",
    "supabase",
    "google-generativeai",
    "pdfplumber",
    "httpx",
    "structlog",
    "tenacity"
)

# Define secrets
secrets = [
    modal.Secret.from_name("mobius-secrets")
]

# Import route handlers
from mobius.api.routes import (
    generate_handler,
    ingest_brand_handler,
    list_brands_handler,
    # ... other handlers
)

# Register endpoints
@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST", label="generate")
async def generate_endpoint(request: dict):
    return await generate_handler(request)

@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST", label="ingest")
async def ingest_endpoint(request: dict):
    return await ingest_brand_handler(request)

# ... register other endpoints
```

### Supabase Connection Pooling

**CRITICAL FOR PRODUCTION**: All database connections MUST use the Supabase connection pooler URL (port 6543) rather than the direct connection (port 5432). This is essential for Modal's serverless architecture where many function instances may run concurrently.

**Configuration**:
1. In Supabase dashboard: Settings > Database > Connection Pooling
2. Use the "Transaction" mode pooler URL
3. Format: `postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`

Without connection pooling, you will hit Supabase's connection limits (default: 60 connections) quickly under load, causing database errors.

### Configuration Management

Environment variables are loaded from Modal secrets:

```python
# src/mobius/config.py
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Required secrets
    fal_api_key: str = os.getenv("FAL_KEY")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY")
    supabase_url: str = os.getenv("SUPABASE_URL")  # Use pooler URL!
    supabase_key: str = os.getenv("SUPABASE_KEY")
    
    # Optional configuration
    max_generation_attempts: int = 3
    compliance_threshold: float = 0.80
    template_threshold: float = 0.95
    job_expiry_hours: int = 24
    webhook_retry_max: int = 5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### Logging Strategy

Structured logging with contextual information:

```python
import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Usage in nodes
logger.info("generation_started", 
    job_id=state["job_id"],
    brand_id=state["brand_id"],
    attempt=state["attempt_count"]
)
```


### Migration Strategy

#### Phase 1 to Phase 2 Migration

1. **Code Refactoring** (Week 1-2):
   - Extract nodes from orchestrator.py into separate files
   - Create storage layer abstractions
   - Set up project structure with pyproject.toml
   - Maintain backward compatibility with Phase 1 API

2. **Database Setup** (Week 2):
   - Run initial schema migrations
   - Create Supabase Storage buckets
   - Set up bucket policies and size limits

3. **Feature Rollout** (Week 3-12):
   - Deploy features incrementally
   - Run both old and new endpoints in parallel during transition
   - Migrate existing data to new schema
   - Deprecate Phase 1 endpoints after validation

#### Backward Compatibility

During migration, maintain Phase 1 endpoint:

```python
@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST", label="run_mobius_job")
async def legacy_endpoint(request: dict):
    """Legacy Phase 1 endpoint - redirects to v1 API."""
    logger.warning("legacy_endpoint_used", message="Please migrate to /v1/generate")
    
    # Transform to v1 format
    v1_request = {
        "brand_id": "default",  # Create default brand for legacy requests
        "prompt": request["prompt"],
        "async_mode": False
    }
    
    return await generate_handler(v1_request)
```

### Performance Considerations

#### Database Indexing

Critical indexes for query performance:
- `idx_brands_org`: Fast brand listing by organization
- `idx_assets_brand`: Fast asset lookup by brand
- `idx_jobs_status`: Fast job status queries
- `idx_feedback_brand`: Fast feedback aggregation

#### Caching Strategy

Future optimization opportunities:
- Cache brand guidelines in Redis for fast access
- Cache template configurations
- Cache compliance scoring prompts
- Implement CDN caching for generated images

#### Async Processing

All I/O operations use async/await:
- Database queries
- External API calls (Flux, Gemini)
- File uploads/downloads
- Webhook deliveries


## Deployment

### Prerequisites

1. Modal account with CLI configured (`modal token set`)
2. Supabase project created with:
   - PostgreSQL database
   - Storage buckets configured
   - API keys generated
3. External API keys:
   - Fal.ai API key
   - Google Gemini API key

### Setup Steps

#### 1. Create Modal Secret

```bash
modal secret create mobius-secrets \
  FAL_KEY=<your-fal-key> \
  GEMINI_API_KEY=<your-gemini-key> \
  SUPABASE_URL=<your-supabase-url> \
  SUPABASE_KEY=<your-supabase-key>
```

#### 2. Run Database Migrations

```bash
# Using Supabase CLI
supabase db push

# Or manually execute migration files
psql $SUPABASE_URL -f supabase/migrations/001_initial_schema.sql
psql $SUPABASE_URL -f supabase/migrations/002_add_templates.sql
psql $SUPABASE_URL -f supabase/migrations/003_add_feedback.sql
```

#### 3. Create Storage Buckets

```bash
# Using Supabase dashboard or CLI
supabase storage create brands --public
supabase storage create assets --public
```

#### 4. Deploy to Modal

```bash
# Deploy the application
modal deploy src/mobius/api/app.py

# Get endpoint URLs
modal app show mobius-v2
```

### Environment Variables

Create `.env` file for local development:

```env
FAL_KEY=fal_xxx
GEMINI_API_KEY=AIzaSyxxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx
MAX_GENERATION_ATTEMPTS=3
COMPLIANCE_THRESHOLD=0.80
TEMPLATE_THRESHOLD=0.95
JOB_EXPIRY_HOURS=24
WEBHOOK_RETRY_MAX=5
```

### Testing Deployment

```bash
# Test health endpoint
curl https://your-modal-app.modal.run/v1/health

# Test brand ingestion
curl -X POST https://your-modal-app.modal.run/v1/brands/ingest \
  -F "organization_id=org-123" \
  -F "brand_name=Test Brand" \
  -F "file=@brand-guidelines.pdf"

# Test generation
curl -X POST https://your-modal-app.modal.run/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": "brand-xxx",
    "prompt": "A modern tech startup logo",
    "async_mode": false
  }'
```


## Monitoring and Observability

### Structured Logging

All components emit structured JSON logs:

```json
{
  "timestamp": "2025-12-05T10:30:45.123Z",
  "level": "info",
  "event": "generation_completed",
  "job_id": "job-abc123",
  "brand_id": "brand-xyz789",
  "attempt_count": 2,
  "compliance_score": 87.5,
  "duration_ms": 4523
}
```

### Key Metrics to Track

- **Generation Metrics**:
  - Average attempts per job
  - Success rate (approved / total)
  - Average compliance score
  - Generation latency (p50, p95, p99)

- **Ingestion Metrics**:
  - PDF parsing success rate
  - Average extraction time
  - Items flagged for review percentage

- **System Metrics**:
  - API request rate
  - Error rate by endpoint
  - Webhook delivery success rate
  - Database query latency

### Health Checks

```python
@app.function(image=image)
@modal.web_endpoint(method="GET", label="health")
async def health_check():
    """System health check endpoint."""
    checks = {
        "database": await check_database(),
        "storage": await check_storage(),
        "gemini": await check_gemini(),
        "flux": await check_flux()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }, status_code
```

## Meta-Learning with Privacy Controls

### Overview

The meta-learning system enables Mobius to improve generation quality over time by learning from user feedback while maintaining strict privacy controls. The system offers three privacy tiers that balance learning effectiveness with data protection, making it suitable for both privacy-conscious enterprises and organizations willing to contribute to industry-wide improvements.

### Privacy Tiers

#### Tier 1: Off (Manual Only)
- No automated learning
- All feedback stored but not used for training
- Suitable for highly regulated industries
- Manual review and adjustment only

#### Tier 2: Private (Default)
- Learn from own brand's feedback only
- Isolated pattern extraction per brand
- Brand-specific prompt optimization
- No data sharing with other brands
- Full data ownership and control

#### Tier 3: Shared (Opt-in)
- Contribute to anonymized industry patterns
- Differential privacy noise injection
- K-anonymity enforcement (minimum 5 brands)
- Pattern contributor anonymization
- Aggregate-only storage (no individual brand traces)
- Network effects with privacy preservation

### Architecture

```mermaid
graph TB
    subgraph "Feedback Collection"
        Feedback[User Feedback]
        FeedbackDB[(Feedback Table)]
    end
    
    subgraph "Private Learning (Per-Brand)"
        PrivateExtract[Pattern Extraction]
        PrivateOptimize[Prompt Optimization]
        PrivateStore[(Brand Learning Data)]
    end
    
    subgraph "Shared Learning (Opt-in)"
        Aggregate[Cohort Aggregation]
        DiffPrivacy[Differential Privacy]
        KAnonymity[K-Anonymity Check]
        SharedStore[(Aggregate Patterns)]
    end
    
    subgraph "Transparency"
        Dashboard[Learning Dashboard]
        AuditLog[Audit Log]
        Export[Data Export]
        Delete[Data Deletion]
    end
    
    Feedback --> FeedbackDB
    FeedbackDB --> PrivateExtract
    PrivateExtract --> PrivateOptimize
    PrivateOptimize --> PrivateStore
    
    FeedbackDB --> Aggregate
    Aggregate --> DiffPrivacy
    DiffPrivacy --> KAnonymity
    KAnonymity --> SharedStore
    
    PrivateStore --> Dashboard
    SharedStore --> Dashboard
    Dashboard --> AuditLog
    Dashboard --> Export
    Dashboard --> Delete
```

### Data Models

#### Learning Privacy Settings (models/learning.py)

```python
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from datetime import datetime

class PrivacyTier(str, Enum):
    OFF = "off"           # No learning
    PRIVATE = "private"   # Brand-only learning (default)
    SHARED = "shared"     # Anonymized industry learning

class LearningSettings(BaseModel):
    brand_id: str
    privacy_tier: PrivacyTier = PrivacyTier.PRIVATE
    consent_date: Optional[datetime] = None
    consent_version: str = "1.0"
    data_retention_days: int = 365
    
class BrandPattern(BaseModel):
    pattern_id: str
    brand_id: str
    pattern_type: str  # "color_preference", "style_preference", "prompt_optimization"
    pattern_data: dict
    confidence_score: float
    sample_count: int
    created_at: datetime
    updated_at: datetime

class IndustryPattern(BaseModel):
    pattern_id: str
    cohort: str  # "fashion", "tech", "food", etc.
    pattern_type: str
    pattern_data: dict
    contributor_count: int  # Must be >= 5 for k-anonymity
    noise_level: float  # Differential privacy noise
    created_at: datetime
    updated_at: datetime

class LearningAuditLog(BaseModel):
    log_id: str
    brand_id: str
    action: str  # "pattern_extracted", "prompt_optimized", "data_exported", "data_deleted"
    details: dict
    timestamp: datetime
```

### Database Schema

#### Migration 004: Learning and Privacy

```sql
-- learning_settings table
CREATE TABLE learning_settings (
    brand_id UUID PRIMARY KEY REFERENCES brands(brand_id),
    privacy_tier VARCHAR(20) NOT NULL DEFAULT 'private' CHECK (privacy_tier IN ('off', 'private', 'shared')),
    consent_date TIMESTAMPTZ,
    consent_version VARCHAR(10) NOT NULL DEFAULT '1.0',
    data_retention_days INT NOT NULL DEFAULT 365,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- brand_patterns table (private learning)
CREATE TABLE brand_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(brand_id),
    pattern_type VARCHAR(50) NOT NULL,
    pattern_data JSONB NOT NULL,
    confidence_score FLOAT NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    sample_count INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_brand_patterns_brand ON brand_patterns(brand_id);
CREATE INDEX idx_brand_patterns_type ON brand_patterns(pattern_type);

-- industry_patterns table (shared learning)
CREATE TABLE industry_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cohort VARCHAR(50) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_data JSONB NOT NULL,
    contributor_count INT NOT NULL CHECK (contributor_count >= 5),  -- K-anonymity
    noise_level FLOAT NOT NULL,  -- Differential privacy
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_industry_patterns_cohort ON industry_patterns(cohort);
CREATE INDEX idx_industry_patterns_type ON industry_patterns(pattern_type);

-- learning_audit_log table
CREATE TABLE learning_audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(brand_id),
    action VARCHAR(50) NOT NULL,
    details JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_learning_audit_brand ON learning_audit_log(brand_id);
CREATE INDEX idx_learning_audit_timestamp ON learning_audit_log(timestamp);
```

### Components

#### Private Learning Engine (learning/private.py)

```python
from mobius.models.learning import BrandPattern, LearningSettings, PrivacyTier
from mobius.storage.database import get_supabase_client
import structlog

logger = structlog.get_logger()

class PrivateLearningEngine:
    """Per-brand learning with full data isolation."""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def extract_patterns(self, brand_id: str) -> List[BrandPattern]:
        """Extract patterns from brand's feedback history."""
        logger.info("extracting_private_patterns", brand_id=brand_id)
        
        # Check privacy settings
        settings = await self._get_settings(brand_id)
        if settings.privacy_tier == PrivacyTier.OFF:
            logger.info("learning_disabled", brand_id=brand_id)
            return []
        
        # Get feedback data
        feedback = self.client.table("feedback").select("*").eq("brand_id", brand_id).execute()
        
        patterns = []
        
        # Extract color preferences
        color_pattern = self._extract_color_preferences(feedback.data)
        if color_pattern:
            patterns.append(color_pattern)
        
        # Extract style preferences
        style_pattern = self._extract_style_preferences(feedback.data)
        if style_pattern:
            patterns.append(style_pattern)
        
        # Store patterns
        for pattern in patterns:
            await self._store_pattern(pattern)
        
        # Log action
        await self._log_action(brand_id, "pattern_extracted", {"pattern_count": len(patterns)})
        
        return patterns
    
    async def optimize_prompt(self, brand_id: str, base_prompt: str) -> str:
        """Optimize prompt based on brand's learned patterns."""
        patterns = await self._get_patterns(brand_id)
        
        # Apply learned optimizations
        optimized = base_prompt
        for pattern in patterns:
            if pattern.pattern_type == "prompt_optimization":
                optimized = self._apply_optimization(optimized, pattern.pattern_data)
        
        return optimized
    
    async def export_learning_data(self, brand_id: str) -> dict:
        """Export all learning data for a brand (GDPR compliance)."""
        patterns = await self._get_patterns(brand_id)
        audit_log = await self._get_audit_log(brand_id)
        
        await self._log_action(brand_id, "data_exported", {})
        
        return {
            "brand_id": brand_id,
            "patterns": [p.model_dump() for p in patterns],
            "audit_log": [log.model_dump() for log in audit_log]
        }
    
    async def delete_learning_data(self, brand_id: str) -> bool:
        """Delete all learning data for a brand (right to deletion)."""
        logger.info("deleting_learning_data", brand_id=brand_id)
        
        # Delete patterns
        self.client.table("brand_patterns").delete().eq("brand_id", brand_id).execute()
        
        # Log deletion
        await self._log_action(brand_id, "data_deleted", {})
        
        return True
```

#### Shared Learning Engine (learning/shared.py)

```python
from mobius.models.learning import IndustryPattern, PrivacyTier
from mobius.storage.database import get_supabase_client
import numpy as np
import structlog

logger = structlog.get_logger()

class SharedLearningEngine:
    """Industry-wide learning with differential privacy."""
    
    MIN_CONTRIBUTORS = 5  # K-anonymity threshold
    NOISE_SCALE = 0.1     # Differential privacy noise
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def aggregate_patterns(self, cohort: str, pattern_type: str) -> Optional[IndustryPattern]:
        """Aggregate patterns from multiple brands with privacy preservation."""
        logger.info("aggregating_shared_patterns", cohort=cohort, pattern_type=pattern_type)
        
        # Get all brands in cohort with shared learning enabled
        brands = await self._get_shared_learning_brands(cohort)
        
        # K-anonymity check
        if len(brands) < self.MIN_CONTRIBUTORS:
            logger.warning("insufficient_contributors", 
                          cohort=cohort, 
                          count=len(brands),
                          required=self.MIN_CONTRIBUTORS)
            return None
        
        # Collect patterns from all contributing brands
        all_patterns = []
        for brand_id in brands:
            patterns = await self._get_brand_patterns(brand_id, pattern_type)
            all_patterns.extend(patterns)
        
        # Aggregate with differential privacy
        aggregated_data = self._aggregate_with_privacy(all_patterns)
        
        # Create industry pattern
        industry_pattern = IndustryPattern(
            pattern_id=str(uuid.uuid4()),
            cohort=cohort,
            pattern_type=pattern_type,
            pattern_data=aggregated_data,
            contributor_count=len(brands),
            noise_level=self.NOISE_SCALE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store pattern
        await self._store_industry_pattern(industry_pattern)
        
        return industry_pattern
    
    def _aggregate_with_privacy(self, patterns: List[dict]) -> dict:
        """Apply differential privacy noise to aggregated data."""
        # Compute aggregate statistics
        aggregated = self._compute_aggregates(patterns)
        
        # Add Laplace noise for differential privacy
        for key, value in aggregated.items():
            if isinstance(value, (int, float)):
                noise = np.random.laplace(0, self.NOISE_SCALE)
                aggregated[key] = value + noise
        
        return aggregated
    
    async def _get_shared_learning_brands(self, cohort: str) -> List[str]:
        """Get brands that opted into shared learning."""
        result = self.client.table("brands").select("brand_id").eq(
            "cohort", cohort
        ).execute()
        
        brand_ids = [b["brand_id"] for b in result.data]
        
        # Filter by privacy settings
        shared_brands = []
        for brand_id in brand_ids:
            settings = self.client.table("learning_settings").select("*").eq(
                "brand_id", brand_id
            ).execute()
            
            if settings.data and settings.data[0]["privacy_tier"] == PrivacyTier.SHARED:
                shared_brands.append(brand_id)
        
        return shared_brands
```

### API Endpoints

#### Learning Management

```
POST   /v1/brands/{brand_id}/learning/settings    - Update privacy tier and consent
GET    /v1/brands/{brand_id}/learning/settings    - Get current learning settings
GET    /v1/brands/{brand_id}/learning/dashboard   - Get learning transparency dashboard
GET    /v1/brands/{brand_id}/learning/patterns    - Get learned patterns
POST   /v1/brands/{brand_id}/learning/export      - Export all learning data
DELETE /v1/brands/{brand_id}/learning/data        - Delete all learning data
GET    /v1/brands/{brand_id}/learning/audit       - Get audit log
```

### Learning Transparency Dashboard

The dashboard provides radical transparency about what the system has learned:

```python
class LearningDashboard(BaseModel):
    brand_id: str
    privacy_tier: PrivacyTier
    patterns_learned: List[dict]  # What patterns were extracted
    data_sources: str  # "Your brand only" or "5 fashion brands"
    impact_metrics: dict  # Compliance score improvements
    audit_log: List[LearningAuditLog]
    last_updated: datetime
```

### Legal & Compliance Documentation

#### Data Processing Addendum Template

Provided as part of the system for enterprise sales:

```markdown
# Data Processing Addendum - Mobius Learning System

## Privacy Tiers

### Private Mode (Default)
- Data stays within your brand
- No sharing with other organizations
- Full data ownership
- Can export or delete at any time

### Shared Mode (Opt-in)
- Contributes to anonymized industry patterns
- Minimum 5 brands required (k-anonymity)
- Differential privacy noise applied
- No individual brand traces stored
- Can opt-out at any time

## Your Rights
- Right to access learning data
- Right to export learning data
- Right to delete learning data
- Right to opt-out of shared learning
```

### Testing Strategy

**Property-Based Tests** for learning system:

#### Property 17: Privacy tier enforcement

*For any* brand with privacy_tier set to "off", no patterns should be extracted or stored.

**Validates: Learning privacy controls**

#### Property 18: K-anonymity enforcement

*For any* industry pattern, the contributor_count should be at least 5.

**Validates: Shared learning privacy**

#### Property 19: Data deletion completeness

*For any* brand, after calling delete_learning_data(), querying for patterns should return an empty list.

**Validates: Right to deletion**

#### Property 20: Differential privacy noise

*For any* aggregated industry pattern, the noise_level should be greater than 0.

**Validates: Differential privacy**

## Future Enhancements

### Phase 3 Roadmap

1. **Authentication & Authorization**:
   - JWT-based authentication
   - Role-based access control (RBAC)
   - Organization-level permissions
   - API key management

2. **Advanced Learning**:
   - ML model training on feedback data
   - Prompt optimization based on approval patterns
   - Personalized generation suggestions
   - A/B testing framework

3. **Collaboration Features**:
   - Approval workflows with stakeholder routing
   - Comments and annotations on assets
   - Version history and rollback
   - Team activity feeds

4. **Performance Optimization**:
   - Redis caching layer
   - Batch generation processing
   - Parallel generation with voting
   - Smart prompt caching

5. **Enterprise Features**:
   - Rate limiting per organization
   - Usage analytics dashboard
   - Cost tracking and budgets
   - SLA monitoring

6. **Integration Ecosystem**:
   - Figma plugin
   - Slack notifications
   - Zapier integration
   - REST webhooks for all events

