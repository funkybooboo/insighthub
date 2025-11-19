"""Document repository."""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from shared.models.document import Document


class DocumentRepository(ABC):
    """Interface for Document repository operations."""

    @abstractmethod
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
        pass

    @abstractmethod
    def get_by_id(self, document_id: int) -> Document | None:
        """Get document by ID."""
        pass

    @abstractmethod
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
        """Get documents by user ID with pagination."""
        pass

    @abstractmethod
    def get_by_content_hash(self, content_hash: str) -> Document | None:
        """Get document by content hash."""
        pass

    @abstractmethod
    def update(self, document_id: int, **kwargs: str | int) -> Document | None:
        """Update document fields."""
        pass

    @abstractmethod
    def delete(self, document_id: int) -> bool:
        """Delete document by ID."""
        pass


class SqlDocumentRepository(DocumentRepository):
    """Repository for Document operations using SQL database."""

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

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
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_id(self, document_id: int) -> Document | None:
        """Get document by ID."""
        return self.db.query(Document).filter(Document.id == document_id).first()

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
        """Get all documents for a user with pagination."""
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_content_hash(self, content_hash: str) -> Document | None:
        """Get document by content hash."""
        return self.db.query(Document).filter(Document.content_hash == content_hash).first()

    def update(self, document_id: int, **kwargs: str | int) -> Document | None:
        """Update document fields."""
        document = self.get_by_id(document_id)
        if document:
            for key, value in kwargs.items():
                if hasattr(document, key):
                    setattr(document, key, value)
            self.db.commit()
            self.db.refresh(document)
        return document

    def delete(self, document_id: int) -> bool:
        """Delete document by ID."""
        document = self.get_by_id(document_id)
        if document:
            self.db.delete(document)
            self.db.commit()
            return True
        return False
