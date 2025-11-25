-- Description: Add performance indexes for common query patterns
-- Created: 2025-11-24

-- Add index for chat session ordering by creation time
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at);

-- Add index for chat message ordering within sessions
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);

-- Add composite index for workspace-user queries (common in permission checks)
CREATE INDEX IF NOT EXISTS idx_workspaces_user_id_active ON workspaces(user_id, is_active);

-- Add composite index for document workspace-user queries
CREATE INDEX IF NOT EXISTS idx_documents_workspace_user ON documents(workspace_id, user_id);

-- Add index for chat session workspace-user queries
CREATE INDEX IF NOT EXISTS idx_chat_sessions_workspace_user ON chat_sessions(workspace_id, user_id);