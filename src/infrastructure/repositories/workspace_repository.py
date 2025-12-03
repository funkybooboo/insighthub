"""PostgreSQL implementation of WorkspaceRepository."""

from datetime import UTC, datetime
from typing import Optional

from returns.result import Failure, Result, Success

from src.infrastructure.logger import create_logger
from src.infrastructure.models import GraphRagConfig, RagConfig, VectorRagConfig, Workspace
from src.infrastructure.sql_database import DatabaseException, SqlDatabase
from src.infrastructure.types import DatabaseError

logger = create_logger(__name__)


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
    ) -> Result[Workspace, DatabaseError]:
        """Create a new workspace (single-user system)."""
        query = """
            INSERT INTO workspaces (name, description, rag_type, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        try:
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
        except DatabaseException as e:
            logger.error(f"Database error creating workspace: {e}")
            return Failure(DatabaseError(e.message, operation="create_workspace"))

        if not result:
            return Failure(DatabaseError("Insert returned no result", operation="create_workspace"))

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

        return Success(workspace)

    def get_by_id(self, workspace_id: int) -> Optional[Workspace]:
        """Get workspace by ID."""
        query = """
            SELECT id, name, description, rag_type, status, created_at, updated_at
            FROM workspaces WHERE id = %s
        """
        try:
            result = self.db.fetch_one(query, (workspace_id,))
        except DatabaseException as e:
            logger.error(f"Database error getting workspace: {e}")
            return None

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
        try:
            results = self.db.fetch_all(query, ())
        except DatabaseException as e:
            logger.error(f"Database error getting all workspaces: {e}")
            return []

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
        try:
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
        except DatabaseException as e:
            logger.error(f"Database error updating workspace: {e}")
            return None

        return workspace

    def delete(self, workspace_id: int) -> bool:
        """Delete workspace by ID."""
        query = "DELETE FROM workspaces WHERE id = %s"
        try:
            affected_rows = self.db.execute(query, (workspace_id,))
        except DatabaseException as e:
            logger.error(f"Database error deleting workspace: {e}")
            return False

        return affected_rows > 0

    def get_vector_rag_config(self, workspace_id: int) -> Optional[VectorRagConfig]:
        """Get vector RAG config for workspace."""
        query = """
            SELECT workspace_id, chunk_size, chunk_overlap, chunker_type as chunking_algorithm,
                   embedding_model as embedding_algorithm, top_k,
                   COALESCE(score_threshold, 0) as score_threshold,
                   created_at, updated_at
            FROM vector_rag_configs
            WHERE workspace_id = %s
        """
        try:
            result = self.db.fetch_one(query, (workspace_id,))
        except DatabaseException as e:
            logger.error(f"Database error getting vector RAG config: {e}")
            return None

        if result:
            return VectorRagConfig(
                workspace_id=result["workspace_id"],
                chunking_algorithm=result["chunking_algorithm"],
                chunk_size=result["chunk_size"],
                chunk_overlap=result["chunk_overlap"],
                embedding_algorithm=result["embedding_algorithm"],
                top_k=result["top_k"],
                rerank_algorithm="none",  # Not stored in DB yet
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        return None

    def get_graph_rag_config(self, workspace_id: int) -> Optional[GraphRagConfig]:
        """Get graph RAG config for workspace."""
        query = """
            SELECT workspace_id,
                   entity_extraction_model as entity_extraction_algorithm,
                   relationship_extraction_model as relationship_extraction_algorithm,
                   clustering_algorithm,
                   created_at, updated_at
            FROM graph_rag_configs
            WHERE workspace_id = %s
        """
        try:
            result = self.db.fetch_one(query, (workspace_id,))
        except DatabaseException as e:
            logger.error(f"Database error getting graph RAG config: {e}")
            return None

        if result:
            return GraphRagConfig(
                workspace_id=result["workspace_id"],
                entity_extraction_algorithm=result["entity_extraction_algorithm"],
                relationship_extraction_algorithm=result["relationship_extraction_algorithm"],
                clustering_algorithm=result["clustering_algorithm"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
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
