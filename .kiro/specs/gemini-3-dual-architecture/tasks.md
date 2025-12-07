# Implementation Plan: Gemini 3 Dual-Architecture Refactoring

## Overview

This implementation plan breaks down the Gemini 3 dual-architecture refactoring into discrete, manageable tasks. Each task builds incrementally on previous work, with checkpoints to ensure tests pass before proceeding.

---

## Phase 1: Configuration and Model Setup

- [x] 1. Update configuration module with Gemini 3 model constants





  - Add `reasoning_model` and `vision_model` constants to `src/mobius/config.py`
  - Remove `fal_api_key` field from Settings class
  - Add validation for `gemini_api_key` presence
  - Update Settings docstrings to reflect new model architecture
  - _Requirements: 1.1, 1.2, 1.4, 1.5_

- [x] 1.1 Write property test for configuration validation


  - **Property 21: Configuration Validation**
  - **Validates: Requirements 1.4**

- [x] 2. Create CompressedDigitalTwin data model





  - Create new model in `src/mobius/models/brand.py`
  - Implement `estimate_tokens()` method for token counting
  - Implement `validate_size()` method to ensure < 60k tokens
  - Add `compressed_twin` field to Brand model
  - _Requirements: 2.2, 2.3, 2.4_

- [x] 2.1 Write property test for token limit compliance


  - **Property 4: Token Limit Compliance**
  - **Validates: Requirements 2.4**

---

## Phase 2: Gemini Client Refactoring

- [x] 3. Refactor GeminiClient to support dual models





  - Update `__init__` to create both `reasoning_model` and `vision_model` instances
  - Update existing methods to use `reasoning_model` explicitly
  - Add model selection logic based on operation type
  - Update error handling to include model name in logs
  - _Requirements: 1.3, 6.1, 6.2, 6.4, 9.1_

- [x] 3.1 Write property test for dual model initialization



  - **Property 1: Dual Model Initialization**
  - **Validates: Requirements 1.3, 6.1**

- [x] 4. Implement compressed guidelines extraction





  - Add `extract_compressed_guidelines()` method to GeminiClient
  - Create prompt that extracts only essential visual rules
  - Implement token counting and validation
  - Add fallback compression if initial extraction exceeds limit
  - _Requirements: 2.1, 2.2, 2.3, 2.4_



- [x] 4.1 Write property test for reasoning model usage in PDF processing






  - **Property 2: Reasoning Model for PDF Processing**

  - **Validates: Requirements 2.1, 6.2**



- [x] 4.2 Write property test for compressed twin structure





  - **Property 3: Compressed Twin Structure**
  - **Validates: Requirements 2.2, 2.3**

- [x] 5. Implement image generation with Vision Model





  - Add `generate_image()` method to GeminiClient
  - Inject Compressed Digital Twin into system prompt
  - Return image_uri from generation
  - Implement retry logic with exponential backoff (3 attempts)
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 6.3_

- [x] 5.1 Write property test for vision model usage in generation


  - **Property 6: Vision Model for Generation**
  - **Validates: Requirements 3.1, 6.3**

- [x] 5.2 Write property test for compressed twin injection


  - **Property 7: Compressed Twin Injection**
  - **Validates: Requirements 3.2**

- [x] 5.3 Write property test for image URI return format


  - **Property 8: Image URI Return Format**
  - **Validates: Requirements 3.3**

- [x] 5.4 Write property test for generation retry behavior


  - **Property 9: Generation Retry Behavior**
  - **Validates: Requirements 3.4**

- [x] 6. Update audit method to use Reasoning Model explicitly





  - Modify `audit_compliance()` method to accept image_uri
  - Use `reasoning_model` instance explicitly
  - Pass full BrandGuidelines (not compressed twin) as context
  - Ensure multimodal vision input is used
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 6.4_

- [x] 6.1 Write property test for reasoning model usage in auditing



  - **Property 10: Reasoning Model for Auditing**
  - **Validates: Requirements 4.1, 6.4**

- [x] 6.2 Write property test for image URI multimodal input








  - **Property 11: Image URI Multimodal Input**
  - **Validates: Requirements 4.2**

- [x] 6.3 Write property test for full guidelines in audit context













  - **Property 12: Full Guidelines in Audit Context**
  - **Validates: Requirements 4.3**

- [x] 6.4 Write property test for structured compliance output





  - **Property 13: Structured Compliance Output**
  - **Validates: Requirements 4.4**

- [x] 7. Checkpoint - Ensure all tests pass






  - Ensure all tests pass, ask the user if questions arise.

---

## Phase 3: Node Refactoring

- [x] 8. Update Ingestion Node to extract compressed twin





  - Modify `extract_visual_node` to call `extract_compressed_guidelines()`
  - Store both full guidelines and compressed twin
  - Update `structure_node` to persist compressed twin to database
  - _Requirements: 2.1, 2.5_

- [x] 8.1 Write property test for compressed twin persistence



  - **Property 5: Compressed Twin Persistence**
  - **Validates: Requirements 2.5**


- [x] 9. Create new Generation Node







  - Create `src/mobius/nodes/generate.py`
  - Implement `generate_node()` function
  - Load compressed twin from brand storage
  - Call GeminiClient.generate_image() with compressed twin
  - Update JobState with image_uri and attempt count
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 10. Update Audit Node to use image_uri






  - Modify `audit_node()` to accept image_uri from state
  - Remove image download logic (use URI directly)
  - Use Reasoning Model explicitly via GeminiClient
  - Pass full BrandGuidelines for comprehensive auditing
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 11. Update generation workflow to use new nodes





  - Update `src/mobius/graphs/generation.py`
  - Replace Fal.ai generation calls with new generate_node
  - Update workflow edges to pass image_uri between nodes
  - Ensure correction loop still works with new architecture
  - _Requirements: 3.1, 7.2_

