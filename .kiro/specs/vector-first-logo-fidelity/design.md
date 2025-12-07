# Design Document: Vector-First Digital Twin (Logo Fidelity)

## Overview

The Vector-First Digital Twin design addresses a critical quality issue where the Gemini 3 Vision Model receives low-resolution logo thumbnails during image generation, causing hallucinated details and distorted text. The solution introduces a `LogoRasterizer` utility that dynamically converts SVG logos to high-fidelity PNGs (up to 2048px) while preserving aspect ratios, and intelligently upscales low-resolution raster logos using Lanczos resampling.

This design integrates seamlessly into the existing generation workflow by intercepting logo bytes before they're passed to the Vision Model, ensuring zero breaking changes to the API or database schema.

## Architecture

### System Context

```
┌─────────────────────────────────────────────────────────────┐
│                    Generation Workflow                       │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │ Generate Node│─────▶│LogoRasterizer│─────▶│  Vision  │ │
│  │              │      │              │      │  Model   │ │
│  │ - Fetch logos│      │ - SVG→PNG    │      │          │ │
│  │ - Download   │      │ - Upscale    │      │ - Generate│ │
│  │   from URLs  │      │ - Preserve   │      │   Image  │ │
│  │              │      │   aspect     │      │          │ │
│  └──────────────┘      └──────────────┘      └──────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

1. **Generate Node** (`src/mobius/nodes/generate.py`):
   - Currently downloads logo bytes from Supabase Storage URLs
   - **NEW**: Passes logo bytes through `LogoRasterizer.prepare_for_vision()` before appending to `logo_bytes_list`
   - No changes to function signature or return values

2. **Gemini Client** (`src/mobius/tools/gemini.py`):
   - Already accepts `logo_bytes: list[bytes]` parameter
   - No changes required - receives processed bytes transparently

3. **Modal Deployment** (assumed in `mobius/app.py` or similar):
   - **NEW**: Add `libcairo2` to `apt_install` list
   - **NEW**: Add `cairosvg` to `pip_install` list

## Components and Interfaces

### LogoRasterizer Class

**Location**: `src/mobius/utils/media.py` (new file)

**Purpose**: Centralized utility for preparing logo images for Vision Model consumption

**Class Definition**:

```python
class LogoRasterizer:
    """
    Utility for preparing logo images for Vision Model consumption.
    
    Handles:
    - SVG to PNG rasterization at high resolution
    - Raster image upscaling with aspect ratio preservation
    - Graceful degradation when dependencies are missing
    """
    
    @staticmethod
    def prepare_for_vision(
        logo_bytes: bytes,
        mime_type: str,
        target_dim: int = 2048
    ) -> bytes:
        """
        Prepare logo for Vision Model by rasterizing or upscaling.
        
        Args:
            logo_bytes: Raw logo file bytes
            mime_type: MIME type (e.g., "image/svg+xml", "image/png")
            target_dim: Maximum dimension for output (default: 2048px)
            
        Returns:
            Processed logo bytes (always PNG format)
            
        Raises:
            Never raises - returns original bytes on error
        """
```

**Key Methods**:

1. `prepare_for_vision()` - Main entry point
   - Detects file type from MIME type
   - Routes to SVG or raster processing path
   - Returns processed bytes or original on error

2. `_rasterize_svg()` - Internal SVG handler
   - Uses `cairosvg.svg2png()` for rendering
   - Calculates dimensions to preserve aspect ratio
   - Returns PNG bytes with transparency

3. `_upscale_raster()` - Internal raster handler
   - Uses PIL to load and analyze image
   - Applies Lanczos resampling if needed
   - Returns PNG bytes with transparency

### Generate Node Integration

**Modified Flow**:

```python
# Current code (lines 116-143 in generate.py):
for logo in brand.guidelines.logos:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(logo.url)
        logo_data = response.content
    logo_bytes_list.append(logo_data)

# NEW code:
from mobius.utils.media import LogoRasterizer

