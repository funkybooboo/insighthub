"""Graph RAG type definitions.

This module defines type-safe structures for graph-based RAG operations including
entities, relationships, communities, and graph subgraphs.
"""

from dataclasses import dataclass
from enum import Enum
from typing import TypedDict


class EntityType(str, Enum):
    """Valid entity types for graph extraction."""

    PERSON = "PERSON"
    ORGANIZATION = "ORG"
    LOCATION = "GPE"
    PRODUCT = "PRODUCT"
    EVENT = "EVENT"
    CONCEPT = "CONCEPT"


class RelationType(str, Enum):
    """Valid relationship types for graph extraction."""

    WORKS_AT = "WORKS_AT"
    LOCATED_IN = "LOCATED_IN"
    RELATED_TO = "RELATED_TO"
    PART_OF = "PART_OF"
    CREATED_BY = "CREATED_BY"


class EntityMetadata(TypedDict, total=False):
    """Type-safe entity metadata.

    All fields are optional (total=False) to allow flexible metadata.
    """

    document_id: str
    document_ids: list[str]
    chunk_id: str
    source_text: str
    extraction_method: str
    confidence_source: str
    version: int


class RelationshipMetadata(TypedDict, total=False):
    """Type-safe relationship metadata.

    All fields are optional (total=False) to allow flexible metadata.
    """

    document_id: str
    chunk_id: str
    sentence: str
    extraction_method: str
    source: str


class CommunityMetadata(TypedDict, total=False):
    """Type-safe community metadata.

    All fields are optional (total=False) to allow flexible metadata.
    """

    detection_algorithm: str
    resolution: float
    modularity: float
    algo: str


@dataclass
class Entity:
    """Represents an entity extracted from text.

    Entities are the nodes in the knowledge graph, representing real-world
    objects, people, organizations, concepts, etc.
    """

    id: str
    text: str
    type: EntityType
    confidence: float
    metadata: EntityMetadata


@dataclass
class Relationship:
    """Represents a relationship between two entities.

    Relationships are the edges in the knowledge graph, connecting entities
    and describing their interactions or associations.
    """

    id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: RelationType
    confidence: float
    context: str
    metadata: RelationshipMetadata


@dataclass
class Community:
    """Represents a community of related entities.

    Communities are groups of densely connected entities identified through
    clustering algorithms like Leiden or Louvain.
    """

    id: str
    workspace_id: str
    entity_ids: list[str]
    level: int
    summary: str
    score: float
    metadata: CommunityMetadata


@dataclass
class GraphSubgraph:
    """Represents a subgraph extracted from the knowledge graph.

    Subgraphs are returned by query operations and contain entities,
    relationships, and information about central entities.
    """

    entities: list[Entity]
    relationships: list[Relationship]
    central_entities: list[str]
