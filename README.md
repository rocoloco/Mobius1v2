# Mobius Phase 2 - Enterprise Brand Governance Platform

Mobius is an AI-powered brand governance platform that automatically generates, audits, and corrects brand-compliant assets. The only platform with a closed-loop auto-correction system that ensures brand compliance without human intervention.

## Features

- **Multi-Brand Management**: Manage multiple client brands in one dashboard
- **PDF Ingestion**: Automatically extract brand guidelines from PDFs
- **Detailed Compliance Scoring**: Get category-level compliance breakdowns
- **Reusable Templates**: Save successful configurations for quick reuse
- **Async Job Management**: Background processing with webhook notifications
- **Learning System**: Learn from feedback with privacy-first architecture
- **Enterprise-Ready**: Modular architecture, comprehensive testing, API versioning

## Quick Start

### Prerequisites

- Python 3.11+
- Modal account (https://modal.com)
- Supabase account (https://supabase.com)
- Google Gemini API key (https://ai.google.dev)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mobius
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Deployment

#### Quick Deployment

1. **Set up Modal**:
```bash
python scripts/setup_modal.py
modal token new  # If not already authenticated
```

2. **Set up Supabase** (use pooler URL for production):
```bash
bash scripts/setup_supabase.sh
# Ensure you use the pooler URL (port 6543) in production:
# postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

3. **Configure Secrets**:
```bash
modal secret create mobius-secrets \
  GEMINI_API_KEY=your_gemini_api_key \
  SUPABASE_URL=your_supabase_pooler_url \
  SUPABASE_KEY=your_supabase_key
```

4. **Deploy**:
```bash
python scripts/deploy.py
# Or manually: modal deploy src/mobius/api/app_consolidated.py
```

5. **Verify Deployment**:
```bash
# Check health endpoint
curl https://your-app.modal.run/v1/health

# View logs
modal app logs mobius-v2
```

#### Critical Configuration Notes

- **Always use Supabase pooler URL (port 6543)** for production to avoid connection exhaustion
- **Gemini API key** is required for both generation and auditing - get from [Google AI Studio](https://ai.google.dev)
- **Async mode** should be enabled in dashboard for better user experience
- **Neo4j sync** uses `await` pattern to prevent routing errors

## Development

### Running Tests

```bash
# Run all tests
pytest -v

# Run specific test suite
pytest tests/unit/ -v
pytest tests/property/ -v
pytest tests/integration/ -v

# Run with coverage
pytest --cov=src/mobius --cov-report=html
```

### Project Structure

```
src/mobius/
├── api/          # API endpoints and routing
├── graphs/       # LangGraph workflows
├── models/       # Data models and state definitions
├── nodes/        # Workflow nodes
├── storage/      # Database and file storage
└── tools/        # External service integrations
```

## Documentation

- [Deployment Guide](docs/DEPLOYMENT-GUIDE.md) - Complete deployment instructions
- [Deployment Checklist](docs/DEPLOYMENT-CHECKLIST.md) - Step-by-step checklist
- [Phase 2 Verification](docs/PHASE-2-VERIFICATION.md) - Feature verification

## API Documentation

After deployment, access API docs at:
```
https://your-app.modal.run/v1/docs
```

### Key Endpoints

- `POST /v1/brands/ingest` - Upload brand guidelines PDF
- `GET /v1/brands` - List all brands
- `POST /v1/generate` - Generate brand-compliant asset
- `GET /v1/jobs/{job_id}` - Get job status
- `POST /v1/templates` - Save template
- `POST /v1/assets/{asset_id}/feedback` - Submit feedback
- `GET /v1/health` - Health check

## Architecture

Mobius uses a modular, serverless architecture:

- **Runtime**: Modal (serverless Python)
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage (CDN)
- **Orchestration**: LangGraph (state machines)
- **Image Generation**: Google Gemini 3 Pro Image Preview (native multimodal)
- **Visual Audit**: Google Gemini 3 Pro Preview (advanced reasoning)

## Testing

Mobius has comprehensive test coverage:

- **Unit Tests**: Test individual components
- **Property-Based Tests**: Test universal properties with Hypothesis
- **Integration Tests**: Test end-to-end workflows

Current coverage: >80%

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests: `pytest -v`
4. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [Your Repo]
- Documentation: [Your Docs]
- Email: [Your Email]

## Mobius Phase 2 - Enterprise Brand Governance Platform

A modular, enterprise-ready platform for AI-powered brand compliance with automated correction workflows.

## Overview

Mobius Phase 2 transforms the MVP into an enterprise platform with:
- **Brand Guidelines Ingestion**: AI-powered PDF parsing to extract structured brand rules
- **Detailed Compliance Scoring**: Category-level breakdowns with specific violation reporting
- **Multi-Brand Management**: Agency-scale portfolio management for 10-50+ brands
- **Reusable Templates**: Save and reuse successful generation configurations
- **Enhanced Async Jobs**: Webhook notifications with retry logic and job status tracking
- **Learning Foundation**: Feedback collection infrastructure for future ML training

## Project Structure

```
mobius/
├── pyproject.toml              # PEP 621 project configuration
├── .env.example                # Environment variables template
├── README.md                   # This file
├── src/
│   └── mobius/
│       ├── config.py           # Centralized configuration
│       ├── constants.py        # Application constants
│       ├── models/             # Data models and state definitions
│       │   ├── state.py        # LangGraph state TypedDicts
│       │   ├── brand.py        # Brand entity models
│       │   ├── compliance.py   # Compliance scoring models
│       │   ├── asset.py        # Asset entity models
│       │   ├── template.py     # Template entity models
│       │   └── job.py          # Job state models
│       ├── api/                # HTTP API endpoints
│       │   ├── utils.py        # Request ID and helpers
│       │   ├── errors.py       # Error handling utilities
│       │   ├── schemas.py      # Pydantic request/response schemas
│       │   └── dependencies.py # Auth dependencies (mock for Phase 2)
│       └── storage/            # Persistence layer
│           └── database.py     # Supabase client with pooling
└── tests/
    ├── conftest.py             # Pytest fixtures
    ├── unit/                   # Unit tests
    │   ├── test_config.py
    │   ├── test_utils.py
    │   └── test_errors.py
    └── property/               # Property-based tests
        └── test_request_id.py
```

## Setup

### Prerequisites

- Python 3.11+
- Supabase account with PostgreSQL database
- API keys for Fal.ai and Google Gemini

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mobius
```

2. Install dependencies:
```bash
pip install -e .
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

5. Edit `.env` with your credentials:
```env
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
```

**IMPORTANT**: For production deployments, use the Supabase pooler URL (port 6543):
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

## Running Tests

The test suite uses Hypothesis for property-based testing with environment-based configuration:
- **Quick mode** (CI/QUICK_TESTS): 10 examples per property test (~2 minutes total)
- **Full mode** (default): 100 examples per property test (~5 minutes total)

### Quick Test (< 5 seconds)
```bash
# Run only unit tests
pytest tests/unit/ -v
```

### Standard Test (< 30 seconds)
```bash
# Run unit and integration tests
pytest tests/unit/ tests/integration/ -v
```

### Quick Full Suite (< 2 minutes) - Recommended for CI/CD
```bash
# Run all tests with reduced property test examples (10 per test)
QUICK_TESTS=1 pytest -v
```

### Full Test Suite (< 5 minutes)
```bash
# Run all tests including property-based tests (100 examples each)
pytest -v
```

### Property Tests Only
```bash
# Quick mode (10 examples per test)
QUICK_TESTS=1 pytest tests/property/ -v

# Full mode (100 examples per test)
pytest tests/property/ -v
```

### Parallel Execution (Recommended)
```bash
# Install pytest-xdist first: pip install pytest-xdist
pytest -n auto -v  # Uses all CPU cores

# With quick mode for even faster execution
QUICK_TESTS=1 pytest -n auto -v
```

### CI/CD Configuration

For continuous integration pipelines, use the `QUICK_TESTS` environment variable:

```yaml
# GitHub Actions example
- name: Run tests
  run: QUICK_TESTS=1 pytest -v --tb=short
  env:
    QUICK_TESTS: 1
```

```yaml
# GitLab CI example
test:
  script:
    - QUICK_TESTS=1 pytest -v --tb=short
  variables:
    QUICK_TESTS: "1"
```

**Note**: Property-based tests run 100 random examples per test by default, which provides thorough coverage but takes time. The `QUICK_TESTS=1` environment variable reduces this to 10 examples per test for faster feedback during development and CI/CD.

See `docs/testing-notes.md` for detailed testing strategies and performance optimization.

## Configuration

### Environment Variables

All configuration is managed through environment variables or `.env` file:

- `GEMINI_API_KEY`: Google Gemini API key for image generation and auditing (REQUIRED)
- `SUPABASE_URL`: Supabase project URL (use pooler URL for production)
- `SUPABASE_KEY`: Supabase anonymous key
- `MAX_GENERATION_ATTEMPTS`: Maximum generation attempts (default: 3)
- `COMPLIANCE_THRESHOLD`: Compliance threshold for approval (default: 0.80)
- `TEMPLATE_THRESHOLD`: Minimum score to save as template (default: 0.95)
- `JOB_EXPIRY_HOURS`: Job expiration time (default: 24)
- `WEBHOOK_RETRY_MAX`: Maximum webhook retry attempts (default: 5)

### Connection Pooling

**CRITICAL**: Always use Supabase connection pooler for serverless deployments.

The system validates your Supabase URL and warns if you're not using the pooler. Direct connections (port 5432) will exhaust connection limits under load in Modal's serverless environment.

## Architecture

### Technology Stack

- **Language**: Python 3.11+ with type hints and async/await
- **Infrastructure**: Modal (serverless Python runtime)
- **Orchestration**: LangGraph (state machine workflows)
- **API Framework**: Pydantic v2 for validation
- **Database**: Supabase PostgreSQL
- **File Storage**: Supabase Storage with CDN
- **Image Generation**: Google Gemini 3 Pro Image Preview (native multimodal)
- **Visual AI**: Google Gemini 3 Pro Preview (advanced reasoning)
- **PDF Processing**: PyMuPDF (fitz) + pdfplumber
- **Testing**: pytest with Hypothesis for property-based tests
- **Logging**: structlog for structured JSON logging

### Key Features

#### Request ID Tracing
Every API request gets a unique request ID for distributed tracing:
```python
from mobius.api.utils import generate_request_id, set_request_id

request_id = generate_request_id()  # "req_abc123456789"
set_request_id(request_id)
```

#### Structured Error Handling
All errors follow a consistent format:
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

#### Configuration Validation
Settings are validated at startup with helpful warnings:
```python
from mobius.config import settings

# Warns if not using pooler URL
settings.supabase_url  # Validated with field_validator
```

## Development

### Code Style

The project uses:
- Black for code formatting (line length: 100)
- Ruff for linting
- Type hints throughout
- Pydantic v2 for data validation

Format code:
```bash
black src/ tests/
```

Lint code:
```bash
ruff check src/ tests/
```

### Testing Strategy

The project uses a dual testing approach:

1. **Unit Tests**: Test specific scenarios and edge cases
   - Configuration validation
   - Request ID generation
   - Error response formatting

2. **Property-Based Tests**: Verify universal properties using Hypothesis
   - Request ID uniqueness across 100+ iterations
   - Concurrent generation without collisions

### Adding New Features

1. Define data models in `src/mobius/models/`
2. Add API schemas in `src/mobius/api/schemas.py`
3. Implement storage layer in `src/mobius/storage/`
4. Write tests in `tests/unit/` and `tests/property/`
5. Update this README

## API Endpoints

All endpoints are prefixed with `/v1/` for versioning.

### Brand Management

#### POST /v1/brands/ingest
Upload and ingest brand guidelines PDF.

**Request:**
```bash
curl -X POST https://your-modal-app.modal.run/v1/brands/ingest \
  -F "organization_id=org-123" \
  -F "brand_name=Acme Corp" \
  -F "file=@brand-guidelines.pdf"
```

**Response:**
```json
{
  "brand_id": "brand-abc123",
  "status": "validation_passed",
  "pdf_url": "https://cdn.supabase.co/...",
  "needs_review": [],
  "request_id": "req_xyz789"
}
```

#### GET /v1/brands
List all brands for an organization.

**Request:**
```bash
curl "https://your-modal-app.modal.run/v1/brands?organization_id=org-123&search=acme&limit=10"
```

**Response:**
```json
{
  "brands": [
    {
      "brand_id": "brand-abc123",
      "name": "Acme Corp",
      "logo_thumbnail_url": "https://...",
      "asset_count": 42,
      "avg_compliance_score": 87.5,
      "last_activity": "2025-12-05T10:30:00Z"
    }
  ],
  "total": 1,
  "request_id": "req_xyz789"
}
```

#### GET /v1/brands/{brand_id}
Get detailed brand information.

**Request:**
```bash
curl "https://your-modal-app.modal.run/v1/brands/brand-abc123"
```

**Response:**
```json
{
  "brand_id": "brand-abc123",
  "organization_id": "org-123",
  "name": "Acme Corp",
  "guidelines": {
    "colors": {
      "primary": ["#FF5733", "#C70039"],
      "secondary": ["#900C3F", "#581845"]
    },
    "typography": {
      "font_families": ["Helvetica", "Arial"],
      "sizes": {"h1": "32px", "body": "16px"}
    }
  },
  "pdf_url": "https://...",
  "logo_thumbnail_url": "https://...",
  "needs_review": [],
  "learning_active": true,
  "feedback_count": 75,
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-12-05T10:30:00Z",
  "request_id": "req_xyz789"
}
```

#### PATCH /v1/brands/{brand_id}
Update brand metadata.

**Request:**
```bash
curl -X PATCH "https://your-modal-app.modal.run/v1/brands/brand-abc123" \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Corporation"}'
```

#### DELETE /v1/brands/{brand_id}
Soft delete a brand (retains data for audit).

**Request:**
```bash
curl -X DELETE "https://your-modal-app.modal.run/v1/brands/brand-abc123"
```

### Asset Generation

#### POST /v1/generate
Generate brand-compliant asset with optional template support.

**Request (Basic):**
```bash
curl -X POST "https://your-modal-app.modal.run/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": "brand-abc123",
    "prompt": "Create a social media post for our summer sale",
    "async_mode": true,
    "webhook_url": "https://your-app.com/webhooks/mobius"
  }'
```

**Request (With Template):**
```bash
curl -X POST "https://your-modal-app.modal.run/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": "brand-abc123",
    "prompt": "Summer sale announcement",
    "template_id": "template-xyz789",
    "idempotency_key": "unique-key-123"
  }'
```

**Response:**
```json
{
  "job_id": "job-def456",
  "status": "pending",
  "message": "Generation job created successfully",
  "request_id": "req_xyz789"
}
```

### Job Management

#### GET /v1/jobs/{job_id}
Get job status and results.

**Request:**
```bash
curl "https://your-modal-app.modal.run/v1/jobs/job-def456"
```

**Response:**
```json
{
  "job_id": "job-def456",
  "status": "completed",
  "progress": 100.0,
  "current_image_url": "https://cdn.supabase.co/...",
  "compliance_score": 92.5,
  "error": null,
  "created_at": "2025-12-05T10:00:00Z",
  "updated_at": "2025-12-05T10:05:00Z",
  "request_id": "req_xyz789"
}
```

#### POST /v1/jobs/{job_id}/cancel
Cancel a running job.

**Request:**
```bash
curl -X POST "https://your-modal-app.modal.run/v1/jobs/job-def456/cancel"
```

### Template Management

#### POST /v1/templates
Save an asset as a reusable template (requires 95%+ compliance score).

**Request:**
```bash
curl -X POST "https://your-modal-app.modal.run/v1/templates" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": "asset-ghi789",
    "template_name": "Summer Sale Template",
    "description": "High-performing template for seasonal promotions"
  }'
