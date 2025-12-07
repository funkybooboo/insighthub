"""Default RAG configuration DTOs."""

from dataclasses import dataclass
from typing import Optional

# ============================================================================
# Request DTOs (User Input)
# ============================================================================


@dataclass
class CreateUpdateDefaultRagConfigRequest:
    """Request DTO for creating/updating default RAG configuration."""

    rag_type: Optional[str] = None
    # Vector config fields
    chunking_algorithm: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    embedding_algorithm: Optional[str] = None
    embedding_model_vector_size: Optional[int] = None
    distance_metric: Optional[str] = None
    top_k: Optional[int] = None
    rerank_algorithm: Optional[str] = None
    # Graph config fields
    entity_extraction_algorithm: Optional[str] = None
    relationship_extraction_algorithm: Optional[str] = None
    clustering_algorithm: Optional[str] = None
    entity_types: Optional[list[str]] = None
    relationship_types: Optional[list[str]] = None
    max_traversal_depth: Optional[int] = None
    top_k_entities: Optional[int] = None
    top_k_communities: Optional[int] = None
    include_entity_neighborhoods: Optional[bool] = None
    community_min_size: Optional[int] = None
    clustering_resolution: Optional[float] = None
    clustering_max_level: Optional[int] = None


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

    entity_extraction_algorithm: str
    relationship_extraction_algorithm: str
    clustering_algorithm: str
    entity_types: list[str]
    relationship_types: list[str]
    max_traversal_depth: int
    top_k_entities: int
    top_k_communities: int
    include_entity_neighborhoods: bool
    community_min_size: int
    clustering_resolution: float
    clustering_max_level: int


@dataclass
class DefaultRagConfigResponse:
    """Response DTO for default RAG configuration."""

    id: int
    rag_type: str
    vector_config: VectorRagConfigResponse
    graph_config: GraphRagConfigResponse
    created_at: str
    updated_at: str
