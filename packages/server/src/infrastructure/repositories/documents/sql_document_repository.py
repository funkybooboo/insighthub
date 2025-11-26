"""SQL implementation of DocumentRepository."""

from datetime import datetime
from typing import Optional

from src.infrastructure.database import SqlDatabase
from src.infrastructure.models import Document

from .document_repository import DocumentRepository


class SqlDocumentRepository(DocumentRepository):
    """SQL implementation of documents repository."""

    def __init__(self, db: SqlDatabase):
        self.db = db

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
        query = """
            INSERT INTO documents (workspace_id, filename, file_size, mime_type, chunk_count, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.db.fetch_one(
            query,
            (
                workspace_id,
                filename,
                file_size,
                mime_type,
                chunk_count,
                processing_status,
                datetime.utcnow(),
            ),
        )

        if result:
            return Document(
                id=result["id"],
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

        raise RuntimeError("Failed to create document")

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        query = """
            SELECT id, workspace_id, filename, file_size, mime_type, chunk_count, status as processing_status, created_at
            FROM documents WHERE id = %s
        """
        result = self.db.fetch_one(query, (document_id,))
        if result:
            return Document(**result)
        return None

    def get_by_content_hash(self, content_hash: str) -> Optional[Document]:
        """Get document by content hash."""
        # Note: content_hash is not stored in DB yet, this is a placeholder
        # TODO: Add content_hash column to documents table
        return None

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
        """Get documents by user ID with pagination."""
        query = """
            SELECT d.id, d.workspace_id, d.filename, d.file_size, d.mime_type, d.chunk_count, d.status as processing_status, d.created_at
            FROM documents d
            JOIN workspaces w ON d.workspace_id = w.id
            WHERE w.user_id = %s
            ORDER BY d.created_at DESC
            LIMIT %s OFFSET %s
        """
        results = self.db.fetch_all(query, (user_id, limit, skip))
        return [Document(**result) for result in results]

    def get_by_workspace(
        self, workspace_id: int, limit: int = 50, offset: int = 0
    ) -> list[Document]:
        """Get documents for a workspace."""
        query = """
            SELECT id, workspace_id, filename, file_size, mime_type, chunk_count, status as processing_status, created_at
            FROM documents WHERE workspace_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        results = self.db.fetch_all(query, (workspace_id, limit, offset))
        return [Document(**result) for result in results]

    def update(self, document_id: int, **kwargs) -> Optional[Document]:
        """Update document fields."""
        # Get current document
        document = self.get_by_id(document_id)
        if not document:
            return None

        # Update fields
        for key, value in kwargs.items():
            if hasattr(document, key):
                setattr(document, key, value)

        # Update in database (only DB fields)
        query = """
            UPDATE documents
            SET filename = %s, file_size = %s, mime_type = %s, chunk_count = %s, status = %s
            WHERE id = %s
        """
        self.db.execute(
            query,
            (
                document.filename,
                document.file_size,
                document.mime_type,
                document.chunk_count,
                document.processing_status,
                document_id,
            ),
        )

        return document

    def update_status(
        self,
        document_id: int,
        status: str,
        error: str | None = None,
        chunk_count: int | None = None,
    ) -> bool:
        """Update document processing status."""
        query = """
            UPDATE documents
            SET status = %s, chunk_count = COALESCE(%s, chunk_count)
            WHERE id = %s
        """
        affected_rows = self.db.execute(query, (status, chunk_count, document_id))
        return affected_rows > 0

    def count_by_workspace(self, workspace_id: int, status_filter: str | None = None) -> int:
        """Count documents in workspace with optional status filter."""
        if status_filter:
            query = (
                "SELECT COUNT(*) as count FROM documents WHERE workspace_id = %s AND status = %s"
            )
            result = self.db.fetch_one(query, (workspace_id, status_filter))
        else:
            query = "SELECT COUNT(*) as count FROM documents WHERE workspace_id = %s"
            result = self.db.fetch_one(query, (workspace_id,))

        return result["count"] if result else 0

    def delete(self, document_id: int) -> bool:
        """Delete a document."""
        query = "DELETE FROM documents WHERE id = %s"
        affected_rows = self.db.execute(query, (document_id,))
        return affected_rows > 0