```

**Response:**
```json
{
  "template_id": "template-xyz789",
  "brand_id": "brand-abc123",
  "name": "Summer Sale Template",
  "description": "High-performing template for seasonal promotions",
  "generation_params": {"prompt": "...", "style": "..."},
  "thumbnail_url": "https://...",
  "created_at": "2025-12-05T10:00:00Z",
  "request_id": "req_xyz789"
}
```

#### GET /v1/templates
List all templates for a brand.

**Request:**
```bash
curl "https://your-modal-app.modal.run/v1/templates?brand_id=brand-abc123&limit=10"
```

#### GET /v1/templates/{template_id}
Get detailed template information.

**Request:**
```bash
curl "https://your-modal-app.modal.run/v1/templates/template-xyz789"
```

#### DELETE /v1/templates/{template_id}
Delete a template.

**Request:**
```bash
curl -X DELETE "https://your-modal-app.modal.run/v1/templates/template-xyz789"
```

### Feedback & Learning

#### POST /v1/assets/{asset_id}/feedback
Submit feedback for an asset.

**Request:**
```bash
curl -X POST "https://your-modal-app.modal.run/v1/assets/asset-ghi789/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "reason": "Perfect brand alignment"
  }'
```

**Response:**
```json
{
  "feedback_id": "feedback-jkl012",
  "brand_id": "brand-abc123",
  "total_feedback_count": 51,
  "learning_active": true,
  "request_id": "req_xyz789"
}
```

#### GET /v1/brands/{brand_id}/feedback
Get feedback statistics for a brand.

**Request:**
```bash
curl "https://your-modal-app.modal.run/v1/brands/brand-abc123/feedback"
```

**Response:**
```json
{
  "brand_id": "brand-abc123",
  "total_feedback": 51,
  "approvals": 42,
  "rejections": 9,
  "learning_active": true,
  "request_id": "req_xyz789"
}
```

### Learning Management

#### POST /v1/brands/{brand_id}/learning/settings
Update learning privacy settings.

**Request:**
```bash
curl -X POST "https://your-modal-app.modal.run/v1/brands/brand-abc123/learning/settings" \
  -H "Content-Type: application/json" \
  -d '{
    "privacy_tier": "PRIVATE",
    "data_retention_days": 365
  }'
