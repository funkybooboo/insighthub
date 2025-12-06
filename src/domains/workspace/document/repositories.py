"""SQL implementation of DocumentRepository."""

from datetime import UTC, datetime
from typing import Optional

from returns.result import Failure, Result, Success

from src.domains.workspace.document.models import Document
from src.infrastructure.logger import create_logger
from src.infrastructure.sql_database import DatabaseException, SqlDatabase
from src.infrastructure.types import DatabaseError

logger = create_logger(__name__)


class DocumentRepository:
    """SQL implementation of document repository."""

    def __init__(self, db: SqlDatabase):
        self.db = db

    def create(
        self,
        workspace_id: int,
        filename: str,
        file_size: int,
        mime_type: str,
        chunk_count: int = 0,
        status: str = "processing",
        error_message: Optional[str]= None,
        file_path: Optional[str]= None,
        content_hash: Optional[str]= None,
        rag_collection: Optional[str]= None,
        parsed_text: Optional[str]= None,
    ) -> Result[Document, DatabaseError]:
        """Create a new document."""
        query = """
            INSERT INTO documents (
                workspace_id, filename, original_filename, size_bytes, mime_type,
                file_hash, storage_path, chunk_count, status, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        try:
            result = self.db.fetch_one(
                query,
                (
                    workspace_id,
                    filename,
                    filename,  # original_filename same as filename
                    file_size,
                    mime_type,
                    content_hash or "",  # file_hash
                    file_path or "",  # storage_path
                    chunk_count,
                    status,
                    datetime.now(UTC),
                ),
            )
        except DatabaseException as e:
            logger.error(f"Database error creating document: {e}")
            return Failure(DatabaseError(e.message, operation="create_document"))

        if not result:
            return Failure(DatabaseError("Insert returned no result", operation="create_document"))

        return Success(
            Document(
                id=result["id"],
                workspace_id=workspace_id,
                filename=filename,
                original_filename=filename,
                file_size=file_size,
                mime_type=mime_type,
                chunk_count=chunk_count,
                status=status,
                error_message=error_message,
                file_path=file_path,
                content_hash=content_hash,
                rag_collection=rag_collection,
                parsed_text=parsed_text,
            )
        )

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        query = """
            SELECT
                id, workspace_id, filename, original_filename,
                size_bytes as file_size, mime_type, chunk_count, status,
                error_message, file_hash as content_hash, storage_path as file_path,
                created_at, updated_at
            FROM documents WHERE id = %s
        """
        try:
            result = self.db.fetch_one(query, (document_id,))
        except DatabaseException as e:
            logger.error(f"Database error getting document: {e}")
            return None

        if result:
            return Document(**result)
        return None

    def get_by_content_hash(self, content_hash: str) -> Optional[Document]:
        """Get document by content hash."""
        # Note: content_hash is not stored in DB yet, this is a placeholder
        # TODO: Add content_hash column to document table
        return None

    def get_by_workspace(
        self, workspace_id: int, limit: int = 50, offset: int = 0
    ) -> list[Document]:
        """Get document for a workspace."""
        query = """
            SELECT
                id, workspace_id, filename, original_filename,
                size_bytes as file_size, mime_type, chunk_count, status,
                error_message, file_hash as content_hash, storage_path as file_path,
                created_at, updated_at
            FROM documents WHERE workspace_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        try:
            results = self.db.fetch_all(query, (workspace_id, limit, offset))
        except DatabaseException as e:
            logger.error(f"Database error getting documents by workspace: {e}")
            return []

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
            SET filename = %s, size_bytes = %s, mime_type = %s, chunk_count = %s, status = %s
            WHERE id = %s
        """
        try:
            self.db.execute(
                query,
                (
                    document.filename,
                    document.file_size,
                    document.mime_type,
                    document.chunk_count,
                    document.status,
                    document_id,
                ),
            )
        except DatabaseException as e:
            logger.error(f"Database error updating document: {e}")
            return None

        return document

    def update_status(
        self,
        document_id: int,
        status: str,
        error: Optional[str]= None,
        chunk_count: Optional[int]= None,
    ) -> bool:
        """Update document processing status."""
        query = """
            UPDATE documents
            SET status = %s, chunk_count = COALESCE(%s, chunk_count)
            WHERE id = %s
        """
        affected_rows = self.db.execute(query, (status, chunk_count, document_id))
        return affected_rows > 0

    def count_by_workspace(self, workspace_id: int, status_filter: Optional[str]= None) -> int:
        """Count document in workspace with optional status filter."""
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
        try:
            affected_rows = self.db.execute(query, (document_id,))
        except DatabaseException as e:
            logger.error(f"Database error deleting document: {e}")
            return False

        return affected_rows > 0
