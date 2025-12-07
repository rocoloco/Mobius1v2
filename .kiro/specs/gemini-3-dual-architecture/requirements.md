# Requirements Document: Gemini 3 Dual-Architecture Refactoring

## Introduction

This specification defines the refactoring of the Mobius backend to use the Gemini 3 model family with a dual-architecture approach. The system will replace the Flux/Ideogram image generation stack with Gemini 3's native image generation capabilities while maintaining separate models for reasoning and vision tasks. This change simplifies the architecture, reduces external dependencies, and leverages Google's latest multimodal AI capabilities.

## Glossary

- **Mobius System**: The complete brand governance platform including ingestion, generation, and audit components
- **Reasoning Model**: The Gemini 3 Pro Preview model optimized for complex reasoning tasks including PDF parsing and compliance auditing
- **Vision Model**: The Gemini 3 Pro Image Preview model optimized for image generation tasks
- **Compressed Digital Twin**: A JSON structure containing essential visual brand rules optimized to fit within the Vision Model's 65k context window
- **Ingestion Node**: The workflow component that parses uploaded PDFs and extracts brand guidelines
- **Generation Node**: The workflow component that creates images using the Vision Model
- **Audit Node**: The workflow component that evaluates image compliance using the Reasoning Model
- **Gemini Client**: The Python client wrapper for Google Generative AI API
- **Brand Guidelines**: Structured data extracted from PDFs including colors, typography, logos, and governance rules
- **Image URI**: A reference to a generated image that can be passed between workflow nodes
- **Context Window**: The maximum token limit for model input (65k tokens for Vision Model)
- **Fal.ai Service**: The legacy external image generation service to be removed
- **Model Configuration**: The settings defining which Gemini model variant to use for each task

## Requirements

### Requirement 1: Model Configuration

**User Story:** As a system architect, I want distinct model configurations for reasoning and vision tasks, so that I can optimize performance and cost for each use case.

#### Acceptance Criteria

1. THE Mobius System SHALL define a REASONING_MODEL constant with value "gemini-3-pro-preview" in the configuration module
2. THE Mobius System SHALL define a VISION_MODEL constant with value "gemini-3-pro-image-preview" in the configuration module
3. WHEN the Gemini Client initializes, THEN the Mobius System SHALL create separate client instances for the Reasoning Model and the Vision Model
4. WHEN configuration is loaded, THEN the Mobius System SHALL validate that the gemini_api_key is present and non-empty
5. THE Mobius System SHALL remove all references to fal_api_key from the configuration module

### Requirement 2: Compressed Digital Twin Extraction

**User Story:** As a system operator, I want PDF parsing to extract only essential visual rules, so that the brand guidelines fit within the Vision Model's context window during generation.

#### Acceptance Criteria

1. WHEN the Ingestion Node processes a PDF, THEN the Mobius System SHALL use the Reasoning Model to extract brand guidelines
2. WHEN brand guidelines are extracted, THEN the Mobius System SHALL create a Compressed Digital Twin containing only hex color codes, font family names, logo usage rules, and critical visual constraints
3. WHEN the Compressed Digital Twin is created, THEN the Mobius System SHALL exclude verbose descriptions, historical context, and non-visual content
4. WHEN the Compressed Digital Twin is serialized, THEN the Mobius System SHALL ensure the JSON representation is under 60,000 tokens
5. WHEN extraction completes, THEN the Mobius System SHALL store the Compressed Digital Twin in the Brand Entity database record

### Requirement 3: Image Generation with Vision Model

**User Story:** As a designer, I want images generated using Gemini's native capabilities, so that I can leverage the latest multimodal AI without external service dependencies.

#### Acceptance Criteria

1. WHEN the Generation Node executes, THEN the Mobius System SHALL use the Vision Model to generate images
2. WHEN generating an image, THEN the Mobius System SHALL inject the Compressed Digital Twin into the system prompt
3. WHEN the Vision Model completes generation, THEN the Mobius System SHALL return an image_uri that references the generated image
4. WHEN generation fails, THEN the Mobius System SHALL retry up to 3 times with exponential backoff
5. THE Mobius System SHALL remove all calls to the Fal.ai Service from the Generation Node

### Requirement 4: Compliance Auditing with Reasoning Model

**User Story:** As a brand manager, I want compliance auditing to use advanced reasoning capabilities, so that I receive accurate and detailed feedback on brand violations.

#### Acceptance Criteria

1. WHEN the Audit Node executes, THEN the Mobius System SHALL use the Reasoning Model to evaluate compliance
2. WHEN auditing an image, THEN the Mobius System SHALL pass the image_uri from the Generation Node as multimodal input to the Reasoning Model
3. WHEN the Reasoning Model analyzes the image, THEN the Mobius System SHALL provide the full Brand Guidelines as context for compliance checking
4. WHEN audit completes, THEN the Mobius System SHALL return structured compliance scores with category breakdowns and violation details
5. THE Mobius System SHALL use the Reasoning Model for auditing because it has superior reasoning capabilities compared to the Vision Model

