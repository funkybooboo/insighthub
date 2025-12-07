"""LLM-based entity extraction implementation.

This module provides entity extraction using large language models (LLMs)
with structured JSON output.
"""

import hashlib
import json
import unicodedata
from typing import Optional

from src.infrastructure.llm.llm_provider import LlmProvider
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.graph_rag.entity_extraction.base import EntityExtractor
from src.infrastructure.types.graph import Entity, EntityMetadata, EntityType

logger = create_logger(__name__)


class LlmEntityExtractor(EntityExtractor):
    """Entity extraction using LLM with structured JSON output.

    This implementation uses an LLM to extract entities from text by prompting
    for structured JSON responses. It supports retries for malformed JSON.
    """

    PROMPT_TEMPLATE = """Extract named entities from the following text. Return ONLY a JSON array with this exact format:
[{{"text": "entity name", "type": "PERSON|ORG|GPE|PRODUCT|EVENT|CONCEPT"}}]

Valid entity types:
- PERSON: People, including fictional characters
- ORG: Organizations, companies, institutions
- GPE: Geopolitical entities (countries, cities, states)
- PRODUCT: Products, vehicles, foods, etc.
- EVENT: Named events, holidays, etc.
- CONCEPT: Abstract concepts, theories, laws

Text: {text}

Return ONLY the JSON array, no other text:"""

    def __init__(
        self,
        llm_provider: LlmProvider,
        entity_types: Optional[list[EntityType]] = None,
        temperature: float = 0.1,
        max_retries: int = 3,
    ):
        """Initialize LLM entity extractor.

        Args:
            llm_provider: LLM provider instance for making LLM calls
            entity_types: List of entity types to extract (None = all types)
            temperature: Temperature for LLM generation (lower = more deterministic)
            max_retries: Maximum number of retries on malformed JSON
        """
        self.llm_provider = llm_provider
        self.entity_types = entity_types
        self.temperature = temperature
        self.max_retries = max_retries

    def extract_entities(self, text: str) -> list[Entity]:
        """Extract entities from text using LLM."""
        prompt = self.PROMPT_TEMPLATE.format(text=text)

        for attempt in range(self.max_retries):
            try:
                # Generate response from LLM
                response = self.llm_provider.generate_response(prompt)

                # Clean response (remove markdown code blocks if present)
                response = self._clean_json_response(response)

                # Parse JSON response
                entities_data = json.loads(response)

                if not isinstance(entities_data, list):
                    raise ValueError("Response is not a JSON array")

                # Convert to Entity objects
                entities = []
                for entity_dict in entities_data:
                    entity = self._parse_entity_dict(entity_dict)
                    if entity:
                        # Filter by entity types if specified
                        if self.entity_types and entity.type not in self.entity_types:
                            continue
                        entities.append(entity)

                logger.debug(f"Extracted {len(entities)} entities from text using LLM")
                return entities

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to extract entities after {self.max_retries} attempts")
                    return []

        return []

    def extract_entities_batch(self, texts: list[str]) -> list[list[Entity]]:
        """Extract entities from multiple texts.

        Note: This implementation processes texts sequentially. For better
        performance with large batches, consider parallelization.
        """
        results = []
        for i, text in enumerate(texts):
            entities = self.extract_entities(text)
            results.append(entities)
            logger.debug(f"Processed {i + 1}/{len(texts)} texts")

        logger.info(f"Extracted entities from {len(texts)} texts in batch")
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

    def _parse_entity_dict(self, entity_dict: dict) -> Optional[Entity]:
        """Parse entity dictionary from LLM response.

        Args:
            entity_dict: Dictionary with 'text' and 'type' keys

        Returns:
            Entity object or None if parsing fails
        """
        try:
            text = entity_dict["text"]
            type_str = entity_dict["type"]

            # Map string type to EntityType enum
            try:
                entity_type = EntityType(type_str)
            except ValueError:
                logger.warning(f"Unknown entity type: {type_str}, skipping")
                return None

            # Normalize entity text
            normalized_text = self._normalize_text(text)

            # Generate deterministic ID
            entity_id = self._generate_entity_id(normalized_text, entity_type)

            # Create metadata
            metadata: EntityMetadata = {
                "source_text": text,
                "extraction_method": "llm",
                "confidence_source": "llm_structured_output",
            }

            return Entity(
                id=entity_id,
                text=normalized_text,
                type=entity_type,
                confidence=0.85,  # Default confidence for LLM extraction
                metadata=metadata,
            )

        except (KeyError, TypeError) as e:
            logger.warning(f"Failed to parse entity dict: {e}")
            return None

    def _normalize_text(self, text: str) -> str:
        """Normalize entity text for consistency.

        Args:
            text: Raw entity text

        Returns:
            Normalized text (lowercase, stripped, Unicode normalized)
        """
        # Normalize Unicode characters
        text = unicodedata.normalize("NFKC", text)
        # Convert to lowercase and strip whitespace
        text = text.lower().strip()
        # Remove extra whitespace
        text = " ".join(text.split())
        return text

    def _generate_entity_id(self, normalized_text: str, entity_type: EntityType) -> str:
        """Generate deterministic entity ID.

        Args:
            normalized_text: Normalized entity text
            entity_type: Entity type enum

        Returns:
            16-character hex ID based on text and type
        """
        # Include entity type in ID to allow same text with different types
        combined = f"{normalized_text}|{entity_type.value}"
        hash_obj = hashlib.sha256(combined.encode("utf-8"))
        return hash_obj.hexdigest()[:16]
