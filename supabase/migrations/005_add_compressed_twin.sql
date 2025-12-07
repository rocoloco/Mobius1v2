-- Migration 005: Add Compressed Digital Twin
-- Adds compressed_twin JSONB column to brands table for Vision Model context optimization
-- This is a non-breaking change (nullable field) to support Gemini 3 dual-architecture

-- Add compressed_twin column to brands table
-- This field stores the optimized brand guidelines for the Vision Model's 65k context window
-- It contains only essential visual rules (colors, fonts, critical constraints)
-- while the full guidelines field retains complete brand information
ALTER TABLE brands 
ADD COLUMN IF NOT EXISTS compressed_twin JSONB;

-- Add index for efficient querying of brands with compressed twins
-- This helps identify which brands have been migrated to the new architecture
CREATE INDEX IF NOT EXISTS idx_brands_compressed_twin 
ON brands(brand_id) 
WHERE compressed_twin IS NOT NULL;

-- Add comment for documentation
COMMENT ON COLUMN brands.compressed_twin IS 
'Compressed brand guidelines optimized for Vision Model context window (max 60k tokens). Contains only essential visual rules: semantic color hierarchy, font families, and critical constraints. Used during image generation with Gemini 3 Vision Model.';
