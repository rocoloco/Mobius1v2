# Mobius Brand Governance Engine - Architecture Documentation

## Executive Summary

Mobius is an AI-powered brand governance platform that automatically generates, audits, and corrects brand-compliant visual assets using Google Gemini 3's dual-model architecture.

**Key Differentiators**: 
- Automated correction loop that learns from audit failures and regenerates until compliant
- Vector-First Digital Twin ensures high-fidelity logo representation in all generated assets
- Dual-model architecture: specialized Vision Model for generation, Reasoning Model for auditing

## Core Capabilities

1. **Brand Guidelines Ingestion**: Upload PDF guidelines → AI extracts structured rules → Creates Digital Twin
2. **AI-Powered Asset Generation**: Text prompts → Gemini 3 Vision Model → Brand-compliant images with high-fidelity logos
3. **Automated Compliance Auditing**: Gemini 3 Reasoning Model analyzes images → Category-level scoring → Violation detection
4. **Auto-Correction Loop**: Failed audits → Automatic prompt refinement → Regenerate (up to 3 attempts)
5. **Multi-Brand Management**: Agency-scale portfolio (10-50+ brands) → Per-brand tracking → Reusable templates


## System Architecture

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Runtime** | Modal (Serverless Python) | Scalable compute with auto-scaling |
| **API Framework** | FastAPI | High-performance async HTTP API |
| **Orchestration** | LangGraph | State machine workflows with checkpointing |
| **Database** | Supabase (PostgreSQL) | Structured data storage with connection pooling |
| **File Storage** | Supabase Storage | CDN-backed object storage for PDFs and images |
| **Image Generation** | Google Gemini 3 Pro Image Preview | Native multimodal image generation with brand context |
| **Visual AI** | Google Gemini 3 Pro Preview | Advanced reasoning for compliance auditing |
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
│  ┌──────────────────────────────┐  ┌──────────────┐            │
│  │   Google Gemini 3 API        │  │  Supabase    │            │
│  │  ┌────────────────────────┐  │  │  (Storage)   │            │
│  │  │ Reasoning Model        │  │  │              │            │
│  │  │ (Pro Preview)          │  │  │              │            │
│  │  │ • PDF Parsing          │  │  │              │            │
│  │  │ • Compliance Auditing  │  │  │              │            │
│  │  └────────────────────────┘  │  │              │            │
│  │  ┌────────────────────────┐  │  │              │            │
│  │  │ Vision Model           │  │  │              │            │
│  │  │ (Pro Image Preview)    │  │  │              │            │
│  │  │ • Image Generation     │  │  │              │            │
│  │  └────────────────────────┘  │  │              │            │
│  └──────────────────────────────┘  └──────────────┘            │
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
User uploads PDF + logo → Validates → Gemini extracts guidelines → Creates Digital Twin
                                                                           ↓
                                                    Stores: PDF, logo, structured data
```

**Process:**
1. Upload PDF guidelines (max 50MB) + optional logo (SVG/PNG)
2. Gemini Reasoning Model extracts: colors, typography, logo rules, voice/tone
3. Creates dual representation: Full Guidelines + Compressed Twin
4. Stores in Supabase: PDF (brands bucket), logo (assets bucket), structured data (database)

**Output:** Brand with Digital Twin ready for generation


### 2. Asset Generation Workflow

```
Prompt → Generate (Vision Model + Compressed Twin + High-Fidelity Logos) 
            ↓
         Audit (Reasoning Model + Full Guidelines)
            ↓
      Approved? → Yes: Complete | No: Correct → Loop (max 3 attempts)
