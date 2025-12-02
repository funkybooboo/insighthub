"""Workspace domain models."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Workspace:
    """Workspace model for organizing document and chat session."""

    id: int
    name: str
    description: str | None = None
    rag_type: str = "vector"  # "vector" or "graph"
    status: str = "ready"  # "ready", "provisioning", "deleting", "failed"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return f"<Workspace(id={self.id}, name={self.name})>"


@dataclass
class VectorRagConfig:
    """Vector RAG configuration for a workspace."""

    workspace_id: int
    embedding_algorithm: str = "ollama"
    chunking_algorithm: str = "sentence"
    rerank_algorithm: str = "none"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class GraphRagConfig:
    """Graph RAG configuration for a workspace."""

    workspace_id: int
    entity_extraction_algorithm: str = "spacy"
    relationship_extraction_algorithm: str = "dependency-parsing"
    clustering_algorithm: str = "leiden"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# Backward compatibility - keep RagConfig for now
@dataclass
class RagConfig:
    """Generic RAG configuration (deprecated - use specific config types)."""

    workspace_id: int
    rag_type: str
    config: dict
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
