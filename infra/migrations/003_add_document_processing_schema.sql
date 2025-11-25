-- Migration: 003_add_document_processing_schema
-- Description: Add tables and columns needed for document processing pipeline
-- Created: 2025-11-24

-- Add parsed_text column to documents table
ALTER TABLE documents ADD COLUMN IF NOT EXISTS parsed_text TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS processing_metadata JSONB DEFAULT '{}';

-- Create document_chunks table for storing text chunks and embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768), -- Default embedding dimension, can be adjusted
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_chunk_index ON document_chunks(chunk_index);

-- Create trigger for document_chunks updated_at
CREATE OR REPLACE TRIGGER update_document_chunks_updated_at
    BEFORE UPDATE ON document_chunks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Record migration as applied
INSERT INTO schema_migrations (version, name) VALUES ('003', 'add_document_processing_schema')
ON CONFLICT (version) DO NOTHING;