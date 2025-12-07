-- Rollback migration 009: Remove vector fields from default_rag_configs table

ALTER TABLE default_rag_configs
DROP COLUMN IF EXISTS vector_embedding_model_vector_size,
DROP COLUMN IF EXISTS vector_distance_metric;
