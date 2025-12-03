-- Rollback: Remove rag_type and add user_id back to chat_sessions

-- Add user_id column back
ALTER TABLE chat_sessions
ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- Create index for user_id
CREATE INDEX IF NOT EXISTS ix_chat_sessions_user_id ON chat_sessions(user_id);

-- Drop rag_type column
ALTER TABLE chat_sessions DROP COLUMN IF EXISTS rag_type;