```

#### GET /v1/brands/{brand_id}/learning/dashboard
Get learning transparency dashboard.

**Request:**
```bash
curl "https://your-modal-app.modal.run/v1/brands/brand-abc123/learning/dashboard"
```

**Response:**
```json
{
  "brand_id": "brand-abc123",
  "privacy_tier": "PRIVATE",
  "patterns_learned": [
    {
      "type": "color_preference",
      "description": "Pattern based on 25 samples",
      "confidence": 0.87
    }
  ],
  "data_sources": "Your brand only",
  "impact_metrics": {
    "patterns_extracted": 5,
    "total_samples": 125,
    "average_confidence": 0.82
  },
  "last_updated": "2025-12-05T10:00:00Z",
  "request_id": "req_xyz789"
}
```

#### POST /v1/brands/{brand_id}/learning/export
Export all learning data (GDPR Article 20 compliance).

**Request:**
```bash
curl -X POST "https://your-modal-app.modal.run/v1/brands/brand-abc123/learning/export"
```

#### DELETE /v1/brands/{brand_id}/learning/data
Delete all learning data (GDPR Article 17 compliance).

**Request:**
```bash
curl -X DELETE "https://your-modal-app.modal.run/v1/brands/brand-abc123/learning/data"
```

### System Endpoints

#### GET /v1/health
Health check for all system components.

**Request:**
```bash
curl "https://your-modal-app.modal.run/v1/health"
```

**Response:**
```json
{
  "status": "healthy",
  "database": "healthy",
  "storage": "healthy",
  "api": "healthy",
  "timestamp": "2025-12-05T10:00:00Z",
  "request_id": "req_xyz789"
}
```

#### GET /v1/docs
Get OpenAPI specification.

**Request:**
```bash
curl "https://your-modal-app.modal.run/v1/docs"
```

## Deployment

### Prerequisites

- Modal account ([sign up](https://modal.com))
- Modal CLI installed: `pip install modal`
- Modal authentication: `modal token new`

### Deploy to Modal

1. Create a deployment script:

```bash
python scripts/deploy.py
```

2. Or deploy manually:

```bash
modal deploy src/mobius/api/app.py
```

3. View deployment logs:

```bash
modal app logs mobius-v2
```

4. Get endpoint URLs:

```bash
modal app list
```

### Environment Variables

Configure secrets in Modal dashboard or via CLI:

```bash
modal secret create mobius-secrets \
  GEMINI_API_KEY=your_gemini_api_key \
  SUPABASE_URL=your_supabase_pooler_url \
  SUPABASE_KEY=your_supabase_key
