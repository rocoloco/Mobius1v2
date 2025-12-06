# Implementation Plan: Mobius Phase 2 - Enterprise Features & Refactoring

This implementation plan follows a 12-week timeline to transform the monolithic Mobius MVP into an enterprise-ready platform with modular architecture and competitive features.

## Week 1-2: Project Structure Refactoring & Foundation

- [x] 1. Set up project structure and core infrastructure





  - Create new project directory with src/mobius/ structure
  - Set up pyproject.toml with PEP 621 configuration
  - Create constants.py with all application constants
  - Create config.py with Pydantic Settings and pooler URL validation
  - Set up .env.example with all required environment variables
  - _Requirements: 1.1, 1.3_

- [x] 1.1 Create data models package


  - Implement state.py with JobState and IngestionState TypedDicts
  - Implement brand.py with Brand, BrandGuidelines, BrandColors models
  - Implement compliance.py with ComplianceScore, CategoryScore, Violation models
  - Implement asset.py with Asset model
  - Implement template.py with Template model
  - Implement job.py with Job model
  - _Requirements: 2.3, 3.2, 5.2_

- [x] 1.2 Create API utilities and error handling


  - Implement api/utils.py with request ID generation and context management
  - Implement api/errors.py with MobiusError, ValidationError, NotFoundError, StorageError
  - Implement api/schemas.py with all Pydantic request/response models including idempotency_key
  - Implement api/dependencies.py with get_current_user() mock dependency (returns user from x-user-id header or test user)
  - Add Depends(get_current_user) to all route handler signatures for Phase 3 auth readiness
  - _Requirements: 9.2, 9.4, 9.5_

- [x] 1.3 Write property test for request ID uniqueness


  - **Property 16 (partial): Request ID uniqueness**
  - **Validates: Requirements 9.5**

- [x] 1.4 Set up database client with connection pooling



  - Implement storage/database.py with get_supabase_client() using pooler URL
  - Add connection pooling validation and warnings
  - Test database connectivity
  - _Requirements: 8.1_

- [x] 1.5 Write unit tests for configuration and utilities


  - Test Settings validation including pooler URL warning
  - Test request ID generation and context management
  - Test error response formatting
  - _Requirements: 1.3, 9.4_

## Week 2: Database Schema & Migrations

- [x] 2. Create database migrations





  - Write supabase/migrations/001_initial_schema.sql with brands, assets, jobs tables
  - Write supabase/migrations/002_add_templates.sql with templates table
  - Write supabase/migrations/003_add_feedback.sql with feedback table and triggers
  - Create Supabase Storage buckets configuration
  - _Requirements: 8.1, 8.6_

- [x] 2.1 Implement storage layer


  - Implement storage/brands.py with BrandStorage CRUD operations
  - Implement storage/assets.py with AssetStorage CRUD operations
  - Implement storage/templates.py with TemplateStorage CRUD operations
  - Implement storage/jobs.py with JobStorage including get_by_idempotency_key()
  - Implement storage/feedback.py with FeedbackStorage operations
  - Implement storage/files.py with FileStorage for Supabase Storage operations
  - _Requirements: 4.1, 4.3, 5.2, 6.4, 7.1, 10.1_

- [x] 2.2 Write property test for brand ID uniqueness


  - **Property 1: Brand ingestion creates valid entity**
  - **Validates: Requirements 2.2, 2.3, 4.1**

- [x] 2.3 Write property test for soft delete preservation


  - **Property 14: Soft delete preserves data**
  - **Validates: Requirements 4.5**

- [x] 2.4 Write unit tests for storage operations


  - Test CRUD operations for all storage classes
  - Test idempotency key lookup
  - Test soft delete behavior
  - _Requirements: 4.1, 4.5, 6.4_

- [x] 2.5 Run database migrations


  - Apply all migrations to development Supabase instance
  - Verify all tables, indexes, and triggers created correctly
  - Create storage buckets with size limits and MIME type restrictions
  - _Requirements: 8.2, 10.5_

