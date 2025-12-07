"""Factory for creating add document workflows."""

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.general.chunking.factory import ChunkerFactory
from src.infrastructure.rag.steps.general.parsing.factory import ParserFactory
from src.infrastructure.rag.steps.vector_rag.embedding.factory import EmbedderFactory
from src.infrastructure.rag.workflows.add_document.add_document_workflow import AddDocumentWorkflow
from src.infrastructure.rag.workflows.add_document.vector_rag_add_document_workflow import (
    VectorRagAddDocumentWorkflow,
)
from src.infrastructure.vector_stores import VectorStoreFactory

logger = create_logger(__name__)


class AddDocumentWorkflowFactory:
    """Factory for creating add document workflows."""

    @staticmethod
    def create(rag_config: dict) -> AddDocumentWorkflow:
        """Create an add document workflow based on configuration.

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
            AddDocumentWorkflow implementation

        Raises:
            ValueError: If rag_type is unsupported or config is invalid
        """
        rag_type = rag_config.get("rag_type", "vector")

        if rag_type == "vector":
            return AddDocumentWorkflowFactory._create_vector(rag_config)
        elif rag_type == "graph":
            return AddDocumentWorkflowFactory._create_graph(rag_config)
        else:
            raise ValueError(f"Unsupported RAG type: {rag_type}")

    @staticmethod
    def _create_vector(config: dict) -> VectorRagAddDocumentWorkflow:
        """Create Vector RAG add document workflow with injected dependencies."""
        logger.info("Creating Vector RAG add document workflow")

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
        workflow = VectorRagAddDocumentWorkflow(
            parser=parser,
            chunker=chunker,
            embedder=embedder,
            vector_store=vector_store,
        )

        logger.info("Vector RAG add document workflow created successfully")
        return workflow

    @staticmethod
    def _create_graph(config: dict) -> AddDocumentWorkflow:
        """Create Graph RAG add document workflow."""
        logger.info("Creating Graph RAG add document workflow")

        from src.infrastructure.graph_stores.factory import GraphStoreFactory
        from src.infrastructure.rag.steps.general.chunking.factory import ChunkerFactory
        from src.infrastructure.rag.steps.general.parsing.factory import ParserFactory
        from src.infrastructure.rag.steps.graph_rag.entity_extraction.factory import (
            EntityExtractorFactory,
        )
        from src.infrastructure.rag.steps.graph_rag.relationship_extraction.factory import (
            RelationshipExtractorFactory,
        )
        from src.infrastructure.rag.workflows.add_document.graph_rag_add_document_workflow import (
            GraphRagAddDocumentWorkflow,
        )

        # Create parser
        parser = ParserFactory.create_parser(config.get("parser_type", "text"))

        # Create chunker
        chunker = ChunkerFactory.create_chunker(
            config.get("chunker_type", "sentence"),
            **config.get("chunker_config", {}),
        )

        # Create entity extractor
        entity_extractor = EntityExtractorFactory.create(
            config.get("entity_extraction_type", "spacy"),
            **config.get("entity_extraction_config", {}),
        )

        # Create relationship extractor
        relationship_extractor = RelationshipExtractorFactory.create(
            config.get("relationship_extraction_type", "dependency-parsing"),
            **config.get("relationship_extraction_config", {}),
        )

        # Create graph store
        graph_store = GraphStoreFactory.create(
            config.get("graph_store_type", "neo4j"),
            **config.get("graph_store_config", {}),
        )

        # Create workflow with clustering parameters
        workflow = GraphRagAddDocumentWorkflow(
            parser=parser,
            chunker=chunker,
            entity_extractor=entity_extractor,
            relationship_extractor=relationship_extractor,
            graph_store=graph_store,
            clustering_algorithm=config.get("clustering_algorithm", "leiden"),
            clustering_resolution=config.get("clustering_resolution", 1.0),
            clustering_max_level=config.get("clustering_max_level", 3),
            community_min_size=config.get("community_min_size", 3),
        )

        logger.info("Graph RAG add document workflow created successfully")
        return workflow