```

**IMPORTANT**: The `GEMINI_API_KEY` is required for both image generation and compliance auditing. Get your API key from [Google AI Studio](https://ai.google.dev).

### Database Migrations

Run migrations before first deployment:

```bash
# Apply all migrations
supabase db push

# Or manually apply migration files
psql $DATABASE_URL < supabase/migrations/001_initial_schema.sql
psql $DATABASE_URL < supabase/migrations/002_add_templates.sql
psql $DATABASE_URL < supabase/migrations/003_add_feedback.sql
psql $DATABASE_URL < supabase/migrations/004_learning_privacy.sql
psql $DATABASE_URL < supabase/migrations/004_storage_buckets.sql
```

### Monitoring

- View logs: `modal app logs mobius-v2`
- Check health: `curl https://your-app.modal.run/v1/health`
- Monitor jobs: Query `jobs` table in Supabase

## Current Status

✅ **Phase 2 Complete**: Enterprise features and refactoring
- ✅ Project structure with modular architecture
- ✅ Brand guidelines ingestion with PDF parsing
- ✅ Detailed compliance scoring with category breakdowns
- ✅ Multi-brand management for agencies
- ✅ Reusable templates with 95% threshold
- ✅ Enhanced async jobs with webhooks and idempotency
- ✅ Feedback collection and learning foundation
- ✅ Privacy-first learning system with GDPR compliance
- ✅ Comprehensive test suite (100+ tests)
- ✅ API documentation with OpenAPI spec

