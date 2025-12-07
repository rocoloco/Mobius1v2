# Design Document: Gemini 3 Dual-Architecture Refactoring

## Overview

This design document specifies the refactoring of the Mobius backend to use Google's Gemini 3 model family with a dual-architecture approach. The system will replace the Flux/Ideogram image generation stack with Gemini 3's native image generation capabilities while maintaining separate, specialized models for reasoning and vision tasks.

### Key Design Decisions

1. **Dual-Model Architecture**: Use `gemini-3-pro-preview` for reasoning-intensive tasks (PDF parsing, compliance auditing) and `gemini-3-pro-image-preview` for image generation
2. **Compressed Digital Twin**: Optimize brand guidelines to fit within the 65k token context window of the Vision Model
3. **Unified Client**: Refactor GeminiClient to manage both model instances with automatic model selection
4. **Zero Breaking Changes**: Maintain API compatibility to avoid disrupting existing integrations
5. **Complete Fal.ai Removal**: Eliminate all external image generation dependencies

### Benefits

- **Simplified Architecture**: Single AI provider (Google) instead of multiple services
- **Cost Optimization**: Leverage Google's pricing and quota management
- **Better Integration**: Native multimodal capabilities without format conversions
- **Improved Reasoning**: Superior compliance auditing with Gemini 3's advanced reasoning
- **Reduced Latency**: Fewer network hops and service dependencies

## Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Mobius API Layer                        │
│  (FastAPI endpoints - unchanged interface)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph Workflows                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Ingestion   │  │  Generation  │  │    Audit     │     │
│  │   Workflow   │  │   Workflow   │  │   Workflow   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Unified Gemini Client                          │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │  Reasoning Model     │  │   Vision Model       │        │
│  │ gemini-3-pro-preview │  │ gemini-3-pro-image-  │        │
│  │                      │  │      preview         │        │
│  │ • PDF Parsing        │  │ • Image Generation   │        │
│  │ • Compliance Audit   │  │ • Style Transfer     │        │
│  │ • Multimodal Vision  │  │                      │        │
│  └──────────────────────┘  └──────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
          │                           │
          ▼                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Google Generative AI API                       │
└─────────────────────────────────────────────────────────────┘
```

### Workflow Changes

#### Ingestion Workflow (Before → After)

**Before:**
```
PDF Upload → Text Extraction → Visual Extraction → Structure → Database
                                (Gemini 2.5)
```

**After:**
```
PDF Upload → Compressed Extraction → Structure → Database
             (Reasoning Model)
```

#### Generation Workflow (Before → After)

**Before:**
```
Prompt → Fal.ai (Flux/Ideogram) → Image URL → Audit
```

**After:**
```
Prompt + Compressed Twin → Vision Model → Image URI → Audit
```

#### Audit Workflow (Before → After)

**Before:**
```
Image URL → Gemini 2.5 → Compliance Score
```

**After:**
```
Image URI → Reasoning Model (Multimodal) → Compliance Score
```

## Components and Interfaces

### 1. Configuration Module (`src/mobius/config.py`)

**Changes:**
- Add `REASONING_MODEL` constant
- Add `VISION_MODEL` constant
- Remove `fal_api_key` field
- Keep `gemini_api_key` field

**New Interface:**

```python
class Settings(BaseSettings):
    # API Keys
    gemini_api_key: str = ""
    supabase_url: str = ""
    supabase_key: str = ""
    
    # Model Configuration
    reasoning_model: str = "gemini-3-pro-preview"
    vision_model: str = "gemini-3-pro-image-preview"
    
    # Existing configuration...
    max_generation_attempts: int = 3
    compliance_threshold: float = 0.80
    # ...
```

### 2. Gemini Client (`src/mobius/tools/gemini.py`)

**Refactored Interface:**

```python
class GeminiClient:
    """Unified client for Gemini 3 model family."""
    
    def __init__(self):
        """Initialize both reasoning and vision model clients."""
        genai.configure(api_key=settings.gemini_api_key)
        self.reasoning_model = genai.GenerativeModel(settings.reasoning_model)
        self.vision_model = genai.GenerativeModel(settings.vision_model)
    
    async def extract_compressed_guidelines(
        self, 
        pdf_bytes: bytes
    ) -> CompressedDigitalTwin:
        """
        Extract compressed brand guidelines using Reasoning Model.
        
        Returns only essential visual rules optimized for Vision Model context.
        """
        pass
    
    async def generate_image(
        self,
        prompt: str,
        compressed_twin: CompressedDigitalTwin,
        **generation_params
    ) -> str:
        """
        Generate image using Vision Model with compressed brand context.
        
        Returns image_uri for downstream processing.
        """
        pass
    
    async def audit_compliance(
        self,
        image_uri: str,
        brand_guidelines: BrandGuidelines
    ) -> ComplianceScore:
        """
        Audit image compliance using Reasoning Model with multimodal vision.
        
        Uses full brand guidelines for comprehensive compliance checking.
        """
        pass
