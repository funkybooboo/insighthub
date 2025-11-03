"""
Factory for creating RAG systems with different configurations

This module provides a convenient way to create RAG systems by specifying
algorithms, chunking strategies, embeddings, and storage backends.
"""

from src.rag.algorithms.vector_rag import VectorRAG
from src.rag.base import BaseRAG, RAGType
from src.rag.chunking import get_chunker
from src.rag.embeddings import EmbeddingModel, OllamaEmbeddings
from src.rag.stores.vector import QdrantVectorStore, VectorStore


def create_rag(
    rag_type: str | RAGType = RAGType.VECTOR,
    # Chunking configuration
    chunking_strategy: str = "sentence",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    # Embedding configuration
    embedding_model: EmbeddingModel | None = None,
    embedding_type: str = "ollama",
    embedding_model_name: str = "nomic-embed-text",
    embedding_base_url: str = "http://localhost:11434",
    # Vector store configuration
    vector_store: VectorStore | None = None,
    vector_store_type: str = "qdrant",
    vector_store_host: str = "localhost",
    vector_store_port: int = 6333,
    vector_store_collection: str = "rag_collection",
) -> BaseRAG:
    """
    Factory function to create a RAG system with specified configuration.

    Args:
        rag_type: Type of RAG system ("vector" or "graph")

        chunking_strategy: Chunking strategy ("character", "sentence", "word")
        chunk_size: Size of chunks
        chunk_overlap: Overlap between chunks

        embedding_model: Pre-configured embedding model (overrides embedding_type)
        embedding_type: Type of embedding ("ollama", "openai", "sentence_transformer")
        embedding_model_name: Name of the embedding model
        embedding_base_url: Base URL for embedding service (Ollama)

        vector_store: Pre-configured vector store (overrides vector_store_type)
        vector_store_type: Type of vector store ("qdrant", "pinecone")
        vector_store_host: Vector store host
        vector_store_port: Vector store port
        vector_store_collection: Collection/index name

    Returns:
        Configured RAG system

    Examples:
        >>> # Create with defaults (sentence chunking, Ollama embeddings, Qdrant)
        >>> rag = create_rag()

        >>> # Create with custom chunking
        >>> rag = create_rag(chunking_strategy="word", chunk_size=200)

        >>> # Create with OpenAI embeddings
        >>> rag = create_rag(
        ...     embedding_type="openai",
        ...     embedding_model_name="text-embedding-3-small"
        ... )
    """
    # Convert string to enum if needed
    if isinstance(rag_type, str):
        rag_type = RAGType(rag_type.lower())

    # Create chunker
    chunker = get_chunker(
        strategy=chunking_strategy, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    # Create or use provided embedding model
    if embedding_model is None:
        if embedding_type == "ollama":
            from src.rag.embeddings import OllamaEmbeddings

            embedding_model = OllamaEmbeddings(
                model=embedding_model_name, base_url=embedding_base_url
            )
        elif embedding_type == "openai":
            import os

            from src.rag.embeddings import OpenAIEmbeddings

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY environment variable required for OpenAI embeddings"
                )
            embedding_model = OpenAIEmbeddings(api_key=api_key, model=embedding_model_name)
        elif embedding_type == "sentence_transformer":
            from src.rag.embeddings import SentenceTransformerEmbeddings

            embedding_model = SentenceTransformerEmbeddings(model_name=embedding_model_name)
        else:
            raise ValueError(
                f"Invalid embedding_type: {embedding_type}. "
                f"Valid options: ollama, openai, sentence_transformer"
            )

    # Create RAG system based on type
    if rag_type == RAGType.VECTOR:
        # Create or use provided vector store
        if vector_store is None:
            if vector_store_type == "qdrant":
                vector_store = QdrantVectorStore(
                    host=vector_store_host,
                    port=vector_store_port,
                    collection_name=vector_store_collection,
                    dimension=embedding_model.get_dimension(),
                    metric="cosine",
                )
            elif vector_store_type == "pinecone":
                import os

                from src.rag.stores.vector import PineconeVectorStore

                api_key = os.getenv("PINECONE_API_KEY")
                if not api_key:
                    raise ValueError(
                        "PINECONE_API_KEY environment variable required for Pinecone"
                    )
                vector_store = PineconeVectorStore(
                    api_key=api_key,
                    index_name=vector_store_collection,
                    dimension=embedding_model.get_dimension(),
                    metric="cosine",
                )
            else:
                raise ValueError(
                    f"Invalid vector_store_type: {vector_store_type}. "
                    f"Valid options: qdrant, pinecone"
                )

        return VectorRAG(
            vector_store=vector_store, embedding_model=embedding_model, chunker=chunker
        )

    elif rag_type == RAGType.GRAPH:
        raise NotImplementedError("Graph RAG not yet implemented. Use RAGType.VECTOR instead.")

    else:
        raise ValueError(f"Invalid rag_type: {rag_type}. Valid options: vector, graph")


def create_vector_rag(
    chunking_strategy: str = "sentence",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    embedding_type: str = "ollama",
    vector_store_type: str = "qdrant",
    **kwargs,
) -> VectorRAG:
    """
    Convenience function to create a Vector RAG system.

    Args:
        chunking_strategy: Chunking strategy
        chunk_size: Size of chunks
        chunk_overlap: Overlap between chunks
        embedding_type: Embedding model type
        vector_store_type: Vector store type
        **kwargs: Additional arguments passed to create_rag

    Returns:
        Configured Vector RAG system
    """
    rag = create_rag(
        rag_type=RAGType.VECTOR,
        chunking_strategy=chunking_strategy,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        embedding_type=embedding_type,
        vector_store_type=vector_store_type,
        **kwargs,
    )
    return rag  # type: ignore[return-value]
