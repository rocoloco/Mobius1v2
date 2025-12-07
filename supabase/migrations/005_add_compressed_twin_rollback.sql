-- Rollback Migration 005: Remove Compressed Digital Twin
-- Removes compressed_twin column from brands table
-- This rollback is safe because the column is nullable and doesn't affect existing data

-- Drop the index first
DROP INDEX IF EXISTS idx_brands_compressed_twin;

-- Remove the compressed_twin column
ALTER TABLE brands 
DROP COLUMN IF EXISTS compressed_twin;