```

### 3. Compressed Digital Twin Model

**Design Philosophy: Semantic Color Hierarchy**

The Compressed Digital Twin must preserve semantic color roles to prevent the **"Confetti Problem"** - where colors are technically correct but aesthetically chaotic due to lack of usage hierarchy. Without semantic roles, the Vision Model might paint backgrounds in neon colors and text in light greys simply because both are "approved."

By capturing the semantic role of each color (primary, secondary, accent, neutral, semantic), we enable the Vision Model to understand HOW to use each color, not just THAT it's approved. This ensures generated images follow proper design principles like the 60-30-10 rule.

**New Data Model:**

```python
class CompressedDigitalTwin(BaseModel):
    """
    Optimized brand guidelines for Vision Model context window.
    
    Contains only essential visual rules to fit within 65k tokens.
    Preserves semantic color hierarchy to prevent the Confetti Problem.
    """
    
    # Semantic color hierarchy (ALL color roles preserved)
    primary_colors: List[str] = Field(description="Hex codes for dominant brand identity (logos, headers)")
    secondary_colors: List[str] = Field(description="Hex codes for supporting elements (shapes, icons)")
    accent_colors: List[str] = Field(description="Hex codes for high-visibility CTAs (buttons, links)")
    neutral_colors: List[str] = Field(description="Hex codes for backgrounds and body text")
    semantic_colors: List[str] = Field(description="Hex codes for functional states (success, error)")
    
    # Typography
    font_families: List[str] = Field(description="Font names only")
    
    # Critical constraints (concise rules)
    visual_dos: List[str] = Field(description="Positive visual rules")
    visual_donts: List[str] = Field(description="Negative visual rules")
    
    # Logo requirements (essential only)
    logo_placement: Optional[str] = Field(description="Placement rule")
    logo_min_size: Optional[str] = Field(description="Minimum size")
    
    def estimate_tokens(self) -> int:
        """Estimate token count for context window validation."""
        pass
    
    def validate_size(self) -> bool:
        """Ensure compressed twin fits within 60k token limit."""
        pass
```

### 4. Node Refactoring

#### Ingestion Node (`src/mobius/nodes/extract_visual.py`)

**Changes:**
- Use `reasoning_model` instead of generic model
- Extract `CompressedDigitalTwin` in addition to full `BrandGuidelines`
- Store both representations in database

#### Generation Node (New: `src/mobius/nodes/generate.py`)

**New Implementation:**

```python
async def generate_node(state: JobState) -> dict:
    """
    Generate image using Vision Model with compressed brand context.
    """
    client = GeminiClient()
    
    # Load compressed twin from brand
    compressed_twin = await load_compressed_twin(state["brand_id"])
    
    # Generate with Vision Model
    image_uri = await client.generate_image(
        prompt=state["prompt"],
        compressed_twin=compressed_twin,
        **state.get("generation_params", {})
    )
    
    return {
        "current_image_url": image_uri,
        "attempt_count": state["attempt_count"] + 1,
        "status": "generated"
    }