for logo in brand.guidelines.logos:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(logo.url)
        logo_data = response.content
        
    # Detect MIME type from response headers
    mime_type = response.headers.get('content-type', 'image/png')
    
    # Process logo for Vision Model
    processed_logo = LogoRasterizer.prepare_for_vision(
        logo_bytes=logo_data,
        mime_type=mime_type,
        target_dim=2048
    )
    
    logo_bytes_list.append(processed_logo)
```

## Data Models

### Input Data

**Logo Metadata** (existing in `BrandGuidelines.logos`):
```python
class LogoInfo(BaseModel):
    variant_name: str
    url: str  # Supabase Storage public URL
    min_width_px: Optional[int]
    clear_space_ratio: Optional[float]
    forbidden_backgrounds: List[str]
```

**HTTP Response**:
- `content`: Raw logo bytes
- `headers['content-type']`: MIME type string

### Processing Data

**MIME Type Detection**:
- SVG: `"image/svg+xml"`, `"image/svg"`, or contains `"svg"`
- PNG: `"image/png"`
- JPEG: `"image/jpeg"`, `"image/jpg"`
- WEBP: `"image/webp"`

**Dimension Calculation** (aspect ratio preservation):
```python
# For SVG:
if width > height:
    output_width = target_dim
    output_height = int(target_dim * (height / width))
else:
    output_height = target_dim
    output_width = int(target_dim * (width / height))

# For raster upscaling:
aspect_ratio = width / height
if width > height:
    new_width = target_dim
    new_height = int(target_dim / aspect_ratio)
else:
    new_height = target_dim
    new_width = int(target_dim * aspect_ratio)
