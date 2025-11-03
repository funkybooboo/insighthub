from src.rag.types import Vector
from src.rag.embeddings.base import EmbeddingModel


class DummyEmbeddings(EmbeddingModel):
    """
    Dummy embeddings for testing (generates random embeddings).
    """

    def __init__(self, dimension: int = 384):
        """
        Initialize dummy embeddings.

        Args:
            dimension: Embedding dimension
        """
        import numpy as np

        self.dimension = dimension
        self.np = np

    def embed(self, texts: str | list[str]) -> list[Vector]:
        """
        Generate random embeddings.

        Args:
            texts: Single text or list of texts

        Returns:
            List of random embedding vectors
        """
        if isinstance(texts, str):
            texts = [texts]

        # Generate random embeddings and normalize them
        embeddings = []
        for _ in texts:
            vec = self.np.random.randn(self.dimension).astype("float32")
            # Normalize
            vec = vec / self.np.linalg.norm(vec)
            embeddings.append(vec.tolist())

        return embeddings

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension
