# Mobius Brand Governance Engine

AI-powered brand governance platform that generates, audits, and refines brand-compliant visual assets.

## Quick Start

### Backend (Modal + Supabase)
```bash
# Install dependencies
pip install -e .

# Set up environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY, NEO4J credentials

# Deploy to Modal
modal deploy src/mobius/api/app_consolidated.py
```

### Frontend (Luminous Dashboard)
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY
npm run dev
```

See [frontend/README.md](frontend/README.md) for detailed frontend documentation.

---

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
| **Frontend** | React + Vite + Tailwind | Luminous Dashboard |

## Frontend: Luminous Dashboard

"Luminous Structuralism" - The UI is the stage; the Brand Asset is the star.

| Zone | Purpose |
|------|---------|
| **Director** | Multi-turn chat for AI interaction |
| **Canvas** | Image viewport with compliance bounding boxes |
| **Compliance Gauge** | Radial score chart + violation list |
| **Context Deck** | Active brand constraints |
| **Twin Data** | Detected colors/fonts inspector |

**Stack**: React 19, Vite, Tailwind CSS, Framer Motion, VisX charts, Supabase Realtime

See [frontend/README.md](frontend/README.md) for component docs and setup.

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

### BrandGuidelines (The Brand Graph)
```python
# Identity Core (MOAT: Strategic positioning)
identity_core: IdentityCore          # Archetype, voice vectors, negative constraints

# Visual DNA
colors: List[Color]                  # With semantic roles + usage weights
typography: List[Typography]
logos: List[LogoRule]

# Verbal Soul
voice: VoiceTone

# Governance Rules
rules: List[BrandRule]               # Category, severity, negative constraints

# Context-Specific Rules (MOAT: Channel governance)
contextual_rules: List[ContextualRule]  # LinkedIn vs Instagram, print vs digital

# Asset Inventory (MOAT: Single source of truth)
asset_graph: AssetGraph              # Logo variants, templates, patterns

# Metadata
version: str                         # Semantic versioning (e.g., "2.1.0")
source_filename, ingested_at
```

### IdentityCore (New - MOAT)
```python
archetype: str                       # "The Sage", "The Hero", "The Rebel"
voice_vectors: Dict[str, float]      # formal: 0.8, witty: 0.2, urgent: 0.0
negative_constraints: List[str]      # "No drop shadows", "No neon colors"
```

### ContextualRule (New - MOAT)
```python
context: str                         # "social_media_linkedin", "print_packaging"
rule: str                            # "Images must contain human subjects"
priority: int                        # 1-10 (higher = more important)
applies_to: List[str]                # ["image", "video", "document"]
```

### AssetGraph (New - MOAT)
```python
logos: Dict[str, str]                # {"primary": "s3://...", "reversed": "s3://..."}
templates: Dict[str, str]            # {"social_post": "s3://...", "email_header": "s3://..."}
patterns: Dict[str, str]             # {"background_texture": "s3://..."}
photography_style: str               # URL to style guide
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

### 1. Brand Graph as Operating System (The Data Moat)

**The Problem**: Competitors can replicate image generation, but they can't replicate your structured brand data if clients integrate it into their internal tools.

**Our Solution**: Expose the brand as a machine-readable "operating system" via API, creating lock-in through developer integrations.

**Why This is a Moat:**

1. **Developer Integration Lock-In**
   - Client dev teams use `GET /v1/brands/{id}/graph` for official hex codes, fonts, rules
   - Internal design systems depend on your API (React components, Figma plugins)
   - Marketing automation pulls brand data (HubSpot, Marketo integrations)
   - Multi-brand dashboards built on your API
   - **Migration cost: $50k-$150k in engineering time**

2. **Structured Data Ownership**
   - PDF is just a render - you own the machine-readable truth
   - Identity core: Archetype, voice vectors (formal: 0.8, witty: 0.2)
   - Contextual rules: LinkedIn vs Instagram, print vs digital
   - Asset graph: Logo variants, templates, patterns
   - **Competitors would need to replicate entire schema + all integrations**

3. **Network Effects at the Data Layer**
   - Every brand added strengthens the platform
   - Color usage patterns emerge across thousands of brands
   - "Brands like yours use these color pairings" insights
   - Cross-brand trend analysis (industry benchmarks)
   - **Competitive differentiation compounds over time**

4. **Relationship Intelligence (Neo4j Graph)**
   - Which brands share similar color palettes?
   - What colors are commonly paired together?
   - Which color combinations drive highest compliance scores?
   - Template recommendations from similar brands
   - **O(1) graph queries vs O(n²) in SQL**

