"""Factory for creating remove document workflows."""

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.workflows.remove_document.remove_document_workflow import (
    RemoveDocumentWorkflow,
)
from src.infrastructure.rag.workflows.remove_document.vector_rag_remove_document_workflow import (
    VectorRagRemoveDocumentWorkflow,
)
from src.infrastructure.vector_stores import QdrantVectorDatabase, create_vector_database

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

        # Use create_vector_database to get VectorDatabase instance (not VectorStore)
        vector_database = create_vector_database(
            db_type=vector_store_type,
            url=vector_store_config.get("url") or vector_store_config.get("host", "localhost"),
            collection_name=vector_store_config.get("collection_name", "document"),
            vector_size=vector_store_config.get("vector_size", 768),
            api_key=vector_store_config.get("api_key"),
        )

        # Type narrow: we know create_vector_database returns QdrantVectorDatabase for "qdrant" type
        if not isinstance(vector_database, QdrantVectorDatabase):
            raise TypeError(f"Expected QdrantVectorDatabase but got {type(vector_database)}")

        workflow = VectorRagRemoveDocumentWorkflow(vector_database=vector_database)
        logger.info("Vector RAG remove document workflow created successfully")
        return workflow

    @staticmethod
    def _create_graph(config: dict) -> RemoveDocumentWorkflow:
        """Create Graph RAG remove document workflow."""
        logger.info("Creating Graph RAG remove document workflow")

        from src.infrastructure.graph_stores.factory import GraphStoreFactory
        from src.infrastructure.rag.workflows.remove_document.graph_rag_remove_document_workflow import (
            GraphRagRemoveDocumentWorkflow,
        )

        # Create graph store
        graph_store = GraphStoreFactory.create(
            config.get("graph_store_type", "neo4j"),
            **config.get("graph_store_config", {}),
        )

        workflow = GraphRagRemoveDocumentWorkflow(graph_store=graph_store)
        logger.info("Graph RAG remove document workflow created successfully")
        return workflow
