# Visual Brand Scraper - Testing Guide

## Quick Start

The visual scraper is a standalone Modal function that can be tested in 3 ways:

### 1. Modal Dashboard (Easiest - No Code)

1. Deploy the function:
   ```bash
   modal deploy src.mobius.ingestion.visual_scraper
   ```

2. Open Modal dashboard: https://modal.com/apps

3. Find `mobius-visual-scraper` → `analyze_brand_visuals`

4. Click "Run" and enter a URL in the web UI

5. View results in real-time

### 2. Modal CLI (Quick Test)

```bash
# Test with default URL (Stripe)
modal run src.mobius.ingestion.visual_scraper

# Test with custom URL
modal run src.mobius.ingestion.visual_scraper --url "https://nike.com"
```

### 3. Python Test Suite (Batch Testing)

```bash
# Run against multiple brands
python scripts/test_visual_scraper.py
```

This tests against Stripe, Nike, Apple, and Patagonia to validate extraction quality.

## What Gets Extracted

The scraper returns structured JSON with:

```json
{
  "identity_core": {
    "archetype": "The Sage",
    "voice_vectors": {
      "formal": 0.7,
      "witty": 0.3,
      "technical": 0.8,
      "urgent": 0.4
    }
  },
  "colors": [
    {
      "name": "Stripe Purple",
      "hex": "#635BFF",
      "usage": "primary",
      "usage_weight": 0.6
    }
  ],
  "typography": [
    {
      "family": "Inter",
      "usage": "Headlines and body text"
    }
  ],
  "visual_style": {
    "keywords": ["minimalist", "technical", "modern"],
    "imagery_style": "abstract gradients and UI mockups"
  },
  "confidence": 0.85
}
```

## Expected Performance

- **Latency**: 8-12 seconds per URL
  - 3-5s: Page load + screenshot
  - 5-7s: Gemini vision analysis

- **Cost**: ~$0.005 per analysis
  - Modal compute: ~$0.001
  - Gemini 1.5 Flash: ~$0.004

- **Success Rate**: 
  - Static sites: ~95%
  - SPAs (React/Vue): ~90%
  - Heavy anti-bot: ~60% (Cloudflare, etc.)

## Troubleshooting

### "Page load timeout"
- Site is slow or has aggressive bot detection
- Try increasing timeout in `visual_scraper.py` (line 234)

### "Browser launch failed"
- Modal image build issue
- Redeploy: `modal deploy src.mobius.ingestion.visual_scraper`

### "Gemini analysis failed"
- Check GEMINI_API_KEY in Modal secrets
- Verify: `modal secret list`

### Low confidence scores (<0.5)
- Site has minimal branding on landing page
- Try a different URL (e.g., /about page)

## Next Steps

Once validated, integrate into your API:

1. Add async job pattern (like twin generation)
2. Store results in `brand_scrapes` table
3. Build "scanner" UI with progress updates
4. Add caching by domain to reduce costs

## Testing Checklist

- [ ] Deploy to Modal successfully
- [ ] Test via Modal dashboard with 1 URL
- [ ] Run CLI test with 3 different brands
- [ ] Verify color extraction accuracy
- [ ] Verify archetype makes sense
- [ ] Check confidence scores (should be >0.6)
- [ ] Test with a SPA (React/Vue site)
- [ ] Test with a site that blocks bots
