-- Add missing vector fields to default_rag_configs table
-- These fields were added to vector_rag_configs in migration 007 but not to default_rag_configs

-- Add embedding_model_vector_size (matching vector_rag_configs schema)
ALTER TABLE default_rag_configs
ADD COLUMN vector_embedding_model_vector_size INTEGER NOT NULL DEFAULT 768;

-- Add distance_metric (matching vector_rag_configs schema)
ALTER TABLE default_rag_configs
ADD COLUMN vector_distance_metric VARCHAR(50) NOT NULL DEFAULT 'cosine';
