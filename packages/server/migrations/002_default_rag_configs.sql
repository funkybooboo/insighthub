-- Default RAG configurations table

CREATE TABLE IF NOT EXISTS default_rag_configs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    embedding_model VARCHAR(255) DEFAULT 'nomic-embed-text',
    embedding_dim INTEGER,
    retriever_type VARCHAR(50) DEFAULT 'vector',
    chunk_size INTEGER DEFAULT 1000,
    chunk_overlap INTEGER DEFAULT 200,
    top_k INTEGER DEFAULT 8,
    rerank_enabled BOOLEAN DEFAULT FALSE,
    rerank_model VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_default_rag_configs_user_id ON default_rag_configs(user_id);
