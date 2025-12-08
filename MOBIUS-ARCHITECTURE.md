# Mobius Brand Governance Engine - Architecture

## Overview

Mobius is an AI-powered brand governance platform that generates, audits, and refines brand-compliant visual assets using Google Gemini 3's dual-model architecture.

**Key Features**: 
- Multi-turn conversation for iterative image refinement
- User-controlled workflow with manual review gates
- Vector-First Digital Twin for high-fidelity logo representation
- Dual-model architecture: Vision Model for generation, Reasoning Model for auditing
- Semantic color hierarchy prevents "confetti problem"


## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Runtime** | Modal (Serverless) | Auto-scaling compute |
| **API** | FastAPI | Async HTTP API |
| **Workflow** | LangGraph | State machine orchestration |
| **Database** | Supabase (PostgreSQL) | Transactional data + source of truth |
| **Graph Database** | Neo4j Aura | Relationship intelligence + brand insights |
| **Storage** | Supabase Storage | CDN-backed files |
| **Vision Model** | Gemini 3 Pro Image Preview | Image generation |
| **Reasoning Model** | Gemini 3 Pro Preview | Auditing + PDF parsing |
| **Logo Processing** | CairoSVG + Pillow | SVG rasterization + upscaling |
| **Validation** | Pydantic v2 | Schema validation |
| **Logging** | structlog | Structured logs |

## System Architecture

```
Client (Dashboard/API) → FastAPI → LangGraph Workflow → Gemini 3
                            ↓                              ↓
                      PostgreSQL ← Dual-Write → Neo4j Graph
                    (Source of Truth)      (Relationship Intelligence)

                            Generate → Audit → Route
                                ↑         ↓
                                └─ Correct (if needed)
```

**Hybrid Database Architecture:**
- **PostgreSQL**: Source of truth, transactional data, CRUD operations
- **Neo4j**: Relationship queries, brand insights, color intelligence
- **Dual-Write Pattern**: Non-blocking async sync (0ms latency impact)

**Workflow Routing:**
- Score ≥95%: Auto-approve
- Score 70-95%: Pause for user review
- Score <70% (first attempt): Pause for user review
- Score <70% (after user decision): Auto-correct
- Max 3 attempts: Fail


## Key Workflows

### 1. Brand Onboarding
```
Upload PDF + logo → Extract guidelines → Create Digital Twin → Store
```
- Gemini Reasoning Model extracts colors, typography, logos, voice
- Creates Full Guidelines (auditing) + Compressed Twin (generation)
- Stores PDF, logo, structured data in Supabase

### 2. Asset Generation
```
Prompt → Generate → Audit → Route → Complete/Review/Correct
```

**Generate Node:**
- Loads Compressed Twin (<60k tokens)
- Downloads and processes logos (SVG→PNG, upscale if needed)
- Vision Model generates with brand context
- Uploads result to Supabase Storage (CDN URL)

**Audit Node:**
- Reasoning Model analyzes with full guidelines
- 2-minute timeout prevents hangs
- Returns score + violations + fix suggestions

**Routing Logic:**
- ≥95%: Auto-approve
- 70-95%: User review (approve/tweak/regenerate)
- <70% (first): User review (no auto-correct)
- <70% (after user decision): Auto-correct
- Max 3 attempts: Fail

### 3. Multi-Turn Tweaks
```
Completed job → User tweak → Correct node → Generate (multi-turn) → Audit
```

**How it works:**
- Preserves session_id for multi-turn conversation
- Increments attempt_count to trigger continue_conversation=True
- Passes previous_image_bytes to Gemini for context
- Gemini refines existing image instead of regenerating
- Works across Modal container restarts (fetches previous image from CDN)


## AI Models

### Gemini 3 Dual-Model Architecture