- [x] 11.1 Write property test for generation request compatibility


  - **Property 15: Generation Request Compatibility**
  - **Validates: Requirements 7.2**

## Phase 4: Fal.ai Removal

- [x] 13. Remove Fal.ai dependencies from codebase





  - Remove `fal-client` from `pyproject.toml`
  - Remove all `import fal_client` statements
  - Remove Fal.ai model references from code comments
  - Search for "fal" and remove all active code references
  - _Requirements: 5.1, 5.2, 5.3, 5.5_

- [x] 14. Remove Fal.ai references from orchestrator





  - Update `.kiro/specs/mobius-brand-governance/orchestrator.py`
  - Remove fal_client imports and calls
  - Remove FAL_KEY from required secrets
  - Update model routing logic to use Gemini only
  - _Requirements: 5.1, 5.2, 5.3, 5.5_

- [x] 15. Update configuration tests






  - Remove fal_api_key tests from `tests/unit/test_config.py`
  - Add tests for reasoning_model and vision_model constants
  - Update test fixtures to remove Fal.ai mocks
  - _Requirements: 1.1, 1.2, 1.5_

---

## Phase 5: Error Handling and Logging

- [x] 17. Implement comprehensive error handling





  - Add model name to all error logs in GeminiClient
  - Implement rate limit error handling (429 status)
  - Implement auth error handling (401 status)
  - Add timeout retry logic with increased timeouts
  - Implement graceful degradation for audit failures
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 17.1 Write property test for error logging completeness


  - **Property 18: Error Logging Completeness**
  - **Validates: Requirements 9.1**

- [x] 17.2 Write property test for timeout retry behavior


  - **Property 19: Timeout Retry Behavior**
  - **Validates: Requirements 9.4**

- [x] 17.3 Write property test for graceful audit degradation


  - **Property 20: Graceful Audit Degradation**
  - **Validates: Requirements 9.5**



- [x] 18. Add structured logging for all operations



  - Add operation_type field to all logs
  - Add model_name field to all Gemini API logs
  - Add token_count tracking for all API calls
  - Add latency_ms tracking for all operations
  - _Requirements: 9.1_

---

## Phase 6: Backward Compatibility and Testing

- [x] 19. Verify API schema compatibility





  - Compare request/response schemas before and after refactoring
  - Ensure all endpoints maintain identical interfaces
  - Test with existing API client code
  - _Requirements: 7.1_

- [x] 19.1 Write property test for API schema compatibility


  - **Property 14: API Schema Compatibility**
  - **Validates: Requirements 7.1**

- [x] 20. Verify audit response compatibility





  - Ensure ComplianceScore structure matches old format
  - Test category breakdowns and violation details
  - Verify approved flag behavior
  - _Requirements: 7.3_

- [x] 20.1 Write property test for audit response compatibility


  - **Property 16: Audit Response Compatibility**
  - **Validates: Requirements 7.3**

- [x] 21. Verify ingestion response compatibility





  - Ensure Brand entity format matches old structure
  - Test with existing brand storage queries
  - Verify needs_review field behavior
  - _Requirements: 7.4_

- [x] 21.1 Write property test for ingestion response compatibility


  - **Property 17: Ingestion Response Compatibility**
  - **Validates: Requirements 7.4**

- [x] 22. Add database migration for compressed_twin field






  - Create migration to add compressed_twin JSONB column to brands table
  - Ensure migration is non-breaking (nullable field)
  - Test migration rollback
  - _Requirements: 7.5_


## Phase 7: Documentation Updates

- [ ] 24. Update MOBIUS-ARCHITECTURE.md
  - Replace Fal.ai references with Gemini 3 descriptions
  - Update architecture diagrams to show dual-model approach
  - Document Reasoning Model and Vision Model usage
  - Update external services section
  - _Requirements: 8.1, 8.2, 8.5_

- [ ] 25. Update deployment documentation
  - Remove FAL_KEY from required secrets in all docs
  - Emphasize GEMINI_API_KEY requirement
  - Update Modal secret creation commands
  - Add Gemini-specific troubleshooting guidance
  - _Requirements: 8.3, 8.4_

- [ ] 26. Update API documentation
  - Ensure OpenAPI specs reflect current implementation
  - Update example requests and responses
  - Document error codes and retry behavior
  - Add rate limiting guidance
  - _Requirements: 8.4_

---

## Phase 8: Integration Testing and Validation

- [ ] 27. Run end-to-end integration tests
  - Test full ingestion workflow: PDF → Compressed Twin → Database
  - Test full generation workflow: Prompt → Vision Model → Image URI
  - Test full audit workflow: Image URI → Reasoning Model → Compliance Score
  - Test correction loop with new architecture
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 28. Perform load testing
  - Test concurrent ingestion requests
  - Test concurrent generation requests
  - Measure latency percentiles (p50, p95, p99)
  - Verify rate limit handling under load
  - _Requirements: 9.2_

- [ ] 29. Validate cost and performance metrics
  - Compare API costs before and after refactoring
  - Measure token usage per operation type
  - Track error rates by operation
  - Verify compressed twin token counts
  - _Requirements: 2.4_

---

## Summary

This implementation plan refactors the Mobius backend to use Gemini 3's dual-model architecture, replacing Fal.ai with native Google AI capabilities. The plan is organized into 8 phases with 30 tasks, including 20 property-based tests to ensure correctness. Each phase builds incrementally with checkpoints to validate progress.
