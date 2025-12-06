-- Migration 003: Feedback
-- Creates feedback table and trigger for learning activation

-- feedback table
CREATE TABLE feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES assets(asset_id),
    brand_id UUID NOT NULL REFERENCES brands(brand_id),
    action VARCHAR(20) NOT NULL CHECK (action IN ('approve', 'reject')),
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_feedback_brand ON feedback(brand_id);
CREATE INDEX idx_feedback_asset ON feedback(asset_id);

-- Trigger to update learning_active flag
CREATE OR REPLACE FUNCTION update_learning_active()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE brands
    SET 
        feedback_count = (SELECT COUNT(*) FROM feedback WHERE brand_id = NEW.brand_id),
        learning_active = (SELECT COUNT(*) FROM feedback WHERE brand_id = NEW.brand_id) >= 50
    WHERE brand_id = NEW.brand_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER feedback_learning_trigger
AFTER INSERT ON feedback
FOR EACH ROW
EXECUTE FUNCTION update_learning_active();