```

**Key Steps:**

1. **Generate Node**: 
   - Loads Compressed Twin + downloads/processes logos (LogoRasterizer)
   - Vision Model generates with brand context + high-fidelity logos
   - Returns image URI

2. **Audit Node**: 
   - Reasoning Model analyzes image with full guidelines
   - Returns: approved (bool), confidence (0-1), fix_suggestion (string)

3. **Routing**: 
   - Approved → Complete
   - Max attempts (3) → Failed
   - Otherwise → Correct Node (refine prompt) → Loop

**Logo Processing in Generate Node:**
- Downloads logos from Supabase Storage
- Applies LogoRasterizer.prepare_for_vision():
  - SVG → High-res PNG (2048px)
  - Low-res raster → Upscaled PNG
  - High-res raster → Passthrough
- Passes processed logos to Vision Model


### 3. Template Workflow

```
High-compliance asset (≥95%) → Save as template → Reuse for future generations
```

**Process:** Asset with ≥95% compliance → Save template (prompt + parameters + thumbnail) → Apply to future generations (pre-filled, editable)


## AI Models Used

### 1. Google Gemini 3 Dual-Architecture

Mobius uses a dual-model architecture that leverages specialized Gemini 3 models for different tasks. This approach optimizes both performance and cost by using the right model for each operation.

**Gemini 3 Pro Image Preview** (`gemini-3-pro-image-preview`) - Vision Model
- **Purpose**: Native multimodal image generation
- **When used**: All image generation requests in the Generate Node
- **Key Features**: 
  - Native image generation without external dependencies
  - Accepts compressed brand guidelines (up to 65k tokens) in system prompt
  - Produces high-quality, brand-consistent images
  - Returns image URIs for downstream processing
  - Integrated retry logic with exponential backoff
- **Cost**: ~$0.03 per generation
- **Context Window**: 65k tokens (accommodates compressed brand guidelines)
- **Architecture Role**: Replaces legacy Fal.ai (Flux/Ideogram) image generation
- **Example prompts**: 
  - "Professional product photo on white background"
  - "Team collaboration in modern office"
  - "Social media banner with headline text"
  - "Logo design with company name"

**Gemini 3 Pro Preview** (`gemini-3-pro-preview`) - Reasoning Model
- **Purpose**: Advanced reasoning for PDF parsing and compliance auditing
- **When used**: 
  - PDF ingestion (extracting brand guidelines)
  - Compliance auditing (evaluating generated images)
- **Key Features**:
  - Superior reasoning capabilities for complex analysis
  - Multimodal vision input (accepts image URIs)
  - Structured JSON output for compliance scores
  - Full brand guidelines context for comprehensive auditing
- **Input**: Image URI + full brand guidelines text
- **Output**: Structured JSON audit result with category breakdowns
- **Cost**: ~$0.001 per audit, ~$0.002 per PDF parse
- **Temperature**: 0.1 (low randomness for consistency)
- **Architecture Role**: Handles all reasoning-intensive tasks

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


### 2. Compressed Digital Twin Architecture

**Design Philosophy**: The Vision Model has a 65k token context window, which is insufficient for full brand guidelines. To solve this, we extract a "Compressed Digital Twin" during ingestion that contains only essential visual rules.

**The Challenge**: Full brand guidelines often contain:
- Verbose color descriptions and emotional attributes
- Detailed typography usage examples
- Historical brand context and evolution
- Comprehensive voice/tone guidelines
- Legal disclaimers and edge cases

This can easily exceed 100k+ tokens, far beyond the Vision Model's 65k limit.

**The Solution**: Dual-representation architecture:
1. **Full BrandGuidelines**: Stored for comprehensive auditing (used by Reasoning Model)
2. **CompressedDigitalTwin**: Optimized for generation (used by Vision Model)

**Extraction Process** (using Reasoning Model):
1. Extract text from PDF using PyMuPDF
2. Send to Gemini 3 Pro Preview (Reasoning Model) with compression prompt
3. Reasoning Model extracts only:
   - Hex color codes (no verbose descriptions)
   - Font family names (no detailed usage)
   - Critical visual constraints (concise bullet points)
   - Logo placement rules (essential only)
4. Validate compressed twin is under 60k tokens
5. Store both full guidelines (for auditing) and compressed twin (for generation)

**Why Two Representations?**
- **Compressed Twin**: Injected into Vision Model during generation (fits in 65k context)
- **Full Guidelines**: Provided to Reasoning Model during auditing (comprehensive analysis)

### 3. Vector-First Digital Twin (Logo Fidelity)

**The Problem**: The Vision Model was receiving low-resolution logo thumbnails (~8KB) during generation, causing hallucinated details and distorted text with jagged edges. This degraded output quality and brand compliance.

**The Solution**: Dynamic logo processing that ensures the Vision Model always receives high-fidelity logo representations:
- **SVG logos**: Rasterized to high-resolution PNGs (up to 2048px) at runtime
- **Low-res raster logos**: Intelligently upscaled using Lanczos resampling
- **High-res logos**: Passed through unchanged (optimization)

**Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Logo Processing Flow                      │
│                                                              │
│  Brand Upload → Supabase Storage → Generation Request       │
│                                            ↓                 │
│                                    ┌───────────────┐        │
│                                    │ Generate Node │        │
│                                    └───────┬───────┘        │
│                                            │                 │
│                                    Download logos           │
│                                            ↓                 │
│                                    ┌───────────────┐        │
│                                    │LogoRasterizer │        │
│                                    │               │        │
│                                    │ • SVG→PNG     │        │
│                                    │ • Upscale     │        │
│                                    │ • Preserve    │        │
│                                    │   aspect      │        │
│                                    └───────┬───────┘        │
│                                            │                 │
│                                    High-fidelity PNG        │
│                                            ↓                 │
│                                    ┌───────────────┐        │
│                                    │ Vision Model  │        │
│                                    │ (Generation)  │        │
│                                    └───────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

**LogoRasterizer Utility** (`src/mobius/utils/media.py`):

The `LogoRasterizer` class provides a single static method for logo processing:

```python
LogoRasterizer.prepare_for_vision(
    logo_bytes: bytes,
    mime_type: str,
    target_dim: int = 2048
) -> bytes
```

**Processing Logic**:

1. **SVG Detection**: Check if `mime_type` contains "svg"
2. **SVG Rasterization** (if SVG):
   - Use `cairosvg.svg2png()` to render at high resolution
   - Calculate dimensions preserving aspect ratio (longest side = target_dim)
   - Preserve transparency in output PNG
   - Fallback to original bytes on error
3. **Raster Upscaling** (if PNG/JPEG/WebP):
   - Load image with PIL
   - If longest dimension < 1000px: upscale to target_dim using Lanczos
   - If longest dimension >= 1000px: return original (passthrough optimization)
   - Preserve transparency and aspect ratio
   - Fallback to original bytes on error
4. **Error Handling**: Never raises exceptions, always returns bytes

**Key Features**:
- **Aspect Ratio Preservation**: Logos maintain original proportions (no forced squares)
- **Transparency Preservation**: Alpha channels preserved in all outputs
- **Graceful Degradation**: Returns original bytes if processing fails
- **Performance Optimization**: High-res images bypass processing
- **Structured Logging**: All operations logged with context

**Deployment Requirements**:

Modal image must include Cairo graphics library:

```python
image = Image.debian_slim() \
    .apt_install("libcairo2")  # OS-level Cairo library \
    .pip_install(
        "cairosvg>=2.7.0",  # Python SVG rasterization
        "pillow>=10.0.0",   # Raster image processing
        # ... other dependencies
    )
