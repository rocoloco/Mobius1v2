# Mobius Brand Governance Engine - Architecture Documentation

## Executive Summary

Mobius is an AI-powered brand governance platform that automatically generates, audits, and corrects brand-compliant visual assets. It's the only platform with a closed-loop auto-correction system that ensures brand compliance without human intervention.

**Key Differentiator**: Automated correction loop that learns from audit failures and regenerates assets until they meet brand standards.

## What Mobius Does

### Core Capabilities

1. **Brand Guidelines Ingestion**
   - Upload PDF brand guidelines
   - AI-powered extraction of brand rules (colors, typography, logos, voice/tone)
   - Creates a "Digital Twin" - a machine-readable representation of the brand

2. **AI-Powered Asset Generation**
   - Generate brand-compliant images from text prompts
   - Gemini 3 Vision Model for high-quality image generation
   - Automatic brand color and style enforcement

3. **Automated Compliance Auditing**
   - Visual AI analysis using Google Gemini
   - Category-level scoring (colors, typography, layout, logo usage)
   - Specific violation detection and reporting

4. **Auto-Correction Loop**
   - Failed audits trigger automatic prompt refinement
   - Up to 3 generation attempts with progressive improvements
   - Learns from audit feedback to fix specific issues

5. **Multi-Brand Management**
   - Agency-scale portfolio management (10-50+ brands)
   - Per-brand statistics and compliance tracking
   - Reusable templates for high-performing configurations


## System Architecture

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Runtime** | Modal (Serverless Python) | Scalable compute with auto-scaling |
| **API Framework** | FastAPI | High-performance async HTTP API |
| **Orchestration** | LangGraph | State machine workflows with checkpointing |
| **Database** | Supabase (PostgreSQL) | Structured data storage with connection pooling |
| **File Storage** | Supabase Storage | CDN-backed object storage for PDFs and images |
| **Image Generation** | Google Gemini 3 Pro Image Preview | High-quality image synthesis |
| **Visual AI** | Google Gemini 3 Pro Preview | Multimodal compliance auditing |
| **PDF Processing** | PyMuPDF (fitz) + pdfplumber | Text and image extraction |
| **Validation** | Pydantic v2 | Request/response validation |
| **Logging** | structlog | Structured JSON logging |
| **Testing** | pytest + Hypothesis | Unit and property-based testing |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  (HTML Dashboard, API Clients, Webhooks)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Brands     │  │  Generation  │  │  Templates   │         │
│  │   Routes     │  │    Routes    │  │   Routes     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Jobs       │  │  Feedback    │  │   Health     │         │
│  │   Routes     │  │   Routes     │  │   Check      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                            │
│                      (LangGraph Workflow)                        │
│                                                                  │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐             │
│  │ Generate │─────▶│  Audit   │─────▶│ Complete │             │
│  │   Node   │      │   Node   │      │          │             │
│  └──────────┘      └─────┬────┘      └──────────┘             │
│       ▲                  │                                      │
│       │                  │ Failed                               │
│       │                  ▼                                      │
│       │            ┌──────────┐                                │
│       └────────────│ Correct  │                                │
│                    │   Node   │                                │
│                    └──────────┘                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │    Gemini    │  │  Supabase    │                            │
│  │ (Vision/AI)  │  │  (Storage)   │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATA LAYER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Brands     │  │    Assets    │  │    Jobs      │         │
│  │   Table      │  │    Table     │  │    Table     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Templates   │  │   Feedback   │  │   Storage    │         │
│  │   Table      │  │    Table     │  │   Buckets    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```


## User Workflow

### 1. Brand Onboarding

```
User uploads PDF → API validates file → PDF Parser extracts guidelines
                                              ↓
                                    Creates Digital Twin
                                              ↓
                        ┌─────────────────────┴─────────────────────┐
                        ▼                                           ▼
                   Colors extracted                          Typography extracted
                   (hex, usage, context)                     (families, weights, usage)
                        ▼                                           ▼
                   Logo rules extracted                      Voice/tone extracted
                   (sizing, restrictions)                    (adjectives, examples)
                        ▼                                           ▼
                        └─────────────────────┬─────────────────────┘
                                              ▼
                              Brand stored in database with:
                              - Structured guidelines (Digital Twin)
                              - PDF URL (original document)
                              - Logo thumbnail (if uploaded)
                              - Needs review flags (if any)
