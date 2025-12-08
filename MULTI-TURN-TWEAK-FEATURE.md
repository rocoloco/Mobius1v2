# Multi-Turn Tweak Feature

## Overview

Added the ability to refine auto-approved images (>= 80% compliance) using multi-turn conversation with Gemini. Users can now tweak completed images without starting from scratch, preserving the conversation context for iterative refinement.

## Backend Changes

### 1. New API Endpoint: `/v1/jobs/{job_id}/tweak`

**File:** `src/mobius/api/app.py`

Added new endpoint for tweaking completed jobs:
```python
@app.function(image=image, secrets=secrets)
@modal.web_endpoint(method="POST", label="v1-tweak-job")
async def v1_tweak_job(request: dict)
```

**Request Body:**
```json
{
  "job_id": "uuid",
  "tweak_instruction": "Make the logo larger and more prominent"
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "resumed",
  "message": "Job resumed for multi-turn tweak",
  "request_id": "req_xxx"
}
```

### 2. New Handler: `tweak_completed_job_handler`

**File:** `src/mobius/api/routes.py`

Implements the tweak logic:
- Validates job is in `completed` status
- Preserves `session_id` for multi-turn conversation
- Increments `attempt_count` to trigger `continue_conversation=True`
- Stores `user_tweak_instruction` in state
- Resumes workflow from correction node

**Key Features:**
- Multi-turn conversation support via session preservation
- Validates tweak instruction is not empty
- Updates job status to `correcting`
- Runs workflow asynchronously in background

## Frontend Changes

### 1. Enhanced Asset Display

**File:** `mobius-dashboard.html`

Added tweak functionality to completed images:

**New UI Elements:**
- "Tweak" button next to "Download" button
- Collapsible tweak UI with textarea for instructions
- Real-time status updates during tweak processing

**Visual Design:**
- Purple theme for tweak actions (distinguishes from generation)
- Clear instructions and examples
- Cancel button to hide tweak UI

### 2. JavaScript Functions

**New Functions:**
- `showTweakUI(jobId)` - Shows the tweak input interface
- `hideTweakUI()` - Hides and resets the tweak interface
- `submitTweak()` - Submits tweak request to API and polls for results

**State Management:**
- `window.currentJobId` - Stores current job ID for tweaking
- `window.currentPrompt` - Stores original prompt for context

### 3. Enhanced Compliance Display

Updated `displayAsset()` to show detailed compliance breakdown:
- Overall score badge with color coding
- Auto-approved status indicator
- Category breakdown with scores and violations
- Specific fix suggestions for each violation
- Compliance summary from audit

**Color Coding:**
- Green (95%+): Excellent compliance
- Blue (80-94%): Good compliance (auto-approved)
- Yellow (60-79%): Needs improvement
- Red (<60%): Poor compliance

## Multi-Turn Workflow

### How It Works

1. **User generates image** → Image scores 86% → Auto-approved
2. **User clicks "Tweak"** → Enters refinement instruction
3. **Backend preserves session** → Increments attempt_count
4. **Gemini uses multi-turn** → Refines existing image with context
5. **New image generated** → Goes through audit again
6. **User can tweak again** → Iterative refinement continues

### Session Preservation

The key to multi-turn is preserving the `session_id`:

```python
# In tweak_completed_job_handler
state["attempt_count"] = current_attempt + 1  # Triggers continue_conversation=True
session_id = state.get("session_id")  # Preserved from original generation
```

In `generate_node`, this triggers:
```python
continue_conversation = attempt_count > 0 and session_id is not None
```

### Gemini Multi-Turn Support

The `GeminiClient` maintains active sessions:
```python
def get_or_create_session(self, job_id: str, system_prompt: str) -> Any:
    if job_id in self.active_sessions:
        return self.active_sessions[job_id]  # Reuse existing session
    # Create new session if not found
```

## User Experience

### Before (No Tweak Support)
1. Generate image → 86% compliance
2. Not satisfied? → Start completely over
3. Lose all context → Gemini doesn't remember previous attempt

### After (With Tweak Support)
1. Generate image → 86% compliance
2. Click "Tweak" → "Make logo more prominent"
3. Gemini refines → Remembers previous image context
4. New image → Can tweak again if needed

## Example Use Cases

### Use Case 1: Logo Adjustment
- **Initial:** Logo is too small on product
- **Tweak:** "Make the logo 50% larger and center it"
- **Result:** Same image, larger logo, maintains other elements

### Use Case 2: Color Correction
- **Initial:** Gold color doesn't match brand exactly
- **Tweak:** "Adjust the gold accent to be more vibrant and match #C4A962 exactly"
- **Result:** Same composition, corrected color

### Use Case 3: Typography Fix
- **Initial:** Using wrong font (Open Sans instead of Playfair Display)
- **Tweak:** "Change the headline font to Playfair Display Bold"
- **Result:** Same image, corrected typography

## Technical Details

### API Flow

```
POST /v1/jobs/{job_id}/tweak
  ↓
tweak_completed_job_handler()
  ↓
Update job state:
  - status: "correcting"
  - user_tweak_instruction: "..."
  - attempt_count: +1
  - session_id: preserved
  ↓
run_generation_workflow()
  ↓
correct_node() → Uses user_tweak_instruction
  ↓
generate_node() → continue_conversation=True
  ↓
Gemini multi-turn → Refines with context
  ↓
audit_node() → Checks compliance
  ↓
Job completed → New image ready
```

### State Management

**Critical State Fields:**
- `session_id`: Gemini conversation session ID
- `attempt_count`: Number of generation attempts (triggers multi-turn)
- `user_tweak_instruction`: User's refinement instruction
- `user_decision`: "tweak" to indicate tweak mode
- `current_image_url`: Previous image for reference

## Testing

### Manual Testing Steps

1. **Generate an image:**
   ```
   Brand: Evergreen Naturals
   Prompt: "A product shot of a water bottle"
   ```

2. **Verify auto-approval:**
   - Check score is 80-94%
   - Verify "Auto-Approved" status shown
   - See detailed compliance breakdown

3. **Click "Tweak" button:**
   - Tweak UI appears
   - Enter: "Make the logo twice as large"
   - Click "Apply Tweak"

4. **Verify multi-turn:**
   - Job status shows "Refining image..."
   - Poll for completion
   - New image appears with larger logo
   - Other elements remain similar

5. **Tweak again:**
   - Click "Tweak" on new image
   - Enter: "Add more condensation droplets"
   - Verify iterative refinement works

## Benefits

1. **Faster Iteration:** No need to regenerate from scratch
2. **Context Preservation:** Gemini remembers previous attempts
3. **Better Results:** Incremental improvements vs. complete regeneration
4. **User Control:** Fine-tune specific aspects without losing good elements
5. **Cost Efficient:** Fewer full generations needed

## Future Enhancements

1. **Tweak History:** Show all tweaks applied to an image
2. **Undo Tweak:** Revert to previous version
3. **Tweak Templates:** Save common tweak instructions
4. **Batch Tweaks:** Apply same tweak to multiple images
5. **AI Suggestions:** Suggest tweaks based on compliance violations
