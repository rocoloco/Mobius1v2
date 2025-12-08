# Auto-Correction Behavior Fix

## Problem

The system was automatically correcting images that scored below 70% without asking for user review first. This caused:

1. **Unwanted auto-corrections**: Image scored 67.5% → System automatically applied AI corrections
2. **No user control**: User never saw the first attempt or had a chance to provide input
3. **Unpredictable results**: AI corrections without user guidance led to unexpected changes

## Root Cause

The routing logic in `route_after_audit()` was:

```python
# If score is between 70-95%, pause for user review
if 70 <= overall_score < 95:
    return "needs_review"

# Otherwise, auto-correct if attempts remain
return "correct"
```

**Problem:** Scores below 70% would skip "needs_review" and go straight to "correct", triggering automatic AI-driven corrections without user input.

## Example from Logs

```
2025-12-07 23:57:57 [info] audit_complete score=67.5
2025-12-07 23:57:57 [info] correct_node_start attempt_count=1
2025-12-07 23:57:57 [info] applying_ai_correction
```

The system:
1. Generated image → 67.5% compliance
2. **Should have:** Paused for user review
3. **Actually did:** Automatically applied AI corrections
4. Regenerated → 94.5% compliance

## Fix Applied

Updated the routing logic to pause for user review on first attempt, regardless of score:

```python
# If score is between 70-95%, pause for user review
if 70 <= overall_score < 95:
    return "needs_review"

# If score is below 70% on first attempt, pause for user review
# (Don't auto-correct without user input)
if overall_score < 70 and state["attempt_count"] == 1:
    logger.info(
        "routing_to_needs_review_low_score",
        job_id=state.get("job_id"),
        overall_score=overall_score,
        reason="First attempt scored below 70%, needs user review"
    )
    return "needs_review"
```

## New Behavior

### Scenario 1: Score 67.5% (Below 70%)

**Before Fix:**
```
Generate → 67.5% → Auto-correct → Regenerate → 94.5% → Complete
❌ User never saw first attempt
❌ No control over corrections
```

**After Fix:**
```
Generate → 67.5% → Pause for Review
✅ User sees violations
✅ User chooses: Approve / Tweak / Regenerate
✅ Full control over next steps
```

### Scenario 2: Score 77.5% (70-95% range)

**Before & After (No Change):**
```
Generate → 77.5% → Pause for Review
✅ User sees violations
✅ User chooses action
```

### Scenario 3: Score 86% (80-95% range)

**Before & After (No Change):**
```
Generate → 86% → Auto-approve
✅ Detailed compliance shown
✅ Tweak button available
```

### Scenario 4: Score 96% (Above 95%)

**Before & After (No Change):**
```
Generate → 96% → Auto-approve
✅ Excellent compliance
✅ Tweak button available
```

## Routing Decision Tree

```
Generate Image
    ↓
Audit Compliance
    ↓
    ├─ Score >= 95% → Auto-approve → Complete
    │
    ├─ Score 70-95% → Pause for Review
    │   ├─ User: Approve → Complete
    │   ├─ User: Tweak → Apply tweak → Regenerate
    │   └─ User: Regenerate → Start fresh
    │
    ├─ Score < 70% (First attempt) → Pause for Review
    │   ├─ User: Approve → Complete (override)
    │   ├─ User: Tweak → Apply tweak → Regenerate
    │   └─ User: Regenerate → Start fresh
    │
    └─ Score < 70% (After user decision) → Correct → Regenerate
        ↓
        Max attempts reached? → Fail
```

## Key Changes

1. **First attempt always pauses for review if < 95%**
   - Gives user visibility and control
   - Prevents unwanted auto-corrections

2. **Auto-correction only after user decision**
   - User chooses "Tweak" or "Regenerate"
   - System applies user's instruction
   - Not AI-driven guesses

3. **Clear threshold boundaries**
   - 95%+: Auto-approve (excellent)
   - 70-95%: User review (good but could be better)
   - <70%: User review (needs work)

## User Experience Improvements

### Before Fix
```
User: "Generate a t-shirt design"
System: *generates* → 67.5%
System: *auto-corrects without asking*
System: *regenerates* → 94.5%
User: "Wait, what happened to my first design?"
```

### After Fix
```
User: "Generate a t-shirt design"
System: *generates* → 67.5%
System: "Here's your image. It scored 67.5% due to:"
        - Typography: Using wrong font
        - Colors: Low contrast on dark background
        - Logo: Visibility issues
        
User sees 3 options:
  1. Approve anyway (I like it despite issues)
  2. Tweak (Fix the font but keep everything else)
  3. Regenerate (Start completely over)
  
User: *chooses action*
System: *follows user's decision*
```

## Testing

### Test Case 1: Low Score First Attempt
1. Generate image that scores < 70%
2. Verify system pauses for review
3. Verify violations are displayed
4. Choose "Tweak" with specific instruction
5. Verify system applies tweak (not random AI correction)

### Test Case 2: Medium Score
1. Generate image that scores 70-95%
2. Verify system pauses for review
3. Verify violations are displayed
4. Test all three options (Approve/Tweak/Regenerate)

### Test Case 3: High Score
1. Generate image that scores 80-94%
2. Verify auto-approval
3. Verify tweak button is available
4. Test manual tweak on approved image

## Deployment

This fix requires redeployment:

```bash
modal deploy src/mobius/api/app.py
```

After deployment, the system will:
- Always pause for user review on first attempt (unless score >= 95%)
- Never auto-correct without user input
- Give users full control over the generation process

## Related Issues

This fix addresses:
1. ✅ Unwanted auto-corrections
2. ✅ Lack of user control
3. ✅ Unpredictable AI behavior
4. ✅ Missing first attempt visibility

## Future Enhancements

Consider adding:
1. **Confidence threshold**: Only auto-approve if score >= 95% AND no critical violations
2. **User preferences**: Let users set their own auto-approve threshold
3. **Correction history**: Show what changed between attempts
4. **Undo**: Allow reverting to previous attempt
