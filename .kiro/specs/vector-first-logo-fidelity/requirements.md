# Requirements Document: Vector-First Digital Twin (Logo Fidelity)

## Introduction

This specification addresses a critical quality issue in the Mobius brand governance system: the Gemini 3 Vision Model receives low-resolution logo thumbnails (approximately 8KB) during image generation, causing the model to hallucinate details and produce distorted text with jagged edges. The solution implements a "Vector-First Digital Twin" strategy where SVG logos are dynamically rasterized to high-fidelity PNGs (max 2048px) at runtime, ensuring the Vision Model always receives perfect geometry regardless of source file size.

## Glossary

- **Mobius System**: The complete brand governance platform running on Modal infrastructure
- **Vision Model**: The Gemini 3 Pro Image Preview model optimized for image generation tasks
- **Generation Node**: The workflow component that creates images using the Vision Model
- **Logo Rasterizer**: A utility class that converts vector logos to high-resolution raster images
- **SVG**: Scalable Vector Graphics, a vector image format that maintains perfect quality at any resolution
- **Rasterization**: The process of converting vector graphics to pixel-based images
- **Target Dimension**: The maximum dimension for rasterized logos (default: 2048px)
- **CairoSVG**: A Python library that renders SVG files to PNG format using the Cairo graphics library
- **Modal Image**: The immutable serverless environment definition used to deploy Mobius
- **Lanczos Resampling**: A high-quality image upscaling algorithm that preserves edge sharpness
- **Aspect Ratio**: The proportional relationship between an image's width and height

## Requirements

### Requirement 1: Dependency Management (Modal Optimized)

**User Story:** As a system operator, I want system dependencies defined in the Modal image, so that the environment is reproducible and guarantees vector processing capabilities.

#### Acceptance Criteria

1. THE Mobius System SHALL include `cairosvg` in the `pip_install` list of the Modal Image definition in `mobius/app.py`
2. THE Mobius System SHALL include `libcairo2` in the `apt_install` list of the Modal Image definition
3. WHEN the Modal app builds, THEN the system SHALL verify successful installation of the Cairo graphics library
4. THE Mobius System SHALL include `pillow` (PIL) for raster image processing
5. THE Mobius System SHALL NOT require manual OS-level installation instructions, relying solely on the Modal environment definition

### Requirement 2: Logo Rasterizer Utility

**User Story:** As a developer, I want a reusable utility class for logo processing, so that I can consistently prepare logos for the Vision Model across all workflows.

#### Acceptance Criteria

1. THE Mobius System SHALL create a `LogoRasterizer` class in `src/mobius/utils/media.py`
2. THE Mobius System SHALL provide a `prepare_for_vision` method that accepts `logo_bytes`, `mime_type`, and optional `target_dim` parameters
3. WHEN `prepare_for_vision` is called, THEN the Mobius System SHALL return processed logo bytes suitable for Vision Model input
4. THE Mobius System SHALL use structlog for all logging operations with structured context fields

### Requirement 3: Vector Logo Rasterization (Aspect Ratio Preserved)

**User Story:** As a brand manager, I want SVG logos rendered at high resolution, so that the Vision Model sees perfect geometry without distortion.

#### Acceptance Criteria

1. WHEN the `mime_type` contains "svg", THEN the Mobius System SHALL use `cairosvg.svg2png` to render the logo
2. WHEN rendering an SVG, THEN the Mobius System SHALL scale the **longest dimension** to `target_dim` while preserving the original aspect ratio (do not force a square output)
3. WHEN rendering an SVG, THEN the Mobius System SHALL preserve transparent backgrounds in the output PNG
4. WHEN SVG rendering succeeds, THEN the Mobius System SHALL log the operation with `target_dimension` context

### Requirement 4: Raster Logo Upscaling (Aspect Ratio Preserved)

**User Story:** As a designer, I want low-resolution raster logos upscaled intelligently, so that the Vision Model receives adequate detail even when vector sources are unavailable.

#### Acceptance Criteria

