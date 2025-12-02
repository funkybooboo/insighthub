"""Factory for creating remove document workflows."""

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.vector_rag.vector_stores.factory import VectorStoreFactory
from src.infrastructure.rag.workflows.remove_document.remove_document_workflow import (
    RemoveDocumentWorkflow,
)
from src.infrastructure.rag.workflows.remove_document.vector_rag_remove_document_workflow import (
    VectorRagRemoveDocumentWorkflow,
)

logger = create_logger(__name__)


class RemoveDocumentWorkflowFactory:
    """Factory for creating remove document workflows."""

    @staticmethod
    def create(rag_config: dict) -> RemoveDocumentWorkflow:
        """Create a remove document workflow based on configuration.

        Args:
            rag_config: RAG configuration dictionary containing:
                - rag_type: "vector" or "graph"
                - vector_store_type: "qdrant", etc.
                - vector_store_config: {host, port, collection, ...}

        Returns:
            RemoveDocumentWorkflow implementation

        Raises:
            ValueError: If rag_type is unsupported or config is invalid
        """
        rag_type = rag_config.get("rag_type", "vector")

        if rag_type == "vector":
            return RemoveDocumentWorkflowFactory._create_vector(rag_config)
        elif rag_type == "graph":
            return RemoveDocumentWorkflowFactory._create_graph(rag_config)
        else:
            raise ValueError(f"Unsupported RAG type: {rag_type}")

    @staticmethod
    def _create_vector(config: dict) -> VectorRagRemoveDocumentWorkflow:
        """Create Vector RAG remove document workflow with injected dependencies."""
        logger.info("Creating Vector RAG remove document workflow")

        # Create vector database (needed for querying/deleting chunks)
        vector_store_type = config.get("vector_store_type", "qdrant")
        vector_store_config = config.get("vector_store_config", {})
        vector_database = VectorStoreFactory.create_vector_store(
            vector_store_type, **vector_store_config
        )

        workflow = VectorRagRemoveDocumentWorkflow(vector_database=vector_database)
        logger.info("Vector RAG remove document workflow created successfully")
        return workflow

    @staticmethod
    def _create_graph(config: dict) -> RemoveDocumentWorkflow:
        """Create Graph RAG remove document workflow."""
        logger.warning("Graph RAG remove document workflow not yet implemented")
        raise NotImplementedError("Graph RAG remove document workflow not yet implemented")
