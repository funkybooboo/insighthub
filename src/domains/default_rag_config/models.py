"""Default RAG configuration model."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class DefaultVectorRagConfig:
    """Default vector RAG configuration (single-user system)."""

    embedding_model_vector_size: int = 768
    distance_metric: str = "cosine"
    embedding_algorithm: str = "nomic-embed-text"
    chunking_algorithm: str = "sentence"
    rerank_algorithm: str = "none"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5


@dataclass
class DefaultGraphRagConfig:
    """Default graph RAG configuration (single-user system)."""

    entity_extraction_algorithm: str = "spacy"
    relationship_extraction_algorithm: str = "dependency-parsing"
    clustering_algorithm: str = "leiden"
    entity_types: list[str] = field(
        default_factory=lambda: ["PERSON", "ORG", "GPE", "PRODUCT", "EVENT", "CONCEPT"]
    )
    relationship_types: list[str] = field(
        default_factory=lambda: ["WORKS_AT", "LOCATED_IN", "RELATED_TO", "PART_OF", "CREATED_BY"]
    )
    max_traversal_depth: int = 2
    top_k_entities: int = 10
    top_k_communities: int = 3
    include_entity_neighborhoods: bool = True
    community_min_size: int = 3
    clustering_resolution: float = 1.0
    clustering_max_level: int = 3


@dataclass
class DefaultRagConfig:
    """Default RAG configuration (single-user system, used when creating new workspace)."""

    id: int
    rag_type: str = "vector"  # "vector" or "graph"
    # Default configurations for different RAG types
    vector_config: DefaultVectorRagConfig = field(default_factory=DefaultVectorRagConfig)
    graph_config: DefaultGraphRagConfig = field(default_factory=DefaultGraphRagConfig)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return f"<DefaultRagConfig(id={self.id}, rag_type={self.rag_type})>"
