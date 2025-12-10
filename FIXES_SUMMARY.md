# Quick Fix Summary

## ✅ Fixed: ERR_CONNECTION_CLOSED (Issue 1)

**Before**:
```
Dashboard → POST /v1/generate (async_mode=true)
                ↓
Backend: "async_mode_not_implemented" warning
                ↓
Runs workflow synchronously (~70 seconds)
                ↓
Connection times out → ERR_CONNECTION_CLOSED ❌
```

**After**:
```
Dashboard → POST /v1/generate (async_mode=true)
                ↓
Backend: Returns immediately with job_id
                ↓
Background task runs workflow (~70 seconds)
                ↓
Dashboard polls /v1/jobs/{job_id} every 3s
                ↓
Gets result when complete ✅
```

## ✅ Fixed: Auto-Approval Threshold (Issue 2)

**Before**:
```
Score: 92.5% → approved=True (≥80 threshold)
                     ↓
              Routes to "complete"
                     ↓
              Auto-approved ❌ (should need review)
```

**After**:
```
Score: 92.5% → approved=False (≥95 threshold)
                     ↓
              Routes to "needs_review"
                     ↓
              User reviews and decides ✅
```

## Changes Made

1. **src/mobius/tools/gemini.py** (line 1473)
   - Changed: `"Set approved=true if overall_score >= 80."`
   - To: `"Set approved=true if overall_score >= 95."`

2. **src/mobius/api/routes.py** (lines 1213-1310)
   - Implemented true async mode with `asyncio.create_task()`
   - Returns immediately when `async_mode=true`
   - Workflow runs in background and updates job status

## ✅ Fixed: Review Tweak Error (Issue 3)

**Before**:
```
User clicks "Apply Tweak"
         ↓
Error: 'Job' object has no attribute 'prompt' ❌
         ↓
Review fails, no regeneration
```

**After**:
```
User clicks "Apply Tweak"
         ↓
Loads prompt from job.state["prompt"]
         ↓
Resumes workflow with existing state
         ↓
Multi-turn refinement works ✅
```

## Changes Made

1. **src/mobius/tools/gemini.py** (line 1473)
   - Changed: `"Set approved=true if overall_score >= 80."`
   - To: `"Set approved=true if overall_score >= 95."`

2. **src/mobius/api/routes.py** (lines 1213-1310)
   - Implemented true async mode with `asyncio.create_task()`
   - Returns immediately when `async_mode=true`
   - Workflow runs in background and updates job status

3. **src/mobius/api/routes.py** (lines 1650-1730)
   - Fixed: Changed `job.prompt` to `state.get("prompt")`
   - Fixed: Resume workflow with existing state instead of creating fresh state
   - Preserves session_id, current_image_url, attempt_count for multi-turn

## Test It

1. Open dashboard: `mobius-dashboard.html`
2. Toggle "Async Mode" ON
3. Generate asset with prompt: "A moody night shot of a brick storefront window..."
4. Should see:
   - Immediate response with "processing" status
   - Polling updates every 3 seconds
   - Final status "needs_review" (score ~86%)
   - Review UI with approve/tweak/regenerate buttons
5. Enter tweak: "add warm lighting and plants"
6. Click "Apply Tweak"
7. Should see:
   - Job status changes to "processing"
   - New refined image appears (not regenerated from scratch)
   - Multi-turn conversation preserved
