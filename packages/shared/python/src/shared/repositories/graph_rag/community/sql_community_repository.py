"""SQL implementation of community repository using PostgresSqlDatabase."""

from typing import Any, Dict, List, Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase
from shared.models.community import Community

from .community_repository import CommunityRepository

# Columns that match the Community model
COMMUNITY_COLUMNS = """
    id, workspace_id, community_id, entity_ids, algorithm_used, metadata, created_at, updated_at
"""


class SqlCommunityRepository(CommunityRepository):
    """Repository for Community operations using direct SQL queries."""

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
        community_id: str,
        entity_ids: List[int],
        algorithm_used: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Community:
        """Create a new community."""
        query = """
        INSERT INTO communities
            (workspace_id, community_id, entity_ids, algorithm_used, metadata)
        VALUES
            (%(workspace_id)s, %(community_id)s, %(entity_ids)s, %(algorithm_used)s, %(metadata)s)
        RETURNING id, workspace_id, community_id, entity_ids, algorithm_used, metadata, created_at, updated_at;
        """
        params = {
            "workspace_id": workspace_id,
            "community_id": community_id,
            "entity_ids": entity_ids,
            "algorithm_used": algorithm_used,
            "metadata": metadata or {},
        }

        row = self._db.fetch_one(query, params)
        if row:
            return Community(
                id=row["id"],
                workspace_id=row["workspace_id"],
                community_id=row["community_id"],
                entity_ids=row["entity_ids"] or [],
                algorithm_used=row["algorithm_used"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        raise RuntimeError("Failed to create community")

    def get_by_id(self, community_id: int) -> Optional[Community]:
        """Get community by ID."""
        query = f"SELECT {COMMUNITY_COLUMNS} FROM communities WHERE id = %(community_id)s"
        row = self._db.fetch_one(query, {"community_id": community_id})
        if row:
            return Community(
                id=row["id"],
                workspace_id=row["workspace_id"],
                community_id=row["community_id"],
                entity_ids=row["entity_ids"] or [],
                algorithm_used=row["algorithm_used"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        return None

    def get_by_workspace(self, workspace_id: int, skip: int = 0, limit: int = 50) -> List[Community]:
        """Get communities by workspace ID with pagination."""
        query = f"""
        SELECT {COMMUNITY_COLUMNS} FROM communities
        WHERE workspace_id = %(workspace_id)s
        ORDER BY created_at DESC
        OFFSET %(skip)s LIMIT %(limit)s
        """
        rows = self._db.fetch_all(query, {"workspace_id": workspace_id, "skip": skip, "limit": limit})
        return [
            Community(
                id=row["id"],
                workspace_id=row["workspace_id"],
                community_id=row["community_id"],
                entity_ids=row["entity_ids"] or [],
                algorithm_used=row["algorithm_used"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def get_by_community_id(self, workspace_id: int, community_id: str) -> Optional[Community]:
        """Get community by community_id within a workspace."""
        query = f"SELECT {COMMUNITY_COLUMNS} FROM communities WHERE workspace_id = %(workspace_id)s AND community_id = %(community_id)s"
        row = self._db.fetch_one(query, {"workspace_id": workspace_id, "community_id": community_id})
        if row:
            return Community(
                id=row["id"],
                workspace_id=row["workspace_id"],
                community_id=row["community_id"],
                entity_ids=row["entity_ids"] or [],
                algorithm_used=row["algorithm_used"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        return None

    def get_by_algorithm(self, workspace_id: int, algorithm_used: str, skip: int = 0, limit: int = 50) -> List[Community]:
        """Get communities by algorithm within a workspace."""
        query = f"""
        SELECT {COMMUNITY_COLUMNS} FROM communities
        WHERE workspace_id = %(workspace_id)s AND algorithm_used = %(algorithm_used)s
        ORDER BY created_at DESC
        OFFSET %(skip)s LIMIT %(limit)s
        """
        rows = self._db.fetch_all(query, {"workspace_id": workspace_id, "algorithm_used": algorithm_used, "skip": skip, "limit": limit})
        return [
            Community(
                id=row["id"],
                workspace_id=row["workspace_id"],
                community_id=row["community_id"],
                entity_ids=row["entity_ids"] or [],
                algorithm_used=row["algorithm_used"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def update(self, community_id: int, **kwargs: Any) -> Optional[Community]:
        """Update community fields."""
        if not kwargs:
            return self.get_by_id(community_id)

        # Build SET clause dynamically
        set_parts = []
        params = {"community_id": community_id}
        for key, value in kwargs.items():
            if key in ["community_id", "entity_ids", "algorithm_used", "metadata"]:
                set_parts.append(f"{key} = %({key})s")
                params[key] = value

        if not set_parts:
            return self.get_by_id(community_id)

        set_clause = ", ".join(set_parts)
        query = f"""
        UPDATE communities SET {set_clause}, updated_at = NOW()
        WHERE id = %(community_id)s
        RETURNING {COMMUNITY_COLUMNS}
        """

        row = self._db.fetch_one(query, params)
        if row:
            return Community(
                id=row["id"],
                workspace_id=row["workspace_id"],
                community_id=row["community_id"],
                entity_ids=row["entity_ids"] or [],
                algorithm_used=row["algorithm_used"],
                metadata=row["metadata"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        return None

    def delete(self, community_id: int) -> bool:
        """Delete community by ID."""
        query = "DELETE FROM communities WHERE id = %(community_id)s"
        result = self._db.execute(query, {"community_id": community_id})
        return result > 0

    def count_by_workspace(self, workspace_id: int) -> int:
        """Count communities in a workspace."""
        query = "SELECT COUNT(*) as count FROM communities WHERE workspace_id = %(workspace_id)s"
        row = self._db.fetch_one(query, {"workspace_id": workspace_id})
        return row["count"] if row else 0

    def delete_by_workspace(self, workspace_id: int) -> int:
        """Delete all communities in a workspace."""
        query = "DELETE FROM communities WHERE workspace_id = %(workspace_id)s"
        return self._db.execute(query, {"workspace_id": workspace_id})