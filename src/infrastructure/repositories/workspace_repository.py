"""PostgreSQL implementation of WorkspaceRepository."""

from datetime import UTC, datetime
from typing import Optional

from src.infrastructure.sql_database import SqlDatabase
from src.infrastructure.models import GraphRagConfig, RagConfig, VectorRagConfig, Workspace




class WorkspaceRepository:
    """SQL implementation of workspace repository."""

    def __init__(self, db: SqlDatabase):
        self.db = db

    def create(
        self,
        name: str,
        description: str | None = None,
        rag_type: str = "vector",
        rag_config: dict | None = None,
        status: str = "ready",
    ) -> Workspace:
        """Create a new workspace (single-user system)."""
        query = """
            INSERT INTO workspaces (name, description, rag_type, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.db.fetch_one(
            query,
            (
                name,
                description,
                rag_type,
                status,
                datetime.now(UTC),
                datetime.now(UTC),
            ),
        )

        if result:
            workspace = Workspace(
                id=result["id"],
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
            SELECT id, name, description, rag_type, status, created_at, updated_at
            FROM workspaces WHERE id = %s
        """
        result = self.db.fetch_one(query, (workspace_id,))
        if result:
            return Workspace(**result)
        return None

    def get_all(self) -> list[Workspace]:
        """Get all workspace (single-user system)."""
        query = """
            SELECT id, name, description, rag_type, status, created_at, updated_at
            FROM workspaces
            ORDER BY created_at DESC
        """
        results = self.db.fetch_all(query, ())
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

        workspace.updated_at = datetime.now(UTC)

        # Update in database
        query = """
            UPDATE workspaces
            SET name = %s, description = %s, rag_type = %s, status = %s, updated_at = %s
            WHERE id = %s
        """
        self.db.execute(
            query,
            (
                workspace.name,
                workspace.description,
                workspace.rag_type,
                workspace.status,
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

    def create_vector_rag_config(self, config: VectorRagConfig) -> VectorRagConfig:
        """Create vector RAG config for workspace."""
        # TODO: Implement when vector_rag_configs table is created
        return config

    def update_vector_rag_config(self, workspace_id: int, **kwargs) -> Optional[VectorRagConfig]:
        """Update vector RAG config for workspace."""
        # TODO: Implement when vector_rag_configs table is created
        return None

    def create_graph_rag_config(self, config: GraphRagConfig) -> GraphRagConfig:
        """Create graph RAG config for workspace."""
        # TODO: Implement when graph_rag_configs table is created
        return config

    def update_graph_rag_config(self, workspace_id: int, **kwargs) -> Optional[GraphRagConfig]:
        """Update graph RAG config for workspace."""
        # TODO: Implement when graph_rag_configs table is created
        return None
