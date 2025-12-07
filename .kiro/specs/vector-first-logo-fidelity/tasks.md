# Implementation Plan: Vector-First Digital Twin (Logo Fidelity)

- [x] 1. Update project dependencies





  - Add `cairosvg>=2.7.0` to `pyproject.toml` dependencies list
  - Verify `pillow>=10.0.0` is present in dependencies
  - Update Modal image definition to include `libcairo2` in `apt_install` list
  - Update Modal image definition to include `cairosvg` in `pip_install` list
  - _Requirements: 1.1, 1.2, 1.4_

- [x] 2. Create LogoRasterizer utility class





  - Create new file `src/mobius/utils/__init__.py` (if not exists)
  - Create new file `src/mobius/utils/media.py`
  - Implement `LogoRasterizer` class with `prepare_for_vision()` static method
  - Implement SVG detection logic (check if "svg" in mime_type)
  - Implement aspect ratio calculation for both SVG and raster images
  - Add structured logging with operation_type, mime_type, dimensions
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 2.1 Implement SVG rasterization logic


  - Add optional cairosvg import with try/except for graceful degradation
  - Implement `_rasterize_svg()` helper method
  - Calculate output dimensions preserving aspect ratio (longest side = target_dim)
  - Use `cairosvg.svg2png()` with output_width and output_height parameters
  - Return PNG bytes with transparency preserved
  - Handle cairosvg missing: log error and return original bytes
  - Handle SVG parsing errors: catch exception, log, return original bytes
  - _Requirements: 3.1, 3.2, 3.3, 5.1_

- [x] 2.2 Implement raster upscaling logic

  - Implement `_upscale_raster()` helper method
  - Load image with PIL from bytes
  - Check longest dimension against 1000px threshold
  - If >= 1000px: return original bytes unchanged (passthrough optimization)
  - If < 1000px: calculate new dimensions preserving aspect ratio
  - Resize using `Image.Resampling.LANCZOS` filter
  - Save as PNG format to preserve transparency
  - Handle PIL loading errors: catch exception, log, return original bytes
  - _Requirements: 4.1, 4.2, 4.5, 4.6, 5.2_


- [x] 2.3 Implement error handling and logging

  - Wrap all processing in try/except to ensure no exceptions propagate
  - Log "rasterizing_vector_logo" with target_dimension for SVG processing
  - Log "upscaling_low_res_logo" with original_width and target for raster upscaling
  - Log "using_original_logo" with width and reason for passthrough
  - Log errors with operation_type, mime_type, error_message, error_type
  - Ensure function never raises exceptions (return original bytes on any error)
  - _Requirements: 5.3, 5.4, 8.1, 8.2, 8.3_

- [x] 2.4 Write unit tests for LogoRasterizer








  - Test SVG to PNG conversion with valid SVG input
  - Test aspect ratio preservation for wide, tall, and square SVGs
  - Test transparency preservation in SVG output
  - Test raster upscaling for images < 1000px
  - Test passthrough for images >= 1000px
  - Test MIME type detection for various formats
  - Test error handling with malformed SVG
  - Test error handling with corrupted raster image
  - Test graceful degradation when cairosvg is missing
  - _Requirements: 9.1, 9.2, 9.3_

- [x] 2.5 Write property-based test for output validity




  - **Property 1: Output Validity and Format**
  - **Validates: Requirements 2.3, 4.6**
  - Use Hypothesis to generate random logo_bytes and mime_type combinations
  - Verify output can be loaded as valid PNG by PIL
  - Run 100+ iterations to test across input space
  - _Requirements: 2.3, 4.6_

- [x] 2.6 Write property-based test for aspect ratio preservation


  - **Property 2: Aspect Ratio Preservation**
  - **Validates: Requirements 3.2, 4.2**
  - Generate test images with random dimensions (100-4000px)
  - Process through LogoRasterizer
  - Verify output aspect ratio matches input within 1% tolerance
  - Test both SVG and raster inputs
  - _Requirements: 3.2, 4.2_


- [x] 2.7 Write property-based test for transparency preservation


  - **Property 3: Transparency Preservation**
  - **Validates: Requirements 3.3**
  - Generate SVG content with transparent regions
  - Process through LogoRasterizer
  - Verify output PNG has alpha channel (mode RGBA, LA, or PA)
  - _Requirements: 3.3_

- [x] 2.8 Write property-based test for high-resolution passthrough


  - **Property 4: High-Resolution Passthrough**
  - **Validates: Requirements 4.5**
  - Generate high-res images (>= 1000px) with random dimensions
  - Process through LogoRasterizer
  - Verify output bytes are identical to input bytes
  - _Requirements: 4.5_



- [x] 2.9 Write property-based test for exception safety

  - **Property 5: Exception Safety**
  - **Validates: Requirements 5.3**
  - Generate random binary data and mime_type strings (including garbage)
  - Call prepare_for_vision() with all combinations
  - Verify function never raises exceptions
  - Verify function always returns bytes
  - _Requirements: 5.3_



- [x] 2.10 Write property-based test for independent processing

  - **Property 6: Independent Processing**
  - **Validates: Requirements 6.3**
  - Generate list of 2-5 logo inputs
  - Process each individually and record results
  - Shuffle list and process again
  - Verify results are order-independent (match by original input)
  - _Requirements: 6.3_

- [x] 3. Integrate LogoRasterizer with Generate Node





  - Import `LogoRasterizer` from `mobius.utils.media` in `src/mobius/nodes/generate.py`
  - Locate logo download loop (around line 118-143)
  - Extract MIME type from HTTP response headers (`response.headers.get('content-type', 'image/png')`)
  - Call `LogoRasterizer.prepare_for_vision()` for each downloaded logo
  - Pass processed bytes to `logo_bytes_list` instead of raw bytes
  - Add logging for logo processing (variant_name, original_size, processed_size)
  - _Requirements: 6.1, 6.2_

- [ ]* 3.1 Write integration test for Generate Node with SVG logo
  - Create test brand with SVG logo in Supabase Storage
  - Trigger generation workflow
  - Verify LogoRasterizer.prepare_for_vision() is called
  - Verify processed logo bytes are passed to Vision Model
  - Verify generation completes successfully
  - _Requirements: 6.1, 6.2, 9.4_

- [ ]* 3.2 Write integration test for Generate Node with multiple logos
  - Create test brand with 3 different logos (SVG, low-res PNG, high-res PNG)
  - Trigger generation workflow
  - Verify each logo is processed independently
  - Verify all processed logos are passed to Vision Model
  - Verify generation completes successfully
  - _Requirements: 6.3_

- [ ]* 3.3 Write integration test for graceful degradation
  - Create test brand with corrupted logo file
  - Trigger generation workflow
  - Verify generation completes without crashing
  - Verify error is logged appropriately
  - Verify original bytes are used as fallback
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 4. Update documentation





  - Update MOBIUS-ARCHITECTURE.md to describe Vector-First Digital Twin strategy
  - Update MOBIUS-ARCHITECTURE.md to make it less verbose and ensure that it's still up to date with the current architecture
  - Document LogoRasterizer utility in architecture section
  - Add section on logo processing flow with diagram
  - Document Modal deployment requirements (libcairo2, cairosvg)
  - Document target_dim parameter as configurable (default 2048px)
  - Add troubleshooting section for common logo processing errors
  - _Requirements: 10.1, 10.2, 10.3_

