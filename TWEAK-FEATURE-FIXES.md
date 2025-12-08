# Tweak Feature Fixes

## Issues Fixed

### Issue 1: Needs Review Not Showing Violations ✅

**Problem:** When an image scored 77.5% and went to `needs_review` status, the UI didn't show why it failed.

**Root Cause:** The `showReviewUI()` function was looking for `job.violations` directly, but violations are nested inside `job.state.compliance_scores[].categories[].violations`.

**Fix Applied:**
```javascript
// Extract compliance data from job state
const complianceScores = job.state?.compliance_scores || [];
const latestCompliance = complianceScores[complianceScores.length - 1] || {};
const categories = latestCompliance.categories || [];

// Extract all violations from categories
let allViolations = [];
categories.forEach(cat => {
  if (cat.violations && cat.violations.length > 0) {
    cat.violations.forEach(v => {
      allViolations.push({
        category: cat.category,
        description: v.description,
        severity: v.severity,
        fix_suggestion: v.fix_suggestion
      });
    });
  }
});
```

**Result:** Now shows:
- Compliance summary from audit
- All violations with category, description, and fix suggestions
- Proper severity indicators (critical/medium/low)

---

### Issue 2: Tweak Endpoint 404 Error ⚠️

**Problem:** 
```
POST /v1/jobs/239eacd8-e0d1-4057-bbae-c080fa954493/tweak -> 404 Not Found
```

**Root Cause:** The new tweak endpoint exists in code but hasn't been deployed to Modal yet.

**Fix Applied:**
1. Updated `tweak_completed_job_handler()` to accept both `completed` and `needs_review` statuses
2. Created deployment script: `deploy_tweak_feature.py`

**To Deploy:**
```bash
python deploy_tweak_feature.py
```

Or manually:
```bash
modal deploy src/mobius/api/app.py
```

**After Deployment:**
The endpoint will be available at:
```
POST https://rocoloco--mobius-v2-final-fastapi-app.modal.run/v1/jobs/{job_id}/tweak
```

---

## Additional Improvements

### 1. Tweak Works for Both Statuses

Updated the handler to accept:
- `completed` status (80%+ auto-approved images)
- `needs_review` status (70-95% images awaiting review)

This means users can tweak images in either state!

### 2. Better Error Messages

```python
raise ValidationError(
    code="JOB_NOT_TWEAKABLE",
    message=f"Job must be completed or needs_review to tweak (current: {job.status})",
    request_id=request_id,
    details={"current_status": job.status, "allowed_statuses": ["completed", "needs_review"]}
)
```

### 3. Compliance Summary Display

Added compliance summary to the review UI:
```javascript
${summary ? `
<div class="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
  <p class="text-xs font-semibold text-blue-900 mb-1">Compliance Summary</p>
  <p class="text-sm text-blue-800">${summary}</p>
</div>
` : ''}
```

---

## Testing After Deployment

### Test Case 1: Needs Review with Violations

1. Generate image that scores 70-95%
2. Verify violations are displayed with:
   - Category name
   - Description
   - Fix suggestion
   - Severity indicator
3. Click "Apply Custom Tweak"
4. Enter instruction addressing violations
5. Verify multi-turn refinement works

### Test Case 2: Completed Image Tweak

1. Generate image that scores 80%+
2. Image auto-approves
3. Click "Tweak" button
4. Enter refinement instruction
5. Verify multi-turn refinement works

### Test Case 3: Iterative Tweaking

1. Generate image
2. Tweak #1: "Make logo larger"
3. Tweak #2: "Adjust color to be more vibrant"
4. Tweak #3: "Add more depth of field"
5. Verify each tweak builds on previous context

---

## Deployment Checklist

- [x] Code changes committed
- [x] Handler updated to accept both statuses
- [x] UI updated to show violations
- [x] Deployment script created
- [ ] Deploy to Modal
- [ ] Test tweak endpoint
- [ ] Verify multi-turn conversation works
- [ ] Test with both completed and needs_review statuses

---

## Expected Behavior After Deployment

### Scenario: 77.5% Compliance Score

**Before Fix:**
```
❌ Image shows but no violations listed
❌ User doesn't know what's wrong
❌ Tweak button gives 404 error
```

**After Fix:**
```
✅ Compliance summary displayed
✅ All violations listed with details:
   - Typography: 65% (Using Open Sans instead of Playfair Display)
   - Colors: 85% (Gold contrast slightly low on metallic surface)
   - Logo: 82% (Water droplets partially obscure logo)
✅ User can click "Apply Custom Tweak"
✅ Multi-turn refinement works
```

### Scenario: 86% Compliance Score

**Before Fix:**
```
✅ Image auto-approved
❌ Tweak button gives 404 error
```

**After Fix:**
```
✅ Image auto-approved
✅ Detailed compliance breakdown shown
✅ Tweak button works
✅ Multi-turn refinement available
```

---

## API Documentation Update

### POST /v1/jobs/{job_id}/tweak

**Description:** Apply multi-turn tweak to refine an existing image.

**Allowed Job Statuses:**
- `completed` (80%+ auto-approved)
- `needs_review` (70-95% awaiting review)

**Request:**
```json
{
  "job_id": "239eacd8-e0d1-4057-bbae-c080fa954493",
  "tweak_instruction": "Make the logo 50% larger and ensure it uses Playfair Display font"
}
```

**Response:**
```json
{
  "job_id": "239eacd8-e0d1-4057-bbae-c080fa954493",
  "status": "resumed",
  "message": "Job resumed for multi-turn tweak",
  "request_id": "req_xxx"
}
```

**Errors:**
- `404 NOT_FOUND`: Job doesn't exist
- `400 JOB_NOT_TWEAKABLE`: Job is not in completed or needs_review status
- `400 TWEAK_INSTRUCTION_REQUIRED`: Tweak instruction is empty

---

## Next Steps

1. **Deploy to Modal:**
   ```bash
   python deploy_tweak_feature.py
   ```

2. **Test the fixes:**
   - Generate an image that scores 70-95%
   - Verify violations are displayed
   - Test tweak functionality
   - Verify multi-turn conversation works

3. **Monitor logs:**
   ```bash
   modal logs mobius-v2-final
   ```

4. **Update dashboard URL if needed:**
   The dashboard currently points to:
   ```
   https://rocoloco--mobius-v2-final-fastapi-app.modal.run/v1
   ```
   
   Verify this matches your deployed app name.
