"""
Integration tests verifying shared package imports work correctly.

These tests ensure all public modules and types can be imported
without errors, validating the package structure is correct.
"""

import pytest


class TestTypeImports:
    """Test that core type imports work."""

    def test_document_and_chunk_types(self) -> None:
        """Test importing Document and Chunk types."""
        from shared.types import Document, Chunk

        # Verify they are importable and are classes
        assert Document is not None
        assert Chunk is not None

    def test_graph_types(self) -> None:
        """Test importing GraphNode and GraphEdge types."""
        from shared.types import GraphNode, GraphEdge

        assert GraphNode is not None
        assert GraphEdge is not None

    def test_result_and_option_types(self) -> None:
        """Test importing Result and Option types."""
        from shared.types.result import Ok, Err, Result
        from shared.types.option import Some, Nothing, Option

        assert Ok is not None
        assert Err is not None
        assert Some is not None
        assert Nothing is not None

    def test_rag_config_types(self) -> None:
        """Test importing RAG configuration types."""
        from shared.types import ChunkerConfig, RagConfig, SearchResult

        assert ChunkerConfig is not None
        assert RagConfig is not None
        assert SearchResult is not None


class TestComponentImports:
    """Test that component imports work from their new locations."""

    def test_document_chunking_imports(self) -> None:
        """Test importing document chunking components."""
        from shared.document_chunking import Chunker, SentenceChunker

        from abc import ABCMeta

        assert isinstance(Chunker, ABCMeta)
        assert SentenceChunker is not None

    def test_vector_embedding_imports(self) -> None:
        """Test importing vector embedding components."""
        from shared.vector_embedding import EmbeddingEncoder, OllamaEmbeddings

        from abc import ABCMeta

        assert isinstance(EmbeddingEncoder, ABCMeta)
        assert OllamaEmbeddings is not None

    def test_vector_database_imports(self) -> None:
        """Test importing vector database components."""
        from shared.vector_database import VectorDatabase, QdrantVectorDatabase

        from abc import ABCMeta

        assert isinstance(VectorDatabase, ABCMeta)
        assert QdrantVectorDatabase is not None

    def test_parsing_imports(self) -> None:
        """Test importing parsing components."""
        from shared.parsing import DocumentParser, ParserFactory

        from abc import ABCMeta

        assert isinstance(DocumentParser, ABCMeta)
        assert ParserFactory is not None


class TestDataTypeInstantiation:
    """Test that data types can be instantiated correctly."""

    def test_document_instantiation(self) -> None:
        """Test creating a Document instance."""
        from shared.types import Document

        doc = Document(
            id="doc_1",
            workspace_id="workspace_1",
            title="Test Document",
            content="This is a test document.",
            metadata={"author": "Test Author", "year": 2025},
        )

        assert doc.id == "doc_1"
        assert doc.title == "Test Document"
        assert doc.metadata["author"] == "Test Author"

    def test_chunk_instantiation(self) -> None:
        """Test creating a Chunk instance."""
        from shared.types import Chunk

        chunk = Chunk(
            id="chunk_1",
            document_id="doc_1",
            text="This is a test chunk.",
            metadata={"index": 0, "source": "test"},
            vector=None,
        )

        assert chunk.id == "chunk_1"
        assert chunk.document_id == "doc_1"
        assert chunk.text == "This is a test chunk."

    def test_graph_node_instantiation(self) -> None:
        """Test creating a GraphNode instance."""
        from shared.types import GraphNode

        node = GraphNode(
            id="node_1",
            labels=["Entity", "Person"],
            properties={"name": "John Doe"},
        )

        assert node.id == "node_1"
        assert "Person" in node.labels
        assert node.properties["name"] == "John Doe"

    def test_graph_edge_instantiation(self) -> None:
        """Test creating a GraphEdge instance."""
        from shared.types import GraphEdge

        edge = GraphEdge(
            id="edge_1",
            source="node_1",
            target="node_2",
            label="knows",
            properties={"since": 2020},
        )

        assert edge.id == "edge_1"
        assert edge.label == "knows"
        assert edge.source == "node_1"
        assert edge.target == "node_2"


class TestBlobStorageImports:
    """Test that blob_storage module imports work."""

    def test_blob_storage_interface(self) -> None:
        """Test importing BlobStorage interface."""
        from shared.blob_storage import BlobStorage

        from abc import ABCMeta

        assert isinstance(BlobStorage, ABCMeta)

    def test_storage_implementations(self) -> None:
        """Test importing storage implementations."""
        from shared.blob_storage import (
            InMemoryBlobStorage,
            FileSystemBlobStorage,
            MinIOBlobStorage,
        )

        assert InMemoryBlobStorage is not None
        assert FileSystemBlobStorage is not None
        assert MinIOBlobStorage is not None

    def test_storage_factory(self) -> None:
        """Test importing storage factory."""
        from shared.blob_storage import create_blob_storage, BlobStorageType

        assert create_blob_storage is not None
        assert BlobStorageType.IN_MEMORY.value == "in_memory"
        assert BlobStorageType.FILE_SYSTEM.value == "file_system"
        assert BlobStorageType.S3.value == "s3"


class TestLlmProviderImports:
    """Test that LLM provider module imports work."""

    def test_llm_provider_interface(self) -> None:
        """Test importing LlmProvider interface."""
        from shared.llm_provider import LlmProvider

        from abc import ABCMeta

        assert isinstance(LlmProvider, ABCMeta)

    def test_llm_provider_implementations(self) -> None:
        """Test importing LLM provider implementations."""
        from shared.llm_provider import (
            OllamaLlmProvider,
            OpenAiLlmProvider,
            ClaudeLlmProvider,
            HuggingFaceLlmProvider,
        )

        assert OllamaLlmProvider is not None
        assert OpenAiLlmProvider is not None
        assert ClaudeLlmProvider is not None
        assert HuggingFaceLlmProvider is not None

    def test_llm_provider_factory(self) -> None:
        """Test importing LLM provider factory."""
        from shared.llm_provider import create_llm_provider, SUPPORTED_LLM_PROVIDERS

        assert create_llm_provider is not None
        assert "ollama" in SUPPORTED_LLM_PROVIDERS
        assert "openai" in SUPPORTED_LLM_PROVIDERS
        assert "claude" in SUPPORTED_LLM_PROVIDERS
        assert "huggingface" in SUPPORTED_LLM_PROVIDERS


class TestMessagingImports:
    """Test that messaging module imports work."""

    def test_rabbitmq_classes(self) -> None:
        """Test importing RabbitMQ classes."""
        from shared.messaging import RabbitMQPublisher, RabbitMQConsumer
        from shared.workers import Worker

        assert RabbitMQPublisher is not None
        assert RabbitMQConsumer is not None
        assert Worker is not None


class TestModelImports:
    """Test that ORM model imports work."""

    def test_model_imports(self) -> None:
        """Test importing SQLAlchemy models."""
        from shared.models import Document, User, ChatSession, ChatMessage

        assert Document is not None
        assert User is not None
        assert ChatSession is not None
        assert ChatMessage is not None


class TestRepositoryImports:
    """Test that repository imports work."""

    def test_repository_interfaces(self) -> None:
        """Test importing repository interfaces."""
        from shared.repositories import (
            DocumentRepository,
            UserRepository,
            ChatSessionRepository,
            ChatMessageRepository,
        )

        from abc import ABCMeta

        assert isinstance(DocumentRepository, ABCMeta)
        assert isinstance(UserRepository, ABCMeta)
