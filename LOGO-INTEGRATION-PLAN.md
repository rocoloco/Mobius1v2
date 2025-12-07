# Logo Integration & Prompt Optimization Plan

## Issues Identified

1. **No Prompt Optimization**: User prompts go directly to Vision Model without enhancement
2. **Logo Not Used**: Brand logos stored in Supabase but not passed to image generation
3. **Logo Manipulation**: Need strategy for lifestyle photos with logos

## Proposed Solutions

### 1. Prompt Optimization (Immediate Implementation)

**Add Reasoning Model pre-processing step:**

```
User Prompt → Reasoning Model (optimize) → Vision Model (generate) → Image
```

**Benefits:**
- Translates vague prompts into specific, brand-compliant instructions
- Adds color hex codes automatically
- Clarifies creative intent while maintaining brand compliance
- Example: "cool tech startup logo" → "minimalist geometric logo featuring #2E5984 (primary), with clean sans-serif typography, professional modern aesthetic"

**Implementation:**
- Add `optimize_prompt()` method to GeminiClient
- Call before `generate_image()` in generation workflow
- Log both original and optimized prompts

### 2. Logo Integration (Two Approaches)

#### Approach A: Multi-modal Input to Vision Model (Recommended for December 2025)

**How it works:**
```python
# Pass both text prompt AND logo image to Vision Model
result = vision_model.generate_content([
    text_prompt,
    {"mime_type": "image/png", "data": logo_bytes},  # Brand logo
    additional_context
])
```

**Pros:**
- Single-step generation
- Vision Model can naturally integrate logo into scene
- Handles perspective, lighting, shadows automatically
- Gemini 3 Pro Image supports multi-modal input

**Cons:**
- Less predictable logo placement
- May distort or modify logo
- Quality depends on model capabilities

#### Approach B: Post-Processing Compositing (Most Reliable)

**How it works:**
```
1. Generate base lifestyle image (without logo)
2. Use separate tool to composite logo onto image
   - Stability AI inpainting API
   - Adobe Firefly API
   - OpenCV/Pillow for simple overlay
3. Adjust for perspective, size, lighting
```

**Pros:**
- Pixel-perfect logo preservation
- Precise control over placement
- No risk of logo distortion
- Better for regulated industries

**Cons:**
- Two-step process
- Additional API costs
- More complex workflow

#### Approach C: Hybrid (Best of Both)

**Workflow:**
```
1. Reasoning Model identifies optimal logo placement
   Input: "water bottle product shot"
   Output: "Place logo centered on front of bottle, 30% of bottle height"

2. Vision Model generates base image with logo guidelines

3. Optional: Post-process for pixel-perfect results if needed
```

**Pros:**
- Leverages AI for creative decisions
- Maintains quality control
- Flexible based on use case

### 3. Recommended Implementation Order

**Phase 1: Prompt Optimization** (2-4 hours)
- Add `optimize_prompt()` method
- Update `generate_node()` to call optimizer
- Add logging for audit trail
- Deploy and test

**Phase 2: Logo Multi-modal Input** (4-6 hours)
- Update `generate_image()` to accept `logo_bytes` parameter
- Fetch logo from storage during generation
- Pass logo to Vision Model as additional input
- Test with various prompts ("water bottle with our logo", "t-shirt mockup")

**Phase 3: Post-Processing (Optional, 8-12 hours)
- Add compositing service (Stability AI or custom)
- Create `composite_logo()` method
- Add workflow decision logic (when to use post-processing)
- Test with complex scenarios

## Current Limitations to Address

### Logo Storage Access

Current state:
- Logos uploaded to Supabase Storage during ingestion
- Logo URL stored in `BrandGuidelines.logos[].url`
- **Not currently fetched during generation**

Need to add:
```python
# In generate_node.py
logo_urls = [logo.url for logo in brand.guidelines.logos]
logo_bytes_list = []
for url in logo_urls:
    # Download from Supabase Storage
    logo_bytes = await storage_client.download(url)
    logo_bytes_list.append(logo_bytes)
```

### Vision Model Capabilities Check

Before implementing, verify:
- Does Gemini 3 Pro Image support multi-modal input with reference images?
- What's the image size limit for reference inputs?
- Can it handle multiple logos (primary, alternate, icon)?

**Action:** Test with Gemini API documentation or example code

## Best Practices for Logo Integration

### When to Use Each Approach

**Use Multi-modal (Approach A) for:**
- Lifestyle photography (logo on products in natural scenes)
- Social media content
- Marketing materials where creative freedom is valued
- Quick iterations

**Use Post-processing (Approach B) for:**
- Legal documents
- Regulated industries (financial, healthcare)
- Exact brand compliance required
- Print materials

**Use Hybrid (Approach C) for:**
- High-value campaigns
- Client presentations
- When budget allows for quality control

### Logo Manipulation Best Practices (December 2025)

1. **Preserve Vector Format When Possible**
   - Request SVG logos during ingestion
   - Convert to high-res PNG only when needed
   - Maintain aspect ratio always

2. **Use AI-Powered Perspective Correction**
   - Tools like Adobe Firefly can apply realistic perspective
   - Better than simple transforms for product shots

3. **Consider Logo Variants**
   - Primary logo for light backgrounds
   - Alternate logo for dark backgrounds
   - Icon-only version for small spaces
   - Store all variants in brand storage

4. **Lighting and Shadow Integration**
   - If using post-processing, add shadows/highlights to match scene
   - Gemini may handle this automatically in multi-modal

## Next Steps

1. **Decide on approach**: Multi-modal, Post-processing, or Hybrid?
2. **Implement Phase 1** (Prompt Optimization) first - low risk, high value
3. **Test logo multi-modal** with Gemini 3 Pro Image
4. **Based on results**, proceed with Phase 2 or evaluate post-processing tools

## Questions for Discussion

1. How critical is pixel-perfect logo reproduction vs. natural integration?
2. What's the budget for additional APIs (Stability AI, Adobe)?
3. Are there specific use cases prioritized (social media vs. print)?
4. Should we support multiple logo variants simultaneously?

