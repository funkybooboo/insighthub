"""Workspace domain models."""

from typing import Optional

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class WorkspaceStatus(str, Enum):
    """Fine-grained workspace lifecycle statuses."""

    # Initial/Creation phase
    PENDING = "pending"  # Workspace created, waiting to start provisioning
    PROVISIONING = "provisioning"  # Setting up workspace infrastructure

    # Provisioning sub-stages
    CREATING_VECTOR_COLLECTION = "creating_vector_collection"  # Creating vector DB collection
    CREATING_GRAPH_STORE = "creating_graph_store"  # Creating graph database structures
    INITIALIZING_CONFIG = "initializing_config"  # Setting up RAG configuration

    # Active states
    READY = "ready"  # Workspace fully provisioned and operational
    ACTIVE = "active"  # Workspace in active use (same as ready, for clarity)

    # Maintenance states
    UPDATING = "updating"  # Workspace configuration being updated
    MIGRATING = "migrating"  # Migrating between RAG types or upgrading

    # Degraded states
    DEGRADED = "degraded"  # Workspace operational but with issues
    QUOTA_EXCEEDED = "quota_exceeded"  # Storage or resource limits reached

    # Deletion phase
    DELETING = "deleting"  # Workspace being deleted
    REMOVING_VECTORS = "removing_vectors"  # Cleaning up vector database
    REMOVING_GRAPHS = "removing_graphs"  # Cleaning up graph database
    REMOVING_DOCUMENTS = "removing_documents"  # Deleting stored documents

    # Terminal states
    DELETED = "deleted"  # Workspace fully removed
    FAILED = "failed"  # Provisioning or operation failed

    @classmethod
    def is_terminal(cls, status: str) -> bool:
        """Check if status is a terminal state."""
        return status in (cls.DELETED.value, cls.FAILED.value)

    @classmethod
    def is_operational(cls, status: str) -> bool:
        """Check if workspace is operational."""
        return status in (cls.READY.value, cls.ACTIVE.value, cls.DEGRADED.value)

    @classmethod
    def is_provisioning(cls, status: str) -> bool:
        """Check if workspace is being provisioned."""
        return status in (
            cls.PROVISIONING.value,
            cls.CREATING_VECTOR_COLLECTION.value,
            cls.CREATING_GRAPH_STORE.value,
            cls.INITIALIZING_CONFIG.value,
        )

    @classmethod
    def is_deleting(cls, status: str) -> bool:
        """Check if workspace is being deleted."""
        return status in (
            cls.DELETING.value,
            cls.REMOVING_VECTORS.value,
            cls.REMOVING_GRAPHS.value,
            cls.REMOVING_DOCUMENTS.value,
        )


@dataclass
class Workspace:
    """Workspace model for organizing document and chat session."""

    id: int
    name: str
    description: Optional[str]= None
    rag_type: str = "vector"  # "vector" or "graph"
    status: str = WorkspaceStatus.READY.value
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return f"<Workspace(id={self.id}, name={self.name})>"


@dataclass
class VectorRagConfig:
    """Vector RAG configuration for a workspace."""

    workspace_id: int
    embedding_model_vector_size: int = 768
    distance_metric: str = "cosine"
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
