# Mobius Phase 2 Deployment Guide

This guide walks you through deploying Mobius to Modal with Supabase production.

## Prerequisites

- Python 3.11+
- Modal account (sign up at https://modal.com)
- Supabase account (sign up at https://supabase.com)
- API keys for Fal.ai and Google Gemini

## Step 1: Install Modal CLI

```bash
pip install modal
```

Verify installation:
```bash
modal --version
```

## Step 2: Authenticate with Modal

```bash
modal token new
```

This will open a browser window to authenticate. Follow the prompts to complete authentication.

## Step 3: Set Up Supabase Production Project

### 3.1 Create New Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Choose a name (e.g., "mobius-production")
4. Select a region close to your users
5. Generate a strong database password
6. Wait for project to be provisioned (~2 minutes)

### 3.2 Get Connection Details

From your Supabase project dashboard:

1. Go to Settings → Database
2. Copy the **Pooler Connection String** (Transaction mode, port 6543)
   - Format: `postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`
3. Go to Settings → API
4. Copy the **anon/public** key
5. Copy the **Project URL**

### 3.3 Run Database Migrations

```bash
# Install Supabase CLI if not already installed
npm install -g supabase

# Link to your project
supabase link --project-ref your-project-ref

# Run migrations
supabase db push
```

Or manually run migrations in the SQL Editor:
1. Go to SQL Editor in Supabase dashboard
2. Run each migration file in order:
   - `supabase/migrations/001_initial_schema.sql`
   - `supabase/migrations/002_add_templates.sql`
   - `supabase/migrations/003_add_feedback.sql`
   - `supabase/migrations/004_learning_privacy.sql`
   - `supabase/migrations/004_storage_buckets.sql`

### 3.4 Create Storage Buckets

In Supabase dashboard:
1. Go to Storage
2. Create bucket "brands" (50MB max file size, public)
3. Create bucket "assets" (10MB max file size, public)

## Step 4: Configure Modal Secrets

Create a Modal secret with all required environment variables:

```bash
modal secret create mobius-secrets \
  FAL_KEY=your_fal_api_key \
  GEMINI_API_KEY=your_gemini_api_key \
  SUPABASE_URL=https://your-project.supabase.co \
  SUPABASE_KEY=your_supabase_anon_key
```

Verify the secret was created:
```bash
modal secret list
```

You should see "mobius-secrets" in the list.

## Step 5: Deploy to Modal

### 5.1 Run Pre-Deployment Checks

```bash
# Run tests
pytest -v

# Check file sizes
python scripts/deploy.py --skip-tests --skip-health-check
```

### 5.2 Deploy to Staging

```bash
python scripts/deploy.py --environment staging
```

Or deploy directly with Modal CLI:
```bash
modal deploy src/mobius/api/app.py
```

### 5.3 Get Endpoint URLs

After deployment, Modal will output the endpoint URLs. They will look like:
```
https://your-workspace--mobius-v2-v1-health.modal.run
https://your-workspace--mobius-v2-v1-generate.modal.run
...
```

Save these URLs for testing.

## Step 6: Verify Deployment

### 6.1 Health Check

```bash
curl https://your-workspace--mobius-v2-v1-health.modal.run
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "storage": "connected",
  "api": "v1",
  "request_id": "..."
}
```

### 6.2 Test Brand Ingestion

```bash
curl -X POST https://your-workspace--mobius-v2-v1-ingest-brand.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "test-org",
    "brand_name": "Test Brand",
    "file": "...",
    "content_type": "application/pdf",
    "filename": "guidelines.pdf"
  }'
```

### 6.3 Test Generation

```bash
curl -X POST https://your-workspace--mobius-v2-v1-generate.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": "your-brand-id",
    "prompt": "A modern logo with clean lines"
  }'
```

## Step 7: Set Up Monitoring

### 7.1 Modal Logs

View real-time logs:
```bash
modal app logs mobius-v2
```

View logs for specific function:
```bash
modal app logs mobius-v2 --function v1_generate
```

### 7.2 Supabase Dashboard

Monitor in Supabase dashboard:
1. Database → Table Editor (view data)
2. Database → Query Performance (monitor queries)
3. Storage → Usage (monitor file storage)
4. Logs → API Logs (view API requests)

### 7.3 Set Up Alerts (Optional)

In Supabase:
1. Go to Settings → Alerts
2. Set up alerts for:
   - Database CPU usage > 80%
   - Storage usage > 80%
   - API error rate > 5%

## Step 8: Production Deployment

Once staging is verified:

```bash
python scripts/deploy.py --environment production
```

**Important:** Production deployment will prompt for confirmation.

## Troubleshooting

### Modal Authentication Issues

```bash
# Re-authenticate
modal token new

# Check current token
modal token list
```

### Database Connection Issues

- Verify you're using the **pooler URL** (port 6543)
- Check database password is correct
- Verify IP allowlist in Supabase (should allow all for serverless)

### Storage Issues

- Verify buckets are created and public
- Check bucket size limits match configuration
- Verify MIME type restrictions

### Deployment Failures

```bash
# View detailed logs
modal app logs mobius-v2 --tail

# Check function status
modal app list

# Redeploy specific function
modal deploy src/mobius/api/app.py
```

## Useful Commands

```bash
# List all Modal apps
modal app list

# View app details
modal app show mobius-v2

# Stop all functions
modal app stop mobius-v2

# View secrets
modal secret list

# Update secret
modal secret create mobius-secrets --force \
  FAL_KEY=new_key \
  ...

# Run function locally for testing
modal run src/mobius/api/app.py::v1_health
```

## Next Steps

1. Set up custom domain (optional)
2. Configure rate limiting
3. Set up CI/CD pipeline
4. Monitor costs in Modal dashboard
5. Set up backup strategy for Supabase

## Support

- Modal Docs: https://modal.com/docs
- Supabase Docs: https://supabase.com/docs
- Modal Discord: https://discord.gg/modal
- Supabase Discord: https://discord.supabase.com