```

#### Audit Node (`src/mobius/nodes/audit.py`)

**Changes:**
- Use `reasoning_model` explicitly
- Accept `image_uri` instead of downloading from URL
- Use full `BrandGuidelines` for comprehensive auditing

## Data Models

### Semantic Color Hierarchy: Preventing the Confetti Problem

**The Problem:**
If we store brand colors as a flat list of approved hex codes, the Vision Model knows THAT colors are approved but not HOW they should be used. This leads to the "Confetti Problem" - generated images that are technically on-brand (correct colors) but aesthetically unusable (chaotic distribution). For example, the model might paint backgrounds in neon green and body text in light grey simply because both are "approved."

**The Solution:**
We implement semantic design tokens that capture the functional role of each color:

- **Primary**: Dominant brand identity (logos, headers) - 30% of visual space
- **Secondary**: Supporting elements (shapes, icons) - 30% of visual space  
- **Accent**: High-visibility CTAs (buttons, links) - 10% of visual space (use sparingly!)
- **Neutral**: Backgrounds, body text (white, black, greys) - 60% of visual space
- **Semantic**: Functional states (success green, error red) - contextual use only

This enables the Vision Model to follow the **60-30-10 design rule** for proper visual hierarchy, ensuring generated images are both on-brand AND aesthetically professional.

**Implementation:**
The Reasoning Model must infer color roles during PDF ingestion by analyzing:
1. Explicit labels in the PDF ("Primary Color", "Brand Colors", etc.)
2. Visual usage patterns (colors used for headers = primary, backgrounds = neutral)
3. Surface area coverage (dominant colors = primary/neutral, sparse colors = accent)

### Color Model with Usage Weight

The `Color` model has been enhanced to support semantic design tokens:

```python
class Color(BaseModel):
    name: str  # e.g., "Midnight Blue"
    hex: str   # e.g., "#0057B8"
    usage: Literal["primary", "secondary", "accent", "neutral", "semantic"]
    usage_weight: float  # 0.0 to 1.0 - estimated usage frequency in source PDF
    context: Optional[str]  # Additional usage constraints
```

**Key Fields:**
- `usage`: Semantic role that tells the Vision Model HOW to use the color
- `usage_weight`: Enables enforcement of the 60-30-10 design rule by capturing how much surface area this color covers in the reference PDF

**Inference Strategy:**
During PDF ingestion, the Reasoning Model estimates `usage_weight` by:
1. Analyzing visual prominence (header colors get higher weight than accent colors)
2. Measuring surface area coverage across PDF pages
3. Identifying dominant vs. sparse color usage patterns

This weight information is then used during generation to ensure proper visual hierarchy.

### Semantic Color Mapping Rules: The "Rosetta Stone"

The Reasoning Model must normalize unstructured PDF terminology into our strict semantic color roles. These mapping rules ensure consistent interpretation across diverse brand guidelines:

**1. Mapping to PRIMARY (Identity)**
- **Logic**: The core brand color used for identity
- **Trigger Terms**: "Primary", "Core", "Dominant", "Main", "Master Brand", "Logo Color", "Brand Identity"
- **Visual Clue**: If no text exists, select the color used for the largest headlines or the logo itself

**2. Mapping to SECONDARY (Support)**
- **Logic**: Supports the primary but doesn't dominate
- **Trigger Terms**: "Secondary", "Supporting", "Complementary", "Palette B", "Pattern", "Graphic Elements", "Shapes"

**3. Mapping to ACCENT (Action)**
- **Logic**: High visibility, low frequency - drives user behavior
- **Trigger Terms**: "Accent", "Highlight", "Spot Color", "CTA", "Call to Action", "Button", "Link", "Hyperlink", "Interaction", "Pop", "Focus"
- **Example**: If PDF says "Use Heritage Gold for CTAs" → map to ACCENT

**4. Mapping to NEUTRAL (Canvas)**
- **Logic**: The structure and whitespace
- **Trigger Terms**: "Neutral", "Background", "Base", "Canvas", "Paper", "Text", "Body Copy", "Typography Color", "Negative Space", "Whitespace"
- **Critical Rule**: If PDF lists "Typography Colors" (e.g., Dark Charcoal), map to NEUTRAL, NOT Primary

**5. Mapping to SEMANTIC (Functional)**
- **Logic**: UI state indicators
- **Trigger Terms**: "Success", "Error", "Warning", "Alert", "Info", "System Status", "Validation"

**Conflict Resolution:**
If a color fits multiple categories (e.g., "Primary Background"), prioritize by usage surface area:
- High surface area (backgrounds) → NEUTRAL or PRIMARY
- Low surface area (buttons, links) → ACCENT

**Implementation in Extraction Prompt:**
The `extract_brand_guidelines()` method in GeminiClient must include these mapping rules in its prompt to ensure the Reasoning Model correctly categorizes colors during PDF ingestion.

### CompressedDigitalTwin Schema

```json
{
  "primary_colors": ["#0057B8", "#1E3A8A"],
  "secondary_colors": ["#FF5733", "#C70039"],
  "accent_colors": ["#FFC300", "#00D9FF"],
  "neutral_colors": ["#FFFFFF", "#F5F5F5", "#333333"],
  "semantic_colors": ["#10B981", "#EF4444"],
  "font_families": ["Helvetica Neue", "Georgia"],
  "visual_dos": [
    "Use primary colors for headers and logos",
    "Maintain 2:1 contrast ratio",
    "Center logo in compositions",
    "Follow 60-30-10 rule: 60% neutral, 30% primary/secondary, 10% accent"
  ],
  "visual_donts": [
    "Never use Comic Sans",
    "Avoid red on green combinations",
    "Do not distort logo aspect ratio",
    "Never use accent colors for backgrounds"
  ],
  "logo_placement": "top-left or center",
  "logo_min_size": "100px width"
}
```

### Brand Entity Update

```python
class Brand(BaseModel):
    # Existing fields...
    guidelines: BrandGuidelines  # Full guidelines
    compressed_twin: CompressedDigitalTwin  # New field for generation
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Dual Model Initialization

