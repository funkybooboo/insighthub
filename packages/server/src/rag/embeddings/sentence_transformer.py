from src.rag.types import Vector
from src.rag.embeddings.base import EmbeddingModel


class SentenceTransformerEmbeddings(EmbeddingModel):
    """
    Sentence Transformers embeddings wrapper.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize Sentence Transformers model.

        Args:
            model_name: Name of the sentence-transformers model
        """
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)
        dim = self.model.get_sentence_embedding_dimension()
        assert dim is not None, "Failed to get embedding dimension"
        self._dimension: int = dim

    def embed(self, texts: str | list[str]) -> list[Vector]:
        """
        Generate embeddings using Sentence Transformers.

        Args:
            texts: Single text or list of texts

        Returns:
            List of embedding vectors
        """
        # Handle single string input
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(texts, convert_to_numpy=True)

        # Convert to list of lists
        return embeddings.tolist()  # type: ignore[no-any-return]

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension
