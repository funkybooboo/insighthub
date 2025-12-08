"""Graph RAG implementation of create RAG resources workflow."""

from typing import Optional

from returns.result import Failure, Result, Success

from src.infrastructure.graph_stores.graph_store import GraphStore
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.workflows.create_resources.create_rag_resources_workflow import (
    CreateRagResourcesWorkflow,
    CreateRagResourcesWorkflowError,
)

logger = create_logger(__name__)


class GraphRagCreateRagResourcesWorkflow(CreateRagResourcesWorkflow):
    """
    Graph RAG implementation of workspace provisioning workflow.

    Pipeline:
    1. Create Neo4j constraints for entity uniqueness
    2. Create indexes for workspace isolation and entity types
    3. Create indexes for community lookup
    4. Return success status
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
        config: Optional[dict[str, str | int | float | bool]] = None,
    ) -> Result[bool, CreateRagResourcesWorkflowError]:
        """Execute provisioning workflow for a workspace.

        Args:
            workspace_id: Unique workspace identifier
            config: Optional configuration parameters (not used currently)

        Returns:
            Result containing success status (True), or error
        """
        try:
            logger.info(
                f"Starting Graph RAG workspace provisioning for workspace_id={workspace_id}"
            )

            # Step 1: Drop old incompatible constraint (if exists from earlier versions)
            # The old constraint on Entity.id alone prevented the same entity from
            # existing in multiple workspaces. We remove it to allow workspace isolation.
            logger.info("Dropping old Entity.id constraint if it exists")
            self.graph_store.drop_constraint("Entity", "id")

            # Step 2: Create workspace isolation indexes
            # Note: We don't create a unique constraint on Entity.id alone because
            # the same entity (same id) can exist in multiple workspaces.
            # The MERGE uses (id, workspace_id) together for uniqueness.
            logger.info("Creating workspace isolation indexes")
            self.graph_store.create_index("Entity", ["workspace_id"])
            self.graph_store.create_index("Entity", ["id", "workspace_id"])

            # Step 3: Create entity type indexes
            logger.info("Creating entity type indexes")
            self.graph_store.create_index("Entity", ["workspace_id", "type"])

            # Step 4: Create community indexes
            logger.info("Creating community indexes")
            self.graph_store.create_index("Community", ["workspace_id", "level"])

            logger.info(f"Graph RAG workspace {workspace_id} provisioned successfully")

            return Success(True)

        except Exception as e:
            logger.error(f"Graph RAG workspace provisioning failed: {e}", exc_info=True)
            return Failure(
                CreateRagResourcesWorkflowError(
                    message=f"Failed to provision Graph RAG workspace: {str(e)}",
                    step="graph_workspace_provisioning",
                )
            )