```

**What happens:**
- User uploads brand guidelines PDF (max 50MB)
- Optional: Upload logo PNG with transparency
- System validates PDF format and size
- Gemini AI extracts structured brand data:
  - Colors with hex codes, usage (primary/secondary/accent), and context
  - Typography with font families, weights, and usage guidelines
  - Logo rules with sizing and background restrictions
  - Voice/tone with adjectives, forbidden words, and example phrases
  - Brand rules with categories and severity levels
- Creates a "Digital Twin" - machine-readable brand representation
- Stores PDF in Supabase Storage (brands bucket)
- Stores logo in Supabase Storage (assets bucket)
- Saves structured guidelines to database

**User sees:**
- Brand details with visual preview of colors
- Typography specifications
- Logo rules and thumbnail
- Voice/tone guidelines
- Any items flagged for manual review


### 2. Asset Generation Workflow

```
User submits prompt → Job created (pending) → LangGraph workflow starts
                                                      ↓
                                              ┌───────────────┐
                                              │ Generate Node │
                                              └───────┬───────┘
                                                      │
                                    Gemini 3 Vision Model generates image
                                                      ↓
                                    Prompt enhanced with brand rules:
                                    "Your prompt + Brand colors: #XXX + 
                                     Style rules: [guidelines]"
                                                      ↓
                                              Image generated
                                                      ↓
                                              ┌───────────────┐
                                              │  Audit Node   │
                                              └───────┬───────┘
                                                      │
                                    Gemini analyzes image bytes:
                                    - Color compliance check
                                    - Style adherence check
                                    - Overall brand alignment
                                                      ↓
                                    Returns JSON with:
                                    - approved: true/false
                                    - confidence: 0-1
                                    - fix_suggestion: "specific fix"
                                                      ↓
                                              ┌───────┴───────┐
                                              │   Approved?   │
                                              └───────┬───────┘
                                                      │
                                    ┌─────────────────┼─────────────────┐
                                    │ YES                               │ NO
                                    ▼                                   ▼
                            ┌───────────────┐                  ┌───────────────┐
                            │   Complete    │                  │ Max attempts? │
                            │   (Success)   │                  └───────┬───────┘
                            └───────────────┘                          │
                                                        ┌───────────────┼───────────────┐
                                                        │ YES                           │ NO
                                                        ▼                               ▼
                                                ┌───────────────┐            ┌───────────────┐
                                                │     Failed    │            │ Correct Node  │
                                                │  (Max tries)  │            └───────┬───────┘
                                                └───────────────┘                    │
                                                                        Apply fix suggestion
                                                                        to prompt
                                                                                     ↓
                                                                        Loop back to Generate
```

**What happens:**

**Step 1: Job Creation**
- User submits prompt + brand_id
- System creates job record (status: pending)
- Returns job_id immediately if async_mode=true

**Step 2: Generate Node**
- Uses Gemini 3 Pro Image Preview model for image generation
- Enhances prompt with brand guidelines:
  ```
  Original: "Summer sale banner"
  Enhanced: "Summer sale banner. Strict Visual Style Rules: [brand rules]. 
             Mandatory Brand Colors: #FF5733, #C70039"
  ```
- Calls Gemini Vision API to generate image
- Stores image URI in job state

**Step 3: Audit Node**
- Receives image URI from generation
- Sends to Gemini 3 Pro Preview (Reasoning Model) with brand guidelines
- Gemini analyzes:
  - Color accuracy and prominence
  - Style rule adherence
  - Overall brand alignment
- Returns structured audit result:
  ```json
  {
    "approved": false,
    "confidence": 0.75,
    "reason": "Brand colors not prominent enough",
    "color_compliance": "partial",
    "style_compliance": "pass",
    "fix_suggestion": "Make brand colors more prominent in the composition"
  }
  ```

**Step 4: Routing Decision**
- If approved → Complete (save asset, return success)
- If max attempts (3) reached → Failed (return with audit history)
- Otherwise → Correct Node

**Step 5: Correct Node**
- Extracts fix_suggestion from audit
- Enhances original prompt:
  ```
  "Summer sale banner. IMPORTANT CORRECTION: Make brand colors 
   more prominent in the composition"
  ```
- Loops back to Generate Node

**User sees:**
- Job status updates (pending → generating → auditing → completed/failed)
- Final image URL if successful
- Compliance score and category breakdown
- Audit history showing all attempts
- Specific violations if any


### 3. Template Workflow

```
User generates asset → High compliance (≥95%) → Save as template
                                                        ↓
                                            Template stored with:
                                            - Generation parameters
                                            - Prompt that worked
                                            - Thumbnail preview
                                                        ↓
                                            Future generations can use template:
                                            - Pre-fills parameters
                                            - User can override specific values
                                            - Ensures consistency
