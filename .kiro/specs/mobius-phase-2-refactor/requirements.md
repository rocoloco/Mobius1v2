# Requirements Document: Mobius Phase 2 - Enterprise Features & Refactoring

## Introduction

Mobius Phase 2 transforms the MVP brand governance engine into an enterprise-ready platform with multi-brand management, automated brand guidelines ingestion, detailed compliance scoring, reusable templates, and learning capabilities. This phase refactors the monolithic architecture into a modular, maintainable codebase while adding competitive features identified through market analysis of Adobe GenStudio, Typeface, Bynder, and Flair.ai.

The core differentiator remains: Mobius is the only platform with a closed-loop auto-correction system that generates, audits, and automatically fixes brand compliance issues without human intervention.

## Glossary

- **Mobius System**: The complete brand governance platform including all Phase 1 and Phase 2 components
- **Brand Entity**: A structured database record containing extracted brand guidelines (colors, fonts, rules, logos)
- **Brand Guidelines PDF**: A document uploaded by users containing visual identity standards
- **PDF Ingestion Workflow**: A LangGraph workflow that extracts structured data from brand PDFs
- **Compliance Score**: A numerical value (0-100%) indicating overall brand adherence
- **Category Score**: Individual compliance metrics for colors, typography, layout, and logo usage
- **Violation**: A specific non-compliance issue with description and severity
- **Brand Manager**: A user role responsible for managing brand guidelines and reviewing assets
- **Agency Account Manager**: A user role managing multiple client brands in one dashboard
- **Template**: A saved generation configuration that can be reused for consistent asset creation
- **Generation Parameters**: The prompt structure, model selection, and style settings for image generation
- **Async Job**: A long-running generation workflow that executes in the background
- **Webhook URL**: An HTTP endpoint that receives POST notifications when async jobs complete
- **Feedback Event**: A user action (approve/reject) on a generated asset with optional reasoning
- **Learning Active Status**: A brand state indicating sufficient feedback data exists for ML training
- **Supabase Storage**: The file storage service for PDFs and generated images with CDN URLs
- **Modal App**: The serverless Python application runtime environment
- **LangGraph Workflow**: A state machine that orchestrates multi-step AI processes
- **Pydantic Model**: A Python data validation class for API request/response schemas
- **API Version Prefix**: The /v1/ URL segment for API versioning and backward compatibility
- **Organization**: A top-level entity representing an agency or company managing multiple brands
- **Job State**: The TypedDict structure containing workflow execution state and history

## Requirements

### Requirement 1: Project Structure Refactoring

**User Story:** As a developer, I want the codebase organized into logical modules, so that I can easily navigate, test, and maintain the system as it grows.

#### Acceptance Criteria

1. THE Mobius System SHALL organize code into the following directory structure: src/mobius/ with subdirectories for models/, nodes/, tools/, graphs/, api/, and storage/
2. WHEN a developer imports a module, THEN the Mobius System SHALL provide clear separation between state definitions (models/), workflow steps (nodes/), external integrations (tools/), orchestration (graphs/), HTTP endpoints (api/), and persistence (storage/)
3. THE Mobius System SHALL use pyproject.toml for project configuration following PEP 621 standards
4. WHEN the project is deployed, THEN the Mobius System SHALL maintain all Phase 1 functionality without regression
5. THE Mobius System SHALL limit individual Python files to a maximum of 300 lines of code

### Requirement 2: Brand Guidelines Ingestion

**User Story:** As a brand manager, I want to upload my brand guidelines PDF so that the system automatically extracts and enforces my brand rules during image generation.

#### Acceptance Criteria

