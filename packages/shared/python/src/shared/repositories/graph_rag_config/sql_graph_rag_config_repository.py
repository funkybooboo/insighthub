"""SQL implementation of Graph RAG configuration repository."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase
from shared.repositories.graph_rag_config.graph_rag_config_repository import GraphRagConfigRepository
from shared.types.rag import GraphRagConfig


class SqlGraphRagConfigRepository(GraphRagConfigRepository):
    """SQL implementation of GraphRagConfig repository."""

    def __init__(self, db: PostgresSqlDatabase):
        """Initialize the repository."""
        self._db = db

    def create_graph_rag_config(
        self,
        workspace_id: int,
        entity_extraction_algorithm: str = "ollama",
        relationship_extraction_algorithm: str = "ollama",
        clustering_algorithm: str = "leiden",
        max_hops: int = 2,
        min_cluster_size: int = 5,
        max_cluster_size: int = 50,
    ) -> GraphRagConfig:
        """Create a new Graph RAG configuration for a workspace."""
        query = """
        INSERT INTO graph_rag_configs (
            workspace_id, entity_extraction_algorithm, relationship_extraction_algorithm,
            clustering_algorithm, max_hops, min_cluster_size, max_cluster_size
        ) VALUES (
            %(workspace_id)s, %(entity_extraction_algorithm)s, %(relationship_extraction_algorithm)s,
            %(clustering_algorithm)s, %(max_hops)s, %(min_cluster_size)s, %(max_cluster_size)s
        )
        RETURNING id, workspace_id, entity_extraction_algorithm, relationship_extraction_algorithm,
                 clustering_algorithm, max_hops, min_cluster_size, max_cluster_size,
                 created_at, updated_at
        """

        params = {
            "workspace_id": workspace_id,
            "entity_extraction_algorithm": entity_extraction_algorithm,
            "relationship_extraction_algorithm": relationship_extraction_algorithm,
            "clustering_algorithm": clustering_algorithm,
            "max_hops": max_hops,
            "min_cluster_size": min_cluster_size,
            "max_cluster_size": max_cluster_size,
        }

        row = self._db.fetchone(query, params)
        if row is None:
            raise RuntimeError("Failed to create graph RAG config")

        return GraphRagConfig(**row)

    def get_graph_rag_config(self, workspace_id: int) -> Optional[GraphRagConfig]:
        """Get Graph RAG configuration for a workspace."""
        query = """
        SELECT id, workspace_id, entity_extraction_algorithm, relationship_extraction_algorithm,
               clustering_algorithm, max_hops, min_cluster_size, max_cluster_size,
               created_at, updated_at
        FROM graph_rag_configs
        WHERE workspace_id = %(workspace_id)s
        """

        row = self._db.fetchone(query, {"workspace_id": workspace_id})
        if row is None:
            return None

        return GraphRagConfig(**row)

    def update_graph_rag_config(
        self,
        workspace_id: int,
        entity_extraction_algorithm: Optional[str] = None,
        relationship_extraction_algorithm: Optional[str] = None,
        clustering_algorithm: Optional[str] = None,
        max_hops: Optional[int] = None,
        min_cluster_size: Optional[int] = None,
        max_cluster_size: Optional[int] = None,
    ) -> Optional[GraphRagConfig]:
        """Update Graph RAG configuration for a workspace."""
        # Build dynamic update query
        update_fields = []
        params: dict = {"workspace_id": workspace_id}

        if entity_extraction_algorithm is not None:
            update_fields.append("entity_extraction_algorithm = %(entity_extraction_algorithm)s")
            params["entity_extraction_algorithm"] = entity_extraction_algorithm
        if relationship_extraction_algorithm is not None:
            update_fields.append("relationship_extraction_algorithm = %(relationship_extraction_algorithm)s")
            params["relationship_extraction_algorithm"] = relationship_extraction_algorithm
        if clustering_algorithm is not None:
            update_fields.append("clustering_algorithm = %(clustering_algorithm)s")
            params["clustering_algorithm"] = clustering_algorithm
        if max_hops is not None:
            update_fields.append("max_hops = %(max_hops)s")
            params["max_hops"] = max_hops
        if min_cluster_size is not None:
            update_fields.append("min_cluster_size = %(min_cluster_size)s")
            params["min_cluster_size"] = min_cluster_size
        if max_cluster_size is not None:
            update_fields.append("max_cluster_size = %(max_cluster_size)s")
            params["max_cluster_size"] = max_cluster_size

        if not update_fields:
            return self.get_graph_rag_config(workspace_id)

        update_fields.append("updated_at = NOW()")

        query = f"""
        UPDATE graph_rag_configs
        SET {', '.join(update_fields)}
        WHERE workspace_id = %(workspace_id)s
        RETURNING id, workspace_id, entity_extraction_algorithm, relationship_extraction_algorithm,
                 clustering_algorithm, max_hops, min_cluster_size, max_cluster_size,
                 created_at, updated_at
        """

        row = self._db.fetchone(query, params)
        if row is None:
            return None

        return GraphRagConfig(**row)

    def delete_graph_rag_config(self, workspace_id: int) -> bool:
        """Delete Graph RAG configuration for a workspace."""
        query = "DELETE FROM graph_rag_configs WHERE workspace_id = %(workspace_id)s"
        self._db.execute(query, {"workspace_id": workspace_id})
        return True