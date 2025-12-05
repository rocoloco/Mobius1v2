# Requirements Document

## Introduction

Mobius is a brand governance API that ensures AI-generated images comply with brand guidelines through an automated audit loop. The system uses serverless infrastructure to orchestrate image generation, visual auditing, and iterative correction until brand compliance is achieved.

## Glossary

- **Mobius System**: The complete brand governance API including orchestration, generation, and audit components
- **Modal App**: The serverless Python application runtime environment
- **LangGraph Workflow**: The state machine that orchestrates the generation-audit-correction loop
- **Generation Node**: The workflow component that creates images using Fal.ai
- **Audit Node**: The workflow component that evaluates image compliance using Gemini
- **Correction Node**: The workflow component that modifies prompts based on audit feedback
- **Fal.ai Service**: The external image generation service using Flux.2 model
- **Gemini Service**: The Google GenAI visual audit service using Gemini 3 Deep Think
- **Supabase Database**: The PostgreSQL database for persistence
- **Audit Result**: A structured JSON response containing approval status, reason, and fix suggestion
- **Brand Compliance**: The state where a generated image meets all brand governance criteria
- **Brand Hex Codes**: A list of hexadecimal color codes representing the brand's approved color palette
- **Brand Rules**: Text description of brand guidelines and visual standards
- **Job State**: The TypedDict structure containing workflow state including prompt, brand data, images, and audit history
- **HTTP Endpoint**: A web-accessible URL that accepts POST requests to trigger workflows
- **Next.js Application**: The frontend client application that consumes the Mobius API

## Requirements

### Requirement 1

**User Story:** As a brand manager, I want to generate images that automatically comply with brand guidelines, so that I can ensure consistent brand representation without manual review.

#### Acceptance Criteria

1. WHEN the Mobius System receives an image generation request, THEN the Mobius System SHALL initiate the LangGraph Workflow with the provided prompt, brand_hex_codes list, and brand_rules text
2. WHEN the Generation Node executes, THEN the Mobius System SHALL call the Fal.ai Service with the current prompt and return the generated image URL
3. WHEN the Audit Node executes, THEN the Mobius System SHALL call the Gemini Service with the generated image, brand_hex_codes, and brand_rules, and return an Audit Result
4. WHEN an Audit Result indicates approval is false, THEN the Mobius System SHALL route to the Correction Node
5. WHEN an Audit Result indicates approval is true, THEN the Mobius System SHALL complete the workflow and return the approved image

### Requirement 2

**User Story:** As a system operator, I want the audit process to provide structured feedback, so that I can understand why images fail and how to improve them.

#### Acceptance Criteria

1. WHEN the Audit Node processes an image, THEN the Gemini Service SHALL return a JSON response conforming to the schema: {"approved": boolean, "reason": string, "fix_suggestion": string}
2. WHEN the Audit Result contains a fix_suggestion, THEN the Correction Node SHALL append the fix_suggestion to the original prompt
3. WHEN the Correction Node completes, THEN the Mobius System SHALL route back to the Generation Node with the corrected prompt

### Requirement 3

**User Story:** As a developer, I want the system to run on serverless infrastructure, so that I can scale automatically and minimize operational overhead.

#### Acceptance Criteria

1. WHEN the orchestrator module is deployed, THEN the Mobius System SHALL run as a Modal App named "mobius-worker"
2. WHEN the Modal App starts, THEN the Mobius System SHALL load secrets for FAL_KEY, GEMINI_API_KEY, SUPABASE_URL, and SUPABASE_KEY from Modal's secret management
3. WHEN the LangGraph Workflow executes, THEN the Mobius System SHALL operate as an asynchronous worker within the Modal runtime

### Requirement 4

**User Story:** As a system architect, I want workflow state to be persisted, so that I can track generation attempts and audit history.

#### Acceptance Criteria

1. WHEN the LangGraph Workflow state changes, THEN the Mobius System SHALL persist the state to the Supabase Database
2. WHEN a workflow completes, THEN the Mobius System SHALL store the final approved image URL and all audit attempts in the Supabase Database
3. WHEN a workflow fails after maximum iterations, THEN the Mobius System SHALL record the failure state and last audit feedback in the Supabase Database
4. WHEN Supabase credentials are missing or invalid, THEN the Mobius System SHALL log state changes to console output instead of crashing

### Requirement 5

**User Story:** As a developer, I want all orchestration logic in a single deployable file, so that I can easily deploy and maintain the system.

#### Acceptance Criteria

1. THE Mobius System SHALL implement all orchestration logic in a single file named orchestrator.py
2. WHEN orchestrator.py is deployed to Modal, THEN the Mobius System SHALL be fully operational without additional configuration files
3. THE orchestrator.py file SHALL define the Modal App, LangGraph Workflow, and all three workflow nodes

### Requirement 6

**User Story:** As a system operator, I want to prevent infinite loops, so that failed generations don't consume excessive resources.

#### Acceptance Criteria

1. WHEN the LangGraph Workflow executes, THEN the Mobius System SHALL enforce a maximum iteration limit
2. WHEN the maximum iteration limit is reached without approval, THEN the Mobius System SHALL terminate the workflow and return an error state
3. WHEN the workflow terminates due to iteration limit, THEN the Mobius System SHALL include the last Audit Result in the error response

### Requirement 7

**User Story:** As a frontend developer, I want to trigger brand governance workflows via HTTP, so that I can integrate the system with the Next.js application.

#### Acceptance Criteria

1. WHEN the Mobius System is deployed, THEN the Mobius System SHALL expose an HTTP POST endpoint for run_mobius_job
2. WHEN a client sends a POST request with prompt, brand_hex_codes, and brand_rules, THEN the Mobius System SHALL execute the workflow and return the final Job State
3. WHEN a workflow completes successfully, THEN the Mobius System SHALL return a 200 status code with the approved image URL and audit history
4. WHEN a workflow fails due to maximum retries, THEN the Mobius System SHALL return a 200 status code with failure status and the last audit feedback
5. WHEN an internal error occurs, THEN the Mobius System SHALL return a 500 status code with an error message
