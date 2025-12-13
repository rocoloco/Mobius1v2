# Bug Report: Logo Configuration Lost During Tweak Operations

## Issue Summary
**Bug ID**: Logo State Management Failure  
**Severity**: Critical  
**Status**: FIXED  
**Date**: December 13, 2025  

## Root Cause Analysis

### The Problem
During tweak operations (when users request modifications to generated images), the system was losing the logo configuration, causing `has_logo=False` and `logo_count=0` in subsequent generations. This resulted in the AI attempting to generate logos from text descriptions rather than using the actual brand logo assets.

### Smoking Gun Evidence
From the logs for Job ID `5e9bcc98-fb8a-4c36-9e85-c5c3099fcd30`:

1. **Original Generation (Correct)**:
   ```
   2025-12-13 16:13:19 [info] generating_image has_logo=True ... logo_count=1 ...
   ```

2. **Tweak Generation (Bug)**:
   ```
   2025-12-13 16:15:19 [info] generating_image has_logo=False ... logo_count=0 ...
   ```

### Technical Root Cause
The bug occurred in the logo detection logic within `src/mobius/nodes/generate.py`. The system used a flawed strategy for determining whether to fetch logos during tweak operations:

```python
# BUGGY CODE (before fix)
elif state.get("user_tweak_instruction"):
    # Check if user's instruction mentions logo
    instruction = state["user_tweak_instruction"].lower()
    logo_keywords = ['logo', 'brand mark', 'icon', 'symbol', 'emblem']
    needs_logos = any(kw in instruction for kw in logo_keywords)
```

**The Issue**: The `user_tweak_instruction` gets cleared in `correct_node` after processing:
```python
return {
    "prompt": correction_prompt,
    "user_tweak_instruction": None,  # Clear after use
    "status": "correcting"
}
```

So when `generate_node` runs, `state.get("user_tweak_instruction")` is `None`, causing the system to skip logo fetching entirely.

## The Fix

### 1. State Preservation Strategy
Added a new field `original_had_logos` to track whether the original generation included logos:

```python
# In JobState model
original_had_logos: bool  # Whether the original generation included logos
```

### 2. Enhanced Logo Detection Logic
Updated the logo detection logic in `generate_node` to preserve original configuration:

```python
# FIXED CODE
else:
    # For tweaks/corrections, check if original generation had logos
    original_had_logos = state.get("original_had_logos", False)
    
    # Also check if user's instruction mentions logo (if instruction still exists)
    user_instruction = state.get("user_tweak_instruction")
    logo_mentioned_in_tweak = False
    if user_instruction:
        instruction = user_instruction.lower()
        logo_keywords = ['logo', 'brand mark', 'icon', 'symbol', 'emblem']
        logo_mentioned_in_tweak = any(kw in instruction for kw in logo_keywords)

    # Use logos if: original had logos OR user specifically mentions logo in tweak
    needs_logos = original_had_logos or logo_mentioned_in_tweak
```

### 3. State Persistence
Ensured the `original_had_logos` flag is:
- Set when logos are first fetched in `generate_node`
- Preserved in `needs_review_node`, `complete_node`, and `tweak_completed_job_handler`
- Inferred from brand guidelines for legacy jobs that don't have this flag

## Files Modified

1. **`src/mobius/nodes/generate.py`**
   - Enhanced logo detection logic for tweak operations
   - Added `original_had_logos` to return state

2. **`src/mobius/models/state.py`**
   - Added `original_had_logos` field to `JobState` model

3. **`src/mobius/api/routes.py`**
   - Preserved `original_had_logos` in tweak handler
   - Added inference logic for legacy jobs

4. **`src/mobius/graphs/generation.py`**
   - Preserved `original_had_logos` in `needs_review_node` and `complete_node`

## Testing

Created comprehensive test suite in `scripts/test_logo_preservation_fix.py` that verifies:

✅ Logo configuration is preserved during tweak operations  
✅ Legacy jobs without the flag are handled safely  
✅ User mentions of logos in tweak instructions are detected  
✅ First-time generations continue to work correctly  

**Test Results**: All tests pass ✅

## Impact Assessment

### Before Fix
- Tweak operations would lose brand logos
- Generated images would have generic/AI-generated logos
- Brand compliance would fail on logo usage
- User experience degraded significantly

### After Fix
- Tweak operations maintain original logo configuration
- Brand logos are consistently preserved across all generations
- Compliance scores remain accurate
- User experience is seamless

## Deployment Notes

This fix is **backward compatible**:
- Legacy jobs without `original_had_logos` flag default to safe behavior
- No database migrations required
- No breaking changes to API contracts

## Prevention Measures

1. **Enhanced Logging**: Added detailed logging for logo detection decisions
2. **State Validation**: Improved state preservation across workflow nodes
3. **Test Coverage**: Comprehensive test suite for logo preservation scenarios

## Verification Steps

To verify the fix is working:

1. Generate an image with a brand that has logos
2. Request a tweak (e.g., "Please fix all critical violations")
3. Check logs for `has_logo=True` and `logo_count > 0` in the tweak generation
4. Verify the tweaked image maintains the brand logo

## Related Issues

This fix resolves the broader category of "state management failures during workflow transitions" and establishes a pattern for preserving critical configuration across multi-turn operations.