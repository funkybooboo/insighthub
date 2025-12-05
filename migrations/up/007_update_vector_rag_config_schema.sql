-- Update vector_rag_configs table to match code expectations
-- Rename columns to match the repository code

-- Rename embedding_dimension to embedding_model_vector_size
ALTER TABLE vector_rag_configs
RENAME COLUMN embedding_dimension TO embedding_model_vector_size;

-- Rename embedding_model to embedding_algorithm
ALTER TABLE vector_rag_configs
RENAME COLUMN embedding_model TO embedding_algorithm;

-- Rename chunker_type to chunking_algorithm
ALTER TABLE vector_rag_configs
RENAME COLUMN chunker_type TO chunking_algorithm;

-- Add distance_metric column (used by the code but not in schema)
ALTER TABLE vector_rag_configs
ADD COLUMN distance_metric VARCHAR(50) NOT NULL DEFAULT 'cosine';

-- Add rerank_algorithm column (used by the code but not in schema)
ALTER TABLE vector_rag_configs
ADD COLUMN rerank_algorithm VARCHAR(50) NOT NULL DEFAULT 'none';

-- Drop columns that are no longer used
ALTER TABLE vector_rag_configs
DROP COLUMN IF EXISTS collection_name,
DROP COLUMN IF EXISTS score_threshold;