```

**Configuration**:
- `target_dim`: Maximum dimension for processed logos (default: 2048px)
- Configurable per-call, but 2048px provides optimal quality/size balance

**Common Issues**:

| Issue | Cause | Solution |
|-------|-------|----------|
| SVG not rasterizing | Missing libcairo2 | Add to Modal image `apt_install` |
| Import error | cairosvg not installed | Add to Modal image `pip_install` |
| Distorted logos | Aspect ratio not preserved | Verify LogoRasterizer calculates dimensions correctly |
| Low quality output | target_dim too low | Increase to 2048px (default) |
| Processing timeout | Very large SVG files | Simplify SVG or increase timeout |

**Performance**:
- SVG rasterization: < 2 seconds for files under 1MB
- Raster upscaling: < 1 second for typical logos
- High-res passthrough: < 10ms (just byte comparison)
- Memory usage: ~150MB peak per logo

### 3. PDF Parsing with Reasoning Model

**Gemini 3 Pro Preview** (`gemini-3-pro-preview`)
- **Purpose**: Extract structured brand guidelines from PDFs
- **Input**: PDF text content + section hints
- **Output**: Two representations:
  - Full BrandGuidelines (comprehensive)
  - CompressedDigitalTwin (optimized for Vision Model)
- **Process**:
  1. Extract text from PDF using PyMuPDF
  2. Identify sections (colors, typography, logos, voice)
  3. Send to Reasoning Model with comprehensive extraction prompt
  4. Parse JSON response into structured models
  5. Generate compressed twin for generation use

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
    guidelines: BrandGuidelines      # Full Digital Twin (for auditing)
    compressed_twin: Optional[CompressedDigitalTwin]  # Optimized for generation
    pdf_url: Optional[str]           # Original PDF location
    logo_thumbnail_url: Optional[str] # Logo image URL
    needs_review: List[str]          # Items flagged for review
    learning_active: bool            # ML learning enabled
    feedback_count: int              # Total feedback events
    created_at: str                  # ISO timestamp
    updated_at: str                  # ISO timestamp
```

