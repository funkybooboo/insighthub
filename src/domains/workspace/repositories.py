"""PostgreSQL implementation of WorkspaceRepository."""

from datetime import UTC, datetime
from typing import Optional

from returns.result import Failure, Result, Success

from src.domains.workspace.models import GraphRagConfig, VectorRagConfig, Workspace
from src.infrastructure.logger import create_logger
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
        description: Optional[str] = None,
        rag_type: str = "vector",
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
        workspace = self.get_by_id(workspace_id)
        if not workspace:
            return None

        for key, value in kwargs.items():
            if hasattr(workspace, key):
                setattr(workspace, key, value)

        workspace.updated_at = datetime.now(UTC)

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
            SELECT workspace_id, chunk_size, chunk_overlap, chunking_algorithm,
                   embedding_algorithm, top_k, embedding_model_vector_size,
                   distance_metric, rerank_algorithm,
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
                embedding_model_vector_size=result["embedding_model_vector_size"],
                distance_metric=result["distance_metric"],
                top_k=result["top_k"],
                rerank_algorithm=result["rerank_algorithm"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        return None

    def get_graph_rag_config(self, workspace_id: int) -> Optional[GraphRagConfig]:
        """Get graph RAG config for workspace."""
        query = """
            SELECT workspace_id,
                   entity_extraction_algorithm,
                   relationship_extraction_algorithm,
                   clustering_algorithm,
                   entity_types,
                   relationship_types,
                   max_traversal_depth,
                   top_k_entities,
                   top_k_communities,
                   include_entity_neighborhoods,
                   community_min_size,
                   clustering_resolution,
                   clustering_max_level,
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
                entity_types=result["entity_types"],
                relationship_types=result["relationship_types"],
                max_traversal_depth=result["max_traversal_depth"],
                top_k_entities=result["top_k_entities"],
                top_k_communities=result["top_k_communities"],
                include_entity_neighborhoods=result["include_entity_neighborhoods"],
                community_min_size=result["community_min_size"],
                clustering_resolution=result["clustering_resolution"],
                clustering_max_level=result["clustering_max_level"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        return None

    def create_vector_rag_config(
        self, config: VectorRagConfig
    ) -> Result[VectorRagConfig, DatabaseError]:
        """Create vector RAG config for a workspace."""
        query = """
            INSERT INTO vector_rag_configs (
                workspace_id, embedding_model_vector_size, distance_metric,
                embedding_algorithm, chunking_algorithm, rerank_algorithm,
                chunk_size, chunk_overlap, top_k, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now(UTC)
        try:
            self.db.execute(
                query,
                (
                    config.workspace_id,
                    config.embedding_model_vector_size,
                    config.distance_metric,
                    config.embedding_algorithm,
                    config.chunking_algorithm,
                    config.rerank_algorithm,
                    config.chunk_size,
                    config.chunk_overlap,
                    config.top_k,
                    now,
                    now,
                ),
            )
            config.created_at = now
            config.updated_at = now
            return Success(config)
        except DatabaseException as e:
            logger.error(f"Database error creating vector RAG config: {e}")
            return Failure(DatabaseError(e.message, "create_vector_rag_config"))

    def create_graph_rag_config(
        self, config: GraphRagConfig
    ) -> Result[GraphRagConfig, DatabaseError]:
        """Create graph RAG config for a workspace."""
        query = """
            INSERT INTO graph_rag_configs (
                workspace_id, entity_extraction_algorithm, relationship_extraction_algorithm,
                clustering_algorithm, entity_types, relationship_types,
                max_traversal_depth, top_k_entities, top_k_communities,
                include_entity_neighborhoods, community_min_size,
                clustering_resolution, clustering_max_level, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        import json

        now = datetime.now(UTC)
        try:
            self.db.execute(
                query,
                (
                    config.workspace_id,
                    config.entity_extraction_algorithm,
                    config.relationship_extraction_algorithm,
                    config.clustering_algorithm,
                    json.dumps(config.entity_types),
                    json.dumps(config.relationship_types),
                    config.max_traversal_depth,
                    config.top_k_entities,
                    config.top_k_communities,
                    config.include_entity_neighborhoods,
                    config.community_min_size,
                    config.clustering_resolution,
                    config.clustering_max_level,
                    now,
                    now,
                ),
            )
            config.created_at = now
            config.updated_at = now
            return Success(config)
        except DatabaseException as e:
            logger.error(f"Database error creating graph RAG config: {e}")
            return Failure(DatabaseError(e.message, "create_graph_rag_config"))

    def update_vector_rag_config(
        self, config: VectorRagConfig
    ) -> Result[VectorRagConfig, DatabaseError]:
        """Update vector RAG config for a workspace."""
        query = """
            UPDATE vector_rag_configs
            SET embedding_model_vector_size = %s, distance_metric = %s,
                embedding_algorithm = %s, chunking_algorithm = %s, rerank_algorithm = %s,
                chunk_size = %s, chunk_overlap = %s, top_k = %s, updated_at = %s
            WHERE workspace_id = %s
        """
        now = datetime.now(UTC)
        try:
            self.db.execute(
                query,
                (
                    config.embedding_model_vector_size,
                    config.distance_metric,
                    config.embedding_algorithm,
                    config.chunking_algorithm,
                    config.rerank_algorithm,
                    config.chunk_size,
                    config.chunk_overlap,
                    config.top_k,
                    now,
                    config.workspace_id,
                ),
            )
            config.updated_at = now
            return Success(config)
        except DatabaseException as e:
            logger.error(f"Database error updating vector RAG config: {e}")
            return Failure(DatabaseError(e.message, "update_vector_rag_config"))

    def update_graph_rag_config(
        self, config: GraphRagConfig
    ) -> Result[GraphRagConfig, DatabaseError]:
        """Update graph RAG config for a workspace."""
        import json

        query = """
            UPDATE graph_rag_configs
            SET entity_extraction_algorithm = %s, relationship_extraction_algorithm = %s,
                clustering_algorithm = %s, entity_types = %s, relationship_types = %s,
                max_traversal_depth = %s, top_k_entities = %s, top_k_communities = %s,
                include_entity_neighborhoods = %s, community_min_size = %s,
                clustering_resolution = %s, clustering_max_level = %s, updated_at = %s
            WHERE workspace_id = %s
        """
        now = datetime.now(UTC)
        try:
            self.db.execute(
                query,
                (
                    config.entity_extraction_algorithm,
                    config.relationship_extraction_algorithm,
                    config.clustering_algorithm,
                    json.dumps(config.entity_types),
                    json.dumps(config.relationship_types),
                    config.max_traversal_depth,
                    config.top_k_entities,
                    config.top_k_communities,
                    config.include_entity_neighborhoods,
                    config.community_min_size,
                    config.clustering_resolution,
                    config.clustering_max_level,
                    now,
                    config.workspace_id,
                ),
            )
            config.updated_at = now
            return Success(config)
        except DatabaseException as e:
            logger.error(f"Database error updating graph RAG config: {e}")
            return Failure(DatabaseError(e.message, "update_graph_rag_config"))

    def delete_vector_rag_config(self, workspace_id: int) -> bool:
        """Delete vector RAG config for a workspace."""
        query = "DELETE FROM vector_rag_configs WHERE workspace_id = %s"
        try:
            affected_rows = self.db.execute(query, (workspace_id,))
        except DatabaseException as e:
            logger.error(f"Database error deleting vector RAG config: {e}")
            return False

        return affected_rows > 0

    def delete_graph_rag_config(self, workspace_id: int) -> bool:
        """Delete graph RAG config for a workspace."""
        query = "DELETE FROM graph_rag_configs WHERE workspace_id = %s"
        try:
            affected_rows = self.db.execute(query, (workspace_id,))
        except DatabaseException as e:
            logger.error(f"Database error deleting graph RAG config: {e}")
            return False

        return affected_rows > 0
