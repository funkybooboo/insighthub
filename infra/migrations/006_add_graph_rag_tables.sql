-- Description: Add tables for Graph RAG entities, relationships, and communities
-- Created: 2025-11-25

-- Entities table for storing extracted entities
CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_id VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_text TEXT NOT NULL,
    confidence_score REAL NOT NULL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Relationships table for storing extracted relationships between entities
CREATE TABLE IF NOT EXISTS relationships (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    source_entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    target_entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    confidence_score REAL NOT NULL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Ensure source and target entities are different
    CHECK (source_entity_id != target_entity_id)
);

-- Communities table for storing detected communities/clusters
CREATE TABLE IF NOT EXISTS communities (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    community_id VARCHAR(255) NOT NULL,
    entity_ids INTEGER[] NOT NULL DEFAULT '{}',
    algorithm_used VARCHAR(50) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_entities_workspace_id ON entities(workspace_id);
CREATE INDEX IF NOT EXISTS idx_entities_document_id ON entities(document_id);
CREATE INDEX IF NOT EXISTS idx_entities_chunk_id ON entities(chunk_id);
CREATE INDEX IF NOT EXISTS idx_entities_entity_type ON entities(entity_type);

CREATE INDEX IF NOT EXISTS idx_relationships_workspace_id ON relationships(workspace_id);
CREATE INDEX IF NOT EXISTS idx_relationships_source_entity_id ON relationships(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target_entity_id ON relationships(target_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_relationship_type ON relationships(relationship_type);

CREATE INDEX IF NOT EXISTS idx_communities_workspace_id ON communities(workspace_id);
CREATE INDEX IF NOT EXISTS idx_communities_community_id ON communities(community_id);
CREATE INDEX IF NOT EXISTS idx_communities_algorithm_used ON communities(algorithm_used);

-- Create unique constraint for community_id within workspace
CREATE UNIQUE INDEX IF NOT EXISTS idx_communities_workspace_community_id ON communities(workspace_id, community_id);

-- Create trigger to update updated_at timestamp for entities
CREATE TRIGGER update_entities_updated_at
    BEFORE UPDATE ON entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create trigger to update updated_at timestamp for relationships
CREATE TRIGGER update_relationships_updated_at
    BEFORE UPDATE ON relationships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create trigger to update updated_at timestamp for communities
CREATE TRIGGER update_communities_updated_at
    BEFORE UPDATE ON communities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();