**Dual Representation Strategy:**
- `guidelines`: Full BrandGuidelines used by Reasoning Model for comprehensive auditing
- `compressed_twin`: CompressedDigitalTwin used by Vision Model for generation (< 60k tokens)

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

**Color Model** (with Semantic Hierarchy):
```python
class Color(BaseModel):
    name: str                        # "Forest Green"
    hex: str                         # "#2D5016"
    usage: Literal["primary", "secondary", "accent", "neutral", "semantic"]
    usage_weight: float              # 0.0-1.0 (estimated usage frequency)
    context: Optional[str]           # Usage guidelines
```

**Semantic Color Roles** (prevents "Confetti Problem"):
- **Primary**: Dominant brand identity (logos, headers) - 30% visual space
- **Secondary**: Supporting elements (shapes, icons) - 30% visual space
- **Accent**: High-visibility CTAs (buttons, links) - 10% visual space
- **Neutral**: Backgrounds, body text - 60% visual space
- **Semantic**: Functional states (success, error) - contextual use

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

**CompressedDigitalTwin Model** (New in Gemini 3):
```python
class CompressedDigitalTwin(BaseModel):
    """
    Optimized brand guidelines for Vision Model context window.
    Contains only essential visual rules to fit within 65k tokens.
    """
    # Semantic color hierarchy (prevents "Confetti Problem")
    primary_colors: List[str]        # ["#0057B8", "#1E3A8A"]
    secondary_colors: List[str]      # ["#FF5733", "#C70039"]
    accent_colors: List[str]         # ["#FFC300", "#00D9FF"]
    neutral_colors: List[str]        # ["#FFFFFF", "#F5F5F5", "#333333"]
    semantic_colors: List[str]       # ["#10B981", "#EF4444"]
    
    # Typography (concise)
    font_families: List[str]         # ["Helvetica Neue", "Georgia"]
    
    # Critical constraints (bullet points only)
    visual_dos: List[str]            # Positive rules
    visual_donts: List[str]          # Negative rules
    
    # Logo requirements (essential only)
    logo_placement: Optional[str]    # "top-left or center"
    logo_min_size: Optional[str]     # "100px width"
    
    def estimate_tokens(self) -> int:
        """Estimate token count for validation."""
        pass
    
    def validate_size(self) -> bool:
        """Ensure < 60k token limit."""
        pass
```

**Why Semantic Color Hierarchy?**

Without semantic roles, the Vision Model knows THAT colors are approved but not HOW to use them. This causes the "Confetti Problem" - technically correct colors but chaotic distribution (e.g., neon backgrounds, light text).

By capturing semantic roles (primary, secondary, accent, neutral, semantic), we enable the Vision Model to follow proper design principles like the 60-30-10 rule, ensuring generated images are both on-brand AND aesthetically professional.


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


### 3. Unified Generation Architecture

**Previous Architecture** (Legacy):
- Multiple external services (Fal.ai with Flux/Ideogram models)
- Complex routing logic between different providers
- Multiple API keys and authentication flows
- Inconsistent quality across models

**Current Architecture** (Gemini 3):
- Single Vision Model for all image generation
- Native Google AI integration
- Simplified authentication (one API key)
- Consistent quality and style

