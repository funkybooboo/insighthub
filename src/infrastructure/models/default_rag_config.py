"""Default RAG configuration model."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DefaultVectorRagConfig:
    """Default vector RAG configuration (single-user system)."""

    embedding_algorithm: str = "ollama"
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


@dataclass
class DefaultRagConfig:
    """Default RAG configuration (single-user system, used when creating new workspaces)."""

    id: int
    rag_type: str = "vector"  # "vector" or "graph"
    # Default configurations for different RAG types
    vector_config: DefaultVectorRagConfig = field(default_factory=DefaultVectorRagConfig)
    graph_config: DefaultGraphRagConfig = field(default_factory=DefaultGraphRagConfig)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<DefaultRagConfig(id={self.id}, rag_type={self.rag_type})>"
