# Mobius Phase 2 - Enterprise Brand Governance Platform

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
FAL_KEY=your_fal_api_key
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
```

**IMPORTANT**: For production deployments, use the Supabase pooler URL (port 6543):
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

## Running Tests

Run all tests:
```bash
pytest
```

Run unit tests only:
```bash
pytest tests/unit/
```

Run property-based tests only:
```bash
pytest tests/property/
```

Run with verbose output:
```bash
pytest -v
```

## Configuration

### Environment Variables

All configuration is managed through environment variables or `.env` file:

- `FAL_KEY`: Fal.ai API key for image generation
- `GEMINI_API_KEY`: Google Gemini API key for auditing
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
- **Image Generation**: Fal.ai (Flux.2 Pro) and Ideogram
- **Visual AI**: Google Gemini 1.5 Pro
- **PDF Processing**: pdfplumber
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

## Current Status

✅ **Task 1 Complete**: Project structure and core infrastructure
- Project structure with src/mobius/ organization
- Configuration management with Pydantic Settings
- Data models for all entities (Brand, Asset, Template, Job, Compliance)
- API utilities (request ID, error handling, schemas)
- Database client with connection pooling
- Comprehensive test suite (23 tests passing)

### Next Steps

See `.kiro/specs/mobius-phase-2-refactor/tasks.md` for the complete implementation plan.

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
