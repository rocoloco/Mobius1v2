# Tweak Workflow Issues & Solutions

## Current Problems

### 1. Job Status Not Updating
**Error:** `failed_to_update_job_status error='no running event loop'`

**Cause:** Using `asyncio.create_task()` in a sync function (complete_node/failed_node)

**Solution:** The nodes are sync functions but we're trying to create async tasks. We need to either:
- Make the nodes async, OR
- Use a different approach to update the job

### 2. Multi-Turn Not Working
**Evidence from logs:**
```
continue_conversation=False
session_id=None
attempt_count=1  (should be 2+ for multi-turn)
```

**Root Cause:** When `tweak_completed_job_handler` calls `run_generation_workflow()`, it creates a FRESH workflow with `initial_state` that has `attempt_count=0`. This loses all the session context.

**What Should Happen:**
1. User tweaks image
2. Load EXISTING job state from database
3. Resume workflow with that state (preserving session_id, attempt_count, etc.)
4. Gemini sees it's a continuation (attempt_count > 0, session_id exists)
5. Uses multi-turn conversation to refine the image

**What's Actually Happening:**
1. User tweaks image
2. Create NEW workflow state with attempt_count=0
3. Start fresh workflow (no session context)
4. Gemini generates completely new image
5. No multi-turn conversation

## The Core Issue

`run_generation_workflow()` always creates a fresh initial state:

```python
initial_state: JobState = {
    "job_id": job_id,
    "brand_id": brand_id,
    "prompt": prompt,
    "attempt_count": 0,  # ← ALWAYS STARTS AT 0!
    "session_id": None,  # ← NO SESSION!
    # ...
}
```

This means:
- Session is lost
- Attempt count resets
- Multi-turn doesn't trigger
- Image is regenerated from scratch

## Proper Solution

### Option 1: Resume Workflow (Recommended)

Instead of calling `run_generation_workflow()`, we should resume the existing workflow:

```python
# In tweak_completed_job_handler:

# Load existing job state from database
job_storage = JobStorage()
job = await job_storage.get_job(job_id)
existing_state = job.state

# Update state with tweak instruction
existing_state["user_tweak_instruction"] = tweak_instruction
existing_state["user_decision"] = "tweak"
existing_state["attempt_count"] = existing_state.get("attempt_count", 0) + 1

# Resume workflow from correct_node with existing state
workflow = create_generation_workflow()
final_state = await workflow.ainvoke(
    existing_state,
    config={"recursion_limit": 10}
)

# Update job with final state
await job_storage.update_job(job_id, {
    "status": final_state["status"],
    "state": final_state
})
```

### Option 2: Pass Initial State to Workflow

Modify `run_generation_workflow()` to accept an optional `initial_state` parameter:

```python
async def run_generation_workflow(
    brand_id: str,
    prompt: str,
    job_id: Optional[str] = None,
    initial_state: Optional[JobState] = None,  # NEW
    **kwargs
) -> dict:
    if initial_state:
        # Use provided state (for resume/tweak)
        state = initial_state
    else:
        # Create fresh state (for new generation)
        state = {
            "job_id": job_id or str(uuid.uuid4()),
            "brand_id": brand_id,
            "prompt": prompt,
            "attempt_count": 0,
            # ...
        }
    
    workflow = create_generation_workflow()
    final_state = await workflow.ainvoke(state)
    return final_state
```

Then in `tweak_completed_job_handler`:

```python
# Load existing state
job = await job_storage.get_job(job_id)
state = job.state

# Update for tweak
state["user_tweak_instruction"] = tweak_instruction
state["attempt_count"] += 1

# Resume with existing state
await run_generation_workflow(
    brand_id=job.brand_id,
    prompt=state["prompt"],
    job_id=job_id,
    initial_state=state  # Pass existing state!
)
```

## Why Multi-Turn Requires This

For Gemini multi-turn to work, the `generate_node` checks:

```python
continue_conversation = attempt_count > 0 and session_id is not None
```

If we start with a fresh state:
- `attempt_count = 0` → `continue_conversation = False`
- `session_id = None` → No session to continue

The session is created on the FIRST attempt and stored in state. On subsequent attempts (tweaks), we need to:
1. Preserve the session_id
2. Increment attempt_count
3. Pass the tweak instruction

This way Gemini knows to refine the existing image instead of generating a new one.

## Job Status Update Fix

The `asyncio.create_task()` approach doesn't work because the nodes are sync functions. Better approach:

### Option A: Make Nodes Async

```python
async def complete_node(state: JobState) -> dict:
    # ... cleanup code ...
    
    # Update job status
    from mobius.storage.jobs import JobStorage
    job_storage = JobStorage()
    await job_storage.update_job(job_id, {
        "status": "completed",
        "progress": 100.0,
        "state": state
    })
    
    return {"status": "completed", "session_id": None}
```

### Option B: Update in Workflow Runner

Update the job status in `run_generation_workflow()` after the workflow completes:

```python
async def run_generation_workflow(...):
    # ... run workflow ...
    final_state = await workflow.ainvoke(initial_state)
    
    # Update job in database
    job_storage = JobStorage()
    await job_storage.update_job(job_id, {
        "status": final_state["status"],
        "progress": 100.0,
        "state": final_state
    })
    
    return final_state
```

## Implementation Priority

1. **Fix multi-turn** (critical for tweak feature)
   - Load existing job state
   - Resume workflow with preserved session
   
2. **Fix job status update** (critical for UI)
   - Update job in database after workflow completes
   
3. **Test multi-turn conversation**
   - Verify session is preserved
   - Verify Gemini refines instead of regenerating

## Testing Multi-Turn

After fixes, verify in logs:

```
# First generation:
attempt_count=0
session_id=None
continue_conversation=False
session_created  ← New session created

# After tweak:
attempt_count=2  ← Incremented!
session_id=<job_id>  ← Preserved!
continue_conversation=True  ← Multi-turn enabled!
session_reused  ← Using existing session!
sending_message_to_session  ← Sending to existing conversation!
```

## Expected Behavior After Fix

1. User generates image → 88% score
2. User clicks "Tweak" → Enters "zoom out to show face"
3. System:
   - Loads existing job state (with session_id)
   - Increments attempt_count to 2
   - Adds user_tweak_instruction
   - Resumes workflow
4. Gemini:
   - Sees attempt_count=2, session_id exists
   - Uses multi-turn conversation
   - Refines the SAME image (zooms out)
   - Doesn't regenerate from scratch
5. New image shows same scene but zoomed out
6. Job status updates to "completed"
7. UI shows refined image

This is the power of multi-turn - iterative refinement instead of complete regeneration!