```

**What happens:**
- User generates asset with ≥95% compliance score
- Clicks "Save as Template"
- System stores:
  - Original prompt
  - Generation parameters (model, style, etc.)
  - Thumbnail URL
  - Source asset reference
- Template appears in brand's template library
- Future generations can select template:
  - Parameters auto-filled
  - User can modify prompt
  - Maintains proven configuration

**User sees:**
- Template library for each brand
- Thumbnail previews
- Template descriptions
- One-click template application


## AI Models Used

### 1. Google Gemini 3 Dual-Architecture

**Gemini 3 Pro Image Preview** (`gemini-3-pro-image-preview`)
- **Purpose**: High-quality image generation
- **When used**: All image generation requests
- **Strengths**: 
  - Native multimodal capabilities
  - Brand-aware generation with compressed guidelines
  - Consistent style and quality
  - Integrated with Google AI ecosystem
- **Cost**: ~$0.03 per generation
- **Context Window**: 65k tokens (accommodates compressed brand guidelines)
- **Example prompts**: 
  - "Professional product photo on white background"
  - "Team collaboration in modern office"
  - "Social media banner with headline text"
  - "Logo design with company name"

**Gemini 3 Pro Preview** (`gemini-3-pro-preview`)
- **Purpose**: Brand compliance auditing
- **Input**: Image bytes + brand guidelines text
- **Output**: Structured JSON audit result
- **Cost**: ~$0.001 per audit
- **Temperature**: 0.1 (low randomness for consistency)

**Audit Process**:
1. Downloads generated image as bytes
2. Determines MIME type (PNG/JPEG/WebP)
3. Sends to Gemini with multimodal prompt:
   - Image bytes
   - Brand guidelines text
   - Required colors list
   - Audit instructions
4. Receives structured JSON response:
   ```json
   {
     "approved": boolean,
     "confidence": 0.0-1.0,
     "reason": "explanation",
     "color_compliance": "pass" | "partial" | "fail",
     "style_compliance": "pass" | "partial" | "fail",
     "fix_suggestion": "specific correction" | null
   }
   ```

**Audit Criteria**:
- **Color Compliance**: Are brand colors present and prominent?
- **Style Compliance**: Does it match visual style rules?
- **Overall Alignment**: Professional and on-brand?

**Example Audit Prompt**:
```
You are a strict Brand Compliance Officer.

**Brand Guidelines:**
- Primary color: #FF5733 (vibrant red-orange)
- Secondary color: #C70039 (deep red)
- Style: Modern, clean, minimalist
- Typography: Sans-serif, bold headlines

**Required Colors:**
#FF5733, #C70039

Analyze the attached image carefully.

1. Does the image adhere to the visual style rules?
2. Are the brand colors correctly represented and prominent?
3. Is the overall composition professional and on-brand?

Return JSON ONLY (no markdown):
{
  "approved": boolean,
  "confidence": 0-1,
  "reason": "concise explanation",
  "color_compliance": "pass" | "partial" | "fail",
  "style_compliance": "pass" | "partial" | "fail",
  "fix_suggestion": "specific fix" | null
}
```


### 3. Gemini for PDF Parsing

**Gemini 3 Pro Preview** (`gemini-3-pro-preview`)
- **Purpose**: Extract structured brand guidelines from PDFs
- **Input**: PDF text content + section hints
- **Output**: Structured JSON with Digital Twin data
- **Process**:
  1. Extract text from PDF using PyMuPDF
  2. Identify sections (colors, typography, logos, voice)
  3. Send to Gemini with comprehensive extraction prompt
  4. Parse JSON response into structured models

**What it extracts**:
- **Colors**: hex, RGB, CMYK, Pantone, usage, emotional attributes, accessibility
- **Typography**: families, weights, sizes, line heights, usage contexts
- **Logos**: variants, sizing rules, clear space, forbidden backgrounds
- **Voice/Tone**: personality traits, messaging pillars, language guidelines, examples
- **Brand Rules**: categories, severity levels, rationale, exceptions

**Example extraction**:
```json
{
  "colors": [
    {
      "name": "Forest Green",
      "hex": "#2D5016",
      "usage": "primary",
      "description": "Primary brand color representing growth",
      "emotional_attributes": ["trustworthy", "natural"],
      "usage_contexts": ["headers", "CTAs"]
    }
  ],
  "typography": [
    {
      "family": "Helvetica Neue",
      "weights": ["regular", "medium", "bold"],
      "usage": "headlines",
      "personality": ["modern", "clean"]
    }
  ],
  "voice": {
    "personality_traits": ["friendly", "professional"],
    "tone_attributes": ["warm", "confident"],
    "language_guidelines": {
      "use": ["active voice", "simple language"],
      "avoid": ["jargon", "corporate speak"]
    }
  }
}
```


## Data Models

### Brand Digital Twin

The core data structure representing a brand:

```python
class Brand(BaseModel):
    brand_id: str                    # UUID
    organization_id: str             # Parent organization
    name: str                        # Brand name
    guidelines: BrandGuidelines      # Digital Twin (see below)
    pdf_url: Optional[str]           # Original PDF location
    logo_thumbnail_url: Optional[str] # Logo image URL
    needs_review: List[str]          # Items flagged for review
    learning_active: bool            # ML learning enabled
    feedback_count: int              # Total feedback events
    created_at: str                  # ISO timestamp
    updated_at: str                  # ISO timestamp
