-- Migration 001: Initial Schema
-- Creates brands, assets, and jobs tables with indexes

-- brands table
CREATE TABLE brands (
    brand_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    guidelines JSONB NOT NULL,
    pdf_url TEXT,
    logo_thumbnail_url TEXT,
    needs_review TEXT[] DEFAULT '{}',
    learning_active BOOLEAN DEFAULT FALSE,
    feedback_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_brands_org ON brands(organization_id) WHERE deleted_at IS NULL;

-- assets table
CREATE TABLE assets (
    asset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(brand_id),
    job_id UUID NOT NULL,
    prompt TEXT NOT NULL,
    image_url TEXT NOT NULL,
    compliance_score FLOAT,
    compliance_details JSONB,
    generation_params JSONB,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_assets_brand ON assets(brand_id);
CREATE INDEX idx_assets_job ON assets(job_id);

-- jobs table
CREATE TABLE jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(brand_id),
    status VARCHAR(50) NOT NULL,
    progress FLOAT DEFAULT 0,
    state JSONB NOT NULL,
    webhook_url TEXT,
    webhook_attempts INT DEFAULT 0,
    idempotency_key VARCHAR(64),
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours'
);

CREATE INDEX idx_jobs_brand ON jobs(brand_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_expires ON jobs(expires_at) WHERE expires_at IS NOT NULL;
CREATE UNIQUE INDEX idx_jobs_idempotency ON jobs(idempotency_key) 
    WHERE idempotency_key IS NOT NULL;
