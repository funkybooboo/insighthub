-- Rollback vector_rag_configs schema changes

-- Add back columns that were dropped
ALTER TABLE vector_rag_configs
ADD COLUMN collection_name VARCHAR(255),
ADD COLUMN score_threshold FLOAT;

-- Drop columns that were added
ALTER TABLE vector_rag_configs
DROP COLUMN IF EXISTS rerank_algorithm,
DROP COLUMN IF EXISTS distance_metric;

-- Rename columns back to original names
ALTER TABLE vector_rag_configs
RENAME COLUMN chunking_algorithm TO chunker_type;

ALTER TABLE vector_rag_configs
RENAME COLUMN embedding_algorithm TO embedding_model;

ALTER TABLE vector_rag_configs
RENAME COLUMN embedding_model_vector_size TO embedding_dimension;