## Week 3-4: Compliance Scoring Enhancement

- [x] 3. Implement enhanced audit node with detailed scoring





  - Implement nodes/audit.py with calculate_overall_score() using CATEGORY_WEIGHTS
  - Update audit prompt to request category breakdowns
  - Parse Gemini response into ComplianceScore with categories and violations
  - Recalculate overall score with weighted average
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 3.1 Write property test for compliance score bounds


  - **Property 2: Compliance score is bounded**
  - **Validates: Requirements 3.1**

- [x] 3.2 Write property test for category score aggregation


  - **Property 3: Category scores aggregate correctly**
  - **Validates: Requirements 3.2**

- [x] 3.3 Write property test for low compliance routing


  - **Property 4: Low compliance triggers correction**
  - **Validates: Requirements 3.4**

- [x] 3.4 Write property test for high compliance approval


  - **Property 5: High compliance approves asset**
  - **Validates: Requirements 3.5**

- [x] 3.5 Update generation workflow with enhanced audit


  - Modify graphs/generation.py to use enhanced audit node
  - Update route_after_audit() to check compliance threshold
  - Store compliance_scores in job state
  - _Requirements: 3.4, 3.5_

- [x] 3.6 Write integration test for generation workflow


  - Test complete workflow with compliance scoring
  - Test correction loop triggered by low scores
  - Test approval on high scores
  - _Requirements: 1.4, 3.4, 3.5_

- [x] 3.7 Checkpoint - Ensure all tests pass


  - Ensure all tests pass, ask the user if questions arise.

## Week 5-6: Multi-Brand Management

- [x] 4. Implement brand management API endpoints





  - Implement POST /v1/brands/ingest handler with PDF validation
  - Implement GET /v1/brands handler with organization filtering
  - Implement GET /v1/brands/{brand_id} handler
  - Implement PATCH /v1/brands/{brand_id} handler
  - Implement DELETE /v1/brands/{brand_id} handler with soft delete
  - _Requirements: 4.1, 4.2, 4.3, 4.5_

- [x] 4.1 Add PDF size and type validation

  - Implement early validation in ingest handler (size, MIME type, PDF header)
  - Return ValidationError with appropriate error codes
  - _Requirements: 2.1, 2.5_

- [x] 4.2 Write property test for brand_id requirement


  - **Property 6: Brand ID is required for generation**
  - **Validates: Requirements 4.2**

- [x] 4.3 Write property test for brand list metadata


  - **Property (custom): Brand list contains required fields**
  - **Validates: Requirements 4.3**

- [x] 4.2 Implement brand list with search and filtering

  - Add query parameters for search by name
  - Add filtering by organization_id
  - Calculate asset_count and avg_compliance_score in query
  - _Requirements: 4.3, 4.4_



- [x] 4.4 Write unit tests for brand API endpoints




  - Test PDF validation (size, type, header)
  - Test brand CRUD operations
  - Test search and filtering
  - Test soft delete
  - _Requirements: 2.1, 2.5, 4.1, 4.3, 4.4, 4.5_

## Week 7-8: Brand Guidelines Ingestion

- [x] 5. Implement PDF parsing tools





  - Implement tools/pdf_parser.py with pdfplumber for raw text extraction
  - Update tools/gemini.py to use response_schema targeting the BrandGuidelines Pydantic model
  - Ensure prompt engineering explicitly handles negative_constraint detection
  - _Requirements: 2.2_

- [x] 5.1 Implement ingestion workflow nodes


  - Implement nodes/extract_text.py for PDF text extraction
  - Implement nodes/extract_visual.py for color/logo extraction with Gemini
  - Implement nodes/structure.py to map raw outputs to BrandGuidelines schema
  - Add logic to default usage Enums if unspecified
  - _Requirements: 2.2, 2.3, 2.4_



