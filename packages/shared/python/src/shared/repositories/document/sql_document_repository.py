"""SQL implementation of document repository."""

from sqlalchemy.orm import Session

from shared.models.document import Document
from shared.types.option import Nothing, Option, Some

from .document_repository import DocumentRepository


class SqlDocumentRepository(DocumentRepository):
    """Repository for Document operations using SQL database."""

    def __init__(self, db: Session) -> None:
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self._db = db

    def create(
        self,
        user_id: int,
        filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        content_hash: str,
        chunk_count: int | None = None,
        rag_collection: str | None = None,
    ) -> Document:
        """Create a new document."""
        document = Document(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            content_hash=content_hash,
            chunk_count=chunk_count,
            rag_collection=rag_collection,
        )
        self._db.add(document)
        self._db.commit()
        self._db.refresh(document)
        return document

    def get_by_id(self, document_id: int) -> Option[Document]:
        """Get document by ID."""
        document = self._db.query(Document).filter(Document.id == document_id).first()
        if document is None:
            return Nothing()
        return Some(document)

    def get_by_user(self, user_id: int, skip: int, limit: int) -> list[Document]:
        """Get all documents for a user with pagination."""
        return (
            self._db.query(Document)
            .filter(Document.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_content_hash(self, content_hash: str) -> Option[Document]:
        """Get document by content hash."""
        document = (
            self._db.query(Document).filter(Document.content_hash == content_hash).first()
        )
        if document is None:
            return Nothing()
        return Some(document)

    def update(self, document_id: int, **kwargs: str | int) -> Option[Document]:
        """Update document fields."""
        result = self.get_by_id(document_id)
        if result.is_nothing():
            return Nothing()

        document = result.unwrap()
        for key, value in kwargs.items():
            if hasattr(document, key):
                setattr(document, key, value)
        self._db.commit()
        self._db.refresh(document)
        return Some(document)

    def delete(self, document_id: int) -> bool:
        """Delete document by ID."""
        result = self.get_by_id(document_id)
        if result.is_nothing():
            return False

        document = result.unwrap()
        self._db.delete(document)
        self._db.commit()
        return True
