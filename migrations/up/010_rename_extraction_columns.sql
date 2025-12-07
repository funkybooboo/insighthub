-- Rename entity_extraction_model to entity_extraction_algorithm for consistency
-- Rename relationship_extraction_model to relationship_extraction_algorithm for consistency
-- This aligns with the naming convention used in default_rag_configs table

ALTER TABLE graph_rag_configs
RENAME COLUMN entity_extraction_model TO entity_extraction_algorithm;

ALTER TABLE graph_rag_configs
RENAME COLUMN relationship_extraction_model TO relationship_extraction_algorithm;