- [x] 5.2 Create brand ingestion workflow

  - Implement graphs/ingestion.py with extract_text → extract_visual → structure flow
  - Implement validation loop: If BrandGuidelines validation fails, populate needs_review

  - Add error handling for extraction failures
  - _Requirements: 2.2, 2.3, 2.4_

- [x] 5.3 Write property test for brand entity creation

  - **Property 1: Brand ingestion creates valid BrandGuidelines object**


  - **Validates: negative_constraint logic and Enum constraints**
  - **Validates: Requirements 2.2, 2.3**

- [x] 5.4 Implement file storage for PDFs

  - Implement upload_pdf() in storage/files.py
  - Store PDFs in brands bucket with brand_id path
  - Return public CDN URL
  - _Requirements: 2.1, 2.6, 10.1, 10.3_

- [x] 5.5 Write property test for CDN URL format


  - **Property 13: File storage returns CDN URL**
  - **Validates: Requirements 10.3**

- [x] 5.6 Write integration test for ingestion workflow


  - Test complete PDF ingestion workflow
  - Test extraction of colors, fonts, rules into Digital Twin format
  - Test Brand entity creation
  - Test needs_review flagging for ambiguous data
  - _Requirements: 2.2, 2.3, 2.4_

- [x] 5.7 Checkpoint - Ensure all tests pass



  - Ensure all tests pass, ask the user if questions arise.

## Week 9-10: Templates & Enhanced Async Jobs

- [x] 6. Implement template management





  - Implement POST /v1/templates handler with 95% threshold check
  - Implement GET /v1/templates handler filtered by brand_id
  - Implement GET /v1/templates/{template_id} handler
  - Implement DELETE /v1/templates/{template_id} handler
  - _Requirements: 5.1, 5.3, 5.6_

- [x] 6.1 Write property test for template threshold



  - **Property 7: Template threshold enforcement**
  - **Validates: Requirements 5.1**

- [x] 6.2 Write property test for template parameter preservation



  - **Property 8: Template parameters are preserved**
  - **Validates: Requirements 5.4**

- [x] 6.3 Update generation handler to support templates


  - Add template_id parameter to GenerateRequest
  - Load template and pre-fill generation parameters
  - Allow parameter overrides
  - _Requirements: 5.4, 5.5_

- [x] 6.4 Write unit tests for template operations



  - Test template creation with threshold check
  - Test template retrieval by brand
  - Test template application with overrides
  - Test template deletion
  - _Requirements: 5.1, 5.3, 5.4, 5.5, 5.6_

- [x] 7. Enhance async job management







  - Add idempotency_key support to job creation
  - Implement idempotency check in generate_handler
  - Implement GET /v1/jobs/{job_id} status endpoint
  - Implement POST /v1/jobs/{job_id}/cancel endpoint
  - _Requirements: 6.1, 6.4_

- [x] 7.1 Write property test for async job response time



  - **Property 9: Async job returns immediately**
  - **Validates: Requirements 6.1**

- [x] 7.2 Write property test for idempotency




  - **Property 16: Idempotency key prevents duplicates**
  - **Validates: Requirements 6.1 (enhanced)**

- [x] 7.3 Implement webhook delivery with retry logic


  - Implement deliver_webhook() with exponential backoff
  - Track webhook_attempts in jobs table
  - Call webhook on job completion
  - _Requirements: 6.3, 6.5_

- [x] 7.4 Write property test for webhook retry exhaustion



  - **Property 10: Webhook retry exhaustion**
  - **Validates: Requirements 6.5**

- [x] 7.5 Write integration tests for async jobs




  - Test async job creation and background processing
  - Test job status polling
  - Test webhook delivery
  - Test webhook retry logic
  - Test idempotency key behavior
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

## Week 11: Feedback & Learning Foundation

- [x] 8. Implement feedback collection


  - Implement POST /v1/assets/{asset_id}/feedback handler
  - Store feedback events with action (approve/reject) and reason
  - Update brand feedback_count via trigger
  - Return updated feedback statistics
  - _Requirements: 7.1, 7.2, 7.4_

