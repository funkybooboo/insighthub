"""Workflow factory for creating RAG workflows based on configuration.

This factory uses dependency injection to wire together steps into workflows
based on workspace RAG configuration.
"""

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.general.chunking.factory import ChunkerFactory
from src.infrastructure.rag.steps.general.parsing.factory import ParserFactory
from src.infrastructure.rag.steps.vector_rag.embedding.factory import EmbedderFactory
from src.infrastructure.rag.steps.vector_rag.reranking.factory import RerankerFactory
from src.infrastructure.rag.steps.vector_rag.vector_stores.factory import VectorStoreFactory
from src.infrastructure.rag.workflows.consume_workflow import ConsumeWorkflow
from src.infrastructure.rag.workflows.graph_rag import (
    GraphRagConsumeWorkflow,
    GraphRagQueryWorkflow,
)
from src.infrastructure.rag.workflows.query_workflow import QueryWorkflow
from src.infrastructure.rag.workflows.vector_rag import (
    VectorRagConsumeWorkflow,
    VectorRagQueryWorkflow,
)

logger = create_logger(__name__)


class WorkflowFactory:
    """
    Factory for creating RAG workflows with dependency injection.

    Creates workflows based on workspace RAG configuration, wiring together
    the appropriate steps (parsers, chunkers, embedders, stores, etc.).
    """

    @staticmethod
    def create_consume_workflow(rag_config: dict) -> ConsumeWorkflow:
        """Create a consume workflow based on RAG configuration.

        Args:
            rag_config: RAG configuration dictionary containing:
                - rag_type: "vector" or "graph"
                - parser_type: "text", "pdf", "html", "docx"
                - chunker_type: "sentence", "character", "semantic"
                - chunker_config: {chunk_size, overlap, ...}
                - embedder_type: "ollama", "openai", etc.
                - embedder_config: {base_url, model_name, ...}
                - vector_store_type: "qdrant", etc.
                - vector_store_config: {host, port, collection, ...}

        Returns:
            ConsumeWorkflow implementation (Vector or Graph RAG)

        Raises:
            ValueError: If rag_type is unsupported or config is invalid
        """
        rag_type = rag_config.get("rag_type", "vector")

        if rag_type == "vector":
            return WorkflowFactory._create_vector_consume_workflow(rag_config)
        elif rag_type == "graph":
            return WorkflowFactory._create_graph_consume_workflow(rag_config)
        else:
            raise ValueError(f"Unsupported RAG type: {rag_type}")

    @staticmethod
    def create_query_workflow(rag_config: dict) -> QueryWorkflow:
        """Create a query workflow based on RAG configuration.

        Args:
            rag_config: RAG configuration dictionary (same as consume_workflow)

        Returns:
            QueryWorkflow implementation (Vector or Graph RAG)

        Raises:
            ValueError: If rag_type is unsupported or config is invalid
        """
        rag_type = rag_config.get("rag_type", "vector")

        if rag_type == "vector":
            return WorkflowFactory._create_vector_query_workflow(rag_config)
        elif rag_type == "graph":
            return WorkflowFactory._create_graph_query_workflow(rag_config)
        else:
            raise ValueError(f"Unsupported RAG type: {rag_type}")

    @staticmethod
    def _create_vector_consume_workflow(config: dict) -> VectorRagConsumeWorkflow:
        """Create Vector RAG consume workflow with injected dependencies."""
        logger.info("Creating Vector RAG consume workflow")

        # Create parser
        parser_type = config.get("parser_type", "text")
        parser = ParserFactory.create_parser(parser_type)
        logger.debug(f"Created parser: {parser_type}")

        # Create chunker
        chunker_type = config.get("chunker_type", "sentence")
        chunker_config = config.get("chunker_config", {})
        chunker = ChunkerFactory.create_chunker(chunker_type, **chunker_config)
        logger.debug(f"Created chunker: {chunker_type} with config {chunker_config}")

        # Create embedder
        embedder_type = config.get("embedder_type", "ollama")
        embedder_config = config.get("embedder_config", {})
        embedder = EmbedderFactory.create_embedder(embedder_type, **embedder_config)
        logger.debug(f"Created embedder: {embedder_type} with config {embedder_config}")

        # Create vector store
        vector_store_type = config.get("vector_store_type", "qdrant")
        vector_store_config = config.get("vector_store_config", {})
        vector_store = VectorStoreFactory.create_vector_store(
            vector_store_type, **vector_store_config
        )
        logger.debug(f"Created vector store: {vector_store_type} with config {vector_store_config}")

        # Wire together into workflow
        workflow = VectorRagConsumeWorkflow(
            parser=parser,
            chunker=chunker,
            embedder=embedder,
            vector_store=vector_store,
        )

        logger.info("Vector RAG consume workflow created successfully")
        return workflow

    @staticmethod
    def _create_vector_query_workflow(config: dict) -> VectorRagQueryWorkflow:
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
    def _create_graph_consume_workflow(config: dict) -> GraphRagConsumeWorkflow:
        """Create Graph RAG consume workflow (placeholder)."""
        logger.warning("Graph RAG consume workflow not yet implemented")
        return GraphRagConsumeWorkflow()

    @staticmethod
    def _create_graph_query_workflow(config: dict) -> GraphRagQueryWorkflow:
        """Create Graph RAG query workflow (placeholder)."""
        logger.warning("Graph RAG query workflow not yet implemented")
        return GraphRagQueryWorkflow()


def create_default_vector_rag_config() -> dict:
    """Create default Vector RAG configuration.

    Returns:
        Default configuration dictionary for Vector RAG
    """
    return {
        "rag_type": "vector",
        "parser_type": "text",
        "chunker_type": "sentence",
        "chunker_config": {
            "chunk_size": 500,
            "overlap": 50,
        },
        "embedder_type": "ollama",
        "embedder_config": {
            "base_url": "http://localhost:11434",
            "model_name": "nomic-embed-text",
        },
        "vector_store_type": "qdrant",
        "vector_store_config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "documents",
        },
        "enable_reranking": False,
    }