```

### Output Data

**Processed Logo Bytes**:
- Format: PNG (always)
- Max dimension: 2048px (configurable)
- Aspect ratio: Preserved from original
- Transparency: Preserved if present
- Typical size: 50KB - 500KB (depending on complexity)

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Output Validity and Format

*For any* logo bytes and valid MIME type, the output from `prepare_for_vision()` should be valid PNG bytes that can be loaded by PIL without errors.

**Validates: Requirements 2.3, 4.6**

**Rationale**: The Vision Model expects consistent image format. By ensuring all outputs are valid PNGs regardless of input format, we guarantee compatibility and simplify downstream processing.

### Property 2: Aspect Ratio Preservation

*For any* logo image (SVG or raster), if the original aspect ratio is W:H, then the processed output should maintain the same aspect ratio within a tolerance of 1%.

**Validates: Requirements 3.2, 4.2**

**Rationale**: Preserving aspect ratio prevents logo distortion, which is critical for brand integrity. Forcing logos into square dimensions would violate brand guidelines and produce visually incorrect results.

### Property 3: Transparency Preservation

*For any* SVG logo with transparent regions, the output PNG should contain an alpha channel with transparency preserved in the same regions.

**Validates: Requirements 3.3**

**Rationale**: Many logos rely on transparency to work on various backgrounds. Losing transparency would force logos onto white backgrounds, limiting their usability and violating brand guidelines.

### Property 4: High-Resolution Passthrough

*For any* raster image where the longest dimension is >= 1000 pixels, the output bytes should be identical to the input bytes (no processing applied).

**Validates: Requirements 4.5**

**Rationale**: Processing already high-quality images wastes compute resources and risks introducing artifacts. The passthrough optimization ensures efficiency while maintaining quality.

### Property 5: Exception Safety

*For any* input bytes and MIME type (including malformed or corrupted data), `prepare_for_vision()` should never raise an exception - it should either return processed bytes or the original bytes.

**Validates: Requirements 5.3**

**Rationale**: Logo processing failures should not halt the entire generation workflow. Graceful degradation ensures the system remains operational even when individual logos are problematic.

### Property 6: Independent Processing

*For any* list of logo bytes, processing each logo should produce the same result regardless of the order or presence of other logos in the list.

**Validates: Requirements 6.3**

**Rationale**: Logo processing must be stateless and independent to prevent cross-contamination. This ensures predictable behavior and simplifies debugging.

## Error Handling

### Error Categories

1. **Missing Dependencies**:
   - **Condition**: `cairosvg` import fails (libcairo not installed)
   - **Handling**: Log error, return original bytes, continue workflow
   - **User Impact**: SVG logos won't be rasterized, but generation continues

2. **Malformed SVG**:
   - **Condition**: SVG XML parsing fails
   - **Handling**: Catch exception, log error, return original bytes
   - **User Impact**: Logo may appear distorted in output, but generation completes

3. **Corrupted Raster Image**:
   - **Condition**: PIL cannot load image bytes
   - **Handling**: Catch exception, log error, return original bytes
   - **User Impact**: Logo may appear distorted in output, but generation completes

4. **Network Timeout**:
   - **Condition**: Logo download from Supabase Storage times out
   - **Handling**: Already handled by `httpx` timeout in Generate Node
   - **User Impact**: Logo excluded from generation, logged as warning

### Error Logging Structure

All errors logged with structured fields:
```python
logger.error(
    "logo_processing_failed",
    operation_type="svg_rasterization" | "raster_upscaling",
    mime_type=mime_type,
    error_message=str(e),
    error_type=type(e).__name__,
    logo_size_bytes=len(logo_bytes)
)
```

### Graceful Degradation Strategy

```
┌─────────────────────────────────────────────────────────┐
│                  Processing Decision Tree                │
│                                                          │
│  Input: logo_bytes + mime_type                          │
│                                                          │
│  ┌─────────────────┐                                    │
│  │ Is SVG?         │                                    │
│  └────┬────────────┘                                    │
│       │                                                  │
│   YES │ NO                                              │
│       │                                                  │
│  ┌────▼────────────┐         ┌──────────────────┐     │
│  │ Try cairosvg    │         │ Load with PIL    │     │
│  │ rasterization   │         │                  │     │
│  └────┬────────────┘         └────┬─────────────┘     │
│       │                            │                    │
│  SUCCESS│ FAIL              SUCCESS│ FAIL              │
│       │                            │                    │
│  ┌────▼────────────┐         ┌────▼─────────────┐     │
│  │ Return PNG      │         │ Check dimensions │     │
│  │ bytes           │         │                  │     │
│  └─────────────────┘         └────┬─────────────┘     │
│                                    │                    │
│                              < 1000px│ >= 1000px       │
│                                    │                    │
│                              ┌─────▼──────────┐        │
│                              │ Upscale with   │        │
│                              │ Lanczos        │        │
│                              └─────┬──────────┘        │
│                                    │                    │
│                              SUCCESS│ FAIL              │
│                                    │                    │
│  ┌─────────────────────────────────▼──────────────┐   │
│  │ Return original bytes (fallback)               │   │
│  └────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Testing Strategy

### Unit Testing

**Test Coverage**:

1. **SVG Rasterization**:
   - Valid SVG → PNG conversion
   - Aspect ratio preservation (wide, tall, square)
   - Transparency preservation
   - Malformed SVG → original bytes returned

2. **Raster Upscaling**:
   - Small PNG (< 1000px) → upscaled PNG
   - Large PNG (>= 1000px) → original bytes
   - Aspect ratio preservation during upscaling
   - Corrupted image → original bytes returned

3. **MIME Type Detection**:
   - Various SVG MIME types recognized
   - PNG, JPEG, WEBP correctly identified
   - Unknown MIME types handled gracefully

4. **Error Handling**:
   - Missing cairosvg dependency
   - PIL loading failures
   - Invalid input bytes

**Test Fixtures**:
- Sample SVG files (wide, tall, square, with/without transparency)
- Sample raster images (various sizes and formats)
- Corrupted/malformed files

### Property-Based Testing

**Framework**: Hypothesis (Python)

**Test Configuration**:
- Minimum 100 iterations per property
- Shrinking enabled for failure reproduction

**Property Tests**:

