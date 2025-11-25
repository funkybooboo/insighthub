-- Migration: 002_add_missing_schema
-- Description: Add missing tables and columns from schema migration
-- Created: 2025-11-23

-- Create schema_migrations table if it doesn't exist
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create the update_updated_at_column function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create workspaces table (needed before foreign keys can reference it)
CREATE TABLE IF NOT EXISTS workspaces (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(50) NOT NULL DEFAULT 'provisioning',
    status_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workspaces_user_id ON workspaces(user_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_status ON workspaces(status);

-- Create rag_configs table
CREATE TABLE IF NOT EXISTS rag_configs (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL UNIQUE REFERENCES workspaces(id) ON DELETE CASCADE,
    embedding_model VARCHAR(100) NOT NULL DEFAULT 'nomic-embed-text',
    embedding_dim INTEGER,
    retriever_type VARCHAR(50) NOT NULL DEFAULT 'vector',
    chunk_size INTEGER NOT NULL DEFAULT 1000,
    chunk_overlap INTEGER NOT NULL DEFAULT 200,
    top_k INTEGER NOT NULL DEFAULT 8,
    rerank_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    rerank_model VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rag_configs_workspace_id ON rag_configs(workspace_id);

-- Create default_rag_configs table
CREATE TABLE IF NOT EXISTS default_rag_configs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    embedding_model VARCHAR(100) NOT NULL DEFAULT 'nomic-embed-text',
    embedding_dim INTEGER,
    retriever_type VARCHAR(50) NOT NULL DEFAULT 'vector',
    chunk_size INTEGER NOT NULL DEFAULT 1000,
    chunk_overlap INTEGER NOT NULL DEFAULT 200,
    top_k INTEGER NOT NULL DEFAULT 8,
    rerank_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    rerank_model VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_default_rag_configs_user_id ON default_rag_configs(user_id);

-- Add missing columns to documents table
ALTER TABLE documents ADD COLUMN IF NOT EXISTS workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS processing_status VARCHAR(50) NOT NULL DEFAULT 'pending';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS processing_error TEXT;

CREATE INDEX IF NOT EXISTS idx_documents_workspace_id ON documents(workspace_id);
CREATE INDEX IF NOT EXISTS idx_documents_processing_status ON documents(processing_status);

-- Add missing column to chat_sessions table
ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_chat_sessions_workspace_id ON chat_sessions(workspace_id);

-- Update timestamp columns to use timezone if they don't already
-- (Old schema used timestamp without time zone)
ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE documents ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE documents ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE chat_sessions ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE chat_sessions ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE chat_messages ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE chat_messages ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

-- Create triggers for all tables
CREATE OR REPLACE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER update_workspaces_updated_at
    BEFORE UPDATE ON workspaces
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER update_rag_configs_updated_at
    BEFORE UPDATE ON rag_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER update_default_rag_configs_updated_at
    BEFORE UPDATE ON default_rag_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER update_chat_sessions_updated_at
    BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER update_chat_messages_updated_at
    BEFORE UPDATE ON chat_messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Drop old alembic_version table if it exists (no longer using Alembic)
DROP TABLE IF EXISTS alembic_version;

-- Record both migrations as applied (001 is implicitly applied via this migration)
INSERT INTO schema_migrations (version, name) VALUES ('001', 'initial_schema')
ON CONFLICT (version) DO NOTHING;
INSERT INTO schema_migrations (version, name) VALUES ('002', 'add_missing_schema')
ON CONFLICT (version) DO NOTHING;
