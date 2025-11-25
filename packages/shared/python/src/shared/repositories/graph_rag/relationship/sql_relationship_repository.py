"""SQL implementation of relationship repository using PostgresSqlDatabase."""

from typing import Any, Dict, List, Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase
from shared.models.relationship import Relationship

from .relationship_repository import RelationshipRepository

# Columns that match the Relationship model
RELATIONSHIP_COLUMNS = """
    id, workspace_id, source_entity_id, target_entity_id, relationship_type,
    confidence_score, metadata, created_at, updated_at
"""


class SqlRelationshipRepository(RelationshipRepository):
    """Repository for Relationship operations using direct SQL queries."""

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
        source_entity_id: int,
        target_entity_id: int,
        relationship_type: str,
        confidence_score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Relationship:
        """Create a new relationship."""
        query = """
        INSERT INTO relationships
            (workspace_id, source_entity_id, target_entity_id, relationship_type, confidence_score, metadata)
        VALUES
            (%(workspace_id)s, %(source_entity_id)s, %(target_entity_id)s, %(relationship_type)s, %(confidence_score)s, %(metadata)s)
        RETURNING id, workspace_id, source_entity_id, target_entity_id, relationship_type, confidence_score, metadata, created_at, updated_at;
        """
        params = {
            "workspace_id": workspace_id,
            "source_entity_id": source_entity_id,
            "target_entity_id": target_entity_id,
            "relationship_type": relationship_type,
            "confidence_score": confidence_score,
            "metadata": metadata or {},
        }

        row = self._db.fetch_one(query, params)
        if row:
            return Relationship(
                id=row["id"],
                workspace_id=row["workspace_id"],
                source_entity_id=row["source_entity_id"],
                target_entity_id=row["target_entity_id"],
                relationship_type=row["relationship_type"],
                confidence_score=row["confidence_score"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        raise RuntimeError("Failed to create relationship")

    def get_by_id(self, relationship_id: int) -> Optional[Relationship]:
        """Get relationship by ID."""
        query = f"SELECT {RELATIONSHIP_COLUMNS} FROM relationships WHERE id = %(relationship_id)s"
        row = self._db.fetch_one(query, {"relationship_id": relationship_id})
        if row:
            return Relationship(
                id=row["id"],
                workspace_id=row["workspace_id"],
                source_entity_id=row["source_entity_id"],
                target_entity_id=row["target_entity_id"],
                relationship_type=row["relationship_type"],
                confidence_score=row["confidence_score"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        return None

    def get_by_workspace(self, workspace_id: int, skip: int = 0, limit: int = 50) -> List[Relationship]:
        """Get relationships by workspace ID with pagination."""
        query = f"""
        SELECT {RELATIONSHIP_COLUMNS} FROM relationships
        WHERE workspace_id = %(workspace_id)s
        ORDER BY created_at DESC
        OFFSET %(skip)s LIMIT %(limit)s
        """
        rows = self._db.fetch_all(query, {"workspace_id": workspace_id, "skip": skip, "limit": limit})
        return [
            Relationship(
                id=row["id"],
                workspace_id=row["workspace_id"],
                source_entity_id=row["source_entity_id"],
                target_entity_id=row["target_entity_id"],
                relationship_type=row["relationship_type"],
                confidence_score=row["confidence_score"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def get_by_entity(self, entity_id: int, skip: int = 0, limit: int = 50) -> List[Relationship]:
        """Get relationships involving a specific entity."""
        query = f"""
        SELECT {RELATIONSHIP_COLUMNS} FROM relationships
        WHERE source_entity_id = %(entity_id)s OR target_entity_id = %(entity_id)s
        ORDER BY created_at DESC
        OFFSET %(skip)s LIMIT %(limit)s
        """
        rows = self._db.fetch_all(query, {"entity_id": entity_id, "skip": skip, "limit": limit})
        return [
            Relationship(
                id=row["id"],
                workspace_id=row["workspace_id"],
                source_entity_id=row["source_entity_id"],
                target_entity_id=row["target_entity_id"],
                relationship_type=row["relationship_type"],
                confidence_score=row["confidence_score"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def get_by_type(self, workspace_id: int, relationship_type: str, skip: int = 0, limit: int = 50) -> List[Relationship]:
        """Get relationships by type within a workspace."""
        query = f"""
        SELECT {RELATIONSHIP_COLUMNS} FROM relationships
        WHERE workspace_id = %(workspace_id)s AND relationship_type = %(relationship_type)s
        ORDER BY created_at DESC
        OFFSET %(skip)s LIMIT %(limit)s
        """
        rows = self._db.fetch_all(query, {"workspace_id": workspace_id, "relationship_type": relationship_type, "skip": skip, "limit": limit})
        return [
            Relationship(
                id=row["id"],
                workspace_id=row["workspace_id"],
                source_entity_id=row["source_entity_id"],
                target_entity_id=row["target_entity_id"],
                relationship_type=row["relationship_type"],
                confidence_score=row["confidence_score"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def update(self, relationship_id: int, **kwargs: Any) -> Optional[Relationship]:
        """Update relationship fields."""
        if not kwargs:
            return self.get_by_id(relationship_id)

        # Build SET clause dynamically
        set_parts = []
        params = {"relationship_id": relationship_id}
        for key, value in kwargs.items():
            if key in ["relationship_type", "confidence_score", "metadata"]:
                set_parts.append(f"{key} = %({key})s")
                params[key] = value

        if not set_parts:
            return self.get_by_id(relationship_id)

        set_clause = ", ".join(set_parts)
        query = f"""
        UPDATE relationships SET {set_clause}, updated_at = NOW()
        WHERE id = %(relationship_id)s
        RETURNING {RELATIONSHIP_COLUMNS}
        """

        row = self._db.fetch_one(query, params)
        if row:
            return Relationship(
                id=row["id"],
                workspace_id=row["workspace_id"],
                source_entity_id=row["source_entity_id"],
                target_entity_id=row["target_entity_id"],
                relationship_type=row["relationship_type"],
                confidence_score=row["confidence_score"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        return None

    def delete(self, relationship_id: int) -> bool:
        """Delete relationship by ID."""
        query = "DELETE FROM relationships WHERE id = %(relationship_id)s"
        result = self._db.execute(query, {"relationship_id": relationship_id})
        return result > 0

    def count_by_workspace(self, workspace_id: int) -> int:
        """Count relationships in a workspace."""
        query = "SELECT COUNT(*) as count FROM relationships WHERE workspace_id = %(workspace_id)s"
        row = self._db.fetch_one(query, {"workspace_id": workspace_id})
        return row["count"] if row else 0

    def delete_by_workspace(self, workspace_id: int) -> int:
        """Delete all relationships in a workspace."""
        query = "DELETE FROM relationships WHERE workspace_id = %(workspace_id)s"
        return self._db.execute(query, {"workspace_id": workspace_id})