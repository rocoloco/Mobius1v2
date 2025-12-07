# Mobius API Documentation

**Version:** 1.0.0  
**Base URL:** `/v1`

Enterprise brand governance platform with AI-powered compliance using Google's Gemini 3 model family.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Error Handling](#error-handling)
5. [Retry Behavior](#retry-behavior)
6. [Endpoints](#endpoints)
7. [Error Codes Reference](#error-codes-reference)
8. [Webhooks](#webhooks)
9. [Examples](#examples)

---

## Architecture Overview

Mobius uses a **dual-model architecture** powered by Google's Gemini 3 family:

### Reasoning Model (gemini-3-pro-preview)
- **Use Cases:** PDF parsing, compliance auditing
- **Strengths:** Advanced reasoning, multimodal vision, complex analysis
- **Context Window:** 2M tokens

### Vision Model (gemini-3-pro-image-preview)
- **Use Cases:** Image generation
- **Strengths:** Native image generation, style consistency
- **Context Window:** 65k tokens

### Compressed Digital Twin

To fit brand guidelines within the Vision Model's 65k token context window, Mobius creates a **Compressed Digital Twin** during ingestion:

- **Semantic color hierarchy** (primary, secondary, accent, neutral, semantic)
- **Font families** (names only, no verbose descriptions)
- **Visual dos and don'ts** (concise rules)
- **Logo requirements** (essential constraints only)
- **Token limit:** <60k tokens

The full Brand Guidelines are preserved for compliance auditing with the Reasoning Model.

---

## Authentication

All API requests require authentication via API key in the `Authorization` header:

```http
Authorization: Bearer YOUR_API_KEY
```

**Error Response (401):**
```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "API key is invalid or expired",
    "request_id": "req_abc123"
  }
}
```

---

## Rate Limiting

API requests are subject to rate limits by endpoint category:

| Category | Limit | Scope |
|----------|-------|-------|
| **Ingestion** | 10 requests/minute | per `organization_id` |
| **Generation** | 30 requests/minute | per `brand_id` |
| **Other Endpoints** | 100 requests/minute | per API key |

### Rate Limit Headers

```http
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1733486400
```

### Rate Limit Exceeded (429)

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please retry after 60 seconds.",
    "details": {
      "retry_after_seconds": 60,
      "limit": "30 requests/minute"
    },
    "request_id": "req_abc123"
  }
}
```

**Response Headers:**
```http
Retry-After: 60
```

**Client Behavior:**
- Wait for `Retry-After` seconds before retrying
- Implement exponential backoff for repeated 429 errors

---

## Error Handling

All errors follow a consistent structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "additional": "context"
    },
    "request_id": "req_abc123"
  }
}
```

### HTTP Status Codes

| Status | Description | Retry? |
|--------|-------------|--------|
| **400** | Bad Request - Invalid input | No |
| **401** | Unauthorized - Invalid API key | No |
| **404** | Not Found - Resource doesn't exist | No |
| **413** | Payload Too Large - File exceeds size limit | No |
| **422** | Unprocessable Entity - Validation error | No |
| **429** | Too Many Requests - Rate limit exceeded | Yes (after delay) |
| **500** | Internal Server Error - Unexpected error | Yes (with backoff) |

---

## Retry Behavior

### Automatic Retries (Server-Side)

Mobius automatically retries transient failures:

| Operation | Max Attempts | Backoff Strategy |
|-----------|--------------|------------------|
| **Image Generation** | 3 | Exponential (1s, 2s, 4s) |
| **Compliance Audit** | 2 | Fixed (2s) |
| **PDF Processing** | 1 | None (large files) |

### Client Retries (Recommended)

For 5xx errors, implement exponential backoff:

```python
import time

def retry_with_backoff(func, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            return func()
        except ServerError as e:
            if attempt == max_attempts - 1:
                raise
            delay = min(2 ** attempt, 60)  # Cap at 60s
            time.sleep(delay)
```

**Do NOT retry:**
- 4xx errors (client errors require fixing the request)
- PDF ingestion failures (investigate before retrying)

---

## Endpoints

### System Endpoints

#### GET /v1/health

Health check for all system components.

**Response (200):**
```json
{
  "status": "healthy",
  "database": "healthy",
  "storage": "healthy",
  "api": "healthy",
  "timestamp": "2025-12-06T10:30:00Z",
  "request_id": "req_health_123"
}
```

#### GET /v1/docs

Get OpenAPI specification.

**Response (200):**
```json
{
  "openapi": "3.0.0",
  "info": { ... },
  "paths": { ... }
}
```

---

### Brand Management

#### POST /v1/brands/ingest

Upload and ingest brand guidelines PDF.

**Processing:**
1. Validates PDF (size, format, header)
2. Extracts guidelines using Reasoning Model
3. Creates Compressed Digital Twin (<60k tokens)
4. Stores both full guidelines and compressed twin

**Request (multipart/form-data):**
```
organization_id: org-123
brand_name: Acme Corp
file: [PDF binary]
```

**Response (200):**
```json
{
  "brand_id": "brand-123",
  "status": "created",
  "pdf_url": "https://cdn.example.com/brands/brand-123/guidelines.pdf",
  "needs_review": [
    "No logo provided - upload logo for best generation results"
  ],
  "request_id": "req_ingest_123"
}
```

**Errors:**
- **400:** Invalid PDF file
- **413:** File too large (>50MB)
- **422:** Duplicate brand name

**Processing Time:**
- Small PDFs (<5MB): 10-30 seconds
- Large PDFs (>20MB): 60-120 seconds

---

#### GET /v1/brands

List all brands for an organization.

**Query Parameters:**
- `organization_id` (required): Organization ID
- `search` (optional): Search term for brand name
- `limit` (optional): Max results (default: 100)

**Response (200):**
```json
{
  "brands": [
    {
      "brand_id": "brand-123",
      "name": "Acme Corp",
      "logo_thumbnail_url": "https://cdn.example.com/logos/brand-123.png",
      "asset_count": 42,
      "avg_compliance_score": 88.5,
      "last_activity": "2025-12-06T10:30:00Z"
    }
  ],
  "total": 1,
  "request_id": "req_list_123"
}
```

---

#### GET /v1/brands/{brand_id}

Get detailed brand information.

**Response (200):**
```json
{
  "brand_id": "brand-123",
  "organization_id": "org-123",
  "name": "Acme Corp",
  "guidelines": {
    "colors": [
      {
        "name": "Primary Blue",
        "hex": "#0057B8",
        "usage": "primary"
      }
    ],
    "typography": [ ... ],
    "logos": [ ... ],
    "voice": { ... },
    "rules": [ ... ]
  },
  "pdf_url": "https://cdn.example.com/brands/brand-123/guidelines.pdf",
  "logo_thumbnail_url": "https://cdn.example.com/logos/brand-123.png",
  "needs_review": [],
  "learning_active": false,
  "feedback_count": 0,
  "created_at": "2025-12-01T10:00:00Z",
  "updated_at": "2025-12-06T10:30:00Z",
  "request_id": "req_get_123"
}
```

**Errors:**
- **404:** Brand not found

---

#### PATCH /v1/brands/{brand_id}

Update brand metadata.

**Request:**
```json
{
  "name": "Acme Corporation",
  "logo_thumbnail_url": "https://cdn.example.com/logos/new-logo.png"
}
```

**Response (200):**
```json
{
  "brand_id": "brand-123",
  "organization_id": "org-123",
  "name": "Acme Corporation",
  ...
}
```

---

#### DELETE /v1/brands/{brand_id}

Soft delete a brand (sets `deleted_at` timestamp).

**Response (200):**
```json
{
  "brand_id": "brand-123",
  "status": "deleted",
  "message": "Brand soft deleted successfully",
  "request_id": "req_delete_123"
}
```

---

### Asset Generation

#### POST /v1/generate

Generate brand-compliant asset using Vision Model.

**Workflow:**
1. Load brand's Compressed Digital Twin
2. Inject compressed guidelines into Vision Model system prompt
3. Generate image with brand constraints
4. Audit compliance using Reasoning Model with full guidelines
5. Retry up to 3 times if compliance score < 80%

**Request:**
```json
{
  "brand_id": "brand-123",
  "prompt": "Create a social media post announcing our new product launch",
  "template_id": "template-456",
  "async_mode": true,
  "webhook_url": "https://your-app.com/webhook",
  "idempotency_key": "client-request-789"
}
```

**Response (200) - Sync:**
```json
{
  "job_id": "job-789",
  "status": "completed",
  "message": "Generation completed successfully",
  "image_url": "https://cdn.example.com/assets/image-123.png",
  "compliance_score": 92.5,
  "request_id": "req_gen_123"
}
```

**Response (200) - Async:**
```json
{
  "job_id": "job-789",
  "status": "pending",
  "message": "Job created successfully. Poll /jobs/{job_id} for status.",
  "request_id": "req_gen_123"
}
```

**Generation Time:**
- Typical: 15-30 seconds
- With retries: 45-90 seconds

**Idempotency:**
- Use `idempotency_key` to prevent duplicate job creation
- If job with same key exists and is not expired, returns existing job
- Keys expire after 24 hours

**Errors:**
- **404:** Brand or template not found
- **422:** Validation error
- **500:** Generation failed after retries

---

### Job Management

#### GET /v1/jobs/{job_id}

Get job status and results.

**Response (200):**
```json
{
  "job_id": "job-789",
  "status": "completed",
  "progress": 100,
  "current_image_url": "https://cdn.example.com/assets/image-123.png",
  "compliance_score": 92.5,
  "error": null,
  "created_at": "2025-12-06T10:00:00Z",
  "updated_at": "2025-12-06T10:00:30Z",
  "request_id": "req_job_123"
}
```

**Job Statuses:**
- `pending`: Job created, waiting to start
- `processing`: Generation in progress
- `completed`: Generation successful
- `failed`: Generation failed after retries
- `cancelled`: Job cancelled by user

**Job Expiration:**
- Jobs expire after 24 hours
- Expired jobs are automatically cleaned up

---

#### POST /v1/jobs/{job_id}/cancel

Cancel a running job.

**Response (200):**
```json
{
  "job_id": "job-789",
  "status": "cancelled",
  "message": "Job cancelled successfully",
  "request_id": "req_cancel_123"
}
```

**Errors:**
- **404:** Job not found
- **422:** Job cannot be cancelled (already completed/failed)

---

### Template Management

#### POST /v1/templates

Save an asset as a reusable template.

**Requirements:**
- Asset must have compliance score >= 95%

**Request:**
```json
{
  "asset_id": "asset-789",
  "template_name": "Social Media Post - Product Launch",
  "description": "High-performing template for product launch announcements"
}
```

**Response (200):**
```json
{
  "template_id": "template-456",
  "brand_id": "brand-123",
  "name": "Social Media Post - Product Launch",
  "description": "High-performing template for product launch announcements",
  "generation_params": { ... },
  "thumbnail_url": "https://cdn.example.com/templates/template-456.png",
  "created_at": "2025-12-06T10:30:00Z",
  "request_id": "req_template_123"
}
```

**Errors:**
- **404:** Asset not found
- **422:** Compliance score too low (<95%)

---

#### GET /v1/templates

List all templates for a brand.

**Query Parameters:**
- `brand_id` (required): Brand ID
- `limit` (optional): Max results (default: 100)

**Response (200):**
```json
{
  "templates": [ ... ],
  "total": 5,
  "request_id": "req_list_templates_123"
}
```

---

#### GET /v1/templates/{template_id}

Get template details.

**Response (200):**
```json
{
  "template_id": "template-456",
  "brand_id": "brand-123",
  "name": "Social Media Post - Product Launch",
  ...
}
```

---

#### DELETE /v1/templates/{template_id}

Delete a template (soft delete).

**Response (200):**
```json
{
  "template_id": "template-456",
  "status": "deleted",
  "message": "Template deleted successfully",
  "request_id": "req_delete_template_123"
}
```

---

### Feedback

#### POST /v1/assets/{asset_id}/feedback

Submit approval or rejection feedback for an asset.

**Request:**
```json
{
  "asset_id": "asset-789",
  "action": "approve",
  "reason": null
}
```

**Response (200):**
```json
{
  "feedback_id": "feedback-123",
  "brand_id": "brand-123",
  "total_feedback_count": 12,
  "learning_active": true,
  "request_id": "req_feedback_123"
}
```

**Learning Activation:**
- Requires 10+ feedback submissions
- Enables privacy-preserving pattern learning
- Improves future generation quality

---

#### GET /v1/brands/{brand_id}/feedback

Get feedback statistics for a brand.

**Response (200):**
```json
{
  "brand_id": "brand-123",
  "total_approvals": 45,
  "total_rejections": 5,
  "learning_active": true,
  "request_id": "req_feedback_stats_123"
}
```

---

## Error Codes Reference

| Code | HTTP Status | Description | Retry? |
|------|-------------|-------------|--------|
| `FILE_TOO_LARGE` | 413 | PDF exceeds 50MB size limit | No - reduce file size |
| `INVALID_FILE_TYPE` | 400 | File is not a PDF | No - upload PDF file |
| `INVALID_PDF` | 400 | File does not have valid PDF header | No - upload valid PDF |
| `DUPLICATE_BRAND` | 422 | Brand name already exists in organization | No - use different name |
| `BRAND_NOT_FOUND` | 404 | Brand does not exist | No - verify brand_id |
| `TEMPLATE_NOT_FOUND` | 404 | Template does not exist | No - verify template_id |
| `ASSET_NOT_FOUND` | 404 | Asset does not exist | No - verify asset_id |
| `JOB_NOT_FOUND` | 404 | Job does not exist or has expired | No - verify job_id |
| `COMPLIANCE_SCORE_TOO_LOW` | 422 | Asset compliance score below 95% threshold | No - improve asset quality |
| `STORAGE_ERROR` | 500 | File storage or database operation failed | Yes - exponential backoff |
| `GENERATION_FAILED` | 500 | Image generation failed after retries | Yes - after delay |
| `AUDIT_FAILED` | 500 | Compliance audit failed | Yes - exponential backoff |
| `RATE_LIMIT_EXCEEDED` | 429 | API rate limit exceeded | Yes - wait for Retry-After |
| `INVALID_API_KEY` | 401 | API key is invalid or expired | No - verify API key |
| `INTERNAL_ERROR` | 500 | Unexpected internal error | Yes - exponential backoff |

---

## Webhooks

For async jobs, provide a `webhook_url` to receive completion notifications.

**Webhook Payload (POST):**
```json
{
  "job_id": "job-789",
  "status": "completed",
  "image_url": "https://cdn.example.com/assets/image-123.png",
  "compliance_score": 92.5,
  "created_at": "2025-12-06T10:00:00Z",
  "completed_at": "2025-12-06T10:00:30Z"
}
```

**Webhook Retry:**
- Up to 3 attempts with exponential backoff
- Requires 2xx response from webhook endpoint

---

## Examples

### Example 1: Ingest Brand Guidelines

```bash
curl -X POST https://api.mobius.example.com/v1/brands/ingest \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "organization_id=org-123" \
  -F "brand_name=Acme Corp" \
  -F "file=@brand-guidelines.pdf"
```

### Example 2: Generate Asset (Sync)

```bash
curl -X POST https://api.mobius.example.com/v1/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": "brand-123",
    "prompt": "Create a social media post announcing our new product launch",
    "async_mode": false
  }'
```

### Example 3: Generate Asset (Async with Webhook)

```bash
curl -X POST https://api.mobius.example.com/v1/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": "brand-123",
    "prompt": "Create a hero banner for homepage",
    "async_mode": true,
    "webhook_url": "https://your-app.com/webhook",
    "idempotency_key": "client-request-789"
  }'
```

### Example 4: Poll Job Status

```bash
curl -X GET https://api.mobius.example.com/v1/jobs/job-789 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Example 5: Save Template

```bash
curl -X POST https://api.mobius.example.com/v1/templates \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": "asset-789",
    "template_name": "Social Media Post - Product Launch",
    "description": "High-performing template for product launch announcements"
  }'
```

---

## Support

- **Documentation:** This guide + README.md + MOBIUS-ARCHITECTURE.md
- **API Docs:** https://api.mobius.example.com/v1/docs
- **Gemini API:** https://ai.google.dev/docs
- **Support:** support@mobius.example.com
