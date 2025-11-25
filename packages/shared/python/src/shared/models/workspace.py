"""Workspace models for multi-tenant document and chat organization."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Workspace:
    """Workspace model for organizing documents and chats."""

    user_id: int
    name: str
    id: int = 0
    description: str | None = None
    is_active: bool = True
    status: str = "provisioning"  # 'provisioning', 'ready', 'error'
    status_message: str | None = None
    rag_type: str = "vector"  # 'vector', 'graph'
    vector_rag_config_id: int | None = None
    graph_rag_config_id: int | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Workspace(id={self.id}, name={self.name}, user_id={self.user_id})>"


@dataclass
class RagConfig:
    """RAG configuration per workspace."""

    workspace_id: int
    id: int = 0
    # Embedding configuration
    embedding_model: str = "nomic-embed-text"
    embedding_dim: int | None = None
    # Retriever configuration
    retriever_type: str = "vector"  # 'vector', 'graph', 'hybrid'
    # Chunking configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    # Retrieval configuration
    top_k: int = 8
    # Reranking configuration
    rerank_enabled: bool = False
    rerank_model: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<RagConfig(id={self.id}, workspace_id={self.workspace_id}, retriever_type={self.retriever_type})>"
