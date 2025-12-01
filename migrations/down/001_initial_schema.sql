-- Rollback initial schema
-- Run with: psql -U insighthub -d insighthub -f migrations/down/001_initial_schema.sql

-- Drop tables in reverse order (respecting foreign keys)
DROP TABLE IF EXISTS default_rag_configs CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS chat_sessions CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS graph_rag_configs CASCADE;
DROP TABLE IF EXISTS vector_rag_configs CASCADE;
DROP TABLE IF EXISTS workspaces CASCADE;

-- Drop the trigger function
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Drop pgvector extension (optional, comment out if other databases use it)
-- DROP EXTENSION IF EXISTS vector;
