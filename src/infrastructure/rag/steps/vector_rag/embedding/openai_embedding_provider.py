"""OpenAI Embedding provider implementation."""

from collections.abc import Iterable

from openai import OpenAI
from returns.result import Failure, Result, Success

from src.infrastructure.rag.steps.vector_rag.embedding.vector_embedder import (
    EmbeddingError,
    VectorEmbeddingEncoder,
)


class OpenAIEmbeddingProvider(VectorEmbeddingEncoder):
    """
    OpenAI Embedding provider.

    Connects to OpenAI's API to generate embeddings.
    """

    def __init__(self, api_key: str, model_name: str = "text-embedding-ada-002") -> None:
        """
        Initialize OpenAI Embedding provider.

        Args:
            api_key: OpenAI API key
            model_name: Name of the OpenAI embedding model to use (default: "text-embedding-ada-002")
        """
        self.api_key = api_key
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key)

    def encode(self, texts: Iterable[str]) -> Result[list[list[float]], EmbeddingError]:
        """
        Encode a list of texts into embeddings.

        Args:
            texts: An iterable of strings to encode.

        Returns:
            Result containing a list of lists of floats, where each inner list is an embedding for the corresponding text.
        """
        texts_list = list(texts)

        try:
            response = self.client.embeddings.create(input=texts_list, model=self.model_name)
            embeddings = [data.embedding for data in response.data]
            return Success(embeddings)
        except Exception as e:
            return Failure(
                EmbeddingError(f"Error generating OpenAI embeddings: {e}", "OPENAI_API_ERROR")
            )

    def encode_one(self, text: str) -> Result[list[float], EmbeddingError]:
        """
        Encode a single text into a vector.

        Args:
            text: Text string to encode

        Returns:
            Result containing vector embedding, or EmbeddingError on failure
        """
        result = self.encode([text])
        return result.map(lambda embeddings: embeddings[0])

    def get_dimension(self) -> int:
        """
        Get the dimension of the embeddings produced by this provider.

        This is a placeholder. In a real implementation, you might query the model
        or have a fixed dimension for a given model.
        """
        # Common dimension for text-embedding-ada-002
        return 1536

    def get_model_name(self) -> str:
        """
        Get the name of the embedding model.

        Returns:
            Model name
        """
        return self.model_name
