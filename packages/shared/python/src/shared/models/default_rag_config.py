"""Default RAG configuration model (per user)."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DefaultRagConfig:
    """Default RAG configuration per user (used when creating new workspaces)."""

    id: int
    user_id: int
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
        return f"<DefaultRagConfig(id={self.id}, user_id={self.user_id}, retriever_type={self.retriever_type})>"