```

### BrandGuidelines (Digital Twin)

```python
class BrandGuidelines(BaseModel):
    colors: List[Color]              # Brand color palette
    typography: List[Typography]     # Font specifications
    logos: List[LogoRule]            # Logo usage rules
    voice: Optional[VoiceTone]       # Brand voice/tone
    rules: List[BrandRule]           # Governance rules
    source_filename: Optional[str]   # Original PDF name
```

**Color Model**:
```python
class Color(BaseModel):
    name: str                        # "Forest Green"
    hex: str                         # "#2D5016"
    usage: Literal["primary", "secondary", "accent", "background"]
    context: Optional[str]           # Usage guidelines
```

**Typography Model**:
```python
class Typography(BaseModel):
    family: str                      # "Helvetica Neue"
    weights: List[str]               # ["regular", "bold"]
    usage: str                       # "headlines | modern, clean"
```

**LogoRule Model**:
```python
class LogoRule(BaseModel):
    variant_name: str                # "Primary Logo"
    url: str                         # Logo file URL
    min_width_px: int                # Minimum size (150)
    clear_space_ratio: float         # Clear space (0.1 = 10%)
    forbidden_backgrounds: List[str] # ["#FF0000", "busy-patterns"]
```

**VoiceTone Model**:
```python
class VoiceTone(BaseModel):
    adjectives: List[str]            # ["friendly", "professional"]
    forbidden_words: List[str]       # ["jargon", "synergy"]
    example_phrases: List[str]       # ["We help you grow"]
```

**BrandRule Model**:
```python
class BrandRule(BaseModel):
    category: Literal["visual", "verbal", "legal"]
    instruction: str                 # "Never use red in materials"
    severity: Literal["warning", "critical"]
    negative_constraint: bool        # True = "Do Not" rule
```


### Job State (LangGraph)

The workflow state that flows through generation nodes:

```python
class JobState(TypedDict):
    # Input
    prompt: str                      # User's generation prompt
    brand_hex_codes: List[str]       # ["#FF5733", "#C70039"]
    brand_rules: str                 # Text description of rules
    
    # Processing state
    current_image_url: Optional[str] # Generated image URL
    attempt_count: int               # Current attempt (1-3)
    audit_history: List[dict]        # All audit results
    is_approved: bool                # Final approval status
    used_model: str                  # "gemini-3-pro-image-preview"
    
    # Metadata
    job_id: str                      # UUID
    created_at: str                  # ISO timestamp
    estimated_cost_usd: float        # Running cost total
    last_error: Optional[str]        # Error message if any
```

### Asset Model

Generated and approved assets:

```python
class Asset(BaseModel):
    asset_id: str                    # UUID
    brand_id: str                    # Parent brand
    job_id: str                      # Generation job
    prompt: str                      # Original prompt
    image_url: str                   # Final image location
    compliance_score: Optional[float] # 0-100 score
    compliance_details: Optional[Dict] # Category breakdown
    generation_params: Optional[Dict] # Model settings used
    status: str                      # "approved", "rejected", "pending"
    created_at: datetime
    updated_at: datetime
```

### Job Model

Async job tracking:

```python
class Job(BaseModel):
    job_id: str                      # UUID
    brand_id: str                    # Parent brand
    status: str                      # "pending", "generating", "auditing", 
                                     # "correcting", "completed", "failed"
    progress: float                  # 0-100 percentage
    state: Dict[str, Any]            # Complete JobState
    webhook_url: Optional[str]       # Completion notification URL
    webhook_attempts: int            # Delivery retry count
    idempotency_key: Optional[str]   # Duplicate prevention key
    error: Optional[str]             # Error message
    created_at: datetime
    updated_at: datetime
    expires_at: datetime             # Auto-cleanup timestamp
```

### Template Model

Reusable generation configurations:

```python
class Template(BaseModel):
    template_id: str                 # UUID
    brand_id: str                    # Parent brand
    name: str                        # "Summer Sale Template"
    description: str                 # User description
    generation_params: Dict[str, Any] # Saved parameters
    thumbnail_url: str               # Preview image
    source_asset_id: str             # Original asset reference
    created_at: datetime
