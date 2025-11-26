-- Update default RAG configurations table to support separate vector/graph configs

-- Add new columns for vector config
ALTER TABLE default_rag_configs
ADD COLUMN IF NOT EXISTS vector_embedding_algorithm VARCHAR(255) DEFAULT 'ollama',
ADD COLUMN IF NOT EXISTS vector_chunking_algorithm VARCHAR(255) DEFAULT 'sentence',
ADD COLUMN IF NOT EXISTS vector_rerank_algorithm VARCHAR(255) DEFAULT 'none',
ADD COLUMN IF NOT EXISTS vector_chunk_size INTEGER DEFAULT 1000,
ADD COLUMN IF NOT EXISTS vector_chunk_overlap INTEGER DEFAULT 200,
ADD COLUMN IF NOT EXISTS vector_top_k INTEGER DEFAULT 5;

-- Add new columns for graph config
ALTER TABLE default_rag_configs
ADD COLUMN IF NOT EXISTS graph_entity_extraction_algorithm VARCHAR(255) DEFAULT 'spacy',
ADD COLUMN IF NOT EXISTS graph_relationship_extraction_algorithm VARCHAR(255) DEFAULT 'dependency-parsing',
ADD COLUMN IF NOT EXISTS graph_clustering_algorithm VARCHAR(255) DEFAULT 'leiden';

-- Migrate existing data to new structure
UPDATE default_rag_configs
SET
    vector_embedding_algorithm = CASE
        WHEN embedding_model IS NOT NULL THEN embedding_model
        ELSE 'ollama'
    END,
    vector_chunking_algorithm = 'sentence',
    vector_rerank_algorithm = CASE
        WHEN rerank_enabled = true AND rerank_model IS NOT NULL THEN rerank_model
        ELSE 'none'
    END,
    vector_chunk_size = COALESCE(chunk_size, 1000),
    vector_chunk_overlap = COALESCE(chunk_overlap, 200),
    vector_top_k = COALESCE(top_k, 5),
    graph_entity_extraction_algorithm = 'spacy',
    graph_relationship_extraction_algorithm = 'dependency-parsing',
    graph_clustering_algorithm = 'leiden'
WHERE vector_embedding_algorithm IS NULL;

-- Remove old columns (optional - keep for backward compatibility)
-- ALTER TABLE default_rag_configs DROP COLUMN IF EXISTS embedding_model;
-- ALTER TABLE default_rag_configs DROP COLUMN IF EXISTS embedding_dim;
-- ALTER TABLE default_rag_configs DROP COLUMN IF EXISTS retriever_type;
-- ALTER TABLE default_rag_configs DROP COLUMN IF EXISTS chunk_size;
-- ALTER TABLE default_rag_configs DROP COLUMN IF EXISTS chunk_overlap;
-- ALTER TABLE default_rag_configs DROP COLUMN IF EXISTS top_k;
-- ALTER TABLE default_rag_configs DROP COLUMN IF EXISTS rerank_enabled;
-- ALTER TABLE default_rag_configs DROP COLUMN IF EXISTS rerank_model;