*For any* GeminiClient instantiation, both reasoning_model and vision_model attributes should be initialized and non-null.

**Validates: Requirements 1.3, 6.1**

### Property 2: Reasoning Model for PDF Processing

*For any* PDF ingestion request, the system should use the reasoning_model instance (gemini-3-pro-preview) to extract brand guidelines.

**Validates: Requirements 2.1, 6.2**

### Property 3: Compressed Twin Structure

*For any* brand guidelines extraction, the resulting Compressed Digital Twin should contain only hex color codes, font family names, logo usage rules, and critical visual constraints, excluding verbose descriptions and historical context.

**Validates: Requirements 2.2, 2.3**

### Property 4: Token Limit Compliance

*For any* Compressed Digital Twin serialization, the JSON representation should be under 60,000 tokens.

**Validates: Requirements 2.4**

### Property 5: Compressed Twin Persistence

*For any* successful brand extraction, the Compressed Digital Twin should be stored in the Brand Entity database record.

**Validates: Requirements 2.5**

### Property 6: Vision Model for Generation

*For any* image generation request, the system should use the vision_model instance (gemini-3-pro-image-preview) to generate images.

**Validates: Requirements 3.1, 6.3**

### Property 7: Compressed Twin Injection

*For any* image generation, the Compressed Digital Twin should be present in the system prompt sent to the Vision Model.

**Validates: Requirements 3.2**

### Property 8: Image URI Return Format

*For any* successful image generation, the system should return an image_uri string that references the generated image.

**Validates: Requirements 3.3**

### Property 9: Generation Retry Behavior

*For any* failed image generation, the system should retry up to 3 times with exponential backoff before returning an error.

**Validates: Requirements 3.4**

### Property 10: Reasoning Model for Auditing

*For any* compliance audit request, the system should use the reasoning_model instance (gemini-3-pro-preview) to evaluate compliance.

**Validates: Requirements 4.1, 6.4**

### Property 11: Image URI Multimodal Input

*For any* audit operation, the image_uri from the Generation Node should be passed as multimodal input to the Reasoning Model.

**Validates: Requirements 4.2**

### Property 12: Full Guidelines in Audit Context

*For any* audit operation, the full Brand Guidelines (not the compressed twin) should be provided as context to the Reasoning Model.

**Validates: Requirements 4.3**

### Property 13: Structured Compliance Output

*For any* completed audit, the system should return a structured compliance score containing category breakdowns and violation details.

**Validates: Requirements 4.4**

### Property 14: API Schema Compatibility

*For any* API endpoint, the request and response schemas should match the pre-refactoring schemas exactly.

**Validates: Requirements 7.1**

### Property 15: Generation Request Compatibility

*For any* generation request using the pre-refactoring format, the system should process it successfully using the new Gemini architecture.

**Validates: Requirements 7.2**

### Property 16: Audit Response Compatibility

*For any* audit operation, the compliance score structure should match the pre-refactoring format.

**Validates: Requirements 7.3**

### Property 17: Ingestion Response Compatibility

*For any* brand ingestion operation, the Brand Entity data should match the pre-refactoring format.

**Validates: Requirements 7.4**

### Property 18: Error Logging Completeness

*For any* Gemini API failure, the error log should contain the model name, operation type, and error details.

**Validates: Requirements 9.1**

### Property 19: Timeout Retry Behavior

*For any* image generation timeout, the system should log the timeout and retry with increased timeout values.

**Validates: Requirements 9.4**

### Property 20: Graceful Audit Degradation

*For any* audit analysis failure, the system should return a partial compliance score with error annotations rather than failing completely.

