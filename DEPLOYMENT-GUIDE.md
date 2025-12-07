# Mobius Deployment Guide

Complete guide for deploying Mobius to Modal with Gemini 3 integration.

## Prerequisites

Before deploying, ensure you have:

1. **Python 3.11+** installed locally
2. **Modal account** - Sign up at https://modal.com
3. **Supabase account** - Sign up at https://supabase.com
4. **Google Gemini API key** - Get from https://ai.google.dev

## Step 1: Get Your Gemini API Key

The Gemini API key is **required** for both image generation and compliance auditing.

1. Visit [Google AI Studio](https://ai.google.dev)
2. Sign in with your Google account
3. Click "Get API Key" in the top right corner
4. Create a new API key or use an existing one
5. Copy the API key (starts with `AIza...`)
6. Save it securely - you'll need it for Modal secrets

**Important Notes**:
- Use the API key from Google AI Studio, NOT Google Cloud Console
- Free tier: 15 requests per minute (RPM)
- Paid tier: 1000+ RPM (recommended for production)
- API key enables access to both Gemini 3 models:
  - `gemini-3-pro-image-preview` (Vision Model for generation)
  - `gemini-3-pro-preview` (Reasoning Model for auditing)

## Step 2: Set Up Supabase

### Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Choose organization and project name
4. Select region (choose closest to your users)
5. Generate a strong database password
6. Wait for project to provision (~2 minutes)

### Get Supabase Credentials

1. Go to Project Settings → API
2. Copy the following:
   - **Project URL**: `https://[project-ref].supabase.co`
   - **Anon/Public Key**: `eyJ...` (long JWT token)

### Get Pooler URL (CRITICAL for Production)

**Why pooler URL?** Modal's serverless architecture can spin up 100+ concurrent containers. Without connection pooling, you'll exhaust Supabase's connection limit (default: 100 connections).

1. Go to Project Settings → Database
2. Find "Connection Pooling" section
3. Copy the **Pooler URL** (port 6543):
   ```
   postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```

**Important**: Always use the pooler URL for production deployments!

### Run Database Migrations

1. Install Supabase CLI:
   ```bash
   npm install -g supabase
   ```

2. Link to your project:
   ```bash
   supabase link --project-ref [your-project-ref]
   ```

3. Apply migrations:
   ```bash
   supabase db push
   ```

   Or manually apply migration files:
   ```bash
   psql $DATABASE_URL < supabase/migrations/001_initial_schema.sql
   psql $DATABASE_URL < supabase/migrations/002_add_templates.sql
   psql $DATABASE_URL < supabase/migrations/003_add_feedback.sql
   psql $DATABASE_URL < supabase/migrations/004_learning_privacy.sql
   psql $DATABASE_URL < supabase/migrations/004_storage_buckets.sql
   psql $DATABASE_URL < supabase/migrations/005_add_compressed_twin.sql
   ```

### Verify Database Setup

```bash
# Check tables exist
psql $DATABASE_URL -c "\dt"

# Should show: brands, assets, jobs, templates, feedback, learning_settings
```

## Step 3: Set Up Modal

### Install Modal CLI

```bash
pip install modal
```

### Authenticate with Modal

```bash
modal token new
```

This will open a browser window to authenticate. Follow the prompts.

### Create Modal Secrets

Modal secrets are environment variables that are securely injected into your functions at runtime.

```bash
modal secret create mobius-secrets \
  GEMINI_API_KEY=your_gemini_api_key \
  SUPABASE_URL=your_supabase_pooler_url \
  SUPABASE_KEY=your_supabase_anon_key
```

**Example**:
```bash
modal secret create mobius-secrets \
  GEMINI_API_KEY=AIzaSyD... \
  SUPABASE_URL=postgresql://postgres.abc:pwd@aws-0-us-east-1.pooler.supabase.com:6543/postgres \
  SUPABASE_KEY=eyJhbGc...
```

### Verify Secrets

```bash
modal secret list
```

You should see `mobius-secrets` in the list.

## Step 4: Deploy to Modal

### Option 1: Using Deployment Script (Recommended)

```bash
python scripts/deploy.py
```

This script will:
1. Validate your Modal authentication
2. Check that secrets are configured
3. Deploy the application
4. Display the web endpoint URL

### Option 2: Manual Deployment

```bash
modal deploy src/mobius/api/app.py
```

### Verify Deployment

```bash
# List deployed apps
modal app list

# Should show: mobius-v2

# View deployment logs
modal app logs mobius-v2
```

### Get Your API Endpoint

```bash
modal app show mobius-v2
```

Look for the "Web endpoints" section. Your API will be available at:
```
https://[your-workspace]--mobius-v2-[function-name].modal.run
```

## Step 5: Test Your Deployment

### Health Check

```bash
curl https://[your-endpoint]/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "healthy",
  "storage": "healthy",
  "api": "healthy",
  "timestamp": "2025-12-06T10:00:00Z",
  "request_id": "req_abc123"
}
```

### Test Brand Ingestion

```bash
curl -X POST https://[your-endpoint]/v1/brands/ingest \
  -F "organization_id=test-org" \
  -F "brand_name=Test Brand" \
  -F "file=@path/to/brand-guidelines.pdf"
```

### Test Image Generation

```bash
curl -X POST https://[your-endpoint]/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": "brand-123",
    "prompt": "Modern tech startup logo",
    "async_mode": false
  }'
```

## Step 6: Monitor Your Deployment

### View Logs

```bash
# Real-time logs
modal app logs mobius-v2 --follow

# Last 100 lines
modal app logs mobius-v2 --lines 100
```

### Check Database

```bash
# Connect to Supabase
psql $DATABASE_URL

# Check recent jobs
SELECT job_id, status, created_at FROM jobs ORDER BY created_at DESC LIMIT 10;

# Check brands
SELECT brand_id, name, created_at FROM brands;
```

### Monitor API Usage

1. Go to [Google AI Studio](https://ai.google.dev)
2. Click on your API key
3. View usage metrics and quotas

## Troubleshooting

### "Invalid API key" (401 Error)

**Cause**: Gemini API key is incorrect or not set

**Solution**:
1. Verify API key in Modal secrets:
   ```bash
   modal secret list
   ```
2. Test API key directly:
   ```bash
   curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
   ```
3. If invalid, recreate the secret:
   ```bash
   modal secret delete mobius-secrets
   modal secret create mobius-secrets GEMINI_API_KEY=new_key ...
   ```

### "Rate limit exceeded" (429 Error)

**Cause**: Exceeded Gemini API rate limits

**Solution**:
- Free tier: 15 RPM (requests per minute)
- Upgrade to paid tier for 1000+ RPM
- System automatically retries with exponential backoff
- Check quota at https://ai.google.dev

### "Too many connections" Error

**Cause**: Not using Supabase pooler URL

**Solution**:
1. Verify you're using pooler URL (port 6543):
   ```bash
   modal secret list
   # Check SUPABASE_URL contains "pooler.supabase.com:6543"
   ```
2. If using direct connection, update secret:
   ```bash
   modal secret delete mobius-secrets
   modal secret create mobius-secrets \
     GEMINI_API_KEY=... \
     SUPABASE_URL=postgresql://...pooler.supabase.com:6543/postgres \
     SUPABASE_KEY=...
   ```

### Deployment Fails

**Cause**: Missing dependencies or configuration

**Solution**:
1. Check Modal authentication:
   ```bash
   modal token new
   ```
2. Verify secrets exist:
   ```bash
   modal secret list
   ```
3. Check deployment logs:
   ```bash
   modal app logs mobius-v2
   ```

### PDF Ingestion Fails

**Cause**: PDF format or Gemini API issues

**Solution**:
1. Verify PDF is under 50MB
2. Ensure PDF has extractable text (not scanned images)
3. Check Gemini API status at https://status.cloud.google.com
4. Review logs for specific errors:
   ```bash
   modal app logs mobius-v2 | grep "ingestion"
   ```

## Production Checklist

Before going to production, ensure:

- [ ] Using Supabase pooler URL (port 6543)
- [ ] Gemini API key is from paid tier (1000+ RPM)
- [ ] Database migrations applied successfully
- [ ] Health check endpoint returns 200
- [ ] Test brand ingestion works
- [ ] Test image generation works
- [ ] Monitoring and alerting configured
- [ ] Backup strategy in place for Supabase
- [ ] API rate limits understood and monitored
- [ ] Webhook endpoints tested (if using async mode)

## Updating Your Deployment

### Update Code

```bash
# Pull latest changes
git pull origin main

# Redeploy
modal deploy src/mobius/api/app.py
```

### Update Secrets

```bash
# Delete old secret
modal secret delete mobius-secrets

# Create new secret with updated values
modal secret create mobius-secrets \
  GEMINI_API_KEY=new_key \
  SUPABASE_URL=new_url \
  SUPABASE_KEY=new_key
```

### Run New Migrations

```bash
supabase db push
```

## Cost Estimates

### Gemini API Costs

| Operation | Model | Cost per Request |
|-----------|-------|------------------|
| Image Generation | Gemini 3 Pro Image Preview | $0.03 |
| Compliance Audit | Gemini 3 Pro Preview | $0.001 |
| PDF Parsing | Gemini 3 Pro Preview | $0.002 |

### Example Monthly Costs

**Small Agency (5 brands, 100 assets/month)**:
- Onboarding: 5 × $0.002 = $0.01
- Generation: 100 × $0.031 = $3.10
- **Total**: ~$3/month

**Medium Agency (20 brands, 500 assets/month)**:
- Onboarding: 20 × $0.002 = $0.04
- Generation: 500 × $0.031 = $15.50
- **Total**: ~$16/month

**Large Agency (50 brands, 2000 assets/month)**:
- Onboarding: 50 × $0.002 = $0.10
- Generation: 2000 × $0.031 = $62
- **Total**: ~$62/month

### Modal Costs

- Free tier: 30 CPU-hours/month
- Paid tier: $0.0001 per CPU-second
- Typical request: 5-10 seconds
- Cost per request: ~$0.0005-$0.001

### Supabase Costs

- Free tier: 500MB database, 1GB storage
- Pro tier: $25/month (8GB database, 100GB storage)
- Recommended for production: Pro tier

## Support

For issues and questions:
- GitHub Issues: [Your Repo]
- Documentation: This guide + README.md + MOBIUS-ARCHITECTURE.md
- API Docs: https://[your-endpoint]/v1/docs
- Gemini API: https://ai.google.dev/docs
- Modal Docs: https://modal.com/docs
- Supabase Docs: https://supabase.com/docs

## Next Steps

After successful deployment:

1. **Configure Monitoring**: Set up alerts for API errors and rate limits
2. **Test Webhooks**: If using async mode, test webhook delivery
3. **Load Testing**: Test with concurrent requests to verify scaling
4. **Backup Strategy**: Configure Supabase backups
5. **Documentation**: Update API documentation with your endpoint URL
6. **Client Integration**: Update frontend to use production endpoint

---

**Deployment Version**: 2.0 (Gemini 3 Dual-Architecture)  
**Last Updated**: December 6, 2025
