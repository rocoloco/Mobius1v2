# Review Workflow Fixes

## Issues Found

### 1. Review Endpoint Not Registered ❌
**Problem**: The `review_job_handler` function existed in `routes.py` but was never registered in `app.py`, making it inaccessible.

**Evidence**: Dashboard was calling `POST /v1/jobs/{job_id}/review` but receiving 404 errors.

**Fix**: Added endpoint registration in `app.py` at line 376-414.

### 2. Workflow Not Resuming ❌
**Problem**: The review handler updated the database but had a `TODO` comment instead of actually resuming the LangGraph workflow.

**Evidence**: Lines 1505-1508 in `routes.py`:
```python
# TODO: Resume LangGraph workflow execution
# This would typically involve calling the workflow runner
# For now, we update the state and the workflow should continue
# when the job processor picks it up
```

**Fix**: Now actually calls `run_generation_workflow()` in a background task.

### 3. Multi-Turn Conversation Not Working ❌
**Problem**: Sessions are created but don't preserve the previous image context between correction attempts.

**Evidence from logs**:
```
2025-12-07 22:52:10 [info] session_created job_id=dce6ba6c-a5f0-4319-a674-b1b79f96b5af
2025-12-07 22:52:10 [info] using_multi_turn_conversation
```

But the second generation created a completely different image instead of modifying the first one.

**Root Cause**: Gemini's `ChatSession` API doesn't work the way we thought. Starting a chat session with `start_chat()` doesn't automatically remember the image from the first generation. We need to pass the image in the session history.

**Status**: ⚠️ NEEDS FIX (next task)

### 4. Slow Workflow Performance 🐌
**Evidence**: Total time 4+ minutes per generation
- Prompt optimization: 24 seconds
- Image generation: 19 seconds
- Compliance audit: 43 seconds
- **Total per attempt**: ~90 seconds
- **3 attempts**: ~4.5 minutes

**Root Cause**: Sequential operations with heavy LLM calls

**Status**: ⚠️ NEEDS OPTIMIZATION

## What's Fixed

✅ Review endpoint now registered and accessible
✅ Workflow resumes when user submits decision
✅ Dashboard can communicate with backend

## What Still Needs Work

### Priority 1: Fix Multi-Turn Image Editing
The current session implementation doesn't preserve images. We need to:

1. Store the generated image URI in session history
2. Pass it back to Gemini with edit instructions
3. Verify Gemini 3 actually supports image-to-image editing in conversations

**Research needed**: Does Gemini 3 support:
```python
session.send_message([
    Part.from_image(previous_image),
    "Please modify this image: make the logo conform to the fabric"
])
```

If not, we may need to use a different approach:
- Option A: Use seed + negative prompts
- Option B: Use external image editing tool (Pillow/OpenCV)
- Option C: Rebuild conversation history with image references

### Priority 2: Optimize Performance
**Target**: Reduce from 4 minutes to under 60 seconds

Potential optimizations:
1. **Parallel audit categories** - Run color/typography/layout checks in parallel
2. **Skip prompt optimization on corrections** - Use correction prompt directly
3. **Reduce audit prompt size** - Currently sending 3.6KB of brand guidelines every time
4. **Cache brand data** - Don't fetch from DB on every node
5. **Streaming responses** - Start audit while generation completes

### Priority 3: Fix Audit Failures
**Error**: `finish_reason is 1` (safety filter triggered)

This happened on the second generation attempt. Possible causes:
- Audit prompt too long
- Generated image triggered safety filter
- Brand guidelines contain blocked content

Need to add retry logic and better error handling.

## Performance Breakdown

From logs:
```
22:45:56 - Workflow started
22:46:22 - Prompt optimized (+26s)
22:46:41 - Image generated (+19s)
22:47:26 - Audit complete (+45s)
22:47:26 - Workflow paused (needs_review)

Total first attempt: 90 seconds
```

**Target per-attempt latency**:
- Prompt optimization: 5s (currently 26s) - **optimize or skip**
- Image generation: 15s (currently 19s) - **acceptable**
- Audit: 10s (currently 45s) - **parallelize categories**

**Target total**: ~30 seconds per attempt, ~90 seconds for 3 attempts

## Next Steps

1. Fix multi-turn conversation (research Gemini API capabilities)
2. Optimize performance (parallel operations, caching)
3. Add better error handling for audit failures
4. Test end-to-end review workflow with real user
