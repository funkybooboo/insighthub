"""SQL implementation of document repository using SqlDatabase."""

from typing import List
from shared.models.document import Document
from shared.types.option import Option, Some, Nothing

from .document_repository import DocumentRepository
from shared.database.sql.sql_database import SqlDatabase


class SqlDocumentRepository(DocumentRepository):
    """Repository for Document operations using direct SQL queries."""

    def __init__(self, db: SqlDatabase) -> None:
        """
        Initialize repository with SqlDatabase.

        Args:
            db: SqlDatabase instance
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
        query = """
        INSERT INTO document 
            (user_id, filename, file_path, file_size, mime_type, content_hash, chunk_count, rag_collection, created_at, updated_at)
        VALUES 
            (%(user_id)s, %(filename)s, %(file_path)s, %(file_size)s, %(mime_type)s, %(content_hash)s, %(chunk_count)s, %(rag_collection)s, NOW(), NOW())
        RETURNING id, user_id, filename, file_path, file_size, mime_type, content_hash, chunk_count, rag_collection, created_at, updated_at;
        """
        params = {
            "user_id": user_id,
            "filename": filename,
            "file_path": file_path,
            "file_size": file_size,
            "mime_type": mime_type,
            "content_hash": content_hash,
            "chunk_count": chunk_count,
            "rag_collection": rag_collection,
        }
        row = self._db.fetchone(query, params)
        return Document(**row)

    def get_by_id(self, document_id: int) -> Option[Document]:
        """Get document by ID."""
        query = "SELECT * FROM document WHERE id = %(id)s;"
        row = self._db.fetchone(query, {"id": document_id})
        if row is None:
            return Nothing()
        return Some(Document(**row))

    def get_by_user(self, user_id: int, skip: int, limit: int) -> List[Document]:
        """Get all documents for a user with pagination."""
        query = """
        SELECT * FROM document
        WHERE user_id = %(user_id)s
        OFFSET %(skip)s
        LIMIT %(limit)s;
        """
        rows = self._db.fetchall(query, {"user_id": user_id, "skip": skip, "limit": limit})
        return [Document(**row) for row in rows]

    def get_by_content_hash(self, content_hash: str) -> Option[Document]:
        """Get document by content hash."""
        query = "SELECT * FROM document WHERE content_hash = %(content_hash)s;"
        row = self._db.fetchone(query, {"content_hash": content_hash})
        if row is None:
            return Nothing()
        return Some(Document(**row))

    def update(self, document_id: int, **kwargs: str | int) -> Option[Document]:
        """Update document fields."""
        if not kwargs:
            return self.get_by_id(document_id)

        set_clause = ", ".join(f"{key} = %({key})s" for key in kwargs.keys())
        kwargs["id"] = document_id
        query = f"""
        UPDATE document
        SET {set_clause}, updated_at = NOW()
        WHERE id = %(id)s
        RETURNING id, user_id, filename, file_path, file_size, mime_type, content_hash, chunk_count, rag_collection, created_at, updated_at;
        """
        row = self._db.fetchone(query, kwargs)
        if row is None:
            return Nothing()
        return Some(Document(**row))

    def delete(self, document_id: int) -> bool:
        """Delete document by ID."""
        query = "DELETE FROM document WHERE id = %(id)s;"
        self._db.execute(query, {"id": document_id})
        return True
