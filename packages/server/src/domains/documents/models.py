"""Document domain models."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.domains.users.models import User


class Document(Base, TimestampMixin):
    """Document model for storing uploaded documents."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    content_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # SHA-256 hash
    chunk_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rag_collection: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # Vector store collection name

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.filename}, user_id={self.user_id})>"