1. WHEN a user uploads a PDF file up to 50MB via the API, THEN the Mobius System SHALL accept the file and store it in Supabase Storage
2. WHEN the PDF Ingestion Workflow executes, THEN the Mobius System SHALL extract primary colors, secondary colors, typography rules, logo usage guidelines, tone of voice descriptors, and visual asset rules
3. WHEN extraction completes successfully, THEN the Mobius System SHALL create a Brand Entity in the database with a unique brand_id and structured JSON fields
4. WHEN extraction encounters ambiguous content, THEN the Mobius System SHALL flag specific items with needs_review status and store partial results
5. IF PDF parsing fails due to file corruption or unsupported format, THEN the Mobius System SHALL return a 400 status code with a descriptive error message
6. WHEN a Brand Entity is created, THEN the Mobius System SHALL return a CDN URL for the stored PDF and the brand_id

### Requirement 3: Detailed Compliance Scoring

**User Story:** As a designer, I want to see a visual compliance score for each generated asset so that I understand exactly what's on-brand and what needs attention.

#### Acceptance Criteria

1. WHEN an asset is generated and audited, THEN the Mobius System SHALL calculate an overall compliance score from 0 to 100 percent
2. WHEN the audit completes, THEN the Mobius System SHALL provide category breakdowns for colors compliance, typography compliance, layout compliance, and logo usage compliance
3. WHEN a category fails compliance, THEN the Mobius System SHALL list specific violations with descriptions and severity levels
4. WHEN the overall compliance score is below 80 percent, THEN the Mobius System SHALL automatically trigger the correction workflow
5. WHEN all category scores are above 90 percent, THEN the Mobius System SHALL mark the asset as approved
6. WHEN audit results are returned, THEN the Mobius System SHALL include pass or fail indicators for each category

### Requirement 4: Multi-Brand Management

**User Story:** As an agency account manager, I want to manage multiple client brands in one dashboard so that my team can quickly switch contexts and generate assets for any client.

#### Acceptance Criteria

1. WHEN a user creates a new brand, THEN the Mobius System SHALL assign a unique brand_id and associate it with an organization_id
2. WHEN a user initiates asset generation, THEN the Mobius System SHALL require a brand_id parameter in the request
3. WHEN a user requests the brand list, THEN the Mobius System SHALL return all brands with brand name, logo thumbnail URL, total asset count, average compliance score, and last activity timestamp
4. IF a user has more than 10 brands, THEN the Mobius System SHALL provide search by name and filtering by organization
5. WHEN a brand is deleted, THEN the Mobius System SHALL soft-delete the record and retain associated assets for audit purposes
6. WHEN brand data is queried, THEN the Mobius System SHALL return results within 500 milliseconds for up to 100 brands

### Requirement 5: Reusable Templates

**User Story:** As a designer, I want to save successful generation configurations as templates so that I can quickly reproduce on-brand assets without re-entering parameters.

#### Acceptance Criteria

1. WHEN an asset achieves a compliance score of 95 percent or higher, THEN the Mobius System SHALL enable the save as template action
2. WHEN a user saves a template, THEN the Mobius System SHALL store the generation parameters, brand association, sample output thumbnail URL, template name, and template description
3. WHEN a user creates a new asset, THEN the Mobius System SHALL return available templates filtered by the selected brand_id
4. WHEN a user selects a template, THEN the Mobius System SHALL pre-fill all generation parameters from the stored template configuration
5. WHEN a template is applied, THEN the Mobius System SHALL allow parameter overrides before generation
6. WHEN a user deletes a template, THEN the Mobius System SHALL remove it from the available templates list without affecting historical assets

### Requirement 6: Enhanced Async Job Management with Webhooks

**User Story:** As a developer integrating Mobius, I want to submit generation jobs asynchronously and receive webhook notifications so that my application can handle long-running jobs gracefully.

#### Acceptance Criteria