```


## Key Features & Implementation

### 1. Digital Twin Concept

**What it is**: A machine-readable, semantically rich representation of a brand that goes beyond simple data extraction.

**Why it matters**:
- Enables automated compliance checking
- Provides context-aware guidance
- Supports predictive validation
- Captures relationships between brand elements

**What it captures**:
- **Visual DNA**: Colors, typography, imagery with semantic meaning
- **Behavioral Rules**: Usage guidelines, restrictions, contexts
- **Semantic Relationships**: How elements work together
- **Contextual Intelligence**: Channel-specific adaptations

**Example**:
```json
{
  "colors": [
    {
      "hex": "#2D5016",
      "name": "Forest Green",
      "usage": "primary",
      "emotional_attributes": ["trustworthy", "natural"],
      "usage_contexts": ["headers", "CTAs"],
      "avoid_contexts": ["body text on white"],
      "pairings": ["cream", "white"],
      "accessibility": {
        "wcag_aa_compliant": true,
        "min_contrast_ratio": 4.5
      }
    }
  ]
}
```

This is NOT just "green = #2D5016". It's:
- Primary brand color (hierarchy)
- Evokes trust and nature (emotion)
- Use for headers and CTAs (context)
- Don't use for body text (constraint)
- Pairs well with cream (relationship)
- Meets accessibility standards (compliance)


### 2. Auto-Correction Loop

**The Problem**: Traditional systems generate once and hope for the best.

**Mobius Solution**: Automated correction loop that learns from failures.

**How it works**:
1. Generate image with brand-enhanced prompt
2. Audit with Gemini (get specific feedback)
3. If failed:
   - Extract fix_suggestion from audit
   - Enhance prompt with correction
   - Regenerate (up to 3 attempts)
4. Each attempt gets progressively better

**Example correction flow**:

**Attempt 1**:
- Prompt: "Summer sale banner"
- Result: Generic banner, brand colors barely visible
- Audit: `{"approved": false, "fix_suggestion": "Make brand colors more prominent"}`

**Attempt 2**:
- Prompt: "Summer sale banner. IMPORTANT CORRECTION: Make brand colors more prominent"
- Result: Better, but composition off
- Audit: `{"approved": false, "fix_suggestion": "Center the main message"}`

**Attempt 3**:
- Prompt: "Summer sale banner. IMPORTANT CORRECTION: Make brand colors more prominent. Center the main message"
- Result: Perfect alignment
- Audit: `{"approved": true}`

**Key insight**: Each failure provides specific, actionable feedback that improves the next attempt.


### 3. Smart Model Routing

**Challenge**: Different types of content need different generation models.

**Solution**: Automatic routing based on prompt analysis.

**Routing Logic**:
```python
# Text/design triggers
text_keywords = ["text", "logo", "font", "typography", "vector", 
                 "illustration", "write", "letter", "word", "headline"]

# Use Gemini 3 Vision Model for all generation
model = "gemini-3-pro-image-preview"
```

**Why this matters**:
- **Unified Model**: Single model handles all types of image generation
- **Consistent Quality**: No need to route between different models
- **Simplified Architecture**: Fewer dependencies and integration points

**Examples**:
- "Product photo on white background" → Gemini 3 Vision
- "Social media banner with headline" → Gemini 3 Vision
- "Logo design with company name" → Gemini 3 Vision
- "Team collaboration in office" → Gemini 3 Vision


### 4. Idempotency & Reliability

**Problem**: Network failures can cause duplicate job creation.

**Solution**: Idempotency keys prevent duplicates.

**How it works**:
```python
# Client provides idempotency key
POST /v1/generate
{
  "brand_id": "brand-123",
  "prompt": "Summer sale",
  "idempotency_key": "client-request-456"
}

# Server checks for existing job with same key
existing_job = await job_storage.get_by_idempotency_key("client-request-456")

if existing_job:
    # Return existing job instead of creating duplicate
    return existing_job

# Otherwise create new job with key
new_job = Job(
    job_id=uuid4(),
    idempotency_key="client-request-456",
    ...
)
```

**Benefits**:
- Safe retries after network failures
- No duplicate charges
- Consistent results for same request

**Expiration**: Jobs expire after 24 hours, allowing key reuse.


### 5. Webhook Notifications

**Problem**: Long-running jobs need async completion notifications.

**Solution**: Webhook callbacks with retry logic.

**Flow**:
```
1. Client submits job with webhook_url
   POST /v1/generate
   {
     "brand_id": "brand-123",
     "prompt": "Summer sale",
     "async_mode": true,
     "webhook_url": "https://client.com/webhooks/mobius"
   }

2. Server returns immediately
   {
     "job_id": "job-456",
     "status": "pending"
   }

3. Job processes in background
   - Generate → Audit → Correct (loop)

4. On completion, POST to webhook_url
   {
     "job_id": "job-456",
     "status": "completed",
     "final_image_url": "https://...",
     "compliance_score": 92.5,
     "attempts": 2
   }

5. Retry logic if webhook fails
   - Exponential backoff
   - Max 5 attempts
   - Track webhook_attempts in database
```

**Benefits**:
- Non-blocking API calls
- Reliable delivery
- Client can process results asynchronously


### 6. Connection Pooling

**Problem**: Serverless functions exhaust database connections.

**Solution**: Supabase connection pooler (PgBouncer).

**Configuration**:
```python
# ❌ WRONG - Direct connection (port 5432)
SUPABASE_URL = "postgresql://postgres.abc:pwd@aws-0-us-east-1.supabase.co:5432/postgres"
# Will exhaust connections under load

