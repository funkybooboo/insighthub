"""Graph RAG implementation of remove RAG resources workflow."""

from returns.result import Failure, Result, Success

from src.infrastructure.graph_stores.graph_store import GraphStore
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.workflows.remove_resources.remove_rag_resources_workflow import (
    RemoveRagResourcesWorkflow,
    RemoveRagResourcesWorkflowError,
)

logger = create_logger(__name__)


class GraphRagRemoveRagResourcesWorkflow(RemoveRagResourcesWorkflow):
    """
    Graph RAG implementation of workspace resource deletion workflow.

    Pipeline:
    1. Delete all entities for the workspace
    2. Delete all relationships for the workspace
    3. Delete all communities for the workspace
    4. Return success status

    Note: This does NOT delete the Neo4j database itself, only the workspace data.
    Constraints and indexes are shared across workspaces.
    """

    def __init__(self, graph_store: GraphStore):
        """Initialize workflow with graph store.

        Args:
            graph_store: Graph store implementation (e.g., Neo4jGraphStore)
        """
        self.graph_store = graph_store

    def execute(
        self,
        workspace_id: str,
    ) -> Result[bool, RemoveRagResourcesWorkflowError]:
        """Execute removal workflow for a workspace.

        Args:
            workspace_id: Unique workspace identifier

        Returns:
            Result containing success status (True), or error
        """
        try:
            logger.info(f"Starting Graph RAG workspace removal for workspace_id={workspace_id}")

            # Delete all graph data for this workspace
            # This includes entities, relationships, and communities
            logger.info(f"Deleting all graph data for workspace {workspace_id}")
            self.graph_store.delete_workspace_graph(workspace_id)

            logger.info(f"Graph RAG workspace {workspace_id} removed successfully")

            return Success(True)

        except Exception as e:
            logger.error(f"Graph RAG workspace removal failed: {e}", exc_info=True)
            return Failure(
                RemoveRagResourcesWorkflowError(
                    message=f"Failed to remove Graph RAG workspace: {str(e)}",
                    step="graph_workspace_removal",
                )
            )
