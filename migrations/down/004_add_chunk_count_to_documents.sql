-- Rollback: Remove chunk_count column from documents table
ALTER TABLE documents DROP COLUMN IF EXISTS chunk_count;