# ✅ CORRECT - Pooler connection (port 6543)
SUPABASE_URL = "postgresql://postgres.abc:pwd@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
# Reuses connections efficiently
```

**Why it matters**:
- Modal spins up many concurrent containers
- Each needs database connection
- Direct connections = 100+ simultaneous connections
- Pooler = 10 connections shared across all containers

**Validation**:
```python
@field_validator("supabase_url")
def validate_pooler_url(cls, v: str) -> str:
    if "pooler.supabase.com" not in v and ":6543" not in v:
        warnings.warn(
            "Consider using Supabase pooler URL for serverless. "
            "Direct connections may exhaust limits under load."
        )
    return v
```


## Cost Tracking

### Per-Operation Costs

| Operation | Model | Cost (USD) |
|-----------|-------|------------|
| Image Generation | Gemini 3 Pro Image Preview | $0.03 |
| Compliance Audit | Gemini 3 Pro Preview | $0.001 |
| PDF Parsing | Gemini 3 Pro Preview | $0.002 |

### Example Job Costs

**Successful First Attempt**:
- 1x Generation: $0.03
- 1x Audit: $0.001
- **Total**: $0.031

**Failed Twice, Success on Third**:
- 3x Generation: $0.09
- 3x Audit: $0.003
- **Total**: $0.093

**Brand Onboarding**:
- 1x PDF Parse: $0.002
- **Total**: $0.002

### Cost Optimization

1. **Unified Model**: Single Gemini 3 model for all generation needs
2. **Early Audit**: Fail fast on obvious violations
3. **Template Reuse**: Skip experimentation with proven configs
4. **Batch Processing**: Process multiple jobs in parallel

### Monthly Estimates

**Small Agency (5 brands, 100 assets/month)**:
- Onboarding: 5 × $0.002 = $0.01
- Generation: 100 × $0.031 (avg) = $3.10
- **Total**: ~$3/month

**Medium Agency (20 brands, 500 assets/month)**:
- Onboarding: 20 × $0.002 = $0.04
- Generation: 500 × $0.031 = $15.50
- **Total**: ~$16/month

**Large Agency (50 brands, 2000 assets/month)**:
- Onboarding: 50 × $0.002 = $0.10
- Generation: 2000 × $0.031 = $62
- **Total**: ~$62/month

*Note: Assumes 70% first-attempt success rate. Actual costs may vary.*


## Deployment Architecture

### Modal Serverless

**Why Modal**:
- Zero infrastructure management
- Auto-scaling (0 to 1000+ containers)
- Pay-per-use pricing
- Built-in GPU support
- Integrated secrets management

**Container Lifecycle**:
```
Request arrives → Modal spins up container → Execute function → Return response
                                          ↓
                                    Container idles
                                          ↓
                                    Reused for next request
                                          ↓
                                    Auto-shutdown after 5min idle
```

**Image Definition**:
```python
image = modal.Image.debian_slim().pip_install(
    "langgraph>=0.2.0",
    "google-genai>=1.0.0",
    "supabase>=2.0.0",
    "httpx>=0.27.0",
    "fastapi>=0.110.0",
)
```

**Function Deployment**:
```python
@app.function(timeout=600)  # 10 minute timeout
@modal.fastapi_endpoint(method="POST")
def generate_handler(request: GenerateRequest):
    # Handler code
    pass
```

### Supabase Backend

**Database (PostgreSQL)**:
- Managed PostgreSQL with connection pooling
- Row-level security (RLS) for multi-tenancy
- Automatic backups
- Real-time subscriptions (future feature)

**Storage (S3-compatible)**:
- CDN-backed object storage
- Two buckets:
  - `brands`: PDF guidelines
  - `assets`: Generated images and logos
- Public read access with signed URLs
- Automatic image optimization

**Tables**:
```sql
brands          -- Brand entities with Digital Twin
assets          -- Generated assets
jobs            -- Async job tracking
templates       -- Reusable configurations
feedback        -- User feedback events
learning_settings -- Privacy preferences
brand_patterns  -- Learned patterns (future)
```


## Security & Privacy

### API Security

**Request ID Tracing**:
- Every request gets unique ID: `req_abc123456789`
- Logged with every operation
- Enables distributed tracing
- Helps debug issues across services

**Error Handling**:
- Consistent error format
- No sensitive data in responses
- Structured logging for debugging

**Rate Limiting** (Future):
- Per-organization limits
- Prevents abuse
- Graceful degradation

### Data Privacy

**Brand Data**:
- Isolated by organization_id
- Soft deletes (audit trail)
- GDPR-compliant data export
- Right to be forgotten

**Learning Privacy Tiers**:
1. **OFF**: No learning, no data collection
2. **PRIVATE**: Learn from your brand only
3. **SHARED**: Contribute to cross-brand patterns (future)

**Consent Management**:
- Explicit opt-in required
- Version-tracked consent
- Configurable retention periods
- Audit log of all changes

### Secrets Management

**Modal Secrets**:
```bash
modal secret create mobius-secrets \
  GEMINI_API_KEY=xxx \
  SUPABASE_URL=xxx \
  SUPABASE_KEY=xxx
