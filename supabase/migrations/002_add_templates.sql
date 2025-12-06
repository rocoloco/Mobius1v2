-- Migration 002: Templates
-- Creates templates table for reusable generation configurations

-- templates table
CREATE TABLE templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(brand_id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    generation_params JSONB NOT NULL,
    thumbnail_url TEXT,
    source_asset_id UUID REFERENCES assets(asset_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_templates_brand ON templates(brand_id) WHERE deleted_at IS NULL;
