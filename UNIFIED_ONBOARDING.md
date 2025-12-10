# Unified Brand Onboarding Flow

## Overview

The Mobius dashboard now features a **unified onboarding experience** where users can provide any combination of brand inputs, and the system intelligently orchestrates the extraction and merging of brand identity data.

## How It Works

### User Inputs (All Optional)

Users can provide any combination of:

1. **Website URL** - AI will scan the website and extract:
   - Brand colors from visual hierarchy
   - Typography families
   - Brand archetype (Jungian)
   - Voice characteristics
   - Visual style keywords

2. **Logo File** - Upload brand logo:
   - SVG (vector) - preferred for best quality
   - PNG with transparency
   - JPG (acceptable but not ideal)

3. **Brand Guidelines PDF** - Traditional brand guidelines document:
   - Colors, typography, voice rules
   - Logo usage guidelines
   - Brand governance rules

### The Magic ✨

When the user clicks **"Create Brand"**, the system:

1. **Scans the website** (if URL provided)
   - Launches headless Chromium browser
   - Captures high-fidelity screenshot
   - Sends to Gemini Vision for analysis
   - Extracts structured brand identity data

2. **Processes all assets together**
   - Uploads logo (if provided)
   - Uploads PDF (if provided)
   - Merges visual scan data with PDF/logo data

3. **Creates unified brand profile**
   - Single brand entity with merged data
   - All sources contribute to the final guidelines
   - Confidence scores indicate data quality

## Example Workflows

### Scenario 1: URL Only
```
User provides: https://stripe.com
System extracts:
- 5 brand colors (Blurple, Downriver, Slate, etc.)
- Typography: Inter, System UI
- Archetype: The Sage/The Ruler
- Voice: Formal (0.7), Technical (0.6)
```

### Scenario 2: URL + Logo
```
User provides: 
- URL: https://stripe.com
- Logo: stripe-logo.svg

System creates:
- Brand with visual identity from website
- High-quality logo asset for generation
- Combined confidence score
```

### Scenario 3: All Three
```
User provides:
- URL: https://stripe.com
- Logo: stripe-logo.svg
- PDF: Stripe_Brand_Guidelines.pdf

System creates:
- Most complete brand profile
- Visual scan validates PDF data
- Logo ready for asset generation
- Highest confidence scores
```

### Scenario 4: PDF Only (Traditional)
```
User provides: Stripe_Brand_Guidelines.pdf

System creates:
- Brand from PDF extraction
- Works like the original flow
```

## Technical Implementation

### Frontend (mobius-dashboard.html)

**New `createBrand()` function:**
- Validates at least one input is provided
- Shows progressive status updates
- Calls `/brands/scan` if URL provided
- Uploads all assets to `/brands/ingest`
- Passes `visual_scan_data` as JSON if available

### Backend (app_consolidated.py)

**Visual Scraper Function:**
- Consolidated into main Modal app
- Uses Playwright + Gemini Vision
- Returns structured JSON matching schema
- 60-second timeout for reliability

**Ingest Endpoint:**
- Accepts optional `visual_scan_data` parameter
- Merges visual scan with PDF extraction
- Prioritizes PDF data when conflicts exist
- Stores all sources for audit trail

## Benefits

1. **Flexibility** - Users choose their preferred input method
2. **Speed** - No separate "scan" button, everything happens at once
3. **Accuracy** - Multiple sources validate each other
4. **User Experience** - Single click, clear progress, unified result

## Testing

Use the provided test PDF generator:

```bash
python scripts/generate_stripe_pdf.py
```

This creates `Stripe_Brand_Guidelines.pdf` with:
- Identity core (archetype, voice vectors)
- Visual tokens (colors, typography)
- Governance rules

Then test in the dashboard:
1. Open `mobius-dashboard.html`
2. Connect to API
3. Try different combinations:
   - URL only: `https://stripe.com`
   - Logo only: Upload any logo file
   - PDF only: Upload generated PDF
   - All three: Complete onboarding

## Future Enhancements

- [ ] Real-time preview of extracted data before submission
- [ ] Conflict resolution UI when PDF and visual scan disagree
- [ ] Batch upload for multiple brands
- [ ] Import from Figma/Sketch design systems
- [ ] Export merged guidelines as new PDF