1. WHEN a user submits an async job with a webhook_url parameter, THEN the Mobius System SHALL return a job_id within 500 milliseconds
2. WHEN an async job is submitted, THEN the Mobius System SHALL process the generation workflow in the background
3. WHEN an async job completes, THEN the Mobius System SHALL POST to the webhook_url with job status, final state, and result URLs
4. WHEN a user queries job status via GET request to the jobs endpoint, THEN the Mobius System SHALL return the current job state including status, progress, and partial results
5. WHEN webhook delivery fails, THEN the Mobius System SHALL retry with exponential backoff for a maximum of 5 attempts
6. IF no webhook_url is provided, THEN the Mobius System SHALL store results for polling retrieval for 24 hours
7. WHEN a job exceeds 24 hours in age, THEN the Mobius System SHALL mark it as expired and remove detailed results

### Requirement 7: Learning from Feedback Foundation

**User Story:** As a brand manager, I want the system to learn from my approvals and rejections so that future generations are more likely to meet my standards.

#### Acceptance Criteria

1. WHEN a user approves an asset, THEN the Mobius System SHALL store a feedback event with asset_id, brand_id, action as approve, and timestamp
2. WHEN a user rejects an asset with a reason, THEN the Mobius System SHALL store a feedback event with asset_id, brand_id, action as reject, rejection reason, and timestamp
3. WHEN a brand accumulates 50 or more feedback events, THEN the Mobius System SHALL set the learning_active flag to true
4. WHEN feedback is submitted, THEN the Mobius System SHALL return a confirmation with the updated feedback count for that brand
5. WHEN a user views brand details, THEN the Mobius System SHALL display total approvals, total rejections, and learning_active status
6. THE Mobius System SHALL store feedback data in a queryable format for future machine learning integration

### Requirement 8: Database Schema and Migrations

**User Story:** As a system architect, I want database schema changes managed through migrations, so that I can safely evolve the data model across environments.

#### Acceptance Criteria

1. THE Mobius System SHALL define database schemas for brands, assets, templates, jobs, and feedback tables
2. WHEN the system is deployed to a new environment, THEN the Mobius System SHALL apply all pending migrations automatically
3. WHEN a schema change is required, THEN the Mobius System SHALL create a new migration file with up and down operations
4. THE Mobius System SHALL use Supabase migrations for schema version control
5. WHEN a migration fails, THEN the Mobius System SHALL rollback changes and log the error without corrupting data
6. THE Mobius System SHALL maintain referential integrity with foreign key constraints between brands, assets, templates, and feedback

### Requirement 9: API Versioning and Standards

**User Story:** As an API consumer, I want versioned endpoints with consistent patterns, so that I can integrate reliably and handle future changes gracefully.

#### Acceptance Criteria

1. THE Mobius System SHALL prefix all API endpoints with the version segment v1
2. WHEN a client makes a request, THEN the Mobius System SHALL validate input using Pydantic models and return 422 status for validation errors
3. WHEN a request succeeds, THEN the Mobius System SHALL return appropriate HTTP status codes: 200 for success, 201 for resource creation, 202 for accepted async jobs
4. WHEN a request fails, THEN the Mobius System SHALL return structured error responses with error code, message, and request_id
5. THE Mobius System SHALL include a request_id in all responses for distributed tracing
6. WHEN API documentation is generated, THEN the Mobius System SHALL expose OpenAPI specification at the docs endpoint

### Requirement 10: Supabase Storage Integration

**User Story:** As a system operator, I want all files stored in Supabase Storage, so that I can leverage CDN delivery and unified access control.

#### Acceptance Criteria

1. WHEN a user uploads a brand guidelines PDF, THEN the Mobius System SHALL store it in the Supabase Storage brands bucket
2. WHEN an image is generated, THEN the Mobius System SHALL download it from the generation service and upload it to the Supabase Storage assets bucket
3. WHEN a file is stored, THEN the Mobius System SHALL return a public CDN URL for client access
4. WHEN a brand or asset is deleted, THEN the Mobius System SHALL remove associated files from Supabase Storage
5. THE Mobius System SHALL configure storage buckets with appropriate size limits: 50MB for PDFs, 10MB for images
6. WHEN storage operations fail, THEN the Mobius System SHALL log errors and return 500 status with retry guidance