**Validates: Requirements 9.5**

### Property 21: Configuration Validation

*For any* configuration loading, the system should validate that gemini_api_key is present and non-empty.

**Validates: Requirements 1.4**

## Error Handling

### Error Categories

1. **Configuration Errors**
   - Missing or invalid `gemini_api_key`
   - Invalid model names
   - **Handling**: Fail fast at startup with clear error messages

2. **API Errors**
   - Rate limit exceeded (429)
   - Authentication failure (401)
   - Service unavailable (503)
   - **Handling**: Exponential backoff with retry, log detailed error context

3. **Token Limit Errors**
   - Compressed Digital Twin exceeds 60k tokens
   - **Handling**: Iteratively compress further, flag for manual review if still too large

4. **Generation Errors**
   - Image generation timeout
   - Content policy violation
   - **Handling**: Retry with adjusted parameters, return partial results if possible

5. **Audit Errors**
   - Multimodal input processing failure
   - Incomplete compliance analysis
   - **Handling**: Return partial compliance score with error annotations

### Error Response Format

```python
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]]
    request_id: str
    retry_after: Optional[int]  # For rate limit errors
```

### Logging Strategy

All errors should be logged with structured logging including:
- `model_name`: Which Gemini model was being used
- `operation_type`: "pdf_parsing", "image_generation", "compliance_audit"
- `error_type`: Category of error
- `error_details`: Full error message and stack trace
- `request_id`: For distributed tracing
- `brand_id`: For context (if available)

## Testing Strategy

### Unit Testing

Unit tests will verify:
1. **Configuration Loading**: Correct model names are loaded from settings
2. **Client Initialization**: Both model instances are created properly
3. **Model Selection**: Correct model is used for each operation type
4. **Error Handling**: Appropriate exceptions are raised and logged
5. **Data Validation**: Compressed Digital Twin structure and token limits

### Property-Based Testing

Property-based tests will use the Hypothesis library to verify:

1. **Property 4: Token Limit Compliance**
   - Generate random Compressed Digital Twins
   - Verify all serializations are under 60k tokens
   - Test with edge cases (maximum colors, fonts, rules)

2. **Property 9: Generation Retry Behavior**
   - Simulate random generation failures
   - Verify retry count is exactly 3
   - Verify exponential backoff timing

3. **Property 14-17: API Compatibility**
   - Generate random valid requests in old format
   - Verify responses match old schema exactly
   - Test with various parameter combinations

4. **Property 18: Error Logging Completeness**
   - Simulate random API failures
   - Verify all required fields are present in logs
   - Test with different error types

5. **Property 20: Graceful Audit Degradation**
   - Simulate random audit failures
   - Verify partial scores are always returned
   - Verify error annotations are present

### Integration Testing

Integration tests will verify:
1. **End-to-End Ingestion**: PDF → Compressed Twin → Database
2. **End-to-End Generation**: Prompt → Vision Model → Image URI
3. **End-to-End Audit**: Image URI → Reasoning Model → Compliance Score
4. **Full Workflow**: Ingestion → Generation → Audit → Correction Loop

### Migration Testing

Migration tests will verify:
1. **Backward Compatibility**: Old API clients work without changes
2. **Data Migration**: Existing brands work with new architecture
3. **Performance**: Response times are comparable or better
4. **Cost**: API costs are tracked and compared

## Deployment Strategy

### Phase 1: Preparation (Week 1)
- Update configuration with new model constants
- Refactor GeminiClient with dual model support
- Implement CompressedDigitalTwin model
- Write unit tests for new components

### Phase 2: Node Refactoring (Week 2)
- Refactor Ingestion Node to use Reasoning Model
- Implement new Generation Node with Vision Model
- Update Audit Node to use Reasoning Model explicitly
- Write integration tests for each node

### Phase 3: Fal.ai Removal (Week 3)
- Remove all Fal.ai imports and calls
- Remove fal-client from dependencies
- Update configuration to remove fal_api_key
- Search and remove all "fal" references

### Phase 4: Testing & Validation (Week 4)
- Run full test suite (unit, property, integration)
- Perform load testing with both architectures
- Validate API compatibility with existing clients
- Compare costs and performance metrics

### Phase 5: Documentation & Deployment (Week 5)
- Update MOBIUS-ARCHITECTURE.md
- Update API documentation
- Update deployment guides
- Deploy to staging environment
- Monitor for 1 week before production

