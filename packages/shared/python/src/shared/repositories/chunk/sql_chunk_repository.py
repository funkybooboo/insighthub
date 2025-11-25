"""SQL implementation of chunk repository using PostgresSqlDatabase."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase
from shared.models.chunk import Chunk

from .chunk_repository import ChunkRepository

# Columns that match the Chunk model
CHUNK_COLUMNS = """
    id, document_id, chunk_index, chunk_text, embedding, created_at, updated_at
"""


class SqlChunkRepository(ChunkRepository):
    """Repository for Chunk operations using direct SQL queries."""

    def __init__(self, db: PostgresSqlDatabase) -> None:
        """
        Initialize repository with PostgresSqlDatabase.

        Args:
            db: PostgresSqlDatabase instance
        """
        self._db = db

    def create(
        self,
        document_id: int,
        chunk_index: int,
        chunk_text: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Chunk:
        """Create a new chunk."""
        query = """
        INSERT INTO document_chunks
            (document_id, chunk_index, chunk_text, embedding)
        VALUES
            (%(document_id)s, %(chunk_index)s, %(chunk_text)s, %(embedding)s)
        RETURNING id, document_id, chunk_index, chunk_text, embedding, created_at, updated_at;
        """
        params = {
            "document_id": document_id,
            "chunk_index": chunk_index,
            "chunk_text": chunk_text,
            "embedding": embedding,
        }

        row = self._db.fetch_one(query, params)
        if row:
            return Chunk(
                id=row["id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                chunk_text=row["chunk_text"],
                embedding=row["embedding"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        raise RuntimeError("Failed to create chunk")

    def get_by_id(self, chunk_id: UUID) -> Optional[Chunk]:
        """Get chunk by ID."""
        query = f"SELECT {CHUNK_COLUMNS} FROM document_chunks WHERE id = %(chunk_id)s"
        row = self._db.fetch_one(query, {"chunk_id": str(chunk_id)})
        if row:
            return Chunk(
                id=row["id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                chunk_text=row["chunk_text"],
                embedding=row["embedding"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        return None

    def get_by_document(self, document_id: int) -> List[Chunk]:
        """Get all chunks for a document."""
        query = f"""
        SELECT {CHUNK_COLUMNS} FROM document_chunks
        WHERE document_id = %(document_id)s
        ORDER BY chunk_index ASC
        """
        rows = self._db.fetch_all(query, {"document_id": document_id})
        return [
            Chunk(
                id=row["id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                chunk_text=row["chunk_text"],
                embedding=row["embedding"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def get_by_document_and_index(self, document_id: int, chunk_index: int) -> Optional[Chunk]:
        """Get chunk by document ID and chunk index."""
        query = f"SELECT {CHUNK_COLUMNS} FROM document_chunks WHERE document_id = %(document_id)s AND chunk_index = %(chunk_index)s"
        row = self._db.fetch_one(query, {"document_id": document_id, "chunk_index": chunk_index})
        if row:
            return Chunk(
                id=row["id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                chunk_text=row["chunk_text"],
                embedding=row["embedding"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        return None

    def update_embedding(self, chunk_id: UUID, embedding: List[float]) -> Optional[Chunk]:
        """Update chunk embedding."""
        query = f"""
        UPDATE document_chunks SET embedding = %(embedding)s, updated_at = NOW()
        WHERE id = %(chunk_id)s
        RETURNING {CHUNK_COLUMNS}
        """
        row = self._db.fetch_one(query, {"chunk_id": str(chunk_id), "embedding": embedding})
        if row:
            return Chunk(
                id=row["id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                chunk_text=row["chunk_text"],
                embedding=row["embedding"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        return None

    def delete_by_document(self, document_id: int) -> int:
        """Delete all chunks for a document."""
        query = "DELETE FROM document_chunks WHERE document_id = %(document_id)s"
        return self._db.execute(query, {"document_id": document_id})