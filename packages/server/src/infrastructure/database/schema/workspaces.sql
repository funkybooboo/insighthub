-- Workspace database schema for InsightHub
-- Implements the workspace-based document grouping system

-- Workspaces table - top-level container for documents and chats
CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RAG configurations table - one per workspace
CREATE TABLE IF NOT EXISTS rag_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID UNIQUE NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    embedding_model TEXT NOT NULL DEFAULT 'nomic-embed-text',
    retriever_type TEXT NOT NULL DEFAULT 'vector',
    chunk_size INTEGER NOT NULL DEFAULT 1000,
    chunk_overlap INTEGER DEFAULT 0,
    top_k INTEGER DEFAULT 8,
    embedding_dim INTEGER,
    rerank_enabled BOOLEAN DEFAULT false,
    rerank_model TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table - workspace-scoped documents
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    processing_error TEXT,
    chunk_count INTEGER,
    embedding_status TEXT,
    title TEXT,
    author TEXT,
    created_date TIMESTAMP WITH TIME ZONE,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat sessions table - workspace-scoped chat sessions
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    system_prompt TEXT,
    temperature DECIMAL(3,2) DEFAULT 0.7 CHECK (temperature >= 0.0 AND temperature <= 2.0),
    max_tokens INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat messages table - messages within sessions
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    token_count INTEGER,
    model_used TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_workspaces_user_id ON workspaces(user_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_is_active ON workspaces(is_active);
CREATE INDEX IF NOT EXISTS idx_documents_workspace_id ON documents(workspace_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_workspace_id ON chat_sessions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);

-- Functions to automatically update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_workspaces_updated_at 
    BEFORE UPDATE ON workspaces 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rag_configs_updated_at 
    BEFORE UPDATE ON rag_configs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at 
    BEFORE UPDATE ON chat_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) policies
-- Enable RLS on all tables
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own workspaces
CREATE POLICY workspaces_user_policy ON workspaces
    FOR ALL TO authenticated_users
    USING (user_id = auth.uid());

-- Policy: Users can access RAG configs only for their workspaces
CREATE POLICY rag_configs_user_policy ON rag_configs
    FOR ALL TO authenticated_users
    USING (
        EXISTS (
            SELECT 1 FROM workspaces 
            WHERE workspaces.id = rag_configs.workspace_id 
            AND workspaces.user_id = auth.uid()
        )
    );

-- Policy: Users can access documents only in their workspaces
CREATE POLICY documents_user_policy ON documents
    FOR ALL TO authenticated_users
    USING (
        EXISTS (
            SELECT 1 FROM workspaces 
            WHERE workspaces.id = documents.workspace_id 
            AND workspaces.user_id = auth.uid()
        )
    );

-- Policy: Users can access chat sessions only in their workspaces
CREATE POLICY chat_sessions_user_policy ON chat_sessions
    FOR ALL TO authenticated_users
    USING (
        EXISTS (
            SELECT 1 FROM workspaces 
            WHERE workspaces.id = chat_sessions.workspace_id 
            AND workspaces.user_id = auth.uid()
        )
    );

-- Policy: Users can access chat messages only in their sessions
CREATE POLICY chat_messages_user_policy ON chat_messages
    FOR ALL TO authenticated_users
    USING (
        EXISTS (
            SELECT 1 FROM chat_sessions
            JOIN workspaces ON workspaces.id = chat_sessions.workspace_id
            WHERE chat_sessions.id = chat_messages.session_id 
            AND workspaces.user_id = auth.uid()
        )
    );

-- Views for common queries
CREATE OR REPLACE VIEW workspace_stats AS
SELECT 
    w.id as workspace_id,
    w.name as workspace_name,
    COUNT(DISTINCT d.id) as document_count,
    COALESCE(SUM(d.file_size), 0) as total_document_size,
    COALESCE(SUM(d.chunk_count), 0) as chunk_count,
    COUNT(DISTINCT cs.id) as chat_session_count,
    COUNT(DISTINCT cm.id) as total_message_count,
    GREATEST(
        MAX(d.uploaded_at),
        MAX(cs.updated_at),
        MAX(cm.created_at)
    ) as last_activity
FROM workspaces w
LEFT JOIN documents d ON d.workspace_id = w.id
LEFT JOIN chat_sessions cs ON cs.workspace_id = w.id  
LEFT JOIN chat_messages cm ON cm.session_id = cs.id
WHERE w.is_active = true
GROUP BY w.id, w.name;