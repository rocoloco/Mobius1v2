-- Migration 004: Storage Buckets Configuration
-- Creates and configures Supabase Storage buckets for brands and assets

-- Create storage buckets
INSERT INTO storage.buckets (id, name, public) VALUES
    ('brands', 'brands', true),
    ('assets', 'assets', true)
ON CONFLICT (id) DO NOTHING;

-- Set size limits
UPDATE storage.buckets SET file_size_limit = 52428800 WHERE id = 'brands';  -- 50MB
UPDATE storage.buckets SET file_size_limit = 10485760 WHERE id = 'assets';  -- 10MB

-- Set allowed MIME types
UPDATE storage.buckets SET allowed_mime_types = ARRAY['application/pdf'] WHERE id = 'brands';
UPDATE storage.buckets SET allowed_mime_types = ARRAY['image/png', 'image/jpeg', 'image/webp'] WHERE id = 'assets';
