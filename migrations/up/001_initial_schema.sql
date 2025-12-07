-- Initial schema for InsightHub
-- Run with: psql -U insighthub -d insighthub -f migrations/001_initial_schema.sql

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Workspaces table (single-user system, no user_id needed)
CREATE TABLE IF NOT EXISTS workspaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    rag_type VARCHAR(50) NOT NULL CHECK (rag_type IN ('vector', 'graph')),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Vector RAG configurations table
CREATE TABLE IF NOT EXISTS vector_rag_configs (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    chunk_size INTEGER NOT NULL DEFAULT 512,
    chunk_overlap INTEGER NOT NULL DEFAULT 50,
    chunker_type VARCHAR(50) NOT NULL DEFAULT 'sentence',
    embedding_model VARCHAR(255) NOT NULL DEFAULT 'nomic-embed-text',
    embedding_dimension INTEGER NOT NULL DEFAULT 768,
    collection_name VARCHAR(255) NOT NULL,
    top_k INTEGER NOT NULL DEFAULT 5,
    score_threshold FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id)
);

CREATE INDEX IF NOT EXISTS ix_vector_rag_configs_workspace_id ON vector_rag_configs(workspace_id);

-- Graph RAG configurations table
CREATE TABLE IF NOT EXISTS graph_rag_configs (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    chunk_size INTEGER NOT NULL DEFAULT 512,
    chunk_overlap INTEGER NOT NULL DEFAULT 50,
    chunker_type VARCHAR(50) NOT NULL DEFAULT 'sentence',
    embedding_model VARCHAR(255) NOT NULL DEFAULT 'nomic-embed-text',
    embedding_dimension INTEGER NOT NULL DEFAULT 768,
    entity_extraction_algorithm VARCHAR(255) NOT NULL DEFAULT 'llama3.2:1b',
    relationship_extraction_algorithm VARCHAR(255) NOT NULL DEFAULT 'llama3.2:1b',
    clustering_algorithm VARCHAR(50) NOT NULL DEFAULT 'leiden',
    clustering_resolution FLOAT NOT NULL DEFAULT 1.0,
    max_cluster_size INTEGER NOT NULL DEFAULT 1000,
    top_k INTEGER NOT NULL DEFAULT 5,
    score_threshold FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id)
);

CREATE INDEX IF NOT EXISTS ix_graph_rag_configs_workspace_id ON graph_rag_configs(workspace_id);

-- Documents table (single-user system, no user_id needed)
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    size_bytes INTEGER NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    storage_path VARCHAR(512) NOT NULL,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_documents_workspace_id ON documents(workspace_id);
CREATE INDEX IF NOT EXISTS ix_documents_file_hash ON documents(file_hash);

-- Chat session table (single-user system, no user_id needed)
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_chat_sessions_workspace_id ON chat_sessions(workspace_id);

-- Chat message table
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    chat_session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_chat_messages_chat_session_id ON chat_messages(chat_session_id);

-- Default RAG configurations table (single-user system, only one row allowed)
CREATE TABLE IF NOT EXISTS default_rag_configs (
    id SERIAL PRIMARY KEY,
    vector_embedding_algorithm VARCHAR(50) NOT NULL DEFAULT 'ollama',
    vector_chunking_algorithm VARCHAR(50) NOT NULL DEFAULT 'sentence',
    vector_rerank_algorithm VARCHAR(50) NOT NULL DEFAULT 'none',
    vector_chunk_size INTEGER NOT NULL DEFAULT 1000,
    vector_chunk_overlap INTEGER NOT NULL DEFAULT 200,
    vector_top_k INTEGER NOT NULL DEFAULT 5,
    graph_entity_extraction_algorithm VARCHAR(50) NOT NULL DEFAULT 'spacy',
    graph_relationship_extraction_algorithm VARCHAR(50) NOT NULL DEFAULT 'dependency-parsing',
    graph_clustering_algorithm VARCHAR(50) NOT NULL DEFAULT 'leiden',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (id = 1)
);

-- Insert default configuration
INSERT INTO default_rag_configs (id) VALUES (1) ON CONFLICT DO NOTHING;

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers to all tables
CREATE TRIGGER update_workspaces_updated_at BEFORE UPDATE ON workspaces FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vector_rag_configs_updated_at BEFORE UPDATE ON vector_rag_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_graph_rag_configs_updated_at BEFORE UPDATE ON graph_rag_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_default_rag_configs_updated_at BEFORE UPDATE ON default_rag_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