```

**Environment Variables**:
- Never committed to git
- Validated at startup
- Separate dev/prod configs


## Testing Strategy

### Test Pyramid

```
                    ▲
                   / \
                  /   \
                 /  E2E \          (Future: Full workflow tests)
                /_______\
               /         \
              / Property  \        (100+ random examples per test)
             /   Tests     \
            /______________\
           /                \
          /   Unit Tests     \    (Specific scenarios & edge cases)
         /____________________\
```

### Unit Tests (tests/unit/)

**What they test**:
- Configuration validation
- Request ID generation
- Error response formatting
- Model validation
- Storage operations

**Example**:
```python
def test_request_id_format():
    """Request IDs should match pattern req_[a-z0-9]{16}"""
    request_id = generate_request_id()
    assert request_id.startswith("req_")
    assert len(request_id) == 20
    assert request_id[4:].isalnum()
```

### Property-Based Tests (tests/property/)

**What they test**: Universal properties that should ALWAYS be true

**Using Hypothesis**:
```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=1, max_value=1000))
def test_request_ids_are_unique(n):
    """Generate N request IDs, all should be unique"""
    ids = [generate_request_id() for _ in range(n)]
    assert len(ids) == len(set(ids))  # No duplicates
```

**Properties tested**:
- Request ID uniqueness (100+ iterations)
- Concurrent generation without collisions
- Idempotency key behavior
- State transitions validity

### Integration Tests (tests/integration/)

**What they test**: End-to-end workflows

**Examples**:
- Brand ingestion → PDF parse → Database storage
- Generation → Audit → Correction loop
- Template save → Template apply
- Webhook delivery with retries

### Test Configuration

**Quick mode** (CI/CD):
```bash
QUICK_TESTS=1 pytest -v  # 10 examples per property test
```

**Full mode** (pre-deploy):
```bash
pytest -v  # 100 examples per property test
```

**Coverage**:
```bash
pytest --cov=src/mobius --cov-report=html
# Target: >80% coverage
```


## Performance Optimization

### 1. Connection Pooling

**HTTP Client Pooling**:
```python
_http_client = httpx.Client(
    timeout=30.0,
    limits=httpx.Limits(
        max_keepalive_connections=10,
        max_connections=100,
        keepalive_expiry=30.0
    )
)
```

**Benefits**:
- Reuse TCP connections
- Reduce handshake overhead
- Faster image downloads

### 2. Retry Logic with Backoff

**Exponential backoff**:
```python
delay = min(base_delay * (2 ** attempt), max_delay)
jitter = random.uniform(0, delay * 0.1)
total_delay = delay + jitter
```

**Why jitter**: Prevents thundering herd when rate limits hit

### 3. Async Operations

**FastAPI async handlers**:
```python
async def generate_handler(request: GenerateRequest):
    brand = await brand_storage.get_brand(request.brand_id)
    job = await job_storage.create_job(job)
    return response
```

**Benefits**:
- Non-blocking I/O
- Handle more concurrent requests
- Better resource utilization

### 4. Caching (Future)

**Planned optimizations**:
- Cache brand guidelines in memory
- Cache audit results for similar images
- CDN caching for generated assets


## Future Enhancements

### Phase 3: Machine Learning

**Planned Features**:
1. **Pattern Recognition**
   - Learn from approved assets
   - Identify successful color combinations
   - Detect preferred composition styles

2. **Predictive Compliance**
   - Pre-audit prompts before generation
   - Suggest improvements upfront
   - Reduce failed attempts

3. **Smart Templates**
   - Auto-generate templates from patterns
   - Recommend templates for prompts
   - A/B test template variations

### Phase 4: Advanced Features

**Multi-Channel Optimization**:
- Platform-specific adaptations (Instagram, LinkedIn, etc.)
- Automatic resizing and cropping
- Format optimization (PNG, JPEG, WebP)

**Collaborative Workflows**:
- Team approval workflows
- Comment and annotation
- Version history

**Advanced Analytics**:
- Compliance trends over time
- Brand drift detection
- ROI tracking

**Real-time Collaboration**:
- Live preview during generation
- Collaborative prompt refinement
- Shared template libraries


## Troubleshooting Guide

### Common Issues

**1. "Too many connections" error**

**Cause**: Not using Supabase pooler URL

**Solution**:
```bash
# Change from direct connection (port 5432)
SUPABASE_URL=postgresql://...supabase.co:5432/postgres