**Why Gemini 3 Vision Model for Everything**:
- **Unified Model**: Single model handles all types of image generation
- **Native Multimodal**: Built-in understanding of visual concepts
- **Brand Context**: Accepts compressed guidelines in system prompt
- **Consistent Quality**: No variation between different providers
- **Simplified Architecture**: Fewer dependencies and integration points
- **Cost Effective**: Competitive pricing with better quality

**Examples**:
- "Product photo on white background" → Gemini 3 Vision Model
- "Social media banner with headline" → Gemini 3 Vision Model
- "Logo design with company name" → Gemini 3 Vision Model
- "Team collaboration in office" → Gemini 3 Vision Model

**Architecture Benefits**:
- Removed Fal.ai dependency entirely
- Eliminated fal-client package
- Simplified deployment (one less API key)
- Better integration with Google ecosystem


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
image = modal.Image.debian_slim() \
    .apt_install("libcairo2")  # Required for SVG rasterization \
    .pip_install(
        "langgraph>=0.2.0",
        "google-genai>=1.0.0",
        "supabase>=2.0.0",
        "httpx>=0.27.0",
        "fastapi>=0.110.0",
        "cairosvg>=2.7.0",  # SVG to PNG conversion
        "pillow>=10.0.0",   # Raster image processing
    )
