-- Add missing fields to graph_rag_configs table
-- Adds 9 new configuration fields for entity types, relationship types, traversal, and clustering

-- Add entity_types as JSONB array
ALTER TABLE graph_rag_configs
ADD COLUMN entity_types JSONB NOT NULL DEFAULT '["PERSON", "ORG", "GPE", "PRODUCT", "EVENT", "CONCEPT"]'::jsonb;

-- Add relationship_types as JSONB array
ALTER TABLE graph_rag_configs
ADD COLUMN relationship_types JSONB NOT NULL DEFAULT '["WORKS_AT", "LOCATED_IN", "RELATED_TO", "PART_OF", "CREATED_BY"]'::jsonb;

-- Add graph traversal depth setting
ALTER TABLE graph_rag_configs
ADD COLUMN max_traversal_depth INTEGER NOT NULL DEFAULT 2;

-- Add top_k settings for entities and communities
ALTER TABLE graph_rag_configs
ADD COLUMN top_k_entities INTEGER NOT NULL DEFAULT 10;

ALTER TABLE graph_rag_configs
ADD COLUMN top_k_communities INTEGER NOT NULL DEFAULT 3;

-- Add flag for including entity neighborhoods
ALTER TABLE graph_rag_configs
ADD COLUMN include_entity_neighborhoods BOOLEAN NOT NULL DEFAULT true;

-- Add community detection settings
ALTER TABLE graph_rag_configs
ADD COLUMN community_min_size INTEGER NOT NULL DEFAULT 3;

-- Note: clustering_resolution already exists in the initial schema (line 49)
-- Verify it exists, and update default if needed
ALTER TABLE graph_rag_configs
ALTER COLUMN clustering_resolution SET DEFAULT 1.0;

-- Add clustering max level
ALTER TABLE graph_rag_configs
ADD COLUMN clustering_max_level INTEGER NOT NULL DEFAULT 3;

-- Also update default_rag_configs table with the same fields
ALTER TABLE default_rag_configs
ADD COLUMN graph_entity_types JSONB NOT NULL DEFAULT '["PERSON", "ORG", "GPE", "PRODUCT", "EVENT", "CONCEPT"]'::jsonb;

ALTER TABLE default_rag_configs
ADD COLUMN graph_relationship_types JSONB NOT NULL DEFAULT '["WORKS_AT", "LOCATED_IN", "RELATED_TO", "PART_OF", "CREATED_BY"]'::jsonb;

ALTER TABLE default_rag_configs
ADD COLUMN graph_max_traversal_depth INTEGER NOT NULL DEFAULT 2;

ALTER TABLE default_rag_configs
ADD COLUMN graph_top_k_entities INTEGER NOT NULL DEFAULT 10;

ALTER TABLE default_rag_configs
ADD COLUMN graph_top_k_communities INTEGER NOT NULL DEFAULT 3;

ALTER TABLE default_rag_configs
ADD COLUMN graph_include_entity_neighborhoods BOOLEAN NOT NULL DEFAULT true;

ALTER TABLE default_rag_configs
ADD COLUMN graph_community_min_size INTEGER NOT NULL DEFAULT 3;

ALTER TABLE default_rag_configs
ADD COLUMN graph_clustering_resolution FLOAT NOT NULL DEFAULT 1.0;

ALTER TABLE default_rag_configs
ADD COLUMN graph_clustering_max_level INTEGER NOT NULL DEFAULT 3;