**Real-World Lock-In Scenarios:**

1. **Internal Design System**
   ```javascript
   // Client's React components depend on your API
   const { visual_tokens } = useBrandGraph('b_123');
   const primaryColor = visual_tokens.colors.find(c => c.semantic_role === 'primary').hex;
   ```

2. **Marketing Automation**
   ```python
   # Client's HubSpot integration pulls brand colors
   brand = requests.get('https://api.mobius.com/v1/brands/b_123/graph').json()
   primary_color = next(c['hex'] for c in brand['visual_tokens']['colors'] 
                        if c['semantic_role'] == 'primary')
   ```

3. **Multi-Brand Dashboard**
   ```typescript
   // Enterprise client's brand management portal
   const brands = await Promise.all(
     brandIds.map(id => fetch(`/v1/brands/${id}/graph`).then(r => r.json()))
   );
   ```

**Technical Implementation:**
```python
# Dual-write pattern (fully async, non-blocking)
asyncio.create_task(graph_storage.sync_brand(brand))

# Brand Graph API (returns full structured data)
GET /v1/brands/{id}/graph
{
  "identity_core": {"archetype": "The Sage", "voice_vectors": {...}},
  "visual_tokens": {"colors": [...], "typography": [...], "logos": [...]},
  "contextual_rules": [{"context": "social_media_linkedin", "rule": "..."}],
  "asset_graph": {"logos": {...}, "templates": {...}},
  "relationships": {"similar_brands": [...], "color_pairings": [...]}
}

# Graph queries (optimized for relationships)
similar_brands = await graph_storage.find_similar_brands(brand_id, limit=10)
color_pairings = await graph_storage.find_color_pairings("#FF6B35")
```

**Data Model:**
- **PostgreSQL**: Source of truth (brands, assets, jobs)
- **Neo4j**: Relationship intelligence (brand similarity, color pairings)
- **Dual-Write**: Non-blocking async sync (0ms latency impact)
- **Nodes**: Brand, Color, Asset, Template, Feedback
- **Relationships**: OWNS_COLOR, GENERATED_ASSET, HAS_TEMPLATE, RECEIVED_FEEDBACK
- **Properties**: usage (primary/secondary/accent), timestamps, scores

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

### Brand Graph as Operating System (THE MOAT)
- **Why**: Competitors can replicate image generation, but not structured brand data integrated into client tools
- **What**: Expose brand as machine-readable API that clients integrate into internal systems
- **Impact**:
  - **Developer lock-in**: Design systems, marketing automation, dashboards depend on your API
  - **Migration cost**: $50k-$150k to extract data + rewrite integrations
  - **Network effects**: More brands = better insights = higher value
  - **Structured data ownership**: You own the truth, PDF is just a render
- **New Schema Fields**:
  - `IdentityCore`: Archetype, voice vectors (formal: 0.8, witty: 0.2), negative constraints
  - `ContextualRule`: Channel-specific rules (LinkedIn vs Instagram, print vs digital)
  - `AssetGraph`: Logo variants, templates, patterns (single source of truth)
- **API Endpoint**: `GET /v1/brands/{id}/graph` returns complete Brand Graph
- **Competitive Advantage**:
  - Midjourney/DALL-E: Just generate images, no structured data
  - Canva: Templates only, no programmatic API
  - Figma: Design tool, not a brand operating system
  - **Mobius**: Only platform exposing brand as machine-readable graph with API

### Neo4j Graph Database Integration (Relationship Intelligence)
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

### Critical System Fixes

#### Async Mode Implementation
- **Issue**: Dashboard getting `ERR_CONNECTION_CLOSED` errors during 70-second generation process
- **Root Cause**: Async mode was not implemented - ran synchronously despite `async_mode=true`
- **Fix**: Implemented true async mode using `asyncio.create_task()` for background processing
- **Result**: Immediate response with polling, no connection timeouts

#### Review Threshold Correction
- **Issue**: Jobs scoring 91-98% were auto-approved instead of triggering review
- **Root Cause**: Gemini audit prompt used ≥80% threshold instead of ≥95%
- **Fix**: Corrected audit prompt to match architecture: 95%+ auto-approve, 70-95% review
- **Result**: Proper workflow routing aligned with documented architecture

#### Neo4j Connection Stability
- **Issue**: "Unable to retrieve routing information" errors during graph sync
- **Root Cause**: Using `asyncio.create_task()` caused connection cleanup race conditions
- **Fix**: Changed to `await` graph sync operations to ensure completion before cleanup
- **Result**: Reliable graph database synchronization

