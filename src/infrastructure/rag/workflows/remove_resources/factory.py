"""Factory for creating remove RAG resources workflows."""

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.workflows.remove_resources.remove_rag_resources_workflow import (
    RemoveRagResourcesWorkflow,
)
from src.infrastructure.rag.workflows.remove_resources.vector_rag_remove_rag_resources_workflow import (
    VectorRagRemoveRagResourcesWorkflow,
)

logger = create_logger(__name__)


class RemoveResourcesWorkflowFactory:
    """Factory for creating remove RAG resources workflows."""

    @staticmethod
    def create(rag_config: dict) -> RemoveRagResourcesWorkflow:
        """Create a remove RAG resources workflow based on configuration.

        Args:
            rag_config: RAG configuration dictionary containing:
                - rag_type: "vector" or "graph"
                - qdrant_url: Qdrant server URL (for vector RAG)

        Returns:
            RemoveRagResourcesWorkflow implementation

        Raises:
            ValueError: If rag_type is unsupported or config is invalid
        """
        rag_type = rag_config.get("rag_type", "vector")

        if rag_type == "vector":
            return RemoveResourcesWorkflowFactory._create_vector(rag_config)
        elif rag_type == "graph":
            return RemoveResourcesWorkflowFactory._create_graph(rag_config)
        else:
            raise ValueError(f"Unsupported RAG type: {rag_type}")

    @staticmethod
    def _create_vector(config: dict) -> VectorRagRemoveRagResourcesWorkflow:
        """Create Vector RAG remove resources workflow."""
        logger.info("Creating Vector RAG remove resources workflow")

        qdrant_url = config.get("qdrant_url", "http://localhost:6333")

        workflow = VectorRagRemoveRagResourcesWorkflow(qdrant_url=qdrant_url)
        logger.info("Vector RAG remove resources workflow created successfully")
        return workflow

    @staticmethod
    def _create_graph(config: dict) -> RemoveRagResourcesWorkflow:
        """Create Graph RAG remove resources workflow."""
        logger.warning("Graph RAG remove resources workflow not yet implemented")
        raise NotImplementedError("Graph RAG remove resources workflow not yet implemented")