**Vision Model** (`gemini-3-pro-image-preview`)
- **Purpose**: Image generation
- **Input**: Prompt + Compressed Twin (<60k tokens) + Logo images
- **Output**: Generated image URI
- **Cost**: $0.03/generation
- **Features**: Multi-turn conversation, retry logic, 30-120s timeout

**Reasoning Model** (`gemini-3-pro-preview`)
- **Purpose**: PDF parsing + compliance auditing
- **Input**: PDF/Image + Full Guidelines
- **Output**: Structured JSON (scores, violations, fixes)
- **Cost**: $0.001/audit, $0.002/parse
- **Features**: 2-minute timeout, graceful degradation


### Compressed Digital Twin

**Problem**: Full guidelines exceed Vision Model's 65k token limit

**Solution**: Dual representation
- **Full Guidelines**: For auditing (Reasoning Model)
- **Compressed Twin**: For generation (Vision Model, <60k tokens)

**Compressed Twin contains:**
- Hex codes only (no descriptions)
- Font names only (no usage details)
- Concise visual rules (bullet points)
- Essential logo requirements

**Semantic Color Hierarchy** (prevents "confetti problem"):
- Primary: Brand identity (30% visual space)
- Secondary: Supporting elements (30%)
- Accent: CTAs (10%)
- Neutral: Backgrounds, text (60%)
- Semantic: Functional states (contextual)

### Vector-First Logo Processing

**Problem**: Low-res logos cause distorted text and hallucinated details

**Solution**: LogoRasterizer dynamically processes logos
- SVG → High-res PNG (2048px) via CairoSVG
- Low-res raster → Upscaled via Lanczos resampling
- High-res raster → Passthrough (optimization)

**Key Features:**
- Preserves aspect ratio and transparency
- Graceful fallback on errors
- <2s processing time

**Deployment Requirements:**
```python
image = Image.debian_slim() \
    .apt_install("libcairo2") \
    .pip_install("cairosvg>=2.7.0", "pillow>=10.0.0")
```


## Core Data Models

### Brand
```python
brand_id, organization_id, name
guidelines: BrandGuidelines          # Full (for auditing)
compressed_twin: CompressedDigitalTwin  # Optimized (<60k tokens)
pdf_url, logo_thumbnail_url
```

### BrandGuidelines
```python
colors: List[Color]                  # With semantic roles
typography: List[Typography]
logos: List[LogoRule]
voice: VoiceTone
rules: List[BrandRule]
```

### JobState (LangGraph)
```python
job_id, brand_id, prompt
current_image_url, attempt_count
session_id                           # For multi-turn
user_tweak_instruction               # For tweaks
audit_history, compliance_scores
is_approved, status
```

### Job (Database)
```python
job_id, brand_id, status, progress
state: Dict[str, Any]                # Complete JobState
webhook_url, idempotency_key
created_at, updated_at, expires_at
```


## Key Features

### 1. Graph-Powered Brand Intelligence (Competitive Moat)

**The Problem**: Traditional brand governance systems treat each brand in isolation, missing critical insights from cross-brand patterns, color relationships, and usage trends.

**Our Solution**: Dual-database architecture with Neo4j graph intelligence layer.

**Why This is a Moat:**

1. **Network Effects at the Data Layer**
   - Every brand added strengthens the entire platform
   - Color usage patterns emerge across thousands of brands
   - "Brands like yours use these color pairings" insights
   - Competitive differentiation compounds over time

2. **Relationship Intelligence No One Else Has**
   - Which brands share similar color palettes?
   - What colors are commonly paired together?
   - How do brand colors evolve over time?
   - Which color combinations drive highest compliance scores?

3. **Zero-Latency Implementation**
   - Non-blocking async dual-write (0ms performance impact)
   - PostgreSQL remains source of truth (zero risk)
   - Graph queries are read-only (data integrity guaranteed)
   - Graceful degradation if Neo4j unavailable

4. **Scalability Built-In**
   - Graph databases excel at relationship queries
   - O(1) lookup for "find similar brands" (vs O(n²) in SQL)
   - 200k nodes, 400k relationships on free tier
   - Sub-100ms query times even at scale

**Real-World Use Cases:**
- "Show me brands with similar color schemes to inspire this design"
- "What colors pair well with #FF6B35 based on successful brands?"
- "Find templates from brands in the same industry with high compliance"
- "Identify color trends across all enterprise brands this quarter"

**Technical Implementation:**
```python
# Dual-write pattern (fully async, non-blocking)
asyncio.create_task(graph_storage.sync_brand(brand))

# Graph queries (optimized for relationships)
similar_brands = await graph_storage.find_similar_brands(brand_id, limit=10)
color_pairings = await graph_storage.find_color_pairings("#FF6B35")
```

**Data Model:**
- Nodes: Brand, Color, Asset, Template, Feedback
- Relationships: OWNS_COLOR, GENERATED_ASSET, HAS_TEMPLATE, RECEIVED_FEEDBACK
- Properties: usage (primary/secondary/accent), timestamps, scores

### 2. Multi-Turn Conversation
- Preserves session_id across tweaks
- Passes previous_image_bytes to Gemini for context
- Gemini refines existing image instead of regenerating
- Works across Modal container restarts (fetches from CDN)

### 3. User-Controlled Workflow
- First attempt always pauses for review (unless ≥95%)
- No auto-correction without user input
- User chooses: Approve / Tweak / Regenerate
- Auto-correction only after user decision

### 4. Robust Error Handling
- 2-minute audit timeout prevents hangs
- Graceful degradation on failures
- Retry logic with exponential backoff
- Defensive state validation

### 5. Connection Pooling
- Use Supabase pooler (port 6543) not direct (5432)
- Prevents connection exhaustion under load
- Shares 10 connections across all containers

### 6. Idempotency
- Client-provided keys prevent duplicate jobs
- Safe retries after network failures
- 24-hour expiration allows key reuse


## Cost Tracking

| Operation | Cost |
|-----------|------|
| Generation | $0.03 |
| Audit | $0.001 |
| PDF Parse | $0.002 |

**Example Job**: $0.031 (1 gen + 1 audit)
**Monthly (500 assets)**: ~$16


## Deployment

### Modal
```python
image = modal.Image.debian_slim() \
    .apt_install("libcairo2") \
    .pip_install("langgraph", "google-genai", "supabase", 
                 "cairosvg", "pillow", "fastapi", "httpx")
```

**Deploy**: `modal deploy src/mobius/api/app_consolidated.py`

### Supabase
- **Database**: PostgreSQL with pooler (port 6543)
- **Storage**: CDN-backed (brands, assets buckets)
- **Tables**: brands, jobs, assets, templates, feedback


## Security

- Request ID tracing for debugging
- Organization-level data isolation
- Soft deletes with audit trail
- Modal secrets for API keys (GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY)


## Testing

- **Unit**: Config validation, model validation, storage ops
- **Property**: Request ID uniqueness, idempotency, state transitions (Hypothesis)
- **Integration**: End-to-end workflows

**Run**: `pytest -v` (target: >80% coverage)


## Performance

- HTTP client pooling (reuse connections)
- Exponential backoff with jitter
- Async FastAPI handlers
- CDN-backed storage (Supabase)
- Image upload to CDN (reduces database size)


## Recent Enhancements (Dec 2024)

### Neo4j Graph Database Integration (MOAT)
- **Why**: Traditional brand systems miss cross-brand insights and relationship patterns
- **What**: Dual-database architecture with PostgreSQL (source of truth) + Neo4j (relationship intelligence)
- **Impact**:
  - Network effects at data layer - every brand strengthens the platform
  - O(1) similarity queries vs O(n²) in SQL
  - Sub-100ms graph queries even at scale
  - Zero performance impact (non-blocking async dual-write)
