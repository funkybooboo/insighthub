from src.rag.types import Vector
from src.rag.embeddings.base import EmbeddingModel


class OpenAIEmbeddings(EmbeddingModel):
    """
    OpenAI embeddings wrapper.
    """

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embeddings.

        Args:
            api_key: OpenAI API key
            model: Model name (text-embedding-3-small, text-embedding-3-large, etc.)
        """
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model

        # Set dimension based on model
        self._dimension_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        self._dimension = self._dimension_map.get(model, 1536)

    def embed(self, texts: str | list[str]) -> list[Vector]:
        """
        Generate embeddings using OpenAI API.

        Args:
            texts: Single text or list of texts

        Returns:
            List of embedding vectors
        """
        # Handle single string input
        if isinstance(texts, str):
            texts = [texts]

        response = self.client.embeddings.create(model=self.model, input=texts)

        return [item.embedding for item in response.data]

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension
