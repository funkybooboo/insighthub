"""Default RAG configuration DTOs."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class VectorRagConfigDTO:
    """DTO for vector RAG configuration."""

    embedding_algorithm: str
    chunking_algorithm: str
    rerank_algorithm: str
    chunk_size: int
    chunk_overlap: int
    top_k: int


@dataclass
class GraphRagConfigDTO:
    """DTO for graph RAG configuration."""

    entity_extraction_algorithm: str
    relationship_extraction_algorithm: str
    clustering_algorithm: str


@dataclass
class DefaultRagConfigDTO:
    """DTO for default RAG configuration response."""

    id: int
    user_id: int
    vector_config: VectorRagConfigDTO
    graph_config: GraphRagConfigDTO
    created_at: str
    updated_at: str


@dataclass
class CreateUpdateDefaultRagConfigDTO:
    """DTO for creating/updating default RAG configuration."""

    vector_config: Optional[VectorRagConfigDTO] = None
    graph_config: Optional[GraphRagConfigDTO] = None


@dataclass
class DefaultRagConfigResponseDTO:
    """DTO for default RAG configuration API response."""

    id: int
    user_id: int
    vector_config: dict
    graph_config: dict
    created_at: str
    updated_at: str
