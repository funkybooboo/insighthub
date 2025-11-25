"""SQL implementation of entity repository using PostgresSqlDatabase."""

from typing import Any, Dict, List, Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase
from shared.models.entity import Entity

from .entity_repository import EntityRepository

# Columns that match the Entity model
ENTITY_COLUMNS = """
    id, workspace_id, document_id, chunk_id, entity_type, entity_text,
    confidence_score, metadata, created_at, updated_at
"""


class SqlEntityRepository(EntityRepository):
    """Repository for Entity operations using direct SQL queries."""

    def __init__(self, db: PostgresSqlDatabase) -> None:
        """
        Initialize repository with PostgresSqlDatabase.

        Args:
            db: PostgresSqlDatabase instance
        """
        self._db = db

    def create(
        self,
        workspace_id: int,
        document_id: int,
        chunk_id: str,
        entity_type: str,
        entity_text: str,
        confidence_score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Entity:
        """Create a new entity."""
        query = """
        INSERT INTO entities
            (workspace_id, document_id, chunk_id, entity_type, entity_text, confidence_score, metadata)
        VALUES
            (%(workspace_id)s, %(document_id)s, %(chunk_id)s, %(entity_type)s, %(entity_text)s, %(confidence_score)s, %(metadata)s)
        RETURNING id, workspace_id, document_id, chunk_id, entity_type, entity_text, confidence_score, metadata, created_at, updated_at;
        """
        params = {
            "workspace_id": workspace_id,
            "document_id": document_id,
            "chunk_id": chunk_id,
            "entity_type": entity_type,
            "entity_text": entity_text,
            "confidence_score": confidence_score,
            "metadata": metadata or {},
        }

        row = self._db.fetch_one(query, params)
        if row:
            return Entity(
                id=row["id"],
                workspace_id=row["workspace_id"],
                document_id=row["document_id"],
                chunk_id=row["chunk_id"],
                entity_type=row["entity_type"],
                entity_text=row["entity_text"],
                confidence_score=row["confidence_score"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        raise RuntimeError("Failed to create entity")

    def get_by_id(self, entity_id: int) -> Optional[Entity]:
        """Get entity by ID."""
        query = f"SELECT {ENTITY_COLUMNS} FROM entities WHERE id = %(entity_id)s"
        row = self._db.fetch_one(query, {"entity_id": entity_id})
        if row:
            return Entity(
                id=row["id"],
                workspace_id=row["workspace_id"],
                document_id=row["document_id"],
                chunk_id=row["chunk_id"],
                entity_type=row["entity_type"],
                entity_text=row["entity_text"],
                confidence_score=row["confidence_score"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        return None

    def get_by_workspace(self, workspace_id: int, skip: int = 0, limit: int = 50) -> List[Entity]:
        """Get entities by workspace ID with pagination."""
        query = f"""
        SELECT {ENTITY_COLUMNS} FROM entities
        WHERE workspace_id = %(workspace_id)s
        ORDER BY created_at DESC
        OFFSET %(skip)s LIMIT %(limit)s
        """
        rows = self._db.fetch_all(query, {"workspace_id": workspace_id, "skip": skip, "limit": limit})
        return [
            Entity(
                id=row["id"],
                workspace_id=row["workspace_id"],
                document_id=row["document_id"],
                chunk_id=row["chunk_id"],
                entity_type=row["entity_type"],
                entity_text=row["entity_text"],
                confidence_score=row["confidence_score"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def get_by_document(self, document_id: int, skip: int = 0, limit: int = 50) -> List[Entity]:
        """Get entities by document ID with pagination."""
        query = f"""
        SELECT {ENTITY_COLUMNS} FROM entities
        WHERE document_id = %(document_id)s
        ORDER BY created_at DESC
        OFFSET %(skip)s LIMIT %(limit)s
        """
        rows = self._db.fetch_all(query, {"document_id": document_id, "skip": skip, "limit": limit})
        return [
            Entity(
                id=row["id"],
                workspace_id=row["workspace_id"],
                document_id=row["document_id"],
                chunk_id=row["chunk_id"],
                entity_type=row["entity_type"],
                entity_text=row["entity_text"],
                confidence_score=row["confidence_score"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def get_by_chunk(self, chunk_id: str) -> List[Entity]:
        """Get entities by chunk ID."""
        query = f"SELECT {ENTITY_COLUMNS} FROM entities WHERE chunk_id = %(chunk_id)s"
        rows = self._db.fetch_all(query, {"chunk_id": chunk_id})
        return [
            Entity(
                id=row["id"],
                workspace_id=row["workspace_id"],
                document_id=row["document_id"],
                chunk_id=row["chunk_id"],
                entity_type=row["entity_type"],
                entity_text=row["entity_text"],
                confidence_score=row["confidence_score"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def get_by_type(self, workspace_id: int, entity_type: str, skip: int = 0, limit: int = 50) -> List[Entity]:
        """Get entities by type within a workspace."""
        query = f"""
        SELECT {ENTITY_COLUMNS} FROM entities
        WHERE workspace_id = %(workspace_id)s AND entity_type = %(entity_type)s
        ORDER BY created_at DESC
        OFFSET %(skip)s LIMIT %(limit)s
        """
        rows = self._db.fetch_all(query, {"workspace_id": workspace_id, "entity_type": entity_type, "skip": skip, "limit": limit})
        return [
            Entity(
                id=row["id"],
                workspace_id=row["workspace_id"],
                document_id=row["document_id"],
                chunk_id=row["chunk_id"],
                entity_type=row["entity_type"],
                entity_text=row["entity_text"],
                confidence_score=row["confidence_score"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def update(self, entity_id: int, **kwargs: Any) -> Optional[Entity]:
        """Update entity fields."""
        if not kwargs:
            return self.get_by_id(entity_id)

        # Build SET clause dynamically
        set_parts = []
        params = {"entity_id": entity_id}
        for key, value in kwargs.items():
            if key in ["entity_type", "entity_text", "confidence_score", "metadata"]:
                set_parts.append(f"{key} = %({key})s")
                params[key] = value

        if not set_parts:
            return self.get_by_id(entity_id)

        set_clause = ", ".join(set_parts)
        query = f"""
        UPDATE entities SET {set_clause}, updated_at = NOW()
        WHERE id = %(entity_id)s
        RETURNING {ENTITY_COLUMNS}
        """

        row = self._db.fetch_one(query, params)
        if row:
            return Entity(
                id=row["id"],
                workspace_id=row["workspace_id"],
                document_id=row["document_id"],
                chunk_id=row["chunk_id"],
                entity_type=row["entity_type"],
                entity_text=row["entity_text"],
                confidence_score=row["confidence_score"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        return None

    def delete(self, entity_id: int) -> bool:
        """Delete entity by ID."""
        query = "DELETE FROM entities WHERE id = %(entity_id)s"
        result = self._db.execute(query, {"entity_id": entity_id})
        return result > 0

    def count_by_workspace(self, workspace_id: int) -> int:
        """Count entities in a workspace."""
        query = "SELECT COUNT(*) as count FROM entities WHERE workspace_id = %(workspace_id)s"
        row = self._db.fetch_one(query, {"workspace_id": workspace_id})
        return row["count"] if row else 0

    def delete_by_workspace(self, workspace_id: int) -> int:
        """Delete all entities in a workspace."""
        query = "DELETE FROM entities WHERE workspace_id = %(workspace_id)s"
        return self._db.execute(query, {"workspace_id": workspace_id})