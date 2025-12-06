# Database Migrations

This directory contains SQL migration files for the Mobius Phase 2 database schema.

## Migration Files

1. **001_initial_schema.sql** - Creates brands, assets, and jobs tables with indexes
2. **002_add_templates.sql** - Creates templates table
3. **003_add_feedback.sql** - Creates feedback table and learning activation trigger
4. **004_storage_buckets.sql** - Configures Supabase Storage buckets

## Running Migrations

### Option 1: Using Supabase CLI (Recommended)

```bash
# Install Supabase CLI if not already installed
npm install -g supabase

# Link to your Supabase project
supabase link --project-ref <your-project-ref>

# Push all migrations
supabase db push
```

### Option 2: Manual Execution

```bash
# Set your Supabase connection string
export SUPABASE_URL="postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres"

# Run migrations in order
psql $SUPABASE_URL -f 001_initial_schema.sql
psql $SUPABASE_URL -f 002_add_templates.sql
psql $SUPABASE_URL -f 003_add_feedback.sql
psql $SUPABASE_URL -f 004_storage_buckets.sql
```

### Option 3: Using Supabase Dashboard

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and paste each migration file content
4. Execute them in order (001, 002, 003, 004)

## Verification

After running migrations, verify the schema:

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check indexes
SELECT indexname, tablename FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;

-- Check triggers
SELECT trigger_name, event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema = 'public';

-- Check storage buckets
SELECT id, name, public, file_size_limit, allowed_mime_types 
FROM storage.buckets;
```

## Expected Schema

After all migrations:

### Tables
- `brands` - Brand entities with guidelines
- `assets` - Generated assets
- `jobs` - Async job tracking
- `templates` - Reusable generation configurations
- `feedback` - User feedback on assets

### Indexes
- `idx_brands_org` - Brand lookup by organization
- `idx_assets_brand` - Asset lookup by brand
- `idx_assets_job` - Asset lookup by job
- `idx_jobs_brand` - Job lookup by brand
- `idx_jobs_status` - Job lookup by status
- `idx_jobs_expires` - Expired job cleanup
- `idx_jobs_idempotency` - Idempotency key uniqueness
- `idx_templates_brand` - Template lookup by brand
- `idx_feedback_brand` - Feedback lookup by brand
- `idx_feedback_asset` - Feedback lookup by asset

### Triggers
- `feedback_learning_trigger` - Updates brand learning_active flag

### Storage Buckets
- `brands` - Brand guidelines PDFs (50MB limit, PDF only)
- `assets` - Generated images (10MB limit, PNG/JPEG/WebP)

## Connection Pooling

**IMPORTANT**: Always use the Supabase pooler URL (port 6543) for serverless deployments:

```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

Direct connections (port 5432) will exhaust connection limits under load in Modal's serverless environment.

## Rollback

To rollback migrations, you'll need to manually drop tables and objects:

```sql
-- Drop in reverse order to handle foreign key constraints
DROP TRIGGER IF EXISTS feedback_learning_trigger ON feedback;
DROP FUNCTION IF EXISTS update_learning_active();
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS templates CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS assets CASCADE;
DROP TABLE IF EXISTS brands CASCADE;

-- Remove storage buckets (via Supabase dashboard or API)
```

## Troubleshooting

### Connection Issues
- Verify your Supabase URL and credentials
- Ensure you're using the pooler URL (port 6543)
- Check that your IP is allowed in Supabase network settings

### Permission Errors
- Ensure you're using the service role key (not anon key)
- Verify your database user has CREATE TABLE permissions

### Storage Bucket Errors
- Storage buckets may need to be created via Supabase dashboard first
- Ensure storage API is enabled in your project
