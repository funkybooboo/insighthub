"""Default RAG configuration DTOs."""

from dataclasses import dataclass
from typing import Optional

# ============================================================================
# Request DTOs (User Input)
# ============================================================================


@dataclass
class CreateUpdateDefaultRagConfigRequest:
    """Request DTO for creating/updating default RAG configuration."""

    # TODO: Add missing vector fields: embedding_model_vector_size, distance_metric
    # TODO: Add missing graph fields: entity_types, relationship_types, max_traversal_depth,
    #       top_k_entities, top_k_communities, include_entity_neighborhoods, community_min_size,
    #       clustering_resolution, clustering_max_level

    rag_type: Optional[str] = None
    # Vector config fields
    chunking_algorithm: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    embedding_algorithm: Optional[str] = None
    top_k: Optional[int] = None
    rerank_algorithm: Optional[str] = None
    # Graph config fields
    entity_extraction_algorithm: Optional[str] = None
    relationship_extraction_algorithm: Optional[str] = None
    clustering_algorithm: Optional[str] = None


# ============================================================================
# Response DTOs (Service Output)
# ============================================================================


@dataclass
class VectorRagConfigResponse:
    """Response DTO for vector RAG configuration."""

    embedding_model_vector_size: int
    distance_metric: str
    embedding_algorithm: str
    chunking_algorithm: str
    rerank_algorithm: str
    chunk_size: int
    chunk_overlap: int
    top_k: int


@dataclass
class GraphRagConfigResponse:
    """Response DTO for graph RAG configuration."""

    # TODO: Add missing fields from migration 008: entity_types (list), relationship_types (list),
    #       max_traversal_depth (int), top_k_entities (int), top_k_communities (int),
    #       include_entity_neighborhoods (bool), community_min_size (int),
    #       clustering_resolution (float), clustering_max_level (int)

    entity_extraction_algorithm: str
    relationship_extraction_algorithm: str
    clustering_algorithm: str


@dataclass
class DefaultRagConfigResponse:
    """Response DTO for default RAG configuration."""

    id: int
    rag_type: str
    vector_config: VectorRagConfigResponse
    graph_config: GraphRagConfigResponse
    created_at: str
    updated_at: str
