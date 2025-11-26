-- Add missing fields to chat_sessions table

ALTER TABLE chat_sessions
ADD COLUMN IF NOT EXISTS user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS rag_type VARCHAR(50) DEFAULT 'vector' CHECK (rag_type IN ('vector', 'graph'));

-- Make title nullable since it can be auto-generated
ALTER TABLE chat_sessions
ALTER COLUMN title DROP NOT NULL;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_rag_type ON chat_sessions(rag_type);