#### Visual Scan Integration
- **Issue**: Visual scraper extracted MOAT data but ingestion handler ignored it
- **Root Cause**: Missing `visual_scan_data` parameter handling in brand ingestion
- **Fix**: Added visual scan data merging to enrich brands with archetype and voice vectors
- **Result**: Complete MOAT structure from website analysis + PDF parsing

#### Multi-Turn Conversation
- **Issue**: Tweaks regenerated from scratch instead of refining existing images
- **Fix**: Preserve session_id, pass previous_image_bytes to Gemini for context
- **Result**: True multi-turn conversation, faster refinements

#### Audit Timeouts
- **Issue**: Audits hung indefinitely, causing 5-minute timeouts
- **Fix**: 2-minute timeout with graceful degradation
- **Result**: Reliable audits, partial scores on timeout

#### Tweak State Validation
- **Issue**: Missing brand_id caused tweak failures across container restarts
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
| ERR_CONNECTION_CLOSED | Enable async mode in dashboard, ensure proper polling |
| Neo4j routing errors | Use `await` instead of `create_task()` for graph sync |
| Visual scan data ignored | Verify `visual_scan_data` parameter in ingestion |
| Auto-approval at 80%+ | Check audit prompt uses ≥95% threshold |
| Missing identity core | Ensure visual scan includes archetype extraction |
| Webhook delivery fails | Check webhook URL accessibility, review retry logs |


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

### Brand Graph API (MOAT - Creates Lock-In)

| Endpoint | Method | Purpose | Lock-In Value |
|----------|--------|---------|---------------|
| `/brands/{id}/graph` | GET | **Full Brand Graph** - identity core, visual tokens, contextual rules, asset graph | **HIGH** - Clients integrate into internal tools |
| `/brands/{id}/similar` | GET | Find brands with similar palettes | Medium - Inspiration features |
| `/colors/{hex}/brands` | GET | Brands using this color | Low - Analytics |
| `/colors/{hex}/pairings` | GET | Common color pairings (MOAT feature) | **HIGH** - Unique intelligence |
| `/health/graph` | GET | Neo4j connection health | Low - Monitoring |

**Key Insight**: `/brands/{id}/graph` is the crown jewel - it returns the complete machine-readable brand operating system that clients will integrate into their design systems, marketing automation, and internal dashboards. This creates lock-in because migrating would require rewriting all those integrations.


## Key Terms

- **Brand Graph**: Machine-readable brand "operating system" exposed via API (THE MOAT)
- **Digital Twin**: Complete brand representation with semantic rules (for auditing)
- **Compressed Twin**: Optimized guidelines (<60k tokens) for Vision Model (for generation)
- **Identity Core**: Brand archetype + voice vectors + negative constraints (MOAT field)
- **Contextual Rules**: Channel-specific governance (LinkedIn vs Instagram) (MOAT field)
- **Asset Graph**: Structured inventory of logos, templates, patterns (MOAT field)
- **Vision Model**: Gemini 3 Pro Image Preview (generation)
- **Reasoning Model**: Gemini 3 Pro Preview (auditing, parsing)
- **Semantic Color Hierarchy**: Primary/secondary/accent/neutral roles prevent "confetti problem"
- **LogoRasterizer**: SVG→PNG converter with upscaling (2048px target)
- **Multi-Turn**: Conversation-based refinement using session_id
- **Idempotency Key**: Prevents duplicate job creation
- **Graph Intelligence**: Neo4j-powered relationship queries for brand insights
- **Dual-Write**: Non-blocking async sync to both PostgreSQL and Neo4j
- **Relationship Intelligence**: Cross-brand patterns, color pairings, similarity matching
- **Developer Lock-In**: Client integrations into design systems, marketing automation, dashboards

---

**Version**: 2.4
**Last Updated**: December 8, 2024
**Major Changes**: 
- **Brand Graph as Operating System** (THE MOAT) - Structured brand data exposed via API creates developer lock-in
- **New Schema Fields**: IdentityCore (archetype, voice vectors), ContextualRule (channel-specific), AssetGraph (asset inventory)
- **Enhanced API**: `GET /v1/brands/{id}/graph` returns complete Brand Graph for client integrations
- Neo4j graph intelligence (relationship queries, brand similarity, color pairings)
- Multi-turn tweaks, user-controlled workflow

For more details, see:
- **BRAND-GRAPH-API.md** - Brand Graph API documentation and lock-in strategy
- **MOAT.md** - Competitive moat strategy and differentiation
- README.md - Setup and deployment
- API documentation at `/v1/docs` endpoint
