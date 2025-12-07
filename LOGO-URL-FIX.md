# Logo URL Hallucination Fix

## Problem

The AI model was hallucinating logos (e.g., New Balance logo) instead of using the actual brand logo during image generation. This was caused by a critical bug where logo URLs were not being properly connected between the upload process and the generation workflow.

## Root Cause

When a brand was ingested:

1. **PDF Parsing**: The `PDFParser` created `LogoRule` objects with `url=""` (empty string)
2. **Logo Upload**: The logo was uploaded to Supabase Storage, and `logo_thumbnail_url` was set on the Brand object
3. **Database Storage**: Both `guidelines.logos[].url` (empty) and `logo_thumbnail_url` (valid URL) were saved
4. **Generation Workflow**: The `generate_node` tried to fetch logos from `guidelines.logos[].url`, which was empty!

This resulted in:
```
[warning] logo_download_failed error="Request URL is missing an 'http://' or 'https://' protocol." logo_url=
```

And the generation proceeded with `has_logo=False`, causing the model to hallucinate logos.

## Solution

### 1. Fixed Brand Ingestion (`src/mobius/api/routes.py`)

Added logic to sync `logo_thumbnail_url` to `guidelines.logos[].url` during brand creation:

```python
# Update logo URLs in guidelines if logo was uploaded
if logo_thumbnail_url and guidelines.logos:
    # Update the first logo rule with the actual uploaded URL
    for logo in guidelines.logos:
        if not logo.url or logo.url == "":
            logo.url = logo_thumbnail_url
            break
elif logo_thumbnail_url and not guidelines.logos:
    # No logos in guidelines, create a default one
    default_logo = LogoRule(
        variant_name="Primary Logo",
        url=logo_thumbnail_url,
        min_width_px=150,
        clear_space_ratio=0.1,
        forbidden_backgrounds=["#FFFFFF", "#000000"]
    )
    guidelines.logos.append(default_logo)
```

### 2. Fixed Brand Updates (`src/mobius/api/routes.py`)

Added the same logic to the `update_brand_handler` to handle logo URL updates.

### 3. Created Migration Script (`scripts/fix_logo_urls.py`)

Created a script to fix existing brands in the database:

```bash
# Fix all brands
python scripts/fix_logo_urls.py

# Fix brands for a specific organization
python scripts/fix_logo_urls.py <organization_id>
```

### 4. Created Verification Script (`scripts/verify_logo_urls.py`)

Created a script to verify logo URLs for a specific brand:

```bash
python scripts/verify_logo_urls.py <brand_id>
```

## Results

- **Fixed 10 brands** in the database with empty logo URLs
- **TestBrand999** (ID: `5ac1941d-97c8-4e8f-9957-42dacbcdc512`) now has a valid logo URL
- Future brand ingestions will automatically sync logo URLs correctly
- Logo updates will also sync properly

## Testing

To verify the fix works for new generations:

1. Run a new generation for the affected brand
2. Check the logs for:
   - `logo_downloaded` (instead of `logo_download_failed`)
   - `has_logo=True` (instead of `has_logo=False`)
   - `logo_count=1` (instead of `logo_count=0`)

The model should now use your actual brand logo instead of hallucinating one.

## Prevention

The fix ensures that:
- Logo URLs are always synced between `logo_thumbnail_url` and `guidelines.logos[].url`
- Default logo rules are created if none exist in the PDF
- Both brand creation and updates handle logo URL syncing
- The generation workflow will receive valid logo URLs

## Files Changed

- `src/mobius/api/routes.py` - Added logo URL syncing logic
- `scripts/fix_logo_urls.py` - Migration script for existing brands
- `scripts/verify_logo_urls.py` - Verification script for debugging
