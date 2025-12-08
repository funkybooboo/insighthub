"""Factory for creating query workflows."""

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.graph_rag.entity_extraction.factory import EntityExtractorFactory
from src.infrastructure.rag.steps.vector_rag.embedding.factory import EmbedderFactory
from src.infrastructure.rag.steps.vector_rag.reranking.factory import RerankerFactory
from src.infrastructure.rag.store_manager import RAGStoreManager
from src.infrastructure.rag.workflows.query.graph_rag_query_workflow import GraphRagQueryWorkflow
from src.infrastructure.rag.workflows.query.hybrid_rag_query_workflow import HybridRagQueryWorkflow
from src.infrastructure.rag.workflows.query.query_workflow import QueryWorkflow
from src.infrastructure.rag.workflows.query.vector_rag_query_workflow import VectorRagQueryWorkflow

logger = create_logger(__name__)


class QueryWorkflowFactory:
    """Factory for creating query workflows."""

    @staticmethod
    def create(rag_config: dict, rag_store_manager: RAGStoreManager) -> QueryWorkflow:
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
            rag_store_manager: RAG store manager
        Returns:
            QueryWorkflow implementation
        Raises:
            ValueError: If rag_type is unsupported or config is invalid
        """
        rag_type = rag_config.get("rag_type", "vector")

        if rag_type == "vector":
            return QueryWorkflowFactory._create_vector(rag_config, rag_store_manager)
        elif rag_type == "graph":
            return QueryWorkflowFactory._create_graph(rag_config, rag_store_manager)
        elif rag_type == "hybrid":
            return QueryWorkflowFactory._create_hybrid(rag_config, rag_store_manager)
        else:
            raise ValueError(f"Unsupported RAG type: {rag_type}")

    @staticmethod
    def _create_vector(config: dict, rag_store_manager: RAGStoreManager) -> VectorRagQueryWorkflow:
        """Create Vector RAG query workflow with injected dependencies."""
        logger.info("Creating Vector RAG query workflow")

        # Create embedder
        embedder_type = config.get("embedder_type", "ollama")
        embedder_config = config.get("embedder_config", {})
        embedder = EmbedderFactory.create_embedder(embedder_type, **embedder_config)

        # Get vector store from manager
        vector_store = rag_store_manager.get_vector_store(config)
        logger.debug("Retrieved vector store from manager")

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
    def _create_hybrid(config: dict, rag_store_manager: RAGStoreManager) -> HybridRagQueryWorkflow:
        """Create Hybrid RAG query workflow."""
        logger.info("Creating Hybrid RAG query workflow")

        vector_workflow = QueryWorkflowFactory._create_vector(config, rag_store_manager)
        graph_workflow = QueryWorkflowFactory._create_graph(config, rag_store_manager)

        workflow = HybridRagQueryWorkflow(
            vector_workflow=vector_workflow,
            graph_workflow=graph_workflow,
        )

        logger.info("Hybrid RAG query workflow created successfully")
        return workflow

    @staticmethod
    def _create_graph(config: dict, rag_store_manager: RAGStoreManager) -> GraphRagQueryWorkflow:
        """Create Graph RAG query workflow."""
        logger.info("Creating Graph RAG query workflow")

        # Create entity extractor
        entity_extractor = EntityExtractorFactory.create(
            config.get("entity_extraction_algorithm", "spacy"),
            **config.get("entity_extraction_config", {}),
        )

        # Get graph store from manager
        graph_store = rag_store_manager.get_graph_store(config)
        logger.debug("Retrieved graph store from manager")

        # Get workspace_id from config (should be provided by caller)
        workspace_id = config.get("workspace_id", "")

        # Create workflow
        workflow = GraphRagQueryWorkflow(
            entity_extractor=entity_extractor,
            graph_store=graph_store,
            workspace_id=workspace_id,
            max_traversal_depth=config.get("max_traversal_depth", 2),
            top_k_entities=config.get("top_k_entities", 10),
            top_k_communities=config.get("top_k_communities", 3),
            include_entity_neighborhoods=config.get("include_entity_neighborhoods", True),
        )

        logger.info("Graph RAG query workflow created successfully")
        return workflow
