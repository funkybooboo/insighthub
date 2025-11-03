from src.rag.types import Vector
from src.rag.embeddings.base import EmbeddingModel


class OllamaEmbeddings(EmbeddingModel):
    """
    Ollama embeddings wrapper for local embedding models.
    """

    def __init__(self, model: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama embeddings.

        Args:
            model: Ollama model name (e.g., 'nomic-embed-text', 'mxbai-embed-large')
            base_url: Base URL for Ollama API
        """
        import requests

        self.model = model
        self.base_url = base_url.rstrip("/")
        self.requests = requests

        # Common Ollama embedding model dimensions
        self._dimension_map = {
            "nomic-embed-text": 768,
            "mxbai-embed-large": 1024,
            "all-minilm": 384,
        }
        self._dimension = self._dimension_map.get(model, 768)

    def embed(self, texts: str | list[str]) -> list[Vector]:
        """
        Generate embeddings using Ollama.

        Args:
            texts: Single text or list of texts

        Returns:
            List of embedding vectors
        """
        # Handle single string input
        if isinstance(texts, str):
            texts = [texts]

        embeddings = []
        for text in texts:
            response = self.requests.post(
                f"{self.base_url}/api/embeddings", json={"model": self.model, "prompt": text}
            )
            response.raise_for_status()
            embedding = response.json()["embedding"]
            embeddings.append(embedding)

            # Update dimension from actual response if needed
            if self._dimension != len(embedding):
                self._dimension = len(embedding)

        return embeddings

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension
