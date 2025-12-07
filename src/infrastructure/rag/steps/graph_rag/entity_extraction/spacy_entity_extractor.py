"""SpaCy-based entity extraction implementation.

This module provides entity extraction using spaCy's transformer-based NER models.
"""

import hashlib
import unicodedata
from typing import Optional

import spacy
from spacy.language import Language

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.graph_rag.entity_extraction.base import EntityExtractor
from src.infrastructure.types.graph import Entity, EntityMetadata, EntityType

logger = create_logger(__name__)


class SpacyEntityExtractor(EntityExtractor):
    """Entity extraction using spaCy NER models.

    This implementation uses spaCy's transformer-based models for high-quality
    named entity recognition. It maps spaCy labels to EntityType enums and
    generates deterministic entity IDs.
    """

    # Mapping from spaCy NER labels to EntityType enum
    LABEL_MAPPING = {
        "PERSON": EntityType.PERSON,
        "ORG": EntityType.ORGANIZATION,
        "GPE": EntityType.LOCATION,
        "LOC": EntityType.LOCATION,
        "PRODUCT": EntityType.PRODUCT,
        "EVENT": EntityType.EVENT,
        "NORP": EntityType.CONCEPT,
        "FAC": EntityType.LOCATION,
        "LAW": EntityType.CONCEPT,
        "LANGUAGE": EntityType.CONCEPT,
        "WORK_OF_ART": EntityType.CONCEPT,
    }

    def __init__(
        self,
        model_name: str = "en_core_web_sm",
        entity_types: Optional[list[EntityType]] = None,
        min_confidence: float = 0.5,
    ):
        """Initialize SpaCy entity extractor.

        Args:
            model_name: Name of spaCy model to load (default: en_core_web_sm)
            entity_types: List of entity types to extract (None = all types)
            min_confidence: Minimum confidence threshold for entities

        Note:
            For better performance, use "en_core_web_trf" transformer model.
            Install with: python -m spacy download en_core_web_trf
        """
        self.model_name = model_name
        self.entity_types = entity_types
        self.min_confidence = min_confidence

        try:
            self.nlp: Language = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.warning(f"Model {model_name} not found, falling back to en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
            self.model_name = "en_core_web_sm"

    def extract_entities(self, text: str) -> list[Entity]:
        """Extract entities from text using spaCy NER."""
        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            # Map spaCy label to EntityType
            entity_type = self._map_label_to_type(ent.label_)
            if entity_type is None:
                continue

            # Filter by entity types if specified
            if self.entity_types and entity_type not in self.entity_types:
                continue

            # Get confidence score (default to 0.8 if not available)
            confidence = self._get_confidence(ent)
            if confidence < self.min_confidence:
                continue

            # Normalize entity text
            normalized_text = self._normalize_text(ent.text)

            # Generate deterministic ID
            entity_id = self._generate_entity_id(normalized_text, entity_type)

            # Create metadata
            metadata: EntityMetadata = {
                "source_text": ent.text,
                "extraction_method": "spacy",
                "confidence_source": self.model_name,
            }

            entities.append(
                Entity(
                    id=entity_id,
                    text=normalized_text,
                    type=entity_type,
                    confidence=confidence,
                    metadata=metadata,
                )
            )

        logger.debug(f"Extracted {len(entities)} entities from text")
        return entities

    def extract_entities_batch(self, texts: list[str]) -> list[list[Entity]]:
        """Extract entities from multiple texts using spaCy's pipe for efficiency."""
        results = []

        # Use spaCy's nlp.pipe for efficient batch processing
        for doc in self.nlp.pipe(texts):
            entities = []
            for ent in doc.ents:
                entity_type = self._map_label_to_type(ent.label_)
                if entity_type is None:
                    continue

                if self.entity_types and entity_type not in self.entity_types:
                    continue

                confidence = self._get_confidence(ent)
                if confidence < self.min_confidence:
                    continue

                normalized_text = self._normalize_text(ent.text)
                entity_id = self._generate_entity_id(normalized_text, entity_type)

                metadata: EntityMetadata = {
                    "source_text": ent.text,
                    "extraction_method": "spacy",
                    "confidence_source": self.model_name,
                }

                entities.append(
                    Entity(
                        id=entity_id,
                        text=normalized_text,
                        type=entity_type,
                        confidence=confidence,
                        metadata=metadata,
                    )
                )

            results.append(entities)

        logger.info(f"Extracted entities from {len(texts)} texts in batch")
        return results

    def _map_label_to_type(self, label: str) -> Optional[EntityType]:
        """Map spaCy NER label to EntityType enum."""
        return self.LABEL_MAPPING.get(label)

    def _get_confidence(self, ent) -> float:
        """Get confidence score from entity.

        SpaCy doesn't provide confidence scores by default in all models.
        Returns a default of 0.8 for recognized entities.
        """
        # Try to get score from entity if available
        if hasattr(ent, "_") and hasattr(ent._, "score"):
            return float(ent._.score)
        return 0.8

    def _normalize_text(self, text: str) -> str:
        """Normalize entity text for consistency.

        Args:
            text: Raw entity text

        Returns:
            Normalized text (lowercase, stripped, Unicode normalized)
        """
        # Normalize Unicode characters (e.g., accented characters)
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
