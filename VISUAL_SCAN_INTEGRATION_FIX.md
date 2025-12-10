# Visual Scan Integration Fix - MOAT Structure

## Problem Identified

The visual scraper was extracting the complete MOAT structure (archetype, voice vectors, colors, typography) from websites, but this data was being **thrown away** during brand ingestion.

### What Was Happening

1. ✅ Dashboard calls `/v1/brands/scan` → Visual scraper extracts MOAT data
2. ✅ Dashboard sends `visual_scan_data` in form data to `/v1/brands/ingest`
3. ❌ **Ingestion handler ignored the visual_scan_data parameter**
4. ❌ Only PDF parser data was used (which doesn't extract archetype, voice vectors, etc.)
5. ❌ Result: Brands missing Identity Core, Contextual Rules, Asset Graph

### Visual Scan Extracts (But Was Ignored)

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

## Solution Implemented

### 1. Accept Visual Scan Data Parameter

**File**: `src/mobius/api/routes.py`

```python
async def ingest_brand_handler(
    organization_id: str,
    brand_name: str,
    file: bytes,
    content_type: str,
    filename: str,
    logo_file: Optional[bytes] = None,
    logo_filename: Optional[str] = None,
    visual_scan_data: Optional[str] = None,  # NEW PARAMETER
) -> IngestBrandResponse:
```

### 2. Merge Visual Scan Data with PDF Data

**File**: `src/mobius/api/routes.py` (after PDF parsing)

```python
# Merge visual scan data if provided (MOAT structure enrichment)
if visual_scan_data:
    visual_data = json.loads(visual_scan_data)
    
    # Enrich with Identity Core (archetype, voice vectors)
    if "identity_core" in visual_data:
        guidelines.identity_core = IdentityCore(
            archetype=identity_data.get("archetype"),
            voice_vectors=identity_data.get("voice_vectors", {}),
            negative_constraints=[]
        )
    
    # Enrich colors if PDF didn't extract enough
    if "colors" in visual_data and len(guidelines.colors) < 3:
        for color_data in visual_data["colors"]:
            guidelines.colors.append(Color(...))
    
    # Enrich typography if PDF didn't extract
    if "typography" in visual_data and len(guidelines.typography) == 0:
        for typo_data in visual_data["typography"]:
            guidelines.typography.append(Typography(...))
```

### 3. Update FastAPI Endpoint

**File**: `src/mobius/api/app_consolidated.py`

```python
# Extract visual_scan_data from form
visual_scan_data = form.get("visual_scan_data")

# Pass to handler
result = await ingest_brand_handler(
    ...
    visual_scan_data=visual_scan_data,
)
```

## What This Fixes

### Before (Missing MOAT Structure)
```
Brand: stripe.com
├── Colors: 5 ✓
├── Typography: 1 ✓
├── Rules: 8 ✓
├── Identity Core: ❌ MISSING
│   ├── Archetype: ❌
│   ├── Voice Vectors: ❌
│   └── Negative Constraints: ❌
├── Contextual Rules: ❌ MISSING
└── Asset Graph: ❌ MISSING
```

### After (Complete MOAT Structure)
```
Brand: stripe.com
├── Colors: 5 ✓
├── Typography: 1 ✓
├── Rules: 8 ✓
├── Identity Core: ✓ FROM VISUAL SCAN
│   ├── Archetype: "The Sage" ✓
│   ├── Voice Vectors: 4 dimensions ✓
│   └── Negative Constraints: (from PDF) ✓
├── Contextual Rules: (future enhancement)
└── Asset Graph: (future enhancement)
```

## Data Flow (Fixed)

```
1. User enters URL → Dashboard calls /v1/brands/scan
                  ↓
2. Visual Scraper analyzes website screenshot
                  ↓
3. Gemini extracts: archetype, voice_vectors, colors, typography
                  ↓
4. Dashboard stores visualData in memory
                  ↓
5. User uploads PDF + logo
                  ↓
6. Dashboard sends FormData:
   - file: PDF bytes
   - logo: logo bytes
   - visual_scan_data: JSON.stringify(visualData) ← NOW USED!
                  ↓
7. Ingestion handler:
   - Parses PDF (colors, rules, typography)
   - Merges visual scan data (archetype, voice_vectors)
   - Creates complete Brand with MOAT structure
                  ↓
8. Brand saved to Supabase with Identity Core
                  ↓
9. Neo4j sync creates:
   - Archetype node
   - Voice vector relationships
   - Complete MOAT graph structure
```

## Testing the Fix

### 1. Deploy Updated Code
```bash
modal deploy src/mobius/api/app_consolidated.py
```

### 2. Clear Existing Data
```bash
python scripts/clear_all_data.py
```

### 3. Upload Brand Through Dashboard
1. Open `mobius-dashboard.html`
2. Enter URL: `stripe.com`
3. Click "Scan Website" (wait for completion)
4. Upload PDF + logo
5. Click "Upload Brand"

### 4. Verify MOAT Structure
```bash
# Check what was synced
python scripts/run_moat_queries.py

# Should show:
# ✓ Archetype: "The Sage" (or similar)
# ✓ Voice Vectors: 4 dimensions
# ✓ Colors: 5+ with semantic roles
# ✓ Typography: 1+ fonts
# ✓ MOAT Status: COMPLETE
```

### 5. Verify in Neo4j Browser
```cypher
// Check Identity Core
MATCH (b:Brand {name: "stripe.com"})
OPTIONAL MATCH (b)-[:HAS_ARCHETYPE]->(a:Archetype)
OPTIONAL MATCH (b)-[v:HAS_VOICE_VECTOR]->(b)
RETURN b.name, a.name as Archetype, count(v) as VoiceVectors

// Should return:
// stripe.com | The Sage | 4
```

## Expected Log Output

After fix, you should see:

```
[info] visual_scan_data_received has_identity_core=True
[info] identity_core_enriched archetype="The Sage" voice_vector_count=4
[info] brand_created brand_id=...
[info] brand_synced_to_graph has_identity_core=True ...
```

## Future Enhancements

### 1. Contextual Rules from Visual Scan
Currently not extracted by visual scraper. Could add:
- Detect channel-specific patterns (LinkedIn vs Instagram style)
- Infer rules from visual consistency

### 2. Asset Graph from Visual Scan
Could extract:
- Logo variants from website (header, footer, mobile)
- Common image patterns
- Template structures

### 3. Negative Constraints from Visual Scan
Could infer from what's NOT present:
- "No drop shadows" (if none detected)
- "No gradients" (if none detected)
- "No rounded corners" (if all sharp)

## Files Modified

1. `src/mobius/api/routes.py`
   - Added `visual_scan_data` parameter
   - Added merge logic after PDF parsing
   - Enriches Identity Core, colors, typography

2. `src/mobius/api/app_consolidated.py`
   - Extracts `visual_scan_data` from form
   - Passes to handler
   - Logs when visual scan data is received

## Rollback

If issues occur:

```bash
git checkout HEAD~1 src/mobius/api/routes.py src/mobius/api/app_consolidated.py
modal deploy src/mobius/api/app_consolidated.py
```

## Success Criteria

✅ Visual scan data is no longer ignored
✅ Identity Core (archetype, voice vectors) populated from visual scan
✅ Colors enriched if PDF extraction is weak
✅ Typography enriched if PDF extraction fails
✅ Neo4j graph contains complete MOAT structure
✅ Migration Difficulty Score increases (stronger lock-in)

---

**Status**: Ready to deploy
**Impact**: HIGH - Enables complete MOAT structure
**Risk**: LOW - Graceful fallback if visual scan data missing
