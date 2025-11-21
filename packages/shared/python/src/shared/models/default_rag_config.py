from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.sql_database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from shared.models.chat import ChatSession
    from shared.models.document import Document
    from shared.models.user import User


class DefaultRagConfig(Base, TimestampMixin):
    """Default RAG configuration per user (used when creating new workspaces)."""

    __tablename__ = "default_rag_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )

    # Embedding configuration
    embedding_model: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="nomic-embed-text"
    )
    embedding_dim: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Retriever configuration
    retriever_type: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="vector"
    )  # 'vector', 'graph', 'hybrid'

    # Chunking configuration
    chunk_size: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1000")
    chunk_overlap: Mapped[int] = mapped_column(Integer, nullable=False, server_default="200")

    # Retrieval configuration
    top_k: Mapped[int] = mapped_column(Integer, nullable=False, server_default="8")

    # Reranking configuration
    rerank_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    rerank_model: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="default_rag_config")

    def __repr__(self) -> str:
        return f"<DefaultRagConfig(id={self.id}, user_id={self.user_id}, retriever_type={self.retriever_type})>"
