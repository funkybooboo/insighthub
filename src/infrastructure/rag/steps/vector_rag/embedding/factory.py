"""Factory for creating embedding encoder instances."""

from enum import Enum

from .dummy_embedding_provider import DummyEmbeddingProvider
from .ollama_vector_embedder import OllamaVectorEmbeddingEncoder
from .vector_embedder import VectorEmbeddingEncoder


class EmbeddingEncoderType(Enum):
    """Enum for embedding encoder implementation types."""

    OLLAMA = "ollama"
    DUMMY = "dummy"


class EmbedderFactory:
    """Factory class for creating embedders."""

    @staticmethod
    def create_embedder(embedder_type: str, **kwargs) -> VectorEmbeddingEncoder:
        """Create an embedder instance. Alias for create_embedder_from_config.

        Args:
            embedder_type: Type of embedder to create
            **kwargs: Additional configuration (base_url, timeout)

        Returns:
            VectorEmbeddingEncoder instance
        """
        base_url = kwargs.get("base_url", "http://localhost:11434")
        timeout = kwargs.get("timeout", 30)
        return create_embedder_from_config(embedder_type, base_url, timeout)


AVAILABLE_EMBEDDERS = {
    "nomic-embed-text": {
        "label": "Nomic Embed Text",
        "description": "Nomic AI embedding model (274M params)",
    },
    "all-MiniLM-L6-v2": {
        "label": "MiniLM",
        "description": "Sentence-BERT embedding model",
    },
    "mxbai-embed-large": {
        "label": "MxBai Embed Large",
        "description": "Large multilingual embedding model",
    },
}


def get_available_embedders() -> list[dict[str, str]]:
    """Get list of available embedding algorithms."""
    return [
        {
            "value": key,
            "label": info["label"],
            "description": info["description"],
        }
        for key, info in AVAILABLE_EMBEDDERS.items()
    ]


def create_embedder_from_config(
    embedding_algorithm: str,
    base_url: str,
    timeout: int = 30,
) -> VectorEmbeddingEncoder:
    """
    Create an embedding encoder instance based on algorithm configuration.

    Args:
        embedding_algorithm: Algorithm/model type ("nomic-embed-text", "all-MiniLM-L6-v2", "dummy", etc.)
        base_url: Ollama server URL
        timeout: Request timeout in seconds (default 30)

    Returns:
        VectorEmbeddingEncoder instance
    """
    # Check if a dummy embedder is requested for testing
    if embedding_algorithm == "dummy":
        return DummyEmbeddingProvider(dimension=384)

    # All other embedding algorithms currently use Ollama infrastructure
    return OllamaVectorEmbeddingEncoder(
        model=embedding_algorithm,
        base_url=base_url,
        timeout=timeout,
    )
