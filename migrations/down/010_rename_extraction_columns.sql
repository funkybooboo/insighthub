-- Revert: Rename entity_extraction_algorithm back to entity_extraction_model
-- Revert: Rename relationship_extraction_algorithm back to relationship_extraction_model

ALTER TABLE graph_rag_configs
RENAME COLUMN entity_extraction_algorithm TO entity_extraction_model;

ALTER TABLE graph_rag_configs
RENAME COLUMN relationship_extraction_algorithm TO relationship_extraction_model;
