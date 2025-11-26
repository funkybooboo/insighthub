"""In-memory implementation of DocumentRepository."""

from typing import Optional

from src.infrastructure.models import Document
from .document_repository import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    """In-memory implementation of DocumentRepository for development/testing."""

    def __init__(self):
        """Initialize the repository."""
        self._documents: dict[int, Document] = {}
        self._next_id = 1

    def create(
        self,
        workspace_id: int,
        filename: str,
        file_size: int,
        mime_type: str,
        chunk_count: int = 0,
        processing_status: str = "processing",
        processing_error: str | None = None,
        file_path: str | None = None,
        content_hash: str | None = None,
        rag_collection: str | None = None,
        parsed_text: str | None = None,
    ) -> Document:
        """Create a new document."""
        document = Document(
            id=self._next_id,
            workspace_id=workspace_id,
            filename=filename,
            file_size=file_size,
            mime_type=mime_type,
            chunk_count=chunk_count,
            processing_status=processing_status,
            processing_error=processing_error,
            file_path=file_path,
            content_hash=content_hash,
            rag_collection=rag_collection,
            parsed_text=parsed_text,
        )
        self._documents[self._next_id] = document
        self._next_id += 1
        return document

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        return self._documents.get(document_id)

    def get_by_content_hash(self, content_hash: str) -> Optional[Document]:
        """Get document by content hash."""
        for doc in self._documents.values():
            if doc.content_hash == content_hash:
                return doc
        return None

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
        """Get documents by users ID with pagination."""
        # Note: This is a simplified implementation since we don't have user_id in Document model
        # In a real implementation, we'd need to join with workspace table
        user_documents = [doc for doc in self._documents.values()]
        return user_documents[skip:skip + limit]

    def get_by_workspace(self, workspace_id: int, limit: int = 50, offset: int = 0) -> list[Document]:
        """Get documents for a workspace."""
        workspace_documents = [doc for doc in self._documents.values() if doc.workspace_id == workspace_id]
        return workspace_documents[offset:offset + limit]

    def update(self, document_id: int, **kwargs) -> Optional[Document]:
        """Update document fields."""
        document = self._documents.get(document_id)
        if not document:
            return None

        for key, value in kwargs.items():
            if hasattr(document, key):
                setattr(document, key, value)

        return document

    def update_status(
        self,
        document_id: int,
        status: str,
        error: str | None = None,
        chunk_count: int | None = None,
    ) -> bool:
        """Update document processing status."""
        document = self._documents.get(document_id)
        if not document:
            return False

        document.processing_status = status
        if error is not None:
            document.processing_error = error
        if chunk_count is not None:
            document.chunk_count = chunk_count

        return True

    def count_by_workspace(self, workspace_id: int, status_filter: str | None = None) -> int:
        """Count documents in workspace with optional status filter."""
        workspace_documents = [doc for doc in self._documents.values() if doc.workspace_id == workspace_id]
        if status_filter:
            workspace_documents = [doc for doc in workspace_documents if doc.processing_status == status_filter]
        return len(workspace_documents)

    def delete(self, document_id: int) -> bool:
        """Delete a document."""
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False