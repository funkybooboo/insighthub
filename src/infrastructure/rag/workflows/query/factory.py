"""Factory for creating query workflows."""

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.vector_rag.embedding.factory import EmbedderFactory
from src.infrastructure.rag.steps.vector_rag.reranking.factory import RerankerFactory
from src.infrastructure.rag.steps.vector_rag.vector_stores.factory import VectorStoreFactory
from src.infrastructure.rag.workflows.query.query_workflow import QueryWorkflow
from src.infrastructure.rag.workflows.query.vector_rag_query_workflow import VectorRagQueryWorkflow

logger = create_logger(__name__)


class QueryWorkflowFactory:
    """Factory for creating query workflows."""

    @staticmethod
    def create(rag_config: dict) -> QueryWorkflow:
        """Create a query workflow based on configuration.

        Args:
            rag_config: RAG configuration dictionary containing:
                - rag_type: "vector" or "graph"
                - embedder_type: "ollama", "openai", etc.
                - embedder_config: {base_url, model_name, ...}
                - vector_store_type: "qdrant", etc.
                - vector_store_config: {host, port, collection, ...}
                - enable_reranking: bool (optional)
                - reranker_type: str (optional)
                - reranker_config: dict (optional)

        Returns:
            QueryWorkflow implementation

        Raises:
            ValueError: If rag_type is unsupported or config is invalid
        """
        rag_type = rag_config.get("rag_type", "vector")

        if rag_type == "vector":
            return QueryWorkflowFactory._create_vector(rag_config)
        elif rag_type == "graph":
            return QueryWorkflowFactory._create_graph(rag_config)
        else:
            raise ValueError(f"Unsupported RAG type: {rag_type}")

    @staticmethod
    def _create_vector(config: dict) -> VectorRagQueryWorkflow:
        """Create Vector RAG query workflow with injected dependencies."""
        logger.info("Creating Vector RAG query workflow")

        # Create embedder
        embedder_type = config.get("embedder_type", "ollama")
        embedder_config = config.get("embedder_config", {})
        embedder = EmbedderFactory.create_embedder(embedder_type, **embedder_config)

        # Create vector store
        vector_store_type = config.get("vector_store_type", "qdrant")
        vector_store_config = config.get("vector_store_config", {})
        vector_store = VectorStoreFactory.create_vector_store(
            vector_store_type, **vector_store_config
        )

        # Create reranker (optional)
        reranker = None
        if config.get("enable_reranking", False):
            reranker_type = config.get("reranker_type", "dummy")
            reranker_config = config.get("reranker_config", {})
            reranker = RerankerFactory.create_reranker(reranker_type, **reranker_config)
            logger.debug(f"Created reranker: {reranker_type}")

        # Wire together into workflow
        workflow = VectorRagQueryWorkflow(
            embedder=embedder,
            vector_store=vector_store,
            reranker=reranker,
        )

        logger.info("Vector RAG query workflow created successfully")
        return workflow

    @staticmethod
    def _create_graph(config: dict) -> QueryWorkflow:
        """Create Graph RAG query workflow."""
        logger.warning("Graph RAG query workflow not yet implemented")
        raise NotImplementedError("Graph RAG query workflow not yet implemented")