1. **Property 1: Output Validity and Format**
   ```python
   @given(
       logo_bytes=st.binary(min_size=100, max_size=1_000_000),
       mime_type=st.sampled_from([
           "image/svg+xml", "image/png", "image/jpeg", "image/webp"
       ])
   )
   def test_output_is_valid_png(logo_bytes, mime_type):
       """Feature: vector-first-logo-fidelity, Property 1: Output Validity and Format"""
       result = LogoRasterizer.prepare_for_vision(logo_bytes, mime_type)
       
       # Should be able to load as PNG
       img = Image.open(io.BytesIO(result))
       assert img.format == "PNG"
   ```

2. **Property 2: Aspect Ratio Preservation**
   ```python
   @given(
       width=st.integers(min_value=100, max_value=4000),
       height=st.integers(min_value=100, max_value=4000)
   )
   def test_aspect_ratio_preserved(width, height):
       """Feature: vector-first-logo-fidelity, Property 2: Aspect Ratio Preservation"""
       # Generate test image with known aspect ratio
       original_img = Image.new('RGBA', (width, height), (255, 0, 0, 128))
       original_bytes = io.BytesIO()
       original_img.save(original_bytes, format='PNG')
       
       result = LogoRasterizer.prepare_for_vision(
           original_bytes.getvalue(), 
           "image/png"
       )
       
       # Check output aspect ratio
       output_img = Image.open(io.BytesIO(result))
       original_ratio = width / height
       output_ratio = output_img.width / output_img.height
       
       # Allow 1% tolerance for rounding
       assert abs(original_ratio - output_ratio) / original_ratio < 0.01
   ```

3. **Property 3: Transparency Preservation**
   ```python
   @given(
       width=st.integers(min_value=100, max_value=1000),
       height=st.integers(min_value=100, max_value=1000)
   )
   def test_transparency_preserved(width, height):
       """Feature: vector-first-logo-fidelity, Property 3: Transparency Preservation"""
       # Create SVG with transparency
       svg_content = f'''
       <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
           <rect width="{width}" height="{height}" fill="red" opacity="0.5"/>
       </svg>
       '''
       
       result = LogoRasterizer.prepare_for_vision(
           svg_content.encode('utf-8'),
           "image/svg+xml"
       )
       
       # Check output has alpha channel
       output_img = Image.open(io.BytesIO(result))
       assert output_img.mode in ('RGBA', 'LA', 'PA')
   ```

4. **Property 4: High-Resolution Passthrough**
   ```python
   @given(
       dimension=st.integers(min_value=1000, max_value=4000)
   )
   def test_high_res_passthrough(dimension):
       """Feature: vector-first-logo-fidelity, Property 4: High-Resolution Passthrough"""
       # Create high-res image
       img = Image.new('RGB', (dimension, dimension), (255, 0, 0))
       original_bytes = io.BytesIO()
       img.save(original_bytes, format='PNG')
       original_data = original_bytes.getvalue()
       
       result = LogoRasterizer.prepare_for_vision(original_data, "image/png")
       
       # Should return identical bytes
       assert result == original_data
   ```

5. **Property 5: Exception Safety**
   ```python
   @given(
       logo_bytes=st.binary(min_size=0, max_size=10_000),
       mime_type=st.text(min_size=1, max_size=100)
   )
   def test_never_raises_exception(logo_bytes, mime_type):
       """Feature: vector-first-logo-fidelity, Property 5: Exception Safety"""
       # Should never raise, even with garbage input
       try:
           result = LogoRasterizer.prepare_for_vision(logo_bytes, mime_type)
           assert isinstance(result, bytes)
       except Exception as e:
           pytest.fail(f"Unexpected exception: {e}")
   ```

