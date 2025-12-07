# Migration 005: Compressed Digital Twin

## Overview

This migration adds support for the Gemini 3 dual-architecture refactoring by adding a `compressed_twin` JSONB column to the brands table.

## What Changed

### Database Schema
- **Added Column**: `compressed_twin JSONB` (nullable)
- **Added Index**: `idx_brands_compressed_twin` on `brands(brand_id)` where `compressed_twin IS NOT NULL`
- **Added Documentation**: Column comment explaining the field's purpose

### Why This Change?

The Gemini 3 Vision Model has a 65k token context window. To fit brand guidelines within this limit during image generation, we need a compressed representation that contains only essential visual rules:

- Semantic color hierarchy (primary, secondary, accent, neutral, semantic)
- Font families (names only)
- Critical visual constraints (dos and don'ts)
- Essential logo requirements

The full `guidelines` field remains unchanged and continues to store complete brand information for auditing and other purposes.

## Non-Breaking Change

This migration is **non-breaking** because:

1. The `compressed_twin` column is **nullable** - existing brands are not affected
2. No existing columns are modified or removed
3. The full `guidelines` field remains the source of truth
4. Applications can continue to work without using `compressed_twin`

## Migration Files

- **005_add_compressed_twin.sql** - Forward migration (adds column and index)
- **005_add_compressed_twin_rollback.sql** - Rollback migration (removes column and index)

## Testing

### Static Verification (No Database Required)
```bash
py scripts/verify_migration_005.py
```

This checks:
- Migration file exists and has correct syntax
- Rollback file exists and has correct syntax
- README is updated
- Brand model has CompressedDigitalTwin class

### Live Database Testing (Requires Supabase Connection)
```bash
py scripts/test_compressed_twin_migration.py
```

This tests:
1. Column exists and is queryable
2. Existing brands are not affected (nullable field)
3. New brands can store compressed twins
4. Compressed twins can be retrieved and updated
5. Token count validation works correctly

## Deployment Steps

### Option 1: Supabase CLI (Recommended)
```bash
supabase db push
```

### Option 2: Supabase Dashboard
1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and paste the content of `005_add_compressed_twin.sql`
4. Execute the SQL

### Option 3: Direct psql
```bash
psql $SUPABASE_URL -f supabase/migrations/005_add_compressed_twin.sql
```

## Rollback

If you need to rollback this migration:

### Option 1: Supabase Dashboard
1. Go to SQL Editor
2. Copy and paste the content of `005_add_compressed_twin_rollback.sql`
3. Execute the SQL

### Option 2: Direct psql
```bash
psql $SUPABASE_URL -f supabase/migrations/005_add_compressed_twin_rollback.sql
```

**Note**: Rollback is safe because the column is nullable. No data will be lost from the `guidelines` field.

## Data Migration Strategy

Existing brands will be migrated lazily:

1. **Lazy Migration**: When a brand is used for generation, if `compressed_twin` is NULL, extract it from the full guidelines
2. **Batch Migration**: A background job can be run to pre-populate `compressed_twin` for all existing brands
3. **Fallback**: If `compressed_twin` is missing, the system can use full guidelines (may hit token limits)

## Verification After Deployment

After applying the migration, verify it worked:

```sql
-- Check column exists
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'brands' AND column_name = 'compressed_twin';

-- Check index exists
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'brands' AND indexname = 'idx_brands_compressed_twin';

-- Check existing brands are unaffected
SELECT brand_id, name, 
       CASE WHEN compressed_twin IS NULL THEN 'NULL' ELSE 'EXISTS' END as compressed_twin_status
FROM brands
LIMIT 10;
```

Expected results:
- Column exists with type `jsonb` and `is_nullable = YES`
- Index exists with partial index condition `WHERE compressed_twin IS NOT NULL`
- Existing brands have `compressed_twin_status = 'NULL'`

## Related Files

- `src/mobius/models/brand.py` - Contains `CompressedDigitalTwin` and `Brand` models
- `src/mobius/tools/gemini.py` - Contains `extract_compressed_guidelines()` method
- `src/mobius/nodes/extract_visual.py` - Extracts compressed twin during ingestion
- `src/mobius/nodes/generate.py` - Uses compressed twin during generation

## Requirements Validated

This migration satisfies:
- **Requirement 2.5**: "WHEN extraction completes, THEN the Mobius System SHALL store the Compressed Digital Twin in the Brand Entity database record"
- **Requirement 7.5**: "THE Mobius System SHALL not introduce breaking changes to the database schema during this refactoring"

## Token Limit Enforcement

The `CompressedDigitalTwin` model includes validation:

```python
def estimate_tokens(self) -> int:
    """Estimate token count using tiktoken."""
    # Uses cl100k_base encoding (GPT-4/Gemini tokenizer)
    
def validate_size(self) -> bool:
    """Ensure compressed twin fits within 60k token limit."""
    return self.estimate_tokens() < 60000
```

This ensures the compressed twin will fit within the Vision Model's 65k context window (with 5k tokens of headroom for prompts).