- [x] 8.1 Write property test for feedback count increment


  - **Property 11: Feedback increments count**
  - **Validates: Requirements 7.1, 7.2**

- [x] 8.2 Write property test for learning activation


  - **Property 12: Learning activation threshold**
  - **Validates: Requirements 7.3**

- [x] 8.3 Implement feedback statistics endpoint

  - Implement GET /v1/brands/{brand_id}/feedback handler
  - Return total approvals, rejections, and learning_active status
  - _Requirements: 7.5_

- [x] 8.4 Write unit tests for feedback operations


  - Test feedback storage for approve/reject
  - Test feedback count updates
  - Test learning_active flag at 50 threshold
  - Test feedback statistics retrieval
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 8.5 Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

## Week 12: Meta-Learning with Privacy Controls

- [x] 9. Design learning privacy tiers
  - Create LearningSettings, BrandPattern, IndustryPattern, LearningAuditLog models in models/learning.py
  - Define PrivacyTier enum with OFF, PRIVATE, SHARED values
  - Document privacy tier behaviors and guarantees
  - Create legal review checklist for shared mode
  - Design consent UI flow with clear examples
  - _Requirements: Privacy-first architecture_

- [x] 9.1 Implement database schema for learning
  - Write supabase/migrations/004_learning_privacy.sql
  - Create learning_settings table with privacy_tier and consent tracking
  - Create brand_patterns table for private learning data
  - Create industry_patterns table with k-anonymity constraints
  - Create learning_audit_log table for transparency
  - Add indexes for efficient querying
  - _Requirements: Privacy-first data model_

- [x] 9.2 Implement private learning engine (default mode)
  - Implement learning/private.py with PrivateLearningEngine class
  - Implement extract_patterns() for per-brand pattern extraction
  - Implement optimize_prompt() for brand-specific prompt optimization
  - Implement export_learning_data() endpoint for GDPR compliance
  - Implement delete_learning_data() endpoint for right to deletion
  - Ensure complete data isolation between brands
  - _Requirements: Maximum privacy by default_

- [x] 9.3 Write property test for privacy tier enforcement
  - **Property 17: Privacy tier enforcement**
  - **Validates: Learning privacy controls**

- [x] 9.4 Write property test for data deletion completeness
  - **Property 19: Data deletion completeness**
  - **Validates: Right to deletion**

- [x] 9.5 Implement shared learning engine (opt-in only)
  - Implement learning/shared.py with SharedLearningEngine class
  - Implement aggregate_patterns() with industry cohort aggregation
  - Implement differential privacy noise injection using Laplace mechanism
  - Implement k-anonymity enforcement (minimum 5 brands)
  - Implement pattern contributor anonymization
  - Ensure aggregate-only storage with no individual brand traces
  - _Requirements: Network effects with privacy preservation_

- [x] 9.6 Write property test for k-anonymity enforcement
  - **Property 18: K-anonymity enforcement**
  - **Validates: Shared learning privacy**

- [x] 9.7 Write property test for differential privacy noise
  - **Property 20: Differential privacy noise**
  - **Validates: Differential privacy**

- [x] 9.8 Implement learning management API endpoints
  - Implement POST /v1/brands/{brand_id}/learning/settings for privacy tier updates
  - Implement GET /v1/brands/{brand_id}/learning/settings for current settings
  - Implement GET /v1/brands/{brand_id}/learning/dashboard for transparency
  - Implement GET /v1/brands/{brand_id}/learning/patterns for learned patterns
  - Implement POST /v1/brands/{brand_id}/learning/export for data export
  - Implement DELETE /v1/brands/{brand_id}/learning/data for data deletion
  - Implement GET /v1/brands/{brand_id}/learning/audit for audit log
  - _Requirements: Transparency and control_

- [x] 9.9 Create learning transparency dashboard
  - Implement dashboard showing what patterns were learned
  - Show data sources (if shared mode: "5 fashion brands", if private: "Your brand only")
  - Show impact on compliance scores with before/after metrics
  - Implement learning audit log export functionality
  - Add one-click disable/delete options
  - _Requirements: Radical transparency_