6. **Property 6: Independent Processing**
   ```python
   @given(
       logo_list=st.lists(
           st.tuples(
               st.binary(min_size=100, max_size=10_000),
               st.sampled_from(["image/png", "image/jpeg"])
           ),
           min_size=2,
           max_size=5
       )
   )
   def test_independent_processing(logo_list):
       """Feature: vector-first-logo-fidelity, Property 6: Independent Processing"""
       # Process each logo individually
       individual_results = [
           LogoRasterizer.prepare_for_vision(logo_bytes, mime_type)
           for logo_bytes, mime_type in logo_list
       ]
       
       # Process in different order
       shuffled_list = logo_list.copy()
       random.shuffle(shuffled_list)
       shuffled_results = [
           LogoRasterizer.prepare_for_vision(logo_bytes, mime_type)
           for logo_bytes, mime_type in shuffled_list
       ]
       
       # Results should be order-independent
       # (Compare by matching original inputs)
       for original_input, expected_output in zip(logo_list, individual_results):
           matching_output = shuffled_results[shuffled_list.index(original_input)]
           assert matching_output == expected_output
   ```

### Integration Testing

**Test Scenarios**:

1. **End-to-End Generation with SVG Logo**:
   - Upload brand with SVG logo
   - Trigger generation
   - Verify Vision Model receives high-res PNG
   - Verify generated image quality

2. **End-to-End Generation with Low-Res Raster Logo**:
   - Upload brand with 500px PNG logo
   - Trigger generation
   - Verify logo is upscaled to 2048px
   - Verify generated image quality

3. **Multiple Logos Processing**:
   - Upload brand with 3 different logos
   - Trigger generation
   - Verify all logos processed independently
   - Verify all logos appear in generated image

