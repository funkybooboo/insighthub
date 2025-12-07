"""Dependency parser-based relationship extraction implementation.

This module provides relationship extraction using spaCy's dependency parsing
to identify subject-verb-object triples.
"""

from typing import Optional

import spacy
from spacy.language import Language
from spacy.tokens import Token

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.graph_rag.relationship_extraction.base import (
    RelationshipExtractor,
)
from src.infrastructure.types.graph import Entity, Relationship, RelationshipMetadata, RelationType

logger = create_logger(__name__)


class DependencyParserExtractor(RelationshipExtractor):
    """Relationship extraction using spaCy dependency parsing.

    This implementation uses spaCy's dependency parser to identify
    subject-verb-object triples and map them to relationships.
    """

    # Mapping from verb lemmas to RelationType enum
    VERB_MAPPING = {
        "work": RelationType.WORKS_AT,
        "employ": RelationType.WORKS_AT,
        "hire": RelationType.WORKS_AT,
        "locate": RelationType.LOCATED_IN,
        "base": RelationType.LOCATED_IN,
        "situate": RelationType.LOCATED_IN,
        "headquarter": RelationType.LOCATED_IN,
        "relate": RelationType.RELATED_TO,
        "connect": RelationType.RELATED_TO,
        "associate": RelationType.RELATED_TO,
        "link": RelationType.RELATED_TO,
        "contain": RelationType.PART_OF,
        "include": RelationType.PART_OF,
        "comprise": RelationType.PART_OF,
        "create": RelationType.CREATED_BY,
        "develop": RelationType.CREATED_BY,
        "build": RelationType.CREATED_BY,
        "make": RelationType.CREATED_BY,
        "design": RelationType.CREATED_BY,
    }

    # Subject dependency labels
    SUBJECT_DEPS = {"nsubj", "nsubjpass"}
    # Object dependency labels
    OBJECT_DEPS = {"dobj", "pobj", "attr"}

    def __init__(
        self,
        model_name: str = "en_core_web_sm",
        relationship_types: Optional[list[RelationType]] = None,
        min_confidence: float = 0.6,
    ):
        """Initialize dependency parser relationship extractor.

        Args:
            model_name: Name of spaCy model to load
            relationship_types: List of relationship types to extract (None = all types)
            min_confidence: Minimum confidence threshold for relationships
        """
        self.model_name = model_name
        self.relationship_types = relationship_types
        self.min_confidence = min_confidence

        try:
            self.nlp: Language = spacy.load(model_name)
            logger.info(f"Loaded spaCy model for dependency parsing: {model_name}")
        except OSError:
            logger.warning(f"Model {model_name} not found, falling back to en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
            self.model_name = "en_core_web_sm"

    def extract_relationships(self, text: str, entities: list[Entity]) -> list[Relationship]:
        """Extract relationships using dependency parsing."""
        if not entities:
            return []

        # Create entity lookup by text for fast matching
        entity_map = {entity.text.lower(): entity for entity in entities}

        doc = self.nlp(text)
        relationships = []

        # Extract subject-verb-object triples
        for token in doc:
            if token.pos_ == "VERB":
                # Find subject and object
                subject = self._find_subject(token)
                obj = self._find_object(token)

                if subject and obj:
                    # Match subject and object to entities
                    subject_entity = self._match_token_to_entity(subject, entity_map)
                    object_entity = self._match_token_to_entity(obj, entity_map)

                    if subject_entity and object_entity:
                        # Map verb to relationship type
                        relation_type = self._map_verb_to_relation_type(token)

                        # Filter by relationship types if specified
                        if self.relationship_types and relation_type not in self.relationship_types:
                            continue

                        # Create relationship
                        relationship = self._create_relationship(
                            source_entity=subject_entity,
                            target_entity=object_entity,
                            relation_type=relation_type,
                            context=token.sent.text,
                            confidence=0.7,  # Default confidence for dependency parsing
                        )
                        relationships.append(relationship)

        logger.debug(f"Extracted {len(relationships)} relationships using dependency parsing")
        return relationships

    def extract_relationships_batch(
        self, texts: list[str], entities_batch: list[list[Entity]]
    ) -> list[list[Relationship]]:
        """Extract relationships from multiple texts using spaCy's pipe."""
        results = []

        for text, entities in zip(texts, entities_batch):
            relationships = self.extract_relationships(text, entities)
            results.append(relationships)

        logger.info(f"Extracted relationships from {len(texts)} texts in batch")
        return results

    def _find_subject(self, verb: Token) -> Optional[Token]:
        """Find the subject of a verb token."""
        for child in verb.children:
            if child.dep_ in self.SUBJECT_DEPS:
                # Return the head of the subject noun phrase
                return self._get_noun_phrase_root(child)
        return None

    def _find_object(self, verb: Token) -> Optional[Token]:
        """Find the object of a verb token."""
        for child in verb.children:
            if child.dep_ in self.OBJECT_DEPS:
                # Return the head of the object noun phrase
                return self._get_noun_phrase_root(child)
        return None

    def _get_noun_phrase_root(self, token: Token) -> Token:
        """Get the root token of a noun phrase."""
        # Follow compound and other noun modifiers to get the main noun
        while token.head != token and token.head.pos_ in {"NOUN", "PROPN"}:
            token = token.head
        return token

    def _match_token_to_entity(
        self, token: Token, entity_map: dict[str, Entity]
    ) -> Optional[Entity]:
        """Match a token to an entity from the entity map.

        Args:
            token: spaCy token to match
            entity_map: Dictionary mapping normalized entity text to Entity objects

        Returns:
            Matched Entity or None
        """
        # Try exact match
        token_text = token.text.lower()
        if token_text in entity_map:
            return entity_map[token_text]

        # Try lemma match
        if token.lemma_.lower() in entity_map:
            return entity_map[token.lemma_.lower()]

        # Try matching the full noun phrase
        noun_phrase = self._get_full_noun_phrase(token)
        if noun_phrase.lower() in entity_map:
            return entity_map[noun_phrase.lower()]

        return None

    def _get_full_noun_phrase(self, token: Token) -> str:
        """Get the full noun phrase containing the token."""
        # Get all tokens in the noun phrase
        subtree = list(token.subtree)
        # Filter to only noun-related tokens
        phrase_tokens = [t for t in subtree if t.pos_ in {"NOUN", "PROPN", "ADJ", "DET"}]
        # Sort by position in sentence
        phrase_tokens.sort(key=lambda t: t.i)
        # Join into phrase
        return " ".join([t.text for t in phrase_tokens])

    def _map_verb_to_relation_type(self, verb: Token) -> RelationType:
        """Map verb token to RelationType enum.

        Args:
            verb: Verb token

        Returns:
            RelationType enum (defaults to RELATED_TO if no mapping found)
        """
        lemma = verb.lemma_.lower()
        return self.VERB_MAPPING.get(lemma, RelationType.RELATED_TO)

    def _create_relationship(
        self,
        source_entity: Entity,
        target_entity: Entity,
        relation_type: RelationType,
        context: str,
        confidence: float,
    ) -> Relationship:
        """Create a Relationship object.

        Args:
            source_entity: Source entity
            target_entity: Target entity
            relation_type: Type of relationship
            context: Sentence or context containing the relationship
            confidence: Confidence score

        Returns:
            Relationship object
        """
        # Generate deterministic ID
        relationship_id = f"{source_entity.id}_{relation_type.value}_{target_entity.id}"

        # Create metadata
        metadata: RelationshipMetadata = {
            "sentence": context,
            "extraction_method": "dependency-parsing",
        }

        return Relationship(
            id=relationship_id,
            source_entity_id=source_entity.id,
            target_entity_id=target_entity.id,
            relation_type=relation_type,
            confidence=confidence,
            context=context,
            metadata=metadata,
        )
