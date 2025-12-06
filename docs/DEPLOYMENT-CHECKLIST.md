# Mobius Deployment Checklist

Use this checklist to ensure all deployment steps are completed.

## Pre-Deployment

- [ ] All tests passing (`pytest -v`)
- [ ] Code coverage > 80%
- [ ] All Phase 2 tasks completed
- [ ] Environment variables documented in `.env.example`
- [ ] API documentation up to date

## Modal Setup

- [ ] Modal CLI installed (`pip install modal`)
- [ ] Modal account created
- [ ] Modal authenticated (`modal token new`)
- [ ] Modal secrets created (`modal secret create mobius-secrets ...`)
- [ ] Modal secrets verified (`modal secret list`)

## Supabase Setup

- [ ] Supabase production project created
- [ ] Database password saved securely
- [ ] Pooler connection string obtained (port 6543)
- [ ] Project URL obtained
- [ ] Anon/public API key obtained
- [ ] Database migrations run successfully
  - [ ] 001_initial_schema.sql
  - [ ] 002_add_templates.sql
  - [ ] 003_add_feedback.sql
  - [ ] 004_learning_privacy.sql
  - [ ] 004_storage_buckets.sql
- [ ] Storage buckets created
  - [ ] "brands" bucket (50MB max, public)
  - [ ] "assets" bucket (10MB max, public)
- [ ] Row Level Security (RLS) policies configured (if needed)

## External Services

- [ ] Fal.ai API key obtained
- [ ] Google Gemini API key obtained
- [ ] API keys tested and working
- [ ] Rate limits understood and documented

## Deployment

- [ ] Staging deployment successful
- [ ] Health check passing
- [ ] Test brand ingestion working
- [ ] Test generation working
- [ ] Test async jobs working
- [ ] Test webhooks working
- [ ] All endpoints responding correctly
- [ ] Production deployment successful

## Post-Deployment Verification

- [ ] Health endpoint accessible
- [ ] API docs endpoint accessible
- [ ] All v1 endpoints responding
- [ ] Legacy endpoint working (backward compatibility)
- [ ] Database connections working
- [ ] Storage uploads working
- [ ] CDN URLs accessible
- [ ] Webhook delivery working
- [ ] Background job cleanup scheduled

## Monitoring Setup

- [ ] Modal logs accessible
- [ ] Supabase dashboard accessible
- [ ] Error tracking configured
- [ ] Performance monitoring enabled
- [ ] Cost alerts configured
- [ ] Uptime monitoring configured (optional)

## Documentation

- [ ] Deployment guide reviewed
- [ ] API documentation published
- [ ] Endpoint URLs documented
- [ ] Troubleshooting guide available
- [ ] Team notified of deployment

## Security

- [ ] Secrets stored securely (not in code)
- [ ] API keys rotated if needed
- [ ] Database password strong and secure
- [ ] Storage buckets have appropriate permissions
- [ ] Rate limiting configured
- [ ] CORS configured correctly

## Rollback Plan

- [ ] Previous version tagged in git
- [ ] Rollback procedure documented
- [ ] Database backup taken
- [ ] Emergency contacts identified

## Success Metrics

After deployment, verify:

- [ ] 3+ brands can be managed
- [ ] Compliance scores visible and accurate
- [ ] PDF ingestion working end-to-end
- [ ] Async jobs with webhooks working
- [ ] Template creation and reuse working
- [ ] Feedback collection working
- [ ] Learning system operational
- [ ] Response times < 500ms for list endpoints
- [ ] Response times < 2s for generation jobs
- [ ] No errors in logs for 1 hour

## Notes

Date deployed: _______________
Deployed by: _______________
Environment: [ ] Staging [ ] Production
Modal app name: mobius-v2
Supabase project: _______________

Issues encountered:
_______________________________________________
_______________________________________________
_______________________________________________

Resolution:
_______________________________________________
_______________________________________________
_______________________________________________
