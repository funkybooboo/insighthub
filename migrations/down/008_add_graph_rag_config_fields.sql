-- Rollback: Remove graph RAG config fields added in migration 008

-- Remove from graph_rag_configs table
ALTER TABLE graph_rag_configs
DROP COLUMN IF EXISTS entity_types,
DROP COLUMN IF EXISTS relationship_types,
DROP COLUMN IF EXISTS max_traversal_depth,
DROP COLUMN IF EXISTS top_k_entities,
DROP COLUMN IF EXISTS top_k_communities,
DROP COLUMN IF EXISTS include_entity_neighborhoods,
DROP COLUMN IF EXISTS community_min_size,
DROP COLUMN IF EXISTS clustering_max_level;

-- Restore clustering_resolution to its original default if it was modified
ALTER TABLE graph_rag_configs
ALTER COLUMN clustering_resolution SET DEFAULT 1.0;

-- Remove from default_rag_configs table
ALTER TABLE default_rag_configs
DROP COLUMN IF EXISTS graph_entity_types,
DROP COLUMN IF EXISTS graph_relationship_types,
DROP COLUMN IF EXISTS graph_max_traversal_depth,
DROP COLUMN IF EXISTS graph_top_k_entities,
DROP COLUMN IF EXISTS graph_top_k_communities,
DROP COLUMN IF EXISTS graph_include_entity_neighborhoods,
DROP COLUMN IF EXISTS graph_community_min_size,
DROP COLUMN IF EXISTS graph_clustering_resolution,
DROP COLUMN IF EXISTS graph_clustering_max_level;
