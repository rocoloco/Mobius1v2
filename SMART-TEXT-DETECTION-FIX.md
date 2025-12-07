# Smart Text Detection Fix

## Problem

The previous fix was too aggressive - it prevented ALL text from being added to images, even when users explicitly requested it for ads, posters, or marketing materials.

## Solution: Intent-Based Text Detection

Implemented smart detection that analyzes the user's prompt to determine if they want text in the image.

### How It Works

#### 1. Keyword Detection

The system checks for text-related keywords in the user's prompt:
- `text`, `headline`, `caption`, `slogan`, `tagline`, `copy`
- `words`, `saying`, `quote`, `message`
- `ad`, `advertisement`, `banner`, `poster`

#### 2. Conditional System Prompt

**If user WANTS text** (keywords detected):
```
## CRITICAL CONSTRAINTS:
- If text/copy is requested, use ONLY the approved brand fonts
- Ensure text colors follow brand palette and meet WCAG contrast standards
- Keep text concise and aligned with brand voice
- DO NOT add text unless explicitly requested by the user
```

**If user DOES NOT want text** (no keywords):
```
## CRITICAL CONSTRAINTS:
- Generate PHOTOGRAPHIC images only - no text overlays, headlines, or marketing copy
- DO NOT add any text, slogans, taglines, or written content to the image
- Focus on the visual scene described in the user prompt
```

#### 3. Prompt Optimization Awareness

The prompt optimizer also receives the text intent flag and adjusts accordingly:

**With text intent**:
- Preserves user's request for text
- Adds typography guidance (approved fonts)
- Ensures brand voice compliance

**Without text intent**:
- Focuses on photographic scene
- Removes any accidental text instructions
- Emphasizes visual elements only

### Example Scenarios

#### Scenario 1: Pure Photo (No Text)
**User Prompt**: "a professional photo of a woman drinking from a water bottle after a long run"

**Detection**: `user_wants_text=False`

**Result**: Pure photographic scene, no text overlays

---

#### Scenario 2: Marketing Ad (With Text)
**User Prompt**: "create an ad with the headline 'Stay Hydrated' showing a woman with a water bottle"

**Detection**: `user_wants_text=True` (keywords: "ad", "headline")

**Result**: Image with "Stay Hydrated" text using approved brand fonts

---

#### Scenario 3: Social Media Post (With Text)
**User Prompt**: "a poster for Instagram with text saying 'Refresh Your Run' and our logo"

**Detection**: `user_wants_text=True` (keywords: "poster", "text", "saying")

**Result**: Poster-style image with the requested text

---

#### Scenario 4: Product Shot (No Text)
**User Prompt**: "a product shot of our water bottle on a wooden table"

**Detection**: `user_wants_text=False`

**Result**: Clean product photo, no text

## Implementation Details

### Files Changed

1. **`src/mobius/tools/gemini.py`**
   - Added `user_wants_text` detection in `optimize_prompt()`
   - Added `allow_text` parameter to `_build_generation_system_prompt()`
   - Added `original_prompt` parameter to `generate_image()`
   - Made system prompt conditional based on text intent

2. **`src/mobius/nodes/generate.py`**
   - Pass `original_prompt` to `generate_image()`
   - Added logging for prompt optimization results

### Logging Enhancements

New log entries for debugging:

```python
# In optimize_prompt()
[info] prompt_analysis user_wants_text=True/False

# In generate_image()
[info] generating_image user_wants_text=True/False

# In generate_node()
[info] prompt_optimization_complete 
       original_prompt="..." 
       optimized_prompt="..."
```

## Testing

### Test 1: Photo Without Text
```bash
python scripts/test_generation.py <brand_id> "a professional photo of a woman drinking from a water bottle"
```

**Expected**:
- `user_wants_text=False` in logs
- No text overlays in image
- Pure photographic scene

### Test 2: Ad With Text
```bash
python scripts/test_generation.py <brand_id> "create an ad with headline 'Stay Hydrated' showing a woman with a water bottle"
```

**Expected**:
- `user_wants_text=True` in logs
- "Stay Hydrated" text appears in image
- Text uses approved brand fonts

### Test 3: Poster With Text
```bash
python scripts/test_generation.py <brand_id> "a poster with text 'Refresh Your Run' and our logo on a water bottle"
```

**Expected**:
- `user_wants_text=True` in logs
- "Refresh Your Run" text appears
- Logo is visible and undistorted

## Monitoring

After deployment, check logs for:

1. **Text Intent Detection**:
   ```
   [info] prompt_analysis user_wants_text=True/False
   ```

2. **Optimized Prompts**:
   ```
   [info] prompt_optimization_complete 
          original_prompt="..." 
          optimized_prompt="..."
   ```

3. **Generation Parameters**:
   ```
   [info] generating_image user_wants_text=True/False
   ```

## Edge Cases

### What if keywords are ambiguous?

Example: "a photo of a text message on a phone screen"

- Contains "text" but refers to SMS messages, not overlay text
- Current implementation would detect `user_wants_text=True`
- The optimizer should clarify intent: "showing a phone displaying a text message"
- The model should understand this is part of the scene, not an overlay

### What if user wants SOME text but not overlays?

Example: "a photo of a billboard with our ad on it"

- Contains "ad" → `user_wants_text=True`
- But the text should be ON the billboard in the scene, not as an overlay
- The optimizer should clarify: "featuring a billboard displaying the brand ad"
- This is correct behavior - the text is part of the photographic scene

## Future Improvements

1. **More sophisticated NLP**: Use the reasoning model to analyze intent rather than keyword matching
2. **User preferences**: Allow users to set default text behavior per brand
3. **Feedback loop**: Learn from audit results and user feedback to improve detection
4. **Explicit flags**: Add optional `include_text: bool` parameter to generation API

## Rollback

If issues occur, the system gracefully degrades:
- If text detection fails, defaults to `user_wants_text=False` (safer)
- If prompt optimization fails, uses original prompt
- All changes are backward compatible
