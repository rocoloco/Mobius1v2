# Image Generation Timeout Fix Summary

## Problem Identified

The image generation was hanging and timing out due to several issues:

1. **Gemini API Timeouts**: The Gemini image generation API was timing out after 30 seconds
2. **Backend Async Task Crashes**: When the API timed out, the LangGraph workflow crashed with async generator errors
3. **Job Status Not Updated**: The background task wasn't properly updating job status to "failed" when crashes occurred
4. **Frontend Infinite Polling**: The frontend kept polling because jobs remained in "pending" state indefinitely

## Changes Made

### Frontend Improvements (`frontend/src/hooks/useJobStatus.ts`)

1. **Extended Timeout**: Increased job timeout from 2 to 3 minutes to account for longer generation times
2. **Better Error Detection**: Added detection for jobs stuck in "processing" or "generating" states
3. **Improved Error Messages**: More descriptive timeout error messages explaining the likely cause
4. **Enhanced Logging**: Better console logging for debugging timeout issues

### Backend Improvements (`src/mobius/api/routes.py`)

1. **Robust Background Task Handling**: 
   - Added proper exception handling for `asyncio.CancelledError`
   - Ensured job status is always updated even if the main workflow fails
   - Added task completion callbacks for better monitoring
   - Multiple fallback attempts to update job status

2. **Better State Tracking**:
   - Update job to "processing" state immediately when workflow starts
   - Add timestamps for started_at, completed_at, failed_at
   - Include error type and detailed error information
   - **Fixed Missing brand_id**: Ensure brand_id is always included in job state for workflow compatibility

3. **Workflow Resume Fix**:
   - Fixed issue where workflow resume after review decisions failed due to missing brand_id
   - Ensure all required fields (brand_id, job_id) are present when resuming workflows

### Workflow Improvements (`src/mobius/graphs/generation.py`)

1. **Workflow Timeout**: Added 5-minute timeout wrapper around the entire generation workflow
2. **Timeout Error Handling**: Proper exception handling for workflow timeouts

### UI Improvements (`frontend/src/context/DashboardContext.tsx`)

1. **Better Error Messages**: More helpful timeout error messages explaining the issue and suggesting solutions

### Diagnostic Tools

1. **Stuck Job Checker** (`scripts/check_stuck_jobs.py`):
   - Find jobs stuck in non-terminal states
   - Check specific job status
   - Optionally mark stuck jobs as failed
   - Usage: `python scripts/check_stuck_jobs.py --help`

## How to Use the Diagnostic Tool

```bash
# Check for jobs stuck longer than 5 minutes
python scripts/check_stuck_jobs.py

# Check for jobs stuck longer than 10 minutes
python scripts/check_stuck_jobs.py --older-than 10

# Check a specific job
python scripts/check_stuck_jobs.py --job-id YOUR_JOB_ID

# Fix stuck jobs (mark them as failed)
python scripts/check_stuck_jobs.py --fix

# On Windows, you can also use:
scripts\check_stuck_jobs.bat --fix
```

## Root Cause Analysis

The main issue was in the async task management. When the Gemini API timed out:

1. The LangGraph workflow would crash with async generator errors
2. The background task would be destroyed before it could update the job status
3. Jobs would remain in "pending" state forever
4. Frontend would poll indefinitely

## Prevention Measures

1. **Workflow Timeout**: 5-minute timeout prevents workflows from hanging indefinitely
2. **Robust Error Handling**: Multiple layers of exception handling ensure job status is always updated
3. **Frontend Timeout Detection**: Client-side timeout detection stops polling after 3 minutes
4. **Monitoring Tools**: Diagnostic script helps identify and fix stuck jobs

## Testing the Fix

1. **Test Initial Generation**:
   - Try generating an image with a complex prompt
   - If it times out, check that:
     - The job status changes to "failed" within 5 minutes
     - The frontend shows a helpful error message
     - Polling stops automatically

2. **Test Review Workflow**:
   - Generate an image that reaches "needs_review" status
   - Try using "Fix Red Violations" or other tweak options
   - Verify the workflow resumes properly without "brand_id is required" errors

3. **Use Diagnostic Tools**:
   - Run `python scripts/check_stuck_jobs.py` to check for any stuck jobs
   - Use `--fix` flag to clean up stuck jobs if needed

## Next Steps

1. Monitor the logs for any remaining async generator errors
2. Consider implementing retry logic for failed generations
3. Add metrics/monitoring for generation success rates
4. Consider using a more robust task queue (like Celery) for background jobs

## Logs to Watch

Look for these log messages to verify the fix is working:

- `async_generation_failed` - Background task caught an exception
- `generation_workflow_timeout` - Workflow timed out (expected for stuck jobs)
- `Background task was cancelled` - Task was cancelled (should be rare now)
- `Failed to update failed job` - Last resort error handling (should be very rare)