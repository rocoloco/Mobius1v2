# Deployment Checklist - Neo4j MOAT Sync

## What Changed

### 1. Neo4j Sync Enhancement (`src/mobius/storage/graph.py`)
- **Before**: Only synced Brand, Color, Asset, Template, Feedback
- **After**: Syncs complete MOAT structure:
  - Identity Core (archetype, voice vectors, negative constraints)
  - Typography
  - Brand Rules
  - Contextual Rules (channel-specific)
  - Asset Graph (logo variants, templates, patterns)

### 2. Connection Fix (All storage files)
- **Before**: Used `asyncio.create_task()` for graph sync (caused routing errors)
- **After**: Uses `await` to ensure sync completes before request cleanup

## Files Modified

1. `src/mobius/storage/graph.py` - Enhanced sync with MOAT structure
2. `src/mobius/storage/brands.py` - Changed create_task to await
3. `src/mobius/storage/assets.py` - Changed create_task to await
4. `src/mobius/storage/templates.py` - Changed create_task to await
5. `src/mobius/storage/feedback.py` - Changed create_task to await

## Deployment Steps

### Option 1: Deploy to Modal (Recommended)

```bash
# Deploy the updated app
modal deploy src/mobius/api/app_consolidated.py

# Verify deployment
curl https://rocoloco--mobius-v2-final-fastapi-app.modal.run/v1/health
```

### Option 2: Test Locally First

```bash
# Run local server
modal serve src/mobius/api/app_consolidated.py

# In another terminal, test with dashboard
# Open mobius-dashboard.html and upload a brand
```

## Post-Deployment Verification

### 1. Upload a Test Brand
- Use the dashboard to upload a brand with PDF + logo
- Check logs for: `brand_synced_to_graph` with all MOAT fields

### 2. Verify Neo4j Sync
```bash
python scripts/inspect_neo4j_graph.py
```

Should show:
- Brand node
- Color nodes
- Typography nodes
- Archetype node (if extracted)
- Rule nodes
- ContextualRule nodes (if extracted)
- Voice vector relationships
- Asset graph relationships

### 3. Test Graph Queries
```bash
python scripts/verify_neo4j_sync.py
```

Should show brands in sync between Supabase and Neo4j.

## Current State

### Supabase (Source of Truth)
- ✅ Stripe brand exists
- ⚠️ Missing MOAT fields (uploaded with old code)

### Neo4j (Relationship Intelligence)
- ✅ Stripe brand synced
- ✅ 5 Colors, 1 Typography, 8 Rules
- ❌ No Identity Core (not in Supabase)
- ❌ No Asset Graph (not in Supabase)
- ❌ No Contextual Rules (not in Supabase)

## To Get Full MOAT Structure

### Option A: Re-upload Stripe Brand
1. Clear existing Stripe brand: `python scripts/clear_all_data.py`
2. Deploy updated code to Modal
3. Upload Stripe brand again through dashboard
4. Verify with `python scripts/inspect_neo4j_graph.py`

### Option B: Wait for Next Brand Upload
- Deploy updated code to Modal
- Upload a new brand (not Stripe)
- New brands will have full MOAT structure

## Testing the MOAT Sync Locally

```bash
# Test with full MOAT structure
python scripts/test_moat_sync.py

# Should show:
# ✅ Archetype synced
# ✅ Voice Vectors synced (4)
# ✅ Negative Constraints synced (3)
# ✅ Colors synced (2)
# ✅ Typography synced (2)
# ✅ Rules synced (2)
# ✅ Contextual Rules synced (2)
# ✅ Logo Variants synced (3)
# ✅ Templates synced (2)
# ✅ Patterns synced (1)
```

## Rollback Plan

If issues occur:

1. **Revert storage files**:
   ```bash
   git checkout HEAD~1 src/mobius/storage/*.py
   ```

2. **Redeploy**:
   ```bash
   modal deploy src/mobius/api/app_consolidated.py
   ```

3. **Clear Neo4j** (if needed):
   ```bash
   python scripts/clear_all_data.py
   ```

## Notes

- The Neo4j "Explore" tab shows random samples - use queries to see all data
- Existing brands won't have MOAT fields until re-uploaded
- The sync is non-blocking (0ms latency impact)
- Graph sync failures are logged but don't block brand creation
