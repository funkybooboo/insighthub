"""LLM-based relationship extraction implementation.

This module provides relationship extraction using large language models (LLMs)
with structured JSON output.
"""

import json
from typing import Optional

from src.infrastructure.llm.llm_provider import LlmProvider
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.graph_rag.relationship_extraction.relationship_extractor import (
    RelationshipExtractor,
)
from src.infrastructure.types.graph import Entity, Relationship, RelationshipMetadata, RelationType

logger = create_logger(__name__)


class LlmRelationshipExtractor(RelationshipExtractor):
    """Relationship extraction using LLM with structured JSON output.

    This implementation uses an LLM to extract relationships between entities
    by prompting for structured JSON responses.
    """

    PROMPT_TEMPLATE = """Extract relationships between the following entities found in the text.

Entities:
{entities}

Text:
{text}

Return ONLY a JSON array of relationships with this exact format:
[{{"source": "entity1 name", "target": "entity2 name", "type": "WORKS_AT|LOCATED_IN|RELATED_TO|PART_OF|CREATED_BY", "context": "sentence describing the relationship"}}]

Valid relationship types:
- WORKS_AT: Person works at organization
- LOCATED_IN: Entity is located in a place
- RELATED_TO: General relationship between entities
- PART_OF: Entity is part of another entity
- CREATED_BY: Entity was created by another entity

Return ONLY the JSON array, no other text:"""

    def __init__(
        self,
        llm_provider: LlmProvider,
        relationship_types: Optional[list[RelationType]] = None,
        temperature: float = 0.1,
        max_retries: int = 3,
    ):
        """Initialize LLM relationship extractor.

        Args:
            llm_provider: LLM provider instance for making LLM calls
            relationship_types: List of relationship types to extract (None = all types)
            temperature: Temperature for LLM generation (lower = more deterministic)
            max_retries: Maximum number of retries on malformed JSON
        """
        self.llm_provider = llm_provider
        self.relationship_types = relationship_types
        self.temperature = temperature
        self.max_retries = max_retries

    def extract_relationships(self, text: str, entities: list[Entity]) -> list[Relationship]:
        """Extract relationships using LLM."""
        if not entities:
            return []

        # Create entity lookup by text for fast matching
        entity_map = {entity.text.lower(): entity for entity in entities}

        # Format entities for prompt
        entity_names = [entity.text for entity in entities]
        entities_str = ", ".join(entity_names)

        prompt = self.PROMPT_TEMPLATE.format(entities=entities_str, text=text)

        for attempt in range(self.max_retries):
            try:
                # Generate response from LLM
                response = self.llm_provider.generate_response(prompt)

                # Clean response
                response = self._clean_json_response(response)

                # Parse JSON response
                relationships_data = json.loads(response)

                if not isinstance(relationships_data, list):
                    raise ValueError("Response is not a JSON array")

                # Convert to Relationship objects
                relationships = []
                for rel_dict in relationships_data:
                    relationship = self._parse_relationship_dict(rel_dict, entity_map)
                    if relationship:
                        # Filter by relationship types if specified
                        if (
                            self.relationship_types
                            and relationship.relation_type not in self.relationship_types
                        ):
                            continue
                        relationships.append(relationship)

                logger.debug(f"Extracted {len(relationships)} relationships from text using LLM")
                return relationships

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(
                        f"Failed to extract relationships after {self.max_retries} attempts"
                    )
                    return []

        return []

    def extract_relationships_batch(
        self, texts: list[str], entities_batch: list[list[Entity]]
    ) -> list[list[Relationship]]:
        """Extract relationships from multiple texts.

        Note: This implementation processes texts sequentially.
        """
        results = []
        for i, (text, entities) in enumerate(zip(texts, entities_batch)):
            relationships = self.extract_relationships(text, entities)
            results.append(relationships)
            logger.debug(f"Processed {i + 1}/{len(texts)} texts")

        logger.info(f"Extracted relationships from {len(texts)} texts in batch")
        return results

    def _clean_json_response(self, response: str) -> str:
        """Clean LLM response to extract JSON.

        Args:
            response: Raw LLM response

        Returns:
            Cleaned JSON string
        """
        response = response.strip()

        # Remove markdown code blocks if present
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()
        return response

    def _parse_relationship_dict(
        self, rel_dict: dict, entity_map: dict[str, Entity]
    ) -> Optional[Relationship]:
        """Parse relationship dictionary from LLM response.

        Args:
            rel_dict: Dictionary with 'source', 'target', 'type', and 'context' keys
            entity_map: Dictionary mapping entity text to Entity objects

        Returns:
            Relationship object or None if parsing fails
        """
        try:
            source_text = rel_dict["source"].lower()
            target_text = rel_dict["target"].lower()
            type_str = rel_dict["type"]
            context = rel_dict.get("context", "")

            # Map to entities
            source_entity = entity_map.get(source_text)
            target_entity = entity_map.get(target_text)

            if not source_entity or not target_entity:
                logger.debug(
                    f"Could not find entities for relationship: {source_text} -> {target_text}"
                )
                return None

            # Map string type to RelationType enum
            try:
                relation_type = RelationType(type_str)
            except ValueError:
                logger.warning(f"Unknown relationship type: {type_str}, using RELATED_TO")
                relation_type = RelationType.RELATED_TO

            # Generate deterministic ID
            relationship_id = f"{source_entity.id}_{relation_type.value}_{target_entity.id}"

            # Create metadata
            metadata: RelationshipMetadata = {
                "sentence": context,
                "extraction_method": "llm",
            }

            return Relationship(
                id=relationship_id,
                source_entity_id=source_entity.id,
                target_entity_id=target_entity.id,
                relation_type=relation_type,
                confidence=0.8,  # Default confidence for LLM extraction
                context=context,
                metadata=metadata,
            )

        except (KeyError, TypeError) as e:
            logger.warning(f"Failed to parse relationship dict: {e}")
            return None
