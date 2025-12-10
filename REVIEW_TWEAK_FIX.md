# Review Tweak Fix

## Issue
When user submitted a tweak from the review UI, the system failed with:
```
[error] review_job_failed error="'Job' object has no attribute 'prompt'"
```

## Root Cause
The `review_job_handler` was trying to access `job.prompt`, but the `Job` model doesn't have a `prompt` attribute. The prompt is stored in `job.state["prompt"]`.

Additionally, the handler was calling `run_generation_workflow()` which creates a fresh initial state, losing all the existing job state (session_id, current_image_url, attempt_count, etc.) needed for multi-turn conversation.

## Fix

### 1. Fixed Prompt Access
Changed from:
```python
prompt=job.prompt  # ❌ Job model doesn't have prompt attribute
```

To:
```python
prompt = state.get("prompt", "")  # ✅ Extract from job.state
```

### 2. Fixed Workflow Resumption
Changed from:
```python
# ❌ Creates fresh state, loses session_id and current_image_url
run_generation_workflow(
    brand_id=job.brand_id,
    prompt=prompt,
    job_id=job_id,
)
```

To:
```python
# ✅ Resumes with existing state preserved
workflow = create_generation_workflow()
final_state = await workflow.ainvoke(state)  # Pass existing state
```

## How It Works Now

**User Tweak Flow:**
1. User sees review UI with image (score 86%)
2. User enters tweak: "add some mid century modern wood furniture..."
3. Review handler:
   - Loads existing job state
   - Adds `user_tweak_instruction` to state
   - Sets `user_decision="tweak"`
   - Updates job status to "correcting"
4. Workflow resumes with existing state:
   - Routes to `correct` node (because user_decision="tweak")
   - Correct node creates multi-turn prompt
   - Routes to `generate` node
   - Generate node sees `attempt_count > 1` → `continue_conversation=True`
   - Fetches `previous_image_bytes` from `current_image_url`
   - Passes to Gemini with session_id for refinement
5. Gemini refines existing image (doesn't regenerate from scratch)
6. Audit node evaluates refined image
7. Routes based on new score

## State Preservation

The fix ensures these critical fields are preserved:
- `session_id`: Maintains conversation context with Gemini
- `current_image_url`: Previous image for multi-turn refinement
- `attempt_count`: Incremented to trigger continue_conversation
- `prompt`: Original prompt for context
- `brand_id`: Required for brand guidelines
- `compliance_scores`: History of audit results
- `audit_history`: Full audit trail

## Files Changed
- `src/mobius/api/routes.py` (lines 1650-1730)

## Test It
1. Generate asset → gets score 70-95% → shows review UI
2. Enter tweak instruction: "add warm lighting"
3. Click "Apply Tweak"
4. Should see:
   - Job status changes to "correcting" → "processing"
   - Dashboard polls for updates
   - New image appears (refined, not regenerated)
   - Multi-turn conversation preserved
