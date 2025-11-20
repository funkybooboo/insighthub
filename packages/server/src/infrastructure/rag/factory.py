"""
Factory for creating RAG instances with different configurations.
"""

from shared.types.rag import RagConfig

# from src.infrastructure.rag.rag import Rag # TODO: Deprecate local Rag interface in favor of shared orchestrators
# from src.infrastructure.rag.types import RagConfig # TODO: Deprecate local RagConfig


def create_rag(config: RagConfig | None = None):
    """
    Factory function to create RAG instances from configuration.

    DEPRECATED: This factory is being replaced by direct usage of shared.orchestrators.
    TODO: Update API to use VectorRAG and GraphRAG orchestrators directly.

    Args:
        config: Optional RagConfig dictionary. If not provided, defaults are used:
            - rag_type: "vector"
            - chunking_strategy: "sentence"
            - embedding_type: "ollama"
            - vector_store_type: "qdrant"
            - top_k: 8
            - workspace_id: "default"
            - embedding_model: "nomic-embed-text"
            - embedding_dim: 768
            - chunk_size: 1000
            - chunk_overlap: 200
            - retriever_type: "vector"
            - rerank_enabled: False
            - rerank_model: None

    Returns:
        Configured RAG instance.

    Raises:
        NotImplementedError: Migration to shared orchestrators in progress
    """
    # Define default configuration
    # TODO: Use pydantic model for defaults
    defaults = RagConfig(
        id=None,
        workspace_id="default",
        rag_type="vector",
        chunking_strategy="sentence",
        embedding_model="nomic-embed-text",
        embedding_dim=768,
        retriever_type="vector",
        chunk_size=1000,
        chunk_overlap=200,
        top_k=8,
        rerank_enabled=False,
        rerank_model=None,
        created_at=None,
        updated_at=None,
    )

    # TODO: Implement factory logic using shared.orchestrators.vector_rag.VectorRAG
    # TODO: Implement factory logic using shared.orchestrators.graph_rag.GraphRAG

    # For now, return None or raise NotImplementedError until we migrate the rest of the server
    raise NotImplementedError("Migration to shared orchestrators in progress")
