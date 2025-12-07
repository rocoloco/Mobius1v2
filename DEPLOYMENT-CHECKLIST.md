# Deployment Checklist - Logo Generation Fixes

## Pre-Deployment

- [x] Fix logo URL syncing in brand ingestion
- [x] Fix logo URL syncing in brand updates
- [x] Create migration script for existing brands
- [x] Run migration script (fixed 10 brands)
- [x] Verify logo URLs are populated
- [x] Add text overlay constraints to system prompt
- [x] Add logo distortion prevention to system prompt
- [x] Add constraints to prompt optimization
- [x] Run diagnostics (no errors)

## Deployment

```bash
# 1. Verify environment variables are set
python -c "import os; print('GEMINI_API_KEY:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'); print('SUPABASE_URL:', os.getenv('SUPABASE_URL', 'NOT SET'))"

# 2. Run tests (if available)
pytest tests/ -v

# 3. Deploy to Modal
modal deploy src/mobius/api/app_consolidated.py

# 4. Verify deployment
curl https://your-modal-url.modal.run/v1/health
```

## Post-Deployment Testing

### Test 1: Logo URL Verification
```bash
# Verify a brand has valid logo URLs
python scripts/verify_logo_urls.py <brand_id>

# Expected output:
# ✅ Logo URL looks valid
# ✅ No logo URL issues detected
```

### Test 2: Image Generation - No Text Overlays
**Prompt**: "a professional photo of a woman drinking from a water bottle after a long run in the city. the water bottle has our logo on it"

**Expected**:
- ✅ Pure photographic scene
- ❌ No text overlays (no "REFRESH YOUR RUN", etc.)
- ✅ Logo visible on bottle
- ✅ Logo appears flat/undistorted

**Check Logs For**:
```
[info] logo_downloaded (not logo_download_failed)
[info] has_logo=True (not False)
[info] logo_count=1 (not 0)
```

### Test 3: Image Generation - Logo Placement
**Prompt**: "a product shot of our water bottle on a wooden table with natural lighting"

**Expected**:
- ✅ Logo on bottle is flat
- ✅ No perspective distortion
- ✅ Logo maintains proper proportions

### Test 4: Audit Compliance
**Check**:
- Overall score >= 80
- Logo_usage category score improves (was 45, should be 70+)
- No violations for "distorted logo"

## Rollback Plan

If issues occur:

```bash
# 1. Revert to previous Modal deployment
modal app stop

# 2. Check previous deployment
modal app list

# 3. Redeploy previous version
# (Modal keeps previous versions)
```

## Monitoring

After deployment, monitor for:

1. **Logo Download Success Rate**
   - Check logs for `logo_downloaded` vs `logo_download_failed`
   - Should be 100% success for brands with logos

2. **Text Overlay Issues**
   - Review generated images for unwanted text
   - Check user feedback/complaints

3. **Logo Distortion Issues**
   - Review audit violations for logo_usage
   - Check for "distorted logo" violations

4. **Audit Scores**
   - Monitor overall_score trends
   - Track logo_usage category scores

## Success Criteria

- [ ] Logo URLs populated for all brands with logos
- [ ] Logo download success rate = 100%
- [ ] Zero text overlays in generated images
- [ ] Logo_usage audit scores >= 70
- [ ] No "distorted logo" violations
- [ ] User satisfaction with generated images

## Contact

If issues arise:
1. Check logs in Modal dashboard
2. Run verification scripts
3. Review audit results
4. Check this documentation for troubleshooting