```

**Critical Dependencies for Logo Processing**:
- `libcairo2`: OS-level Cairo graphics library (apt_install)
- `cairosvg`: Python SVG rasterization library (pip_install)
- `pillow`: Python image processing library (pip_install)

Without these dependencies, SVG logos will not be rasterized and may appear distorted in generated images.

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

# Note: FAL_KEY no longer required (Fal.ai removed in Gemini 3 refactor)
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


## Architecture Migration: Fal.ai to Gemini 3

### Previous Architecture (Legacy)

**Image Generation Stack:**
- External service: Fal.ai
- Models: Flux Pro, Ideogram v2
- Authentication: Separate FAL_KEY required
- Integration: REST API with polling
- Context: Limited brand context in prompts
- Cost: Variable pricing per model

**Limitations:**
- Multiple external dependencies
- Complex model routing logic
- Inconsistent quality across models
- Limited brand context injection
- Additional API key management
- Network latency from multiple hops

### Current Architecture (Gemini 3 Dual-Model)

**Image Generation Stack:**
- Native service: Google Gemini 3
- Models: 
  - Vision Model (gemini-3-pro-image-preview) for generation
  - Reasoning Model (gemini-3-pro-preview) for auditing
- Authentication: Single GEMINI_API_KEY
- Integration: Native Google AI SDK
- Context: Compressed Digital Twin (up to 65k tokens)
- Cost: Predictable pricing ($0.03/generation)

**Benefits:**
- Single AI provider (simplified architecture)
- Specialized models for each task
- Consistent quality and style
- Rich brand context in generation
- Unified authentication
- Better integration with Google ecosystem
- Reduced network latency

**Migration Impact:**
- Removed `fal-client` package dependency
- Removed `fal_api_key` from configuration
- Simplified deployment (one less secret)
- Improved generation quality
- Better brand compliance
- Lower operational complexity

### Backward Compatibility

**API Compatibility:** ✅ Maintained
- All endpoints unchanged
- Request/response schemas identical
- Existing clients work without modification

**Data Compatibility:** ✅ Maintained
- Database schema unchanged (added optional `compressed_twin` field)
- Existing brands work with new architecture
- Lazy migration: compressed twin generated on first use

**Feature Parity:** ✅ Maintained
- All features preserved
- Auto-correction loop unchanged
- Template system unchanged
- Webhook notifications unchanged

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

**2. Gemini API rate limit errors (429)**

**Cause**: Exceeded Gemini API rate limits

**Solution**:
- Automatic retry with exponential backoff (built-in)
- Check API quota in [Google AI Studio](https://ai.google.dev)
- Upgrade API tier if needed for production workloads
- Monitor rate limit errors in logs (includes model name for debugging)
- Free tier: 15 RPM, Paid tier: 1000+ RPM

**Rate Limit Best Practices**:
- Implement request queuing for high-volume scenarios
- Use idempotency keys to prevent duplicate requests
- Monitor `retry-after` header in error responses
- Consider batch processing during off-peak hours

**3. Gemini API authentication errors (401)**

**Cause**: Invalid or missing API key

**Solution**:
- Verify `GEMINI_API_KEY` is set in Modal secrets:
  ```bash
  modal secret list  # Check if mobius-secrets exists
  ```
- Ensure API key is from [Google AI Studio](https://ai.google.dev), not Google Cloud Console
- Test API key validity:
  ```bash
  curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
  ```
- Check API key hasn't expired or been revoked
- Confirm Gemini API access is enabled for your key

**4. Image generation timeouts**

**Cause**: Complex prompts or API latency

**Solution**:
- System automatically retries with increased timeout (built-in)
- Check Gemini API status at [Google Cloud Status](https://status.cloud.google.com)
- Simplify complex prompts if possible
- Review logs for timeout duration and model name
- Consider breaking complex generations into simpler steps

**Timeout Configuration**:
- Default: 30 seconds
- Retry 1: 45 seconds
- Retry 2: 60 seconds
- Max retries: 3 attempts

**5. Compressed twin token limit exceeded**

**Cause**: Brand guidelines too verbose for Vision Model context window

**Solution**:
- System automatically compresses to fit 60k token limit
- If still failing, PDF may contain excessive repetition
- Review PDF for boilerplate text or redundant sections
- Manually edit PDF to remove non-essential content
- Check logs for actual token count estimate

**Token Optimization Tips**:
- Remove historical brand context
- Eliminate verbose color descriptions
- Use concise bullet points for rules
- Focus on visual guidelines only

**6. PDF ingestion fails**

**Possible causes**:
- PDF exceeds 50MB limit
- PDF is corrupted or password-protected
- PDF contains no extractable text (scanned images)
- Gemini API error during extraction

**Solution**:
- Compress PDF or split into sections
- Remove password protection
- OCR scanned PDFs before upload
- Check logs for specific Gemini API errors
- Verify PDF has extractable text (not just images)

**7. Webhook not received**

**Possible causes**:
- Webhook URL not publicly accessible
- Endpoint returns non-200 status
- Firewall blocking requests

**Solution**:
- Test webhook URL with curl
- Check webhook endpoint logs
- Review `webhook_attempts` in jobs table
- Verify firewall rules

**8. Low compliance scores**

**Possible causes**:
- Brand guidelines too vague
- Conflicting style rules
- Unrealistic expectations
- Compressed twin missing critical context

**Solution**:
- Review and refine brand guidelines
- Add more specific color/style rules
- Use templates from successful generations
- Provide more detailed prompts
- Check compressed twin contains essential rules

**9. Model selection errors**

**Cause**: Incorrect model name or configuration

**Solution**:
- Verify model names in configuration:
  - Vision Model: `gemini-3-pro-image-preview`
  - Reasoning Model: `gemini-3-pro-preview`
- Check logs for model initialization errors
- Ensure both models are available in your region
- Confirm API key has access to both models

**10. Multimodal input errors**

**Cause**: Image URI format or size issues

**Solution**:
- Verify image URI is accessible
- Check image size is under 20MB
- Ensure image format is supported (PNG, JPEG, WebP)
- Review logs for specific multimodal input errors
- Test image URI accessibility with curl

**11. Logo processing failures**

**Cause**: SVG rasterization or image upscaling errors

**Solution**:
- Verify `libcairo2` is installed in Modal image:
  ```python
  image = Image.debian_slim().apt_install("libcairo2")
  ```
- Ensure `cairosvg>=2.7.0` is in pip dependencies
- Check logs for "logo_processing_failed" events
- Review error_type and error_message in structured logs
- Test with simpler SVG files to isolate complexity issues
- Verify logo files are not corrupted

**Common Logo Processing Errors**:
- `ImportError: cairosvg not found`: Add to Modal image pip_install
- `OSError: cannot load library 'libcairo.so.2'`: Add libcairo2 to apt_install
- `SVGParseError`: Malformed SVG XML (system falls back to original)
- `PIL.UnidentifiedImageError`: Corrupted raster image (system falls back to original)

**12. Distorted or low-quality logos in generated images**

**Cause**: Logo processing not applied or insufficient resolution

**Solution**:
- Verify LogoRasterizer is integrated in Generate Node
- Check logs for "rasterizing_vector_logo" or "upscaling_low_res_logo" events
- Confirm target_dim is set to 2048px (default)
- Ensure logos are being processed before Vision Model input
- Review original logo file quality and format
- Test with known good SVG files

**Quality Checklist**:
- SVG logos should show "rasterizing_vector_logo" in logs
- Low-res rasters should show "upscaling_low_res_logo" in logs
- High-res rasters should show "using_original_logo" in logs
- Processed logos should be PNG format
- Aspect ratios should match original (no squashing)


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

**Compressed Digital Twin**: An optimized subset of brand guidelines (< 60k tokens) designed to fit within the Vision Model's context window. Contains only essential visual rules: hex codes, font names, and concise constraints.

**Brand Guidelines**: PDF document containing brand identity rules (colors, typography, logos, voice/tone).

**Compliance Score**: 0-100 score indicating how well an asset adheres to brand guidelines.

**Reasoning Model**: Gemini 3 Pro Preview - specialized for complex reasoning tasks (PDF parsing, compliance auditing). Superior analytical capabilities with multimodal vision input.

**Vision Model**: Gemini 3 Pro Image Preview - specialized for image generation. Accepts compressed brand guidelines in system prompt (up to 65k tokens).

**Audit Node**: LangGraph node that uses Reasoning Model to evaluate brand compliance with full guidelines context.

**Generate Node**: LangGraph node that creates images using Vision Model with compressed twin injection.

**Correct Node**: LangGraph node that refines prompts based on audit feedback.

**Template**: Reusable generation configuration saved from high-performing assets (≥95% compliance).

**Idempotency Key**: Client-provided unique identifier to prevent duplicate job creation.

**Webhook**: HTTP callback for async job completion notifications.

**Job State**: Complete workflow state that flows through LangGraph nodes.

**Connection Pooler**: PgBouncer instance that manages database connections efficiently.

**Smart Routing**: Automatic model selection based on prompt content analysis.

**Auto-Correction Loop**: Automated workflow that regenerates assets with refined prompts until compliance is achieved.

**Semantic Color Hierarchy**: Color categorization system (primary, secondary, accent, neutral, semantic) that prevents the "Confetti Problem" by teaching the Vision Model HOW to use colors, not just THAT they're approved.

**Confetti Problem**: When colors are technically correct but aesthetically chaotic due to lack of usage hierarchy (e.g., neon backgrounds, light text). Solved by semantic color roles.

**Vector-First Digital Twin**: Strategy where SVG logos are dynamically rasterized to high-fidelity PNGs at runtime, ensuring the Vision Model receives perfect geometry regardless of source file size.

**LogoRasterizer**: Utility class that converts vector logos to high-resolution raster images and upscales low-resolution logos while preserving aspect ratios and transparency.

**Rasterization**: The process of converting vector graphics (SVG) to pixel-based images (PNG) at a specific resolution.

**Lanczos Resampling**: High-quality image upscaling algorithm that preserves edge sharpness and detail when enlarging raster images.

**CairoSVG**: Python library that renders SVG files to PNG format using the Cairo graphics library, enabling high-fidelity vector-to-raster conversion.

**Target Dimension**: Maximum dimension (width or height) for processed logos, default 2048px, providing optimal quality for Vision Model input.

---

## Document Version

**Version**: 2.1  
**Last Updated**: December 7, 2025  
**Status**: Vector-First Digital Twin (Logo Fidelity Enhancement)  
**Major Changes**: 
- Replaced Fal.ai with Gemini 3 native image generation (v2.0)
- Implemented dual-model architecture (Reasoning + Vision) (v2.0)
- Added Compressed Digital Twin for context optimization (v2.0)
- Implemented Vector-First Digital Twin for logo fidelity (v2.1)
- Added LogoRasterizer utility for dynamic SVG rasterization (v2.1)

For questions or clarifications, refer to:
- README.md - Setup and deployment
- DEPLOYMENT-GUIDE.md - Detailed deployment instructions
- API documentation at `/v1/docs` endpoint
