# Gemini Visual Analysis Fix - Identity Core Extraction

## Problem Discovered

Gemini WAS analyzing the screenshot, but the schema in `app_consolidated.py` was **not requiring** `identity_core`, so Gemini was skipping the archetype and voice vector analysis.

### What Was Happening

1. ✅ Playwright captures screenshot of website
2. ✅ Screenshot sent to Gemini Vision (`gemini-2.0-flash-exp`)
3. ❌ **Weak prompt** - only 3 lines, no archetype guide
4. ❌ **Schema missing "required" field** - Gemini skipped identity_core
5. ❌ Result: Visual scan returned colors/typography but NO archetype or voice vectors

### Evidence

**Test output from `visual_scan_stripe.com.json`:**
```json
{
  "colors": [...],          // ✓ Present
  "typography": [...],      // ✓ Present
  "visual_style": {...},    // ✓ Present
  // ❌ identity_core: MISSING!
}
```

**Expected output:**
```json
{
  "identity_core": {
    "archetype": "The Sage",
    "voice_vectors": {
      "formal": 0.8,
      "witty": 0.2,
      "technical": 0.7,
      "urgent": 0.1
    }
  },
  "colors": [...],
  "typography": [...],
  "visual_style": {...}
}
```

## Root Cause

The `app_consolidated.py` had a **simplified version** of the visual scraper with:

### Before (Broken)
```python
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "identity_core": {...},
        "colors": {...},
        ...
    },
    # ❌ NO "required" FIELD!
}

EXTRACTION_PROMPT = """You are an expert Brand Strategist analyzing a website screenshot.
Analyze the visual hierarchy, colors, typography, imagery, and copy tone.
Infer the Jungian archetype and voice characteristics.
Return strict JSON matching the schema."""
# ❌ Only 3 lines, no archetype guide!
```

**Result**: Gemini treated `identity_core` as optional and skipped it.

## Solution Implemented

### 1. Added "required" Field to Schema

```python
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "identity_core": {...},
        "colors": {...},
        "typography": {...},
        "visual_style": {...},
        "confidence": {...},
    },
    "required": ["identity_core", "colors", "typography", "visual_style", "confidence"],
    # ✓ NOW REQUIRED!
}
```

### 2. Enhanced Prompt with Archetype Guide

```python
EXTRACTION_PROMPT = """You are an expert Brand Strategist analyzing a website screenshot.

Your task is to infer the brand's identity by analyzing:
1. **Visual Hierarchy**: What elements dominate? What's emphasized?
2. **Color Psychology**: What emotions do the colors evoke?
3. **Typography**: What does the font choice communicate?
4. **Imagery Style**: What's the photography/illustration aesthetic?
5. **Copy Tone**: Analyze headlines and CTAs for voice characteristics

CRITICAL INSTRUCTIONS:
- Focus on the "above the fold" content (first screen)
- Identify the PRIMARY brand color (used for logos/headers)
- Identify ACCENT colors (used for buttons/CTAs)
- Infer the Jungian archetype based on visual + verbal cues
- Estimate voice vectors by analyzing headline tone and word choice
- Assign usage_weight based on visual prominence (0.0-1.0)

ARCHETYPE GUIDE:
- The Sage: Wisdom, expertise, thought leadership (e.g., universities, consultancies)
- The Hero: Achievement, courage, making an impact (e.g., Nike, sports brands)
- The Rebel: Disruption, revolution, breaking rules (e.g., Harley-Davidson, Tesla)
- The Innocent: Simplicity, purity, nostalgia (e.g., Dove, Coca-Cola)
- The Explorer: Freedom, discovery, adventure (e.g., Patagonia, Jeep)
- The Creator: Innovation, imagination, self-expression (e.g., Adobe, Lego)
- The Ruler: Control, leadership, responsibility (e.g., Mercedes-Benz, Rolex)
- The Magician: Transformation, vision, making dreams reality (e.g., Disney, Apple)
- The Lover: Intimacy, passion, sensuality (e.g., Chanel, Godiva)
- The Caregiver: Service, compassion, nurturing (e.g., Johnson & Johnson, UNICEF)
- The Jester: Joy, humor, living in the moment (e.g., Ben & Jerry's, Old Spice)
- The Everyman: Belonging, authenticity, down-to-earth (e.g., IKEA, Target)

Return strict JSON matching the schema. Be decisive - make your best inference even with limited information."""
```

### 3. Added Descriptions to Schema Fields

