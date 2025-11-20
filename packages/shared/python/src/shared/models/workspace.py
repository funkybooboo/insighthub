"""Workspace models for multi-tenant document and chat organization."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database.base import Base, TimestampMixin

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


class Workspace(Base, TimestampMixin):
    """Workspace model for organizing documents and chats."""

    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="provisioning", index=True
    )  # 'provisioning', 'ready', 'error'
    status_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="workspaces")
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="workspace", cascade="all, delete-orphan"
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession", back_populates="workspace", cascade="all, delete-orphan"
    )
    rag_config: Mapped["RagConfig"] = relationship(
        "RagConfig", back_populates="workspace", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Workspace(id={self.id}, name={self.name}, user_id={self.user_id})>"


class RagConfig(Base, TimestampMixin):
    """RAG configuration per workspace."""

    __tablename__ = "rag_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
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
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="rag_config")

    def __repr__(self) -> str:
        return f"<RagConfig(id={self.id}, workspace_id={self.workspace_id}, retriever_type={self.retriever_type})>"
