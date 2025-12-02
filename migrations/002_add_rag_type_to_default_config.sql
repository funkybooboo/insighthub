-- Add rag_type column to default_rag_configs table
ALTER TABLE default_rag_configs
ADD COLUMN rag_type VARCHAR(20) NOT NULL DEFAULT 'vector';

-- Add check constraint to ensure rag_type is either 'vector' or 'graph'
ALTER TABLE default_rag_configs
ADD CONSTRAINT rag_type_check CHECK (rag_type IN ('vector', 'graph'));