### Requirement 5: Fal.ai Service Removal

**User Story:** As a developer, I want all Fal.ai dependencies removed from the codebase, so that the system has a simplified architecture with fewer external dependencies.

#### Acceptance Criteria

1. THE Mobius System SHALL remove the fal-client package from all dependency lists
2. WHEN searching the codebase for "fal", THEN the Mobius System SHALL return no matches in active code files
3. THE Mobius System SHALL remove all import statements for fal_client
4. THE Mobius System SHALL remove all references to Flux Pro and Ideogram models from documentation
5. WHEN deployment secrets are configured, THEN the Mobius System SHALL not require FAL_KEY

### Requirement 6: Gemini Client Refactoring

**User Story:** As a developer, I want a unified Gemini client that handles both reasoning and vision tasks, so that I can easily switch between models based on the use case.

#### Acceptance Criteria

1. WHEN the Gemini Client is instantiated, THEN the Mobius System SHALL initialize both reasoning_model and vision_model attributes
2. WHEN analyzing a PDF, THEN the Gemini Client SHALL use the reasoning_model instance
3. WHEN generating an image, THEN the Gemini Client SHALL use the vision_model instance
4. WHEN auditing an image, THEN the Gemini Client SHALL use the reasoning_model instance with multimodal vision input
5. WHEN a method is called on the Gemini Client, THEN the Mobius System SHALL automatically select the appropriate model based on the operation type

### Requirement 7: Backward Compatibility

**User Story:** As a system operator, I want the refactoring to maintain API compatibility, so that existing integrations continue to work without changes.

#### Acceptance Criteria

1. WHEN the refactoring is complete, THEN the Mobius System SHALL maintain all existing API endpoints with identical request and response schemas
2. WHEN a client submits a generation request, THEN the Mobius System SHALL process it using the new Gemini architecture without requiring client changes
3. WHEN audit results are returned, THEN the Mobius System SHALL provide the same compliance score structure as before the refactoring
4. WHEN brand ingestion completes, THEN the Mobius System SHALL return Brand Entity data in the same format as the previous implementation
5. THE Mobius System SHALL not introduce breaking changes to the database schema during this refactoring

### Requirement 8: Documentation Updates

**User Story:** As a developer, I want updated documentation that reflects the new Gemini architecture, so that I can understand the system design and troubleshoot issues.

#### Acceptance Criteria

1. WHEN documentation is updated, THEN the Mobius System SHALL replace all references to Fal.ai with Gemini 3 model descriptions
2. WHEN architecture diagrams are updated, THEN the Mobius System SHALL show the dual-model approach with Reasoning Model and Vision Model
3. WHEN deployment guides are updated, THEN the Mobius System SHALL remove FAL_KEY from required secrets and emphasize GEMINI_API_KEY
4. WHEN troubleshooting guides are updated, THEN the Mobius System SHALL include Gemini-specific error handling and rate limit guidance
5. THE Mobius System SHALL update the MOBIUS-ARCHITECTURE.md file to reflect the new Gemini 3 dual-architecture design

### Requirement 9: Error Handling and Logging

**User Story:** As a system operator, I want clear error messages and logging for Gemini API interactions, so that I can quickly diagnose and resolve issues.

#### Acceptance Criteria

1. WHEN a Gemini API call fails, THEN the Mobius System SHALL log the error with model name, operation type, and error details
2. WHEN rate limits are exceeded, THEN the Mobius System SHALL return a 429 status code with retry-after guidance
3. WHEN the API key is invalid, THEN the Mobius System SHALL return a 401 status code with clear authentication error message
4. WHEN image generation times out, THEN the Mobius System SHALL log the timeout and retry with increased timeout values
5. WHEN audit analysis fails, THEN the Mobius System SHALL return a partial compliance score with error annotations rather than failing completely

### Requirement 10: Testing and Validation

**User Story:** As a quality assurance engineer, I want comprehensive tests for the new Gemini integration, so that I can verify correctness and prevent regressions.

#### Acceptance Criteria

1. WHEN unit tests are executed, THEN the Mobius System SHALL verify that the Reasoning Model is used for PDF parsing
2. WHEN unit tests are executed, THEN the Mobius System SHALL verify that the Vision Model is used for image generation
3. WHEN unit tests are executed, THEN the Mobius System SHALL verify that the Reasoning Model is used for compliance auditing
4. WHEN integration tests are executed, THEN the Mobius System SHALL verify end-to-end workflows produce valid compliance scores
5. WHEN property-based tests are executed, THEN the Mobius System SHALL verify that Compressed Digital Twin serialization stays under token limits