- [x] 9.10 Write unit tests for learning system
  - Test private learning pattern extraction
  - Test shared learning aggregation
  - Test privacy tier switching
  - Test data export functionality
  - Test data deletion functionality
  - Test k-anonymity enforcement
  - Test differential privacy noise application
  - _Requirements: Privacy guarantees_

- [x] 9.11 Create legal & compliance documentation
  - Write data processing addendum template for enterprise customers
  - Create learning modes comparison chart for sales team
  - Write privacy impact assessment document
  - Document right-to-deletion workflow
  - Create consent flow documentation with screenshots
  - _Requirements: Enterprise sales enablement_

- [x] 9.12 Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Week 13: Integration, Testing & Documentation

- [x] 10. Implement background job cleanup





  - Implement cleanup_expired_jobs() scheduled function with Modal Cron
  - Delete expired jobs from database
  - Clean up temporary files for failed jobs
  - Run hourly
  - _Requirements: 6.7_

- [x] 10.1 Write property test for job expiration



  - **Property (custom): Jobs expire after 24 hours**
  - **Validates: Requirements 6.7**

- [x] 10.2 Implement system endpoints


  - Implement GET /v1/health with database, storage, and API checks
  - Implement GET /v1/docs with OpenAPI specification
  - _Requirements: 9.6_

- [x] 10.3 Write unit tests for system endpoints



  - Test health check with all services healthy
  - Test health check with degraded services
  - Test OpenAPI docs generation
  - _Requirements: 9.6_

- [x] 11. Implement Modal app with all endpoints





  - Create api/app.py with Modal app definition
  - Register all v1 endpoints with @app.web_endpoint decorators
  - Add legacy Phase 1 endpoint for backward compatibility
  - Configure Modal image with all dependencies
  - Configure Modal secrets
  - _Requirements: 1.4, 9.1_

- [x] 11.1 Write property test for API versioning



  - **Property 15: API versioning consistency**
  - **Validates: Requirements 9.1**

- [x] 11.2 Implement route handlers


  - Implement all route handlers in api/routes.py
  - Add request ID generation to all handlers
  - Add error handling with structured responses
  - Add logging with structlog
  - _Requirements: 9.2, 9.3, 9.4, 9.5_

- [x] 11.3 Write property test for error responses



  - **Property (custom): Error responses include request_id**
  - **Validates: Requirements 9.4, 9.5**

- [x] 11.4 Write property test for HTTP status codes



  - **Property (custom): Appropriate status codes returned**
  - **Validates: Requirements 9.3**

- [x] 12. End-to-end integration testing






  - Test complete generation workflow with multi-brand
  - Test brand ingestion → generation → feedback loop
  - Test template creation and reuse
  - Test async jobs with webhooks
  - Test backward compatibility with Phase 1
  - _Requirements: 1.4_

- [x] 12.1 Write property tests for file storage



  - **Property (custom): Files stored in correct buckets**
  - **Validates: Requirements 10.1, 10.2**

- [x] 12.2 Write property test for file cleanup



  - **Property (custom): Files removed on deletion**
  - **Validates: Requirements 10.4**

- [x] 13. Documentation and deployment





  - Write README.md with setup instructions
  - Document all API endpoints with examples
  - Create deployment script scripts/deploy.py
  - Test deployment to Modal staging environment
  - Verify all endpoints accessible
  - _Requirements: 1.4_

- [x] 13.1 Final checkpoint - Ensure all tests pass


  - Ensure all tests pass, ask the user if questions arise.



- [x] 13.2 Verify success metrics







 
  - Confirm 3+ brands can be managed
  - Confirm compliance scores visible
  - Confirm PDF ingestion works
  - Confirm async jobs with webhooks work
  - Confirm test coverage >80%
  - Confirm API documentation complete
  - _Requirements: 1.5_