### Rollback Plan

If issues are discovered:
1. Revert to previous version using git
2. Restore Fal.ai dependencies if needed
3. Switch configuration back to old model names
4. Notify stakeholders of rollback

## Performance Considerations

### Token Optimization

The Compressed Digital Twin must fit within 60k tokens. Optimization strategies:

1. **Color Compression**: Store only hex codes, not names or descriptions
2. **Font Compression**: Store only family names, not weights or detailed usage
3. **Rule Compression**: Use concise bullet points, not full sentences
4. **Exclusions**: Remove all historical context, brand story, and verbose descriptions

### Latency Optimization

1. **Parallel Processing**: Run text and visual extraction in parallel during ingestion
2. **Caching**: Cache Compressed Digital Twins in memory for frequently used brands
3. **Batch Processing**: Process multiple audit categories in a single API call
4. **Connection Pooling**: Reuse HTTP connections to Google API

### Cost Optimization

1. **Model Selection**: Use cheaper Reasoning Model for auditing (better reasoning, lower cost than Vision Model)
2. **Token Minimization**: Compressed Digital Twin reduces input tokens for generation
3. **Retry Strategy**: Exponential backoff prevents excessive retry costs
4. **Monitoring**: Track API usage and costs per operation type

## Security Considerations

### API Key Management

1. **Secret Storage**: Store `gemini_api_key` in Modal secrets or environment variables
2. **Key Rotation**: Support key rotation without downtime
3. **Access Control**: Limit API key access to authorized services only

### Data Privacy

1. **PDF Content**: Brand guidelines may contain confidential information
2. **Image Content**: Generated images may contain sensitive brand assets
3. **Audit Logs**: Compliance scores may reveal brand strategy

**Mitigation**:
- Encrypt PDFs at rest in Supabase Storage
- Use signed URLs with expiration for image access
- Implement audit log retention policies

### Rate Limiting

1. **Google API Limits**: Respect Gemini API rate limits
2. **Client Rate Limiting**: Implement per-client rate limits to prevent abuse
3. **Backoff Strategy**: Use exponential backoff to avoid thundering herd

## Monitoring and Observability

### Key Metrics

1. **Model Usage**:
   - Reasoning Model API calls per hour
   - Vision Model API calls per hour
   - Average tokens per request by model

2. **Performance**:
   - PDF extraction latency (p50, p95, p99)
   - Image generation latency (p50, p95, p99)
   - Audit latency (p50, p95, p99)

3. **Quality**:
   - Compressed Twin token count distribution
   - Compliance score distribution
   - Retry rate by operation type

4. **Errors**:
   - API error rate by error type
   - Timeout rate by operation
   - Partial result rate for audits

### Logging

Use structured logging with:
- `model_name`: Which model was used
- `operation_type`: Type of operation
- `latency_ms`: Operation duration
- `token_count`: Input/output tokens
- `success`: Boolean success indicator
- `error_type`: If failed, error category

### Alerting

Set up alerts for:
- API error rate > 5%
- Average latency > 10 seconds
- Compressed Twin token count > 55k (warning threshold)
- Rate limit errors > 10 per hour

## Migration Path

### Existing Brands

Brands ingested with the old architecture need migration:

1. **Lazy Migration**: Re-extract Compressed Digital Twin on first generation request
2. **Batch Migration**: Background job to re-process all existing brands
3. **Fallback**: If Compressed Twin missing, use full guidelines (may hit token limits)

### API Clients

No changes required for API clients:
- Request schemas remain identical
- Response schemas remain identical
- Endpoint URLs remain identical
- Authentication remains identical

### Database Schema

Add new field to brands table:
```sql
ALTER TABLE brands 
ADD COLUMN compressed_twin JSONB;
```

This is a non-breaking change (nullable field).

## Future Enhancements

### Phase 2 Improvements

1. **Adaptive Compression**: Dynamically adjust compression based on brand complexity
2. **Multi-Model Generation**: Use multiple Vision Model variants for different asset types
3. **Streaming Responses**: Stream image generation progress to clients
4. **Fine-Tuning**: Fine-tune models on brand-specific data for better compliance

### Advanced Features

1. **Style Transfer**: Use Vision Model for brand-consistent style transfer
2. **Batch Generation**: Generate multiple variations in parallel
3. **A/B Testing**: Compare compliance scores across model versions
4. **Cost Optimization**: Automatically select cheapest model that meets quality threshold
