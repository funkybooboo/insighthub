"""SQL implementation of document repository using PostgresSqlDatabase."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase
from shared.models.document import Document
from .document_repository import DocumentRepository


class SqlDocumentRepository(DocumentRepository):
    """Repository for Document operations using direct SQL queries."""

    def __init__(self, db: PostgresSqlDatabase) -> None:
        """
        Initialize repository with PostgresSqlDatabase.

        Args:
            db: PostgresSqlDatabase instance
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
        workspace_id: int | None = None,
        chunk_count: int | None = None,
        rag_collection: str | None = None,
    ) -> Document:
        """Create a new document."""
        query = """
        INSERT INTO documents
            (user_id, workspace_id, filename, file_path, file_size, mime_type, content_hash, chunk_count, rag_collection, processing_status, processing_error)
        VALUES
            (%(user_id)s, %(workspace_id)s, %(filename)s, %(file_path)s, %(file_size)s, %(mime_type)s, %(content_hash)s, %(chunk_count)s, %(rag_collection)s, %(processing_status)s, %(processing_error)s)
        RETURNING *;
        """
        params = {
            "user_id": user_id,
            "workspace_id": workspace_id,
            "filename": filename,
            "file_path": file_path,
            "file_size": file_size,
            "mime_type": mime_type,
            "content_hash": content_hash,
            "chunk_count": chunk_count,
            "rag_collection": rag_collection,
            "processing_status": "pending",
            "processing_error": None,
        }
        row = self._db.fetchone(query, params)
        if row is None:
            raise ValueError("Failed to create document")
        return Document(**row)

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        query = "SELECT * FROM documents WHERE id = %(id)s;"
        row = self._db.fetchone(query, {"id": document_id})
        if row is None:
            return None
        return Document(**row)

    def get_by_user(self, user_id: int, skip: int, limit: int) -> list[Document]:
        """Get all documents for a user with pagination."""
        query = """
        SELECT * FROM documents
        WHERE user_id = %(user_id)s
        OFFSET %(skip)s
        LIMIT %(limit)s;
        """
        rows = self._db.fetchall(query, {"user_id": user_id, "skip": skip, "limit": limit})
        return [Document(**row) for row in rows]

    def get_by_content_hash(self, content_hash: str) -> Optional[Document]:
        """Get document by content hash."""
        query = "SELECT * FROM documents WHERE content_hash = %(content_hash)s;"
        row = self._db.fetchone(query, {"content_hash": content_hash})
        if row is None:
            return None
        return Document(**row)

    def update(self, document_id: int, **kwargs: str | int | None) -> Optional[Document]:
        """Update document fields."""
        if not kwargs:
            return self.get_by_id(document_id)

        set_clause = ", ".join(f"{key} = %({key})s" for key in kwargs.keys())
        kwargs["id"] = document_id
        query = f"""
        UPDATE documents
        SET {set_clause}, updated_at = NOW()
        WHERE id = %(id)s
        RETURNING *;
        """
        row = self._db.fetchone(query, kwargs)
        if row is None:
            return None
        return Document(**row)

    def delete(self, document_id: int) -> bool:
        """Delete document by ID."""
        query = "DELETE FROM documents WHERE id = %(id)s;"
        self._db.execute(query, {"id": document_id})
        return True

    def get_by_workspace(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 50,
        status_filter: str | None = None,
    ) -> list[Document]:
        """Get documents by workspace ID with pagination and optional status filter."""
        base_query = """
        SELECT * FROM documents
        WHERE workspace_id = %(workspace_id)s
        """
        params = {"workspace_id": workspace_id}

        if status_filter:
            base_query += " AND processing_status = %(status_filter)s"
            params["status_filter"] = status_filter

        base_query += " ORDER BY created_at DESC LIMIT %(limit)s OFFSET %(skip)s"
        params["limit"] = limit
        params["skip"] = skip

        rows = self._db.fetchall(base_query, params)
        return [Document(**row) for row in rows]

    def count_by_workspace(self, workspace_id: int, status_filter: str | None = None) -> int:
        """Count documents in a workspace with optional status filter."""
        base_query = "SELECT COUNT(*) as count FROM documents WHERE workspace_id = %(workspace_id)s"
        params = {"workspace_id": workspace_id}

        if status_filter:
            base_query += " AND processing_status = %(status_filter)s"
            params["status_filter"] = status_filter

        row = self._db.fetchone(base_query, params)
        return row["count"] if row else 0
