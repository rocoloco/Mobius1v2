# Tweak Feature - Complete Fix

## Issues Fixed

### Issue 1: Missing brand_id Error
When users clicked the "Tweak" button, the workflow failed with error:
```
[error] tweak_workflow_failed error="'brand_id'" job_id=3950f2f9-002b-46e0-9d3e-6670a33a7a97
```

### Issue 2: Tweak Instruction Not Being Applied
Even after fixing the brand_id error, the tweak instruction wasn't being passed to the model. The workflow was starting from `generate` node without first building the correction prompt.

## Root Causes

### Cause 1: Missing State Fields
The `tweak_completed_job_handler` was loading the job state from the database and resuming the workflow with that state. However, the state stored in the database didn't contain all the required fields that the workflow expects:

**Required by workflow:**
- `brand_id` (used by generate_node to load brand)
- `prompt` (used by generate_node)
- `job_id` (used for logging)
- `generation_params` (used by generate_node)
- `compliance_scores` (used by audit routing)
- `audit_history` (used by correct_node)

**What was in database state:**
- Only the fields that were explicitly set during workflow execution
- Missing core fields like `brand_id`, `prompt`, etc.

### Cause 2: Workflow Entry Point
When calling `workflow.ainvoke(state)`, LangGraph always starts from the entry point, which is `generate` node. But for a tweak:
1. We need to first run `correct_node` to convert the user's tweak instruction into a correction prompt
2. Then run `generate` with that correction prompt
3. Then run `audit` to check the result

Without running `correct_node` first, the user's tweak instruction was never converted into a prompt that the model could understand.

## The Fixes

### Fix 1: Populate Missing State Fields
Added code to ensure all required fields are present in the state before resuming the workflow:

```python
# Load existing state from job
state = job.state or {}

# CRITICAL: Ensure all required fields are present
# The workflow expects these fields to be in the state
if "brand_id" not in state:
    state["brand_id"] = job.brand_id
if "prompt" not in state:
    state["prompt"] = job.prompt
if "job_id" not in state:
    state["job_id"] = job_id
if "generation_params" not in state:
    state["generation_params"] = {}
if "compliance_scores" not in state:
    state["compliance_scores"] = []
if "audit_history" not in state:
    state["audit_history"] = []
```

These fields are populated from the Job model, which has them stored in separate columns.

### Fix 2: Run correct_node Before Workflow
Added code to manually run `correct_node` before starting the workflow:

```python
# CRITICAL: First run correct_node to build the tweak prompt
logger.info(
    "running_correct_node_for_tweak",
    job_id=job_id,
    user_instruction=state.get("user_tweak_instruction")
)

correction_result = await correct_node(state)

# Merge correction result into state
state.update(correction_result)

logger.info(
    "correction_prompt_built",
    job_id=job_id,
    correction_prompt=state.get("prompt", "")[:100]
)

# Now create workflow and resume from generate node
workflow = create_generation_workflow()

# Resume with updated state (now has correction prompt)
final_state = await workflow.ainvoke(state)
```

This ensures:
1. User's tweak instruction is converted to a proper correction prompt
2. The correction prompt tells Gemini to edit the existing image (multi-turn)
3. The workflow starts with the correct prompt

## Why This Happened

The workflow state is stored in the database as a JSON blob in the `state` column. However, some critical fields like `brand_id` and `prompt` are stored in separate columns on the Job model for querying purposes.

When we resume the workflow, we need to reconstruct the full state by:
1. Loading the state JSON blob
2. Adding back the fields from the Job model columns

## Testing

After deployment, test the tweak feature:

1. Generate an image (should complete successfully)
2. Click "Tweak" button
3. Enter instruction: "Change the background to an urban location"
4. Verify:
   - No `'brand_id'` error
   - Workflow resumes successfully
   - Image is generated with the tweak applied

## Expected Log Output

### Before Fix:
```
[info] tweak_state_prepared attempt_count=2 has_session=False session_id=None
[info] resuming_workflow_for_tweak
[error] tweak_workflow_failed error="'brand_id'"  ← ERROR!
```

### After Fix:
```
[info] tweak_state_prepared attempt_count=2 has_session=False session_id=None brand_id=52e6a867-... prompt="A close-up product shot..."
[info] resuming_workflow_for_tweak
[info] generate_node_start attempt_count=2 brand_id=52e6a867-...
[info] compressed_twin_loaded
[info] generating_image continue_conversation=True  ← Multi-turn!
[info] image_generated
[info] tweak_workflow_completed final_status=completed
```

## Note on Multi-Turn

You'll notice `session_id=None` and `has_session=False` in the logs. This is expected because:

1. **First generation** creates a session and stores `session_id` in state
2. **Session is stored in memory** on the Modal container (not in database)
3. **When container restarts**, the session is lost
4. **On tweak**, the session_id from database state is `None` because the container restarted

This means the first tweak after a container restart will NOT use multi-turn (it will regenerate). However:
- Subsequent tweaks within the same container session WILL use multi-turn
- The session is created on first generation and reused for tweaks
- Session TTL is 1 hour

To enable true persistent multi-turn across container restarts, we would need to:
- Store session state in database or external cache (Redis)
- Reconstruct session from stored state on resume

For now, multi-turn works within a single container session, which is sufficient for most use cases (users typically tweak immediately after generation).

## Files Changed

- `src/mobius/api/routes.py` - `tweak_completed_job_handler()` - Added state field validation

## Deployment

```bash
modal deploy src/mobius/api/app_consolidated.py
```

Deployed successfully at: https://rocoloco--mobius-v2-final-fastapi-app.modal.run/v1