- **Competitive Advantage**:
  - Brand similarity matching
  - Color pairing recommendations based on successful brands
  - Cross-brand trend analysis
  - Template recommendations from similar brands
  - Data moat that compounds over time

### Multi-Turn Tweaks
- **Issue**: Tweaks regenerated from scratch instead of refining
- **Fix**: Preserve session_id, pass previous_image_bytes to Gemini
- **Result**: True multi-turn conversation, faster refinements

### User-Controlled Workflow
- **Issue**: Auto-correction without user input on low scores
- **Fix**: First attempt always pauses for review (unless ≥95%)
- **Result**: Users control the process, no unwanted changes

### Audit Timeouts
- **Issue**: Audits hung indefinitely, causing 5-minute timeouts
- **Fix**: 2-minute timeout with graceful degradation
- **Result**: Reliable audits, partial scores on timeout

### Tweak State Validation
- **Issue**: Missing brand_id caused tweak failures
- **Fix**: Defensive state validation, populate from Job model
- **Result**: Robust tweak workflow across container restarts


## Troubleshooting

| Issue | Solution |
|-------|----------|
| Too many connections | Use pooler URL (port 6543) not direct (5432) |
| Rate limit (429) | Auto-retry built-in, check quota at ai.google.dev |
| Auth error (401) | Verify GEMINI_API_KEY in Modal secrets |
| Generation timeout | Auto-retry with 30s→60s→120s timeouts |
| Audit timeout | 2-minute timeout, graceful degradation |
| Logo processing fails | Ensure libcairo2 + cairosvg installed |
| Distorted logos | Check logs for rasterization events |
| Tweak not working | Check brand_id in state, verify session handling |
| Low compliance | Refine guidelines, use templates |


## API Reference

**Base URL**: `https://rocoloco--mobius-v2-final-fastapi-app.modal.run/v1`

### Core Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/brands/ingest` | POST | Upload PDF + logo |
| `/brands` | GET | List brands |
| `/brands/{id}` | GET/PATCH/DELETE | Manage brand |
| `/generate` | POST | Generate asset |
| `/jobs/{id}` | GET | Job status |
| `/jobs/{id}/tweak` | POST | Apply tweak |
| `/templates` | POST/GET | Manage templates |
| `/health` | GET | Health check |
| `/docs` | GET | API docs |

### Graph Intelligence Endpoints (New)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health/graph` | GET | Neo4j connection health |
| `/brands/{id}/graph` | GET | Brand colors + relationships |
| `/brands/{id}/similar` | GET | Find brands with similar palettes |
| `/colors/{hex}/brands` | GET | Brands using this color |
| `/colors/{hex}/pairings` | GET | Common color pairings |


## Key Terms

- **Digital Twin**: Machine-readable brand representation with semantic rules
- **Compressed Twin**: Optimized guidelines (<60k tokens) for Vision Model
- **Vision Model**: Gemini 3 Pro Image Preview (generation)
- **Reasoning Model**: Gemini 3 Pro Preview (auditing, parsing)
- **Semantic Color Hierarchy**: Primary/secondary/accent/neutral roles prevent "confetti problem"
- **LogoRasterizer**: SVG→PNG converter with upscaling (2048px target)
- **Multi-Turn**: Conversation-based refinement using session_id
- **Idempotency Key**: Prevents duplicate job creation
- **Graph Intelligence**: Neo4j-powered relationship queries for brand insights
- **Dual-Write**: Non-blocking async sync to both PostgreSQL and Neo4j
- **Relationship Intelligence**: Cross-brand patterns, color pairings, similarity matching

---

**Version**: 2.3
**Last Updated**: December 7, 2024
**Major Changes**: Neo4j graph intelligence (competitive moat), multi-turn tweaks, user-controlled workflow

For more details, see:
- README.md - Setup and deployment
- DEPLOYMENT-GUIDE.md - Detailed deployment instructions
- API documentation at `/v1/docs` endpoint