### Success Metrics

- ✅ No files exceed 300 lines
- ✅ 3+ brands can be managed
- ✅ Compliance scores visible with category breakdowns
- ✅ PDF ingestion extracts structured brand data
- ✅ Async jobs with webhook notifications
- ✅ Test coverage >80%
- ✅ Complete API documentation

## Troubleshooting

### Connection Pool Exhaustion

**Problem:** "Too many connections" errors in logs

**Solution:** Ensure you're using the Supabase pooler URL (port 6543):
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

### Dashboard Connection Issues

**Problem:** `ERR_CONNECTION_CLOSED` errors during asset generation

**Solution:**
1. Enable "Async Mode" toggle in dashboard
2. Ensure backend is deployed with async mode implementation
3. Dashboard should poll `/v1/jobs/{job_id}` every 3 seconds
4. Check that generation endpoint returns immediately with `status="processing"`

### Workflow Routing Issues

**Problem:** Assets scoring 80-95% are auto-approved instead of requiring review

**Solution:**
1. Verify Gemini audit prompt uses ≥95% threshold for auto-approval
2. Check workflow routing: 95%+ → completed, 70-95% → needs_review, <70% → failed
3. Review audit logs for `approved=true/false` decisions

### Neo4j Graph Sync Failures

**Problem:** "Unable to retrieve routing information" errors

