-- Rollback: Remove rag_type column from default_rag_configs table

-- Drop the check constraint first
ALTER TABLE default_rag_configs
DROP CONSTRAINT IF EXISTS rag_type_check;

-- Drop the rag_type column
ALTER TABLE default_rag_configs
DROP COLUMN IF EXISTS rag_type;