1. WHEN the `mime_type` indicates a raster format (PNG, JPEG, WEBP), THEN the Mobius System SHALL load the image using PIL
2. WHEN a raster logo's **longest dimension** is less than 1000 pixels, THEN the Mobius System SHALL calculate a new size where the longest side equals `target_dim` and the shorter side scales proportionally
3. WHEN the new size is calculated, THEN the Mobius System SHALL resize the image using `Lanczos` resampling
4. WHEN upscaling occurs, THEN the Mobius System SHALL log a warning with `original_width` and `target` context fields
5. WHEN a raster logo's longest dimension is 1000 pixels or greater, THEN the Mobius System SHALL return the original bytes without modification
6. WHEN saving upscaled images, THEN the Mobius System SHALL use PNG format to preserve transparency

### Requirement 5: Error Handling

**User Story:** As a system operator, I want logo processing to fail gracefully, so that generation workflows continue even when files are malformed.

#### Acceptance Criteria

1. WHEN SVG rasterization fails (e.g., malformed XML), THEN the Mobius System SHALL catch the exception, log the error, and return the original logo bytes
2. WHEN raster image loading fails, THEN the Mobius System SHALL catch the exception, log the error, and return the original logo bytes
3. WHEN any processing step fails, THEN the Mobius System SHALL not raise exceptions that would halt the generation workflow
4. WHEN errors are logged, THEN the Mobius System SHALL include `operation_type`, `mime_type`, and `error_message` in structured log fields

### Requirement 6: Generation Node Integration

**User Story:** As a developer, I want the Generation Node to automatically use high-fidelity logos, so that the Vision Model receives optimal input without manual intervention.

#### Acceptance Criteria

1. WHEN the Generation Node prepares brand context, THEN the Mobius System SHALL invoke `LogoRasterizer.prepare_for_vision` for all logo assets
2. WHEN logo processing completes, THEN the Mobius System SHALL pass the processed logo bytes to the Vision Model client
3. WHEN multiple logos exist for a brand, THEN the Mobius System SHALL process each logo independently
4. THE Mobius System SHALL maintain backward compatibility with existing generation workflows

### Requirement 7: Performance Optimization

**User Story:** As a system architect, I want logo processing to be efficient, so that generation latency remains acceptable.

#### Acceptance Criteria

1. WHEN a logo is already high-resolution, THEN the Mobius System SHALL skip processing and return original bytes
2. WHEN processing is skipped, THEN the Mobius System SHALL log the decision with original resolution context
3. WHEN SVG rendering is required, THEN the Mobius System SHALL complete the operation within 2 seconds for files under 1MB
4. THE Mobius System SHALL not cache processed logos to avoid stale data issues (rely on fast compute)

### Requirement 8: Logging and Observability

**User Story:** As a system operator, I want detailed logs for logo processing operations, so that I can diagnose quality issues.

#### Acceptance Criteria

1. WHEN a vector logo is rasterized, THEN the Mobius System SHALL log "rasterizing_vector_logo" with `target_dimension` field
2. WHEN a raster logo is upscaled, THEN the Mobius System SHALL log "upscaling_low_res_logo" with `original_width` and `target` fields
3. WHEN processing is skipped, THEN the Mobius System SHALL log "using_original_logo" with `width` and `reason` fields

### Requirement 9: Testing and Validation

**User Story:** As a quality assurance engineer, I want comprehensive tests for logo processing, so that I can verify correctness and prevent distortion.

#### Acceptance Criteria

1. WHEN unit tests execute, THEN the Mobius System SHALL verify that SVG inputs produce high-res PNG outputs
2. WHEN unit tests execute, THEN the Mobius System SHALL verify that the **aspect ratio** of the output matches the input (e.g., a wide logo remains wide)
3. WHEN unit tests execute, THEN the Mobius System SHALL verify that low-resolution raster inputs are upscaled using Lanczos
4. WHEN integration tests execute, THEN the Mobius System SHALL verify that the Generation Node successfully uses processed logos

### Requirement 10: Documentation

**User Story:** As a developer, I want clear documentation on logo processing requirements.

#### Acceptance Criteria

1. WHEN architecture documentation is updated, THEN the Mobius System SHALL describe the Vector-First Digital Twin strategy
2. WHEN developer guides are updated, THEN the Mobius System SHALL reference the Modal `apt_install` configuration as the source of truth for dependencies
3. THE Mobius System SHALL document the 2048px target dimension as a configurable parameter