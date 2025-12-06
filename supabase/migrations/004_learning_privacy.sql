-- Migration 004: Learning Privacy System
-- 
-- This migration creates the database schema for Mobius's meta-learning system
-- with privacy controls. It supports three privacy tiers:
-- - OFF: No learning
-- - PRIVATE: Brand-only learning (default)
-- - SHARED: Anonymized industry learning (opt-in)

-- learning_settings table
-- Stores privacy preferences and consent tracking for each brand
CREATE TABLE learning_settings (
    brand_id UUID PRIMARY KEY REFERENCES brands(brand_id) ON DELETE CASCADE,
    privacy_tier VARCHAR(20) NOT NULL DEFAULT 'private' 
        CHECK (privacy_tier IN ('off', 'private', 'shared')),
    consent_date TIMESTAMPTZ,
    consent_version VARCHAR(10) NOT NULL DEFAULT '1.0',
    data_retention_days INT NOT NULL DEFAULT 365 CHECK (data_retention_days > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for querying settings
CREATE INDEX idx_learning_settings_tier ON learning_settings(privacy_tier);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_learning_settings_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER learning_settings_updated_at
    BEFORE UPDATE ON learning_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_learning_settings_timestamp();


-- brand_patterns table
-- Stores learned patterns from individual brands (private learning)
-- Data is isolated per brand and never shared
CREATE TABLE brand_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(brand_id) ON DELETE CASCADE,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_data JSONB NOT NULL,
    confidence_score FLOAT NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    sample_count INT NOT NULL CHECK (sample_count >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX idx_brand_patterns_brand ON brand_patterns(brand_id);
CREATE INDEX idx_brand_patterns_type ON brand_patterns(pattern_type);
CREATE INDEX idx_brand_patterns_brand_type ON brand_patterns(brand_id, pattern_type);
CREATE INDEX idx_brand_patterns_confidence ON brand_patterns(confidence_score DESC);

-- Trigger to update updated_at timestamp
CREATE TRIGGER brand_patterns_updated_at
    BEFORE UPDATE ON brand_patterns
    FOR EACH ROW
    EXECUTE FUNCTION update_learning_settings_timestamp();


-- industry_patterns table
-- Stores aggregated patterns from multiple brands (shared learning)
-- Enforces k-anonymity (minimum 5 contributors) and differential privacy
CREATE TABLE industry_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cohort VARCHAR(50) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_data JSONB NOT NULL,
    contributor_count INT NOT NULL CHECK (contributor_count >= 5),  -- K-anonymity enforcement
    noise_level FLOAT NOT NULL CHECK (noise_level > 0),  -- Differential privacy
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX idx_industry_patterns_cohort ON industry_patterns(cohort);
CREATE INDEX idx_industry_patterns_type ON industry_patterns(pattern_type);
CREATE INDEX idx_industry_patterns_cohort_type ON industry_patterns(cohort, pattern_type);
CREATE INDEX idx_industry_patterns_contributors ON industry_patterns(contributor_count DESC);

-- Trigger to update updated_at timestamp
CREATE TRIGGER industry_patterns_updated_at
    BEFORE UPDATE ON industry_patterns
    FOR EACH ROW
    EXECUTE FUNCTION update_learning_settings_timestamp();


-- learning_audit_log table
-- Provides transparency by logging all learning-related actions
CREATE TABLE learning_audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(brand_id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    details JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX idx_learning_audit_brand ON learning_audit_log(brand_id);
CREATE INDEX idx_learning_audit_timestamp ON learning_audit_log(timestamp DESC);
CREATE INDEX idx_learning_audit_action ON learning_audit_log(action);
CREATE INDEX idx_learning_audit_brand_timestamp ON learning_audit_log(brand_id, timestamp DESC);


-- Function to automatically create default learning settings for new brands
CREATE OR REPLACE FUNCTION create_default_learning_settings()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO learning_settings (brand_id, privacy_tier, consent_date)
    VALUES (NEW.brand_id, 'private', NOW())
    ON CONFLICT (brand_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to create default learning settings when a brand is created
CREATE TRIGGER brand_learning_settings_default
    AFTER INSERT ON brands
    FOR EACH ROW
    EXECUTE FUNCTION create_default_learning_settings();


-- Function to log privacy tier changes
CREATE OR REPLACE FUNCTION log_privacy_tier_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.privacy_tier IS DISTINCT FROM NEW.privacy_tier THEN
        INSERT INTO learning_audit_log (brand_id, action, details)
        VALUES (
            NEW.brand_id,
            'privacy_tier_changed',
            jsonb_build_object(
                'old_tier', OLD.privacy_tier,
                'new_tier', NEW.privacy_tier,
                'consent_date', NEW.consent_date
            )
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically log privacy tier changes
CREATE TRIGGER learning_settings_tier_change_log
    AFTER UPDATE ON learning_settings
    FOR EACH ROW
    WHEN (OLD.privacy_tier IS DISTINCT FROM NEW.privacy_tier)
    EXECUTE FUNCTION log_privacy_tier_change();


-- Add cohort column to brands table for shared learning grouping
-- This allows brands to be grouped into industry cohorts (fashion, tech, food, etc.)
ALTER TABLE brands ADD COLUMN IF NOT EXISTS cohort VARCHAR(50);
CREATE INDEX IF NOT EXISTS idx_brands_cohort ON brands(cohort) WHERE cohort IS NOT NULL;


-- Comments for documentation
COMMENT ON TABLE learning_settings IS 'Privacy settings and consent tracking for brand learning';
COMMENT ON TABLE brand_patterns IS 'Learned patterns from individual brands (private learning with data isolation)';
COMMENT ON TABLE industry_patterns IS 'Aggregated patterns from multiple brands (shared learning with k-anonymity and differential privacy)';
COMMENT ON TABLE learning_audit_log IS 'Audit log for all learning-related actions (transparency and compliance)';

COMMENT ON COLUMN learning_settings.privacy_tier IS 'Privacy tier: off (no learning), private (brand-only), shared (anonymized industry)';
COMMENT ON COLUMN learning_settings.consent_date IS 'When user consented to current privacy tier';
COMMENT ON COLUMN learning_settings.data_retention_days IS 'How long to retain learning data (default 365 days)';

COMMENT ON COLUMN brand_patterns.pattern_type IS 'Type of pattern: color_preference, style_preference, prompt_optimization';
COMMENT ON COLUMN brand_patterns.confidence_score IS 'Confidence in this pattern (0-1)';
COMMENT ON COLUMN brand_patterns.sample_count IS 'Number of feedback samples used to extract this pattern';

COMMENT ON COLUMN industry_patterns.cohort IS 'Industry cohort: fashion, tech, food, etc.';
COMMENT ON COLUMN industry_patterns.contributor_count IS 'Number of brands contributing (minimum 5 for k-anonymity)';
COMMENT ON COLUMN industry_patterns.noise_level IS 'Differential privacy noise scale applied';

COMMENT ON COLUMN learning_audit_log.action IS 'Action: pattern_extracted, prompt_optimized, data_exported, data_deleted, privacy_tier_changed';
