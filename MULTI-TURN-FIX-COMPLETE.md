# Multi-Turn Tweak Fix - Complete Implementation

## Changes Made

### 1. Fixed Tweak Handler to Preserve State

**File:** `src/mobius/api/routes.py` - `tweak_completed_job_handler()`

**Key Changes:**
- Load existing job state from database
- Preserve `session_id` for multi-turn conversation
- Increment `attempt_count` to trigger multi-turn mode
- Resume workflow with existing state instead of creating new workflow
- Update job status in database after workflow completes

**Before:**
```python
# Created fresh workflow - lost all session context
asyncio.create_task(
    run_generation_workflow(
        brand_id=job.brand_id,
        prompt=prompt,
        job_id=job_id,
    )
)
```

**After:**
```python
# Resume workflow with existing state - preserves session
workflow = create_generation_workflow()
final_state = await workflow.ainvoke(state)  # Uses existing state!

# Update job in database
await job_storage.update_job(job_id, {
    "status": final_state.get("status", "completed"),
    "progress": 100.0,
    "state": final_state
})
```

### 2. Removed Broken Job Status Updates

**File:** `src/mobius/graphs/generation.py` - `complete_node()` and `failed_node()`

**Issue:** Using `asyncio.create_task()` in sync functions caused `'no running event loop'` error

**Solution:** Removed the database update code from nodes. The job status is now updated by the workflow runner (`resume_workflow()` in the tweak handler).

## How Multi-Turn Now Works

### First Generation (attempt_count=0)
```
User: "Generate a t-shirt design"
↓
generate_node checks:
  - attempt_count = 0
  - session_id = None
  - continue_conversation = False
↓
Creates NEW session:
  - session = vision_model.start_chat()
  - session_id = job_id
  - Stores in state
↓
Generates image from scratch
```

### Tweak (attempt_count=2+)
```
User: "Zoom out to show the model's face"
↓
tweak_handler:
  - Loads existing state from database
  - session_id = <preserved from first gen>
  - attempt_count = 1 → 2
  - user_tweak_instruction = "Zoom out..."
↓
generate_node checks:
  - attempt_count = 2 (> 0)
  - session_id = <exists>
  - continue_conversation = TRUE ✓
↓
Uses EXISTING session:
  - session = get_or_create_session(job_id)  # Returns existing!
  - session.send_message(tweak_prompt)  # Multi-turn!
↓
Gemini refines the SAME image (doesn't regenerate)
```

## Key Differences

| Aspect | Before Fix | After Fix |
|--------|-----------|-----------|
| State | Fresh state created | Existing state loaded |
| attempt_count | Always 0 | Incremented (2, 3, 4...) |
| session_id | Always None | Preserved from first gen |
| continue_conversation | Always False | True for tweaks |
| Gemini behavior | Regenerates from scratch | Refines existing image |
| Job status | Stuck at "correcting" | Updates to "completed" |

## Expected Log Output After Fix

### First Generation:
```
[info] generate_node_start attempt_count=0
[info] generating_image continue_conversation=False session_id=None
[info] session_created job_id=<uuid> total_active_sessions=1
[info] image_generated session_id=<uuid>
```

### After Tweak:
```
[info] tweak_state_prepared attempt_count=2 session_id=<uuid> has_session=True
[info] generate_node_start attempt_count=2
[info] generating_image continue_conversation=True session_id=<uuid>
[info] session_reused job_id=<uuid> session_age_seconds=45.2
[info] using_multi_turn_conversation session_id=<uuid>
[info] sending_message_to_session is_correction=True
[info] image_generated session_id=<uuid>
[info] tweak_workflow_completed final_status=completed
```

## Testing Checklist

### Test 1: First Generation
- [ ] Generate image
- [ ] Verify `session_created` in logs
- [ ] Verify `continue_conversation=False`
- [ ] Verify image is generated

### Test 2: Tweak Completed Image
- [ ] Click "Tweak" button
- [ ] Enter instruction: "Zoom out to show face"
- [ ] Verify `session_reused` in logs
- [ ] Verify `continue_conversation=True`
- [ ] Verify `sending_message_to_session`
- [ ] Verify refined image (not completely new)
- [ ] Verify job status updates to "completed"

### Test 3: Multiple Tweaks
- [ ] Tweak #1: "Make logo larger"
- [ ] Verify attempt_count=2
- [ ] Tweak #2: "Adjust lighting"
- [ ] Verify attempt_count=3
- [ ] Verify each tweak builds on previous

### Test 4: Tweak Needs Review Image
- [ ] Generate image that scores 70-95%
- [ ] Click "Apply Custom Tweak"
- [ ] Verify multi-turn works for needs_review too

## Gemini Multi-Turn API Pattern

Based on the Google Generative AI Python SDK:

```python
# Create session (first generation)
model = genai.GenerativeModel("gemini-3-pro-image-preview")
chat = model.start_chat(history=[])

# First message
response1 = chat.send_message(
    ["Generate a t-shirt design", logo_image],
    generation_config=config
)

# Multi-turn refinement (preserves context)
response2 = chat.send_message(
    "Zoom out to show the model's face",
    generation_config=config
)

# Gemini remembers:
# - Previous image generated
# - Previous prompt
# - Conversation context
# Result: Refines the same image instead of regenerating
```

## Benefits of This Fix

1. **True Multi-Turn**: Gemini refines existing images instead of regenerating
2. **Faster**: Refinement is faster than full regeneration
3. **Better Results**: Preserves what's good, only changes what's requested
4. **User Control**: Iterative refinement with user guidance
5. **Job Status**: Properly updates in database, UI stops polling

## Deployment

```bash
modal deploy src/mobius/api/app_consolidated.py
```

After deployment, the tweak feature will use true multi-turn conversation with Gemini!
