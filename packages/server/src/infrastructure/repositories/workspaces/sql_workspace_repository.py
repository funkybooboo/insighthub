"""SQL implementation of WorkspaceRepository."""

from datetime import datetime
from typing import Optional

from src.infrastructure.database import SqlDatabase
from src.infrastructure.models import GraphRagConfig, RagConfig, VectorRagConfig, Workspace

from .workspace_repository import WorkspaceRepository


class SqlWorkspaceRepository(WorkspaceRepository):
    """SQL implementation of workspaces repository."""

    def __init__(self, db: SqlDatabase):
        self.db = db

    def create(
        self,
        user_id: int,
        name: str,
        description: str | None = None,
        rag_type: str = "vector",
        rag_config: dict | None = None,
        status: str = "ready",
    ) -> Workspace:
        """Create a new workspace."""
        query = """
            INSERT INTO workspaces (user_id, name, description, rag_type, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.db.fetch_one(
            query,
            (
                user_id,
                name,
                description,
                rag_type,
                status,
                datetime.utcnow(),
                datetime.utcnow(),
            ),
        )

        if result:
            workspace = Workspace(
                id=result["id"],
                user_id=user_id,
                name=name,
                description=description,
                rag_type=rag_type,
                status=status,
            )

            # Store RAG config if provided
            if rag_config:
                if rag_type == "vector":
                    self._create_vector_rag_config(result["id"], rag_config)
                elif rag_type == "graph":
                    self._create_graph_rag_config(result["id"], rag_config)

            return workspace

        raise RuntimeError("Failed to create workspace")

    def get_by_id(self, workspace_id: int) -> Optional[Workspace]:
        """Get workspace by ID."""
        query = """
            SELECT id, user_id, name, description, rag_type, created_at, updated_at
            FROM workspaces WHERE id = %s
        """
        result = self.db.fetch_one(query, (workspace_id,))
        if result:
            return Workspace(**result)
        return None

    def get_by_user(self, user_id: int) -> list[Workspace]:
        """Get all workspaces for a user."""
        query = """
            SELECT id, user_id, name, description, rag_type, created_at, updated_at
            FROM workspaces WHERE user_id = %s
            ORDER BY created_at DESC
        """
        results = self.db.fetch_all(query, (user_id,))
        return [Workspace(**result) for result in results]

    def update(self, workspace_id: int, **kwargs) -> Optional[Workspace]:
        """Update workspace fields."""
        # Get current workspace
        workspace = self.get_by_id(workspace_id)
        if not workspace:
            return None

        # Update fields
        for key, value in kwargs.items():
            if hasattr(workspace, key):
                setattr(workspace, key, value)

        workspace.updated_at = datetime.utcnow()

        # Update in database
        query = """
            UPDATE workspaces
            SET name = %s, description = %s, rag_type = %s, updated_at = %s
            WHERE id = %s
        """
        self.db.execute(
            query,
            (
                workspace.name,
                workspace.description,
                workspace.rag_type,
                workspace.updated_at,
                workspace_id,
            ),
        )

        return workspace

    def delete(self, workspace_id: int) -> bool:
        """Delete workspace by ID."""
        query = "DELETE FROM workspaces WHERE id = %s"
        affected_rows = self.db.execute(query, (workspace_id,))
        return affected_rows > 0

    def get_vector_rag_config(self, workspace_id: int) -> Optional[VectorRagConfig]:
        """Get vector RAG config for workspace."""
        # For now, return None as the table might not exist yet
        # TODO: Implement when vector_rag_configs table is created
        return None

    def get_graph_rag_config(self, workspace_id: int) -> Optional[GraphRagConfig]:
        """Get graph RAG config for workspace."""
        # For now, return None as the table might not exist yet
        # TODO: Implement when graph_rag_configs table is created
        return None

    def get_rag_config(self, workspace_id: int) -> Optional[RagConfig]:
        """Get generic RAG config for workspace."""
        # For now, return None as the table might not exist yet
        # TODO: Implement when rag_configs table is created
        return None

    def _create_vector_rag_config(self, workspace_id: int, config: dict) -> None:
        """Create vector RAG config for workspace."""
        # TODO: Implement when vector_rag_configs table is created
        pass

    def _create_graph_rag_config(self, workspace_id: int, config: dict) -> None:
        """Create graph RAG config for workspace."""
        # TODO: Implement when graph_rag_configs table is created
        pass