```python
"identity_core": {
    "type": "object",
    "properties": {
        "archetype": {
            "type": "string",
            "description": "Jungian brand archetype (e.g., 'The Sage', 'The Hero', 'The Rebel')"
        },
        "voice_vectors": {
            "type": "object",
            "description": "Voice dimensions as 0.0-1.0 scores",
            "properties": {
                "formal": {
                    "type": "number",
                    "description": "0.0 = casual, 1.0 = formal/professional"
                },
                ...
            }
        }
    }
}
```

## What This Fixes

### Before
```
Visual Scan → Gemini Analysis
                    ↓
{
  "colors": [4 colors],
  "typography": [1 font],
  "visual_style": {...},
  // ❌ identity_core: MISSING
}
```

### After
```
Visual Scan → Gemini Analysis (with detailed prompt + required fields)
                    ↓
{
  "identity_core": {
    "archetype": "The Sage",
    "voice_vectors": {
      "formal": 0.8,
      "witty": 0.2,
      "technical": 0.7,
      "urgent": 0.1
    }
  },
  "colors": [4 colors],
  "typography": [1 font],
  "visual_style": {...}
}
                    ↓
Ingestion Handler (now accepts visual_scan_data)
                    ↓
Brand with complete MOAT structure
                    ↓
Neo4j sync creates:
  - Archetype node
  - Voice vector relationships
  - Complete brand graph
```

## Testing the Fix

### 1. Deploy Updated Code
```bash
modal deploy src/mobius/api/app_consolidated.py
```

### 2. Test Visual Scan Directly
```bash
# Test the scan endpoint
python scripts/test_live_visual_scan.py

# Should now show:
# ✓ Archetype: "The Sage" (or similar)
# ✓ Voice Vectors: formal=0.8, witty=0.2, technical=0.7, urgent=0.1
```

### 3. Upload Brand Through Dashboard
1. Open `mobius-dashboard.html`
2. Enter URL: `stripe.com`
3. Click "Scan Website"
4. **Verify scan results show archetype** (check browser console)
5. Upload PDF + logo
6. Click "Upload Brand"

### 4. Verify Complete MOAT Structure
```bash
python scripts/run_moat_queries.py

# Should show:
# ✓ Archetype: "The Sage"
# ✓ Voice Vectors: 4 dimensions
# ✓ MOAT Status: COMPLETE
```

## Expected Log Output

After fix, visual scan should log:

```
🌐 Analyzing brand visuals for: https://stripe.com
  → Launching headless browser...
  → Visiting https://stripe.com...
  → Capturing screenshot...
  ✓ Screenshot captured (87285 bytes)
🧠 Analyzing with Gemini Vision...
  ✓ Analysis complete (confidence: 0.85)
  → Archetype: The Sage
  → Colors extracted: 4
```

Then during ingestion:

```
[info] visual_scan_data_received has_identity_core=True
[info] identity_core_enriched archetype="The Sage" voice_vector_count=4
[info] brand_created brand_id=...
[info] brand_synced_to_graph has_identity_core=True ...
```

## Why This Matters (MOAT Impact)

Without `identity_core`, brands are missing:

- ❌ Strategic positioning (archetype)
- ❌ Voice profile (formal, witty, technical, urgent scores)
- ❌ Brand similarity matching
- ❌ Voice-based recommendations
- ❌ Cross-brand trend analysis

With `identity_core`, you can:

- ✅ Find brands with similar archetypes
- ✅ Match voice profiles (formal + technical = enterprise SaaS)
- ✅ Recommend templates from similar brands
- ✅ Analyze industry trends by archetype
- ✅ **Stronger MOAT** - competitors can't replicate this intelligence

## Files Modified

1. `src/mobius/api/app_consolidated.py`
   - Added `"required"` field to EXTRACTION_SCHEMA
   - Enhanced EXTRACTION_PROMPT with archetype guide
   - Added descriptions to all schema fields

2. `src/mobius/api/routes.py` (previous fix)
   - Added `visual_scan_data` parameter
   - Added merge logic for identity_core

## Rollback

If issues occur:

```bash
git checkout HEAD~1 src/mobius/api/app_consolidated.py
modal deploy src/mobius/api/app_consolidated.py
```

## Success Criteria

✅ Visual scan returns `identity_core` with archetype and voice_vectors
✅ Ingestion handler merges visual scan data
✅ Brands have complete MOAT structure in Supabase
✅ Neo4j graph contains Archetype nodes and voice vector relationships
✅ MOAT queries return complete data

---

**Status**: Ready to deploy
**Impact**: CRITICAL - Enables complete MOAT structure
**Risk**: LOW - Gemini will now be required to provide identity_core
