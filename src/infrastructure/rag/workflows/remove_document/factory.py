"""Factory for creating remove document workflows."""

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.store_manager import RAGStoreManager
from src.infrastructure.rag.workflows.remove_document.graph_rag_remove_document_workflow import (
    GraphRagRemoveDocumentWorkflow,
)
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
    def create(rag_config: dict, rag_store_manager: RAGStoreManager) -> RemoveDocumentWorkflow:
        """Create a remove document workflow based on configuration.
        Args:
            rag_config: RAG configuration dictionary containing:
                - rag_type: "vector" or "graph"
                - vector_store_type: "qdrant", etc.
                - vector_store_config: {host, port, collection, ...}
            rag_store_manager: RAG store manager
        Returns:
            RemoveDocumentWorkflow implementation
        Raises:
            ValueError: If rag_type is unsupported or config is invalid
        """
        rag_type = rag_config.get("rag_type", "vector")

        if rag_type == "vector":
            return RemoveDocumentWorkflowFactory._create_vector(rag_config, rag_store_manager)
        elif rag_type == "graph":
            return RemoveDocumentWorkflowFactory._create_graph(rag_config, rag_store_manager)
        else:
            raise ValueError(f"Unsupported RAG type: {rag_type}")

    @staticmethod
    def _create_vector(
        config: dict, rag_store_manager: RAGStoreManager
    ) -> VectorRagRemoveDocumentWorkflow:
        """Create Vector RAG remove document workflow with injected dependencies."""
        logger.info("Creating Vector RAG remove document workflow")

        # Get vector store from manager
        vector_store = rag_store_manager.get_vector_store(config)
        logger.debug("Retrieved vector store from manager")

        workflow = VectorRagRemoveDocumentWorkflow(vector_store=vector_store)
        logger.info("Vector RAG remove document workflow created successfully")
        return workflow

    @staticmethod
    def _create_graph(
        config: dict, rag_store_manager: RAGStoreManager
    ) -> GraphRagRemoveDocumentWorkflow:
        """Create Graph RAG remove document workflow."""
        logger.info("Creating Graph RAG remove document workflow")

        # Get graph store from manager
        graph_store = rag_store_manager.get_graph_store(config)
        logger.debug("Retrieved graph store from manager")

        workflow = GraphRagRemoveDocumentWorkflow(graph_store=graph_store)
        logger.info("Graph RAG remove document workflow created successfully")
        return workflow
