# Async Mode & Review Threshold Fix

## Issues Fixed

### Issue 1: ERR_CONNECTION_CLOSED
**Problem**: Dashboard was getting `ERR_CONNECTION_CLOSED` errors because the backend was running the workflow synchronously despite `async_mode=true`, causing the HTTP connection to timeout during the ~70 second generation process.

**Root Cause**: The async mode was not implemented - it just logged a warning and ran synchronously anyway:
```python
if async_mode:
    logger.warning("async_mode_not_implemented", request_id=request_id)
    # For now, run synchronously
    final_state = await run_generation_workflow(...)
```

**Fix**: Implemented true async mode using `asyncio.create_task()` to run the workflow in the background:
- When `async_mode=true`, the endpoint now returns immediately with `status="processing"`
- The workflow runs in a background task with its own `JobStorage` instance
- Background task updates the job status when complete (or on error)
- Dashboard polls `/v1/jobs/{job_id}` every 3 seconds to check status
- Connection no longer times out

**Files Changed**:
- `src/mobius/api/routes.py` (lines 1213-1310)

**Implementation Details**:
- Background task creates its own `JobStorage` instance to avoid shared state issues
- Proper error handling updates job status to "failed" on exceptions
- Logs async_generation_started, async_generation_completed, and async_generation_failed events

### Issue 2: Auto-Approval Instead of Review
**Problem**: Jobs scoring 91-98% were being auto-approved when they should trigger `needs_review` status according to the architecture.

**Root Cause**: The Gemini audit prompt instructed:
```
Set approved=true if overall_score >= 80.
```

But according to `MOBIUS-ARCHITECTURE.md`, the routing should be:
- **95-100%**: Auto-approved → `completed`
- **70-95%**: Needs review → `needs_review`
- **<70%**: Auto-rejected → `failed`

**Fix**: Changed the Gemini audit prompt threshold from ≥80 to ≥95:
```python
"Set approved=true if overall_score >= 95.",
```

Now the workflow correctly routes:
- Score 95+: `is_approved=True` → routes to `complete`
- Score 70-94: `is_approved=False` → routes to `needs_review`
- Score <70: `is_approved=False` → routes to `needs_review` (first attempt) or `failed` (max attempts)

**Files Changed**:
- `src/mobius/tools/gemini.py` (line 1473)

## Verification

### Test Async Mode
```bash
# Start the Modal app
modal serve src/mobius/api/app_consolidated.py

# In dashboard, ensure "Async Mode" toggle is ON
# Generate an asset - should return immediately with "processing" status
# Dashboard should poll and update when complete
```

### Test Review Threshold
```bash
# Generate assets with prompts that score 70-95%
# Example: "A moody night shot..." (scored 91.75% and 92.5% in logs)
# Should now show "needs_review" status instead of auto-approving
```

## Expected Behavior

### Async Mode Flow
1. User clicks "Generate Asset" with async mode ON
2. API returns immediately: `{"job_id": "...", "status": "processing"}`
3. Dashboard shows "Job: processing" and polls every 3 seconds
4. Workflow runs in background (~70 seconds)
5. Job status updates to `completed` or `needs_review`
6. Dashboard displays result

### Review Threshold Flow
1. Asset generates with score 91% (example from logs)
2. Audit node sets `is_approved=False` (because 91 < 95)
3. Router checks score: 70 ≤ 91 < 95 → routes to `needs_review`
4. Job status becomes `needs_review`
5. Dashboard shows review UI with violations and action buttons
6. User can approve, tweak, or regenerate

## Architecture Alignment

These fixes align the implementation with the documented architecture:

**From MOBIUS-ARCHITECTURE.md**:
> **Routing Logic**:
> - **95-100%**: Auto-approved → `completed`
> - **70-95%**: Needs review → `needs_review` (pause workflow)
> - **<70%**: Auto-rejected → `failed` (or `needs_review` on first attempt)

**From logs (before fix)**:
```
2025-12-09 03:52:30 [info] audit_complete approved=True score=92.5  ❌ WRONG
2025-12-09 03:53:41 [info] audit_complete approved=True score=91.75 ❌ WRONG
```

**After fix**:
```
2025-12-09 XX:XX:XX [info] audit_complete approved=False score=92.5  ✅ CORRECT
2025-12-09 XX:XX:XX [info] routing_to_needs_review overall_score=92.5 ✅ CORRECT
```

## Notes

- The dashboard already had proper polling logic implemented
- The `route_after_audit()` function in `generation.py` already had correct 70-95% routing logic
- The issue was that Gemini was setting `approved=True` too early (at 80% instead of 95%)
- Async mode now uses `asyncio.create_task()` which is the standard Python approach for background tasks