# To pooler connection (port 6543)
SUPABASE_URL=postgresql://...pooler.supabase.com:6543/postgres
```

**2. Generation fails with "Rate limit" error**

**Cause**: Exceeded Gemini rate limits

**Solution**:
- Automatic retry with exponential backoff
- Check API quota in provider dashboard
- Upgrade API tier if needed

**3. PDF ingestion fails**

**Possible causes**:
- PDF exceeds 50MB limit
- PDF is corrupted or password-protected
- PDF contains no extractable text (scanned images)

**Solution**:
- Compress PDF or split into sections
- Remove password protection
- OCR scanned PDFs before upload

**4. Webhook not received**

**Possible causes**:
- Webhook URL not publicly accessible
- Endpoint returns non-200 status
- Firewall blocking requests

**Solution**:
- Test webhook URL with curl
- Check webhook endpoint logs
- Review `webhook_attempts` in jobs table
- Verify firewall rules

**5. Low compliance scores**

**Possible causes**:
- Brand guidelines too vague
- Conflicting style rules
- Unrealistic expectations

**Solution**:
- Review and refine brand guidelines
- Add more specific color/style rules
- Use templates from successful generations
- Provide more detailed prompts


## API Quick Reference

### Brand Management

```bash
# Upload brand guidelines
POST /v1/brands/ingest
Content-Type: multipart/form-data
- organization_id: string
- brand_name: string
- file: PDF file
- logo: PNG file (optional)

# List brands
GET /v1/brands?organization_id={id}&search={term}&limit={n}

# Get brand details
GET /v1/brands/{brand_id}

# Update brand
PATCH /v1/brands/{brand_id}
Content-Type: application/json
{"name": "New Name"}

# Delete brand (soft delete)
DELETE /v1/brands/{brand_id}
```

### Asset Generation

```bash
# Generate asset (async)
POST /v1/generate
Content-Type: application/json
{
  "brand_id": "brand-123",
  "prompt": "Summer sale banner",
  "async_mode": true,
  "webhook_url": "https://your-app.com/webhook",
  "idempotency_key": "unique-key-123"
}

# Get job status
GET /v1/jobs/{job_id}

# Cancel job
POST /v1/jobs/{job_id}/cancel
```

### Templates

```bash
# Save template (requires 95%+ compliance)
POST /v1/templates
Content-Type: application/json
{
  "asset_id": "asset-123",
  "template_name": "Summer Sale",
  "description": "High-performing template"
}

# List templates
GET /v1/templates?brand_id={id}&limit={n}

# Get template
GET /v1/templates/{template_id}

# Delete template
DELETE /v1/templates/{template_id}

# Use template
POST /v1/generate
{
  "brand_id": "brand-123",
  "prompt": "New sale announcement",
  "template_id": "template-456"
}
```

### Feedback

```bash
# Submit feedback
POST /v1/assets/{asset_id}/feedback
Content-Type: application/json
{
  "action": "approve",  # or "reject"
  "reason": "Perfect alignment"
}

# Get feedback stats
GET /v1/brands/{brand_id}/feedback
```

### System

```bash
# Health check
GET /v1/health

# API documentation
GET /v1/docs
```


## Glossary

**Digital Twin**: A machine-readable, semantically rich representation of a brand that captures not just visual elements, but relationships, rules, and context.

**Brand Guidelines**: PDF document containing brand identity rules (colors, typography, logos, voice/tone).

**Compliance Score**: 0-100 score indicating how well an asset adheres to brand guidelines.

**Audit Node**: LangGraph node that uses Gemini 3 Pro Preview (Reasoning Model) to evaluate brand compliance.

**Generate Node**: LangGraph node that creates images using Gemini 3 Pro Image Preview (Vision Model).

**Correct Node**: LangGraph node that refines prompts based on audit feedback.

**Template**: Reusable generation configuration saved from high-performing assets (≥95% compliance).

**Idempotency Key**: Client-provided unique identifier to prevent duplicate job creation.

**Webhook**: HTTP callback for async job completion notifications.

**Job State**: Complete workflow state that flows through LangGraph nodes.

**Connection Pooler**: PgBouncer instance that manages database connections efficiently.

**Smart Routing**: Automatic model selection based on prompt content analysis.

**Auto-Correction Loop**: Automated workflow that regenerates assets with refined prompts until compliance is achieved.

---

## Document Version

**Version**: 1.0  
**Last Updated**: December 6, 2025  
**Status**: Phase 2 Complete  

For questions or clarifications, refer to:
- README.md - Setup and deployment
- DEPLOYMENT-GUIDE.md - Detailed deployment instructions
- API documentation at `/v1/docs` endpoint
