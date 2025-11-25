-- Description: Create separate tables for Vector RAG and Graph RAG configurations
-- Created: 2025-11-25

-- Vector RAG configuration table
CREATE TABLE IF NOT EXISTS vector_rag_configs (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    embedding_algorithm VARCHAR(100) NOT NULL DEFAULT 'nomic-embed-text',
    chunking_algorithm VARCHAR(50) NOT NULL DEFAULT 'sentence',
    chunk_size INTEGER NOT NULL DEFAULT 1000 CHECK (chunk_size >= 100 AND chunk_size <= 5000),
    chunk_overlap INTEGER NOT NULL DEFAULT 200 CHECK (chunk_overlap >= 0 AND chunk_overlap <= 1000),
    top_k INTEGER NOT NULL DEFAULT 8 CHECK (top_k >= 1 AND top_k <= 50),
    rerank_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    rerank_algorithm VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Graph RAG configuration table
CREATE TABLE IF NOT EXISTS graph_rag_configs (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    entity_extraction_algorithm VARCHAR(50) NOT NULL DEFAULT 'ollama',
    relationship_extraction_algorithm VARCHAR(50) NOT NULL DEFAULT 'ollama',
    clustering_algorithm VARCHAR(50) NOT NULL DEFAULT 'leiden',
    max_hops INTEGER NOT NULL DEFAULT 2 CHECK (max_hops >= 1 AND max_hops <= 10),
    min_cluster_size INTEGER NOT NULL DEFAULT 5 CHECK (min_cluster_size >= 1),
    max_cluster_size INTEGER NOT NULL DEFAULT 50 CHECK (max_cluster_size >= min_cluster_size),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add foreign key columns to workspaces table
ALTER TABLE workspaces
ADD COLUMN IF NOT EXISTS vector_rag_config_id INTEGER REFERENCES vector_rag_configs(id),
ADD COLUMN IF NOT EXISTS graph_rag_config_id INTEGER REFERENCES graph_rag_configs(id);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_vector_rag_configs_workspace_id ON vector_rag_configs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_graph_rag_configs_workspace_id ON graph_rag_configs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_vector_rag_config_id ON workspaces(vector_rag_config_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_graph_rag_config_id ON workspaces(graph_rag_config_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_vector_rag_configs_updated_at
    BEFORE UPDATE ON vector_rag_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_graph_rag_configs_updated_at
    BEFORE UPDATE ON graph_rag_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();