4. **Graceful Degradation with Malformed Logo**:
   - Upload brand with corrupted logo file
   - Trigger generation
   - Verify generation completes (doesn't crash)
   - Verify error logged appropriately

## Performance Considerations

### Processing Time Estimates

| Operation | Input Size | Expected Time | Notes |
|-----------|-----------|---------------|-------|
| SVG Rasterization | < 1MB | < 2 seconds | Depends on SVG complexity |
| Raster Upscaling | 500px → 2048px | < 1 second | Lanczos is fast |
| High-Res Passthrough | Any size | < 10ms | Just byte comparison |
| PIL Image Load | < 5MB | < 500ms | Memory-bound |

### Memory Usage

- **SVG Rasterization**: ~50MB peak (Cairo rendering buffer)
- **Raster Upscaling**: ~100MB peak (input + output buffers)
- **Total per logo**: ~150MB worst case
- **Multiple logos**: Processed sequentially (no parallel memory spike)

### Optimization Strategies

1. **Early Exit for High-Res Images**:
   - Check dimensions before loading full image
   - Saves ~500ms per high-res logo

2. **Sequential Processing**:
   - Process logos one at a time
   - Prevents memory spikes from parallel processing
   - Acceptable latency (< 5 seconds for 3 logos)

3. **No Caching**:
   - Logos may change between generations
   - Modal's fast compute makes caching unnecessary
   - Simplifies implementation

### Scalability

- **Concurrent Generations**: Each generation processes logos independently
- **Logo Count**: Linear scaling (O(n) where n = number of logos)
- **Logo Size**: Bounded by Supabase Storage limits (50MB per file)

## Deployment

### Modal Image Configuration

**File**: `mobius/app.py` (or equivalent Modal app definition)

**Required Changes**:

```python
from modal import Image, App

# Current image definition (example):
image = Image.debian_slim().pip_install(
    "fastapi",
    "langgraph",
    # ... other dependencies
)

# NEW image definition with Cairo support:
image = Image.debian_slim() \
    .apt_install("libcairo2")  # OS-level Cairo library \
    .pip_install(
        "fastapi",
        "langgraph",
        "cairosvg",  # Python SVG rasterization library
        # ... other dependencies
    )
```

### Dependency Versions

**pyproject.toml additions**:
```toml
dependencies = [
    # ... existing dependencies
    "cairosvg>=2.7.0",  # SVG to PNG conversion
    "pillow>=10.0.0",   # Already present, ensure version
]
```

### Verification Steps

1. **Build Verification**:
   ```bash
   modal deploy mobius/app.py
   # Check logs for successful libcairo2 installation
   ```

2. **Runtime Verification**:
   ```python
   # In Modal function:
   try:
       import cairosvg
       logger.info("cairosvg_available", version=cairosvg.__version__)
   except ImportError as e:
       logger.error("cairosvg_missing", error=str(e))
   ```

3. **Integration Test**:
   - Upload test brand with SVG logo
   - Trigger generation via API
   - Verify logs show "rasterizing_vector_logo"
   - Verify generated image quality

### Rollback Plan

If issues arise:

1. **Immediate**: Revert Modal image to previous version
2. **Temporary**: Comment out `LogoRasterizer` integration in Generate Node
3. **Fallback**: System continues with original low-res logos (degraded quality but functional)

### Monitoring

**Key Metrics**:
- Logo processing time (p50, p95, p99)
- Logo processing failures (count, error types)
- SVG rasterization success rate
- Memory usage during logo processing

**Alerts**:
- Logo processing time > 5 seconds (p95)
- Logo processing failure rate > 5%
- cairosvg import failures

## Migration Strategy

### Phase 1: Deploy Infrastructure (Week 1)

1. Update Modal image with libcairo2 and cairosvg
2. Deploy updated image to staging
3. Verify dependencies installed correctly
4. Run smoke tests

### Phase 2: Implement LogoRasterizer (Week 1)

1. Create `src/mobius/utils/media.py`
2. Implement `LogoRasterizer` class
3. Write unit tests
4. Write property-based tests
5. Achieve 100% test coverage

### Phase 3: Integrate with Generate Node (Week 2)

1. Update `src/mobius/nodes/generate.py`
2. Add MIME type detection from HTTP headers
3. Call `LogoRasterizer.prepare_for_vision()` for each logo
4. Write integration tests
5. Test on staging with real brand data

### Phase 4: Production Rollout (Week 2)

1. Deploy to production with feature flag (optional)
2. Monitor logs for errors
3. Compare generated image quality (before/after)
4. Gradually enable for all brands
5. Document results

### Backward Compatibility

- **API**: No changes to request/response schemas
- **Database**: No schema changes required
- **Existing Brands**: Work immediately with new processing
- **Existing Workflows**: Transparent upgrade (no code changes needed)

## Success Criteria

### Quality Metrics

1. **Logo Clarity**: Vision Model receives logos at >= 1000px resolution
2. **Aspect Ratio**: 100% of processed logos maintain original aspect ratio
3. **Transparency**: 100% of transparent logos preserve alpha channel
4. **Error Rate**: < 1% of logo processing operations fail

### Performance Metrics

1. **Processing Time**: p95 < 3 seconds per logo
2. **Memory Usage**: < 200MB peak per generation
3. **Workflow Impact**: < 5 seconds added to total generation time

### Operational Metrics

1. **Deployment Success**: Modal image builds without errors
2. **Dependency Availability**: cairosvg imports successfully in 100% of runs
3. **Graceful Degradation**: 0 generation failures due to logo processing errors

## Future Enhancements

### Potential Improvements

1. **Adaptive Resolution**:
   - Detect Vision Model's optimal input resolution
   - Adjust target_dim dynamically based on model version

2. **Format Detection**:
   - Use magic bytes instead of MIME type for more reliable detection
   - Support additional formats (TIFF, BMP, etc.)

3. **Parallel Processing**:
   - Process multiple logos concurrently
   - Requires careful memory management

4. **Caching Layer**:
   - Cache processed logos by hash
   - Requires cache invalidation strategy

5. **Quality Metrics**:
   - Measure logo sharpness before/after processing
   - Automatically adjust processing parameters

### Non-Goals

- **Real-time Processing**: Logos processed at generation time (not upload time)
- **Logo Editing**: No cropping, color adjustment, or other modifications
- **Format Conversion**: Always output PNG (no JPEG, WEBP, etc.)
- **Compression**: No file size optimization (quality over size)
