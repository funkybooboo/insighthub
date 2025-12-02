-- Remove user_id from chat_sessions and add rag_type
-- Single-user system, no user_id needed

-- Add rag_type column
ALTER TABLE chat_sessions
ADD COLUMN IF NOT EXISTS rag_type VARCHAR(50) NOT NULL DEFAULT 'vector' CHECK (rag_type IN ('vector', 'graph'));

-- Drop user_id column and its index
DROP INDEX IF EXISTS ix_chat_sessions_user_id;
ALTER TABLE chat_sessions DROP COLUMN IF EXISTS user_id;