**Solution:**
1. Use `await` instead of `asyncio.create_task()` for graph sync operations
2. Ensure graph sync completes before request context cleanup
3. Check Neo4j connection health in logs
4. Verify Neo4j credentials and network connectivity

### Visual Scan Integration Issues

**Problem:** Website scan extracts data but brand ingestion ignores it

**Solution:**
1. Verify `visual_scan_data` parameter is included in ingestion request
2. Check that visual scan includes `identity_core` with archetype and voice vectors
3. Ensure ingestion handler merges visual scan data with PDF parsing results
4. Review logs for `visual_scan_data_received` events

### Gemini API Rate Limits

**Problem:** Generation fails with "Rate limit exceeded" or 429 errors

**Solution:**
1. System automatically retries with exponential backoff (built-in)
2. Check your API quota in [Google AI Studio](https://ai.google.dev)
3. Upgrade to higher tier if needed for production workloads
4. Monitor rate limit errors in logs (includes model name for debugging)
5. Consider implementing request queuing for high-volume scenarios

**Rate Limit Details:**
- Free tier: 15 requests per minute (RPM)
- Paid tier: 1000+ RPM (varies by plan)
- Error includes `retry-after` header for backoff timing

### Gemini API Authentication Errors

**Problem:** 401 Unauthorized or "Invalid API key" errors

**Solution:**
1. Verify `GEMINI_API_KEY` is set correctly in Modal secrets
2. Ensure API key is from [Google AI Studio](https://ai.google.dev), not Google Cloud Console
3. Check API key hasn't expired or been revoked
4. Confirm API key has Gemini API access enabled
5. Test API key with a simple curl request:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
```

### Multi-Turn Conversation Issues

**Problem:** Tweaks regenerate from scratch instead of refining existing images

**Solution:**
1. Verify `session_id` is preserved across tweak requests
2. Check that `previous_image_bytes` are passed to Gemini for context
3. Ensure `attempt_count > 1` triggers `continue_conversation=True`
4. Review logs for multi-turn conversation events

### Audit Timeout Issues

**Problem:** Audits hang indefinitely or timeout after 5 minutes

**Solution:**
1. System uses 2-minute timeout with graceful degradation
2. Check Gemini API status for service issues
3. Review audit prompt complexity - simplify if needed
4. Monitor logs for timeout events and partial scores

### Template Creation Fails

**Problem:** Cannot save asset as template

**Solution:**
1. Verify asset compliance score is ≥95%
2. Check asset exists and is not deleted
3. Ensure brand_id matches asset's brand

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
