# Text Overlay and Logo Distortion Fix

## Problems

After fixing the logo URL issue, two new problems emerged:

1. **Unwanted Text Overlays**: The model added marketing text ("REFRESH YOUR RUN", "Stay hydrated with Evergreen Naturals") even though the user only requested a photo
2. **Distorted Logo on Product**: The logo on the water bottle was warped/distorted due to the curved surface, violating brand guidelines

## Root Cause

The system prompt for image generation didn't explicitly constrain the model from:
- Adding text overlays, headlines, or marketing copy
- Wrapping logos around curved surfaces (causing distortion)

The model interpreted "brand-compliant image generator" as creating full marketing materials with headlines and copy, rather than just photographic scenes.

## Solution

### 1. Updated System Prompt (`src/mobius/tools/gemini.py`)

Added explicit constraints to the image generation system prompt:

```python
## CRITICAL CONSTRAINTS:
- Generate PHOTOGRAPHIC images only - no text overlays, headlines, or marketing copy
- DO NOT add any text, slogans, taglines, or written content to the image
- Focus on the visual scene described in the user prompt
- Follow the 60-30-10 design rule: 60% neutral, 30% primary/secondary, 10% accent
```

### 2. Enhanced Logo Usage Guidelines

Updated logo placement instructions to prevent distortion:

```python
## Logo Usage:
- Brand logo images are provided as reference
- Use the provided logo(s) in the generated image when appropriate
- Maintain logo integrity - do not distort, recolor, or modify the logo design
- When placing logos on products (bottles, packaging, etc.), apply them as FLAT overlays that maintain proper proportions
- DO NOT wrap logos around curved surfaces or apply perspective distortion
- If a product surface is curved, place the logo on a flat label area or use a straight-on angle
```

### 3. Updated Prompt Optimization

Added constraints to the prompt optimization phase to prevent text instructions:

```python
## CRITICAL CONSTRAINTS:
- The output should describe a PHOTOGRAPHIC SCENE ONLY
- DO NOT include instructions to add text, headlines, slogans, or marketing copy
- DO NOT mention adding taglines, captions, or written content
- Focus purely on the visual elements, composition, lighting, and colors
- When logos are mentioned, describe them as physical elements in the scene (e.g., "on the product") not as overlays
```

## Expected Results

After these changes, when generating images:

1. **No Text Overlays**: The model will generate pure photographic scenes without adding headlines, slogans, or marketing copy
2. **Flat Logo Placement**: Logos on products will be applied as flat overlays or on flat surfaces, preventing distortion
3. **Better Compliance**: The audit node should score higher on logo_usage category

## Testing

To verify the fix:

1. Deploy the updated code to Modal
2. Run a new generation with the same prompt:
   ```
   "a professional photo of a woman drinking from a water bottle after a long run in the city. the water bottle has our logo on it"
   ```
3. Check that:
   - No text overlays appear in the image
   - The logo on the bottle is flat and undistorted
   - The audit score for logo_usage improves

## Deployment

```bash
# Deploy to Modal
modal deploy src/mobius/api/app_consolidated.py
```

## Files Changed

- `src/mobius/tools/gemini.py` - Updated system prompt and prompt optimization constraints
