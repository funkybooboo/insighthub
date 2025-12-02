"""Factory for creating create RAG resources workflows."""

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.workflows.create_resources.create_rag_resources_workflow import (
    CreateRagResourcesWorkflow,
)
from src.infrastructure.rag.workflows.create_resources.vector_rag_create_rag_resources_workflow import (
    VectorRagCreateRagResourcesWorkflow,
)

logger = create_logger(__name__)


class CreateResourcesWorkflowFactory:
    """Factory for creating create RAG resources workflows."""

    @staticmethod
    def create(rag_config: dict) -> CreateRagResourcesWorkflow:
        """Create a create RAG resources workflow based on configuration.

        Args:
            rag_config: RAG configuration dictionary containing:
                - rag_type: "vector" or "graph"
                - qdrant_url: Qdrant server URL (for vector RAG)
                - vector_size: Vector dimension (for vector RAG)
                - distance: Distance metric (for vector RAG)

        Returns:
            CreateRagResourcesWorkflow implementation

        Raises:
            ValueError: If rag_type is unsupported or config is invalid
        """
        rag_type = rag_config.get("rag_type", "vector")

        if rag_type == "vector":
            return CreateResourcesWorkflowFactory._create_vector(rag_config)
        elif rag_type == "graph":
            return CreateResourcesWorkflowFactory._create_graph(rag_config)
        else:
            raise ValueError(f"Unsupported RAG type: {rag_type}")

    @staticmethod
    def _create_vector(config: dict) -> VectorRagCreateRagResourcesWorkflow:
        """Create Vector RAG create resources workflow."""
        logger.info("Creating Vector RAG create resources workflow")

        qdrant_url = config.get("qdrant_url", "http://localhost:6333")
        vector_size = config.get("vector_size", 768)
        distance = config.get("distance", "cosine")

        workflow = VectorRagCreateRagResourcesWorkflow(
            qdrant_url=qdrant_url,
            vector_size=vector_size,
            distance=distance,
        )
        logger.info("Vector RAG create resources workflow created successfully")
        return workflow

    @staticmethod
    def _create_graph(config: dict) -> CreateRagResourcesWorkflow:
        """Create Graph RAG create resources workflow."""
        logger.warning("Graph RAG create resources workflow not yet implemented")
        raise NotImplementedError("Graph RAG create resources workflow not yet implemented")
