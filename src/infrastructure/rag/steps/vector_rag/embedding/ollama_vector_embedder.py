"""Ollama vector embedding encoder implementation."""

from collections.abc import Iterable

import requests
from returns.result import Failure, Result, Success

from src.infrastructure.logger import create_logger
from src.infrastructure.types.common import HealthStatus

from .vector_embedder import EmbeddingError, VectorEmbeddingEncoder

logger = create_logger(__name__)


class OllamaVectorEmbeddingEncoder(VectorEmbeddingEncoder):
    """
    Generates embeddings using Ollama local LLM server.

    Connects to a local Ollama instance to generate text embeddings.
    Supports batch encoding for efficiency.

    Example:
        encoder = OllamaVectorEmbeddingEncoder(
            model="nomic-embed-text",
            base_url="http://localhost:11434"
        )
        result = encoder.encode(["Hello, world!", "Another text"])
        if result.is_ok():
            vectors = result.unwrap()
    """

    MODEL_DIMENSIONS: dict[str, int] = {
        "nomic-embed-text": 768,
        "mxbai-embed-large": 1024,
        "all-minilm": 384,
        "bge-base": 768,
        "bge-large": 1024,
    }

    def __init__(
        self,
        model: str,
        base_url: str,
        timeout: int,
    ) -> None:
        """
        Initialize Ollama embeddings.

        Args:
            model: Name of the embedding model (e.g., "nomic-embed-text")
            base_url: Ollama server URL
            timeout: Request timeout in seconds
        """
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._dimension: int | None = None

    def encode(self, texts: Iterable[str]) -> Result[list[list[float]], EmbeddingError]:
        """
        Batch encode multiple texts into vectors.

        Args:
            texts: Iterable of text strings to encode

        Returns:
            Result containing list of embedding vectors, or EmbeddingError on failure
        """
        texts_list = list(texts)
        if not texts_list:
            return Success([])

        embeddings: list[list[float]] = []

        for text in texts_list:
            result = self.encode_one(text)
            if isinstance(result, Failure):
                return Failure(result.failure())
            embeddings.append(result.unwrap())

        return Success(embeddings)

    def encode_one(self, text: str) -> Result[list[float], EmbeddingError]:
        """
        Encode a single text into a vector.

        Args:
            text: Text string to encode

        Returns:
            Result containing embedding vector, or EmbeddingError on failure
        """
        try:
            response = requests.post(
                f"{self._base_url}/api/embed",
                json={
                    "model": self._model,
                    "input": text,
                },
                timeout=self._timeout,
            )
            response.raise_for_status()

            result = response.json()
            # Ollama 0.13+ returns embeddings as array of arrays
            embeddings_list = result.get("embeddings", result.get("embedding", []))
            embedding: list[float] = (
                embeddings_list[0]
                if embeddings_list and isinstance(embeddings_list[0], list)
                else embeddings_list
            )

            if self._dimension is None and embedding:
                self._dimension = len(embedding)

            return Success(embedding)

        except requests.exceptions.ConnectionError as e:
            logger.error("Connection failed to Ollama", extra={"error": str(e)})
            return Failure(
                EmbeddingError(f"Connection failed to Ollama: {e}", code="CONNECTION_ERROR")
            )
        except requests.exceptions.Timeout as e:
            logger.error("Request timeout to Ollama", extra={"error": str(e)})
            return Failure(EmbeddingError(f"Request timeout: {e}", code="TIMEOUT_ERROR"))
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error from Ollama", extra={"error": str(e)})
            return Failure(EmbeddingError(f"HTTP error: {e}", code="HTTP_ERROR"))
        except requests.exceptions.RequestException as e:
            logger.error("Failed to get embedding from Ollama", extra={"error": str(e)})
            return Failure(EmbeddingError(f"Ollama embedding failed: {e}", code="REQUEST_ERROR"))

    def get_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.

        Returns:
            Vector dimension

        Note:
            If dimension is not yet known (no embeddings generated),
            returns the default dimension for the model or 768.
        """
        if self._dimension is not None:
            return self._dimension

        return self.MODEL_DIMENSIONS.get(self._model, 768)

    def get_model_name(self) -> str:
        """
        Get the name of the embedding model.

        Returns:
            Model name string
        """
        return self._model

    def health_check(self) -> HealthStatus:
        """
        Check if Ollama service is available.

        Returns:
            Dictionary with health status
        """
        try:
            response = requests.get(f"{self._base_url}/api/tags", timeout=5)
            response.raise_for_status()

            models_data = response.json().get("models", [])
            model_names = [m.get("name", "").split(":")[0] for m in models_data]
            model_available = self._model in model_names

            return {
                "status": "healthy",
                "provider": "ollama",
                "model_available": model_available,
            }
        except requests.exceptions.RequestException:
            return {
                "status": "unhealthy",
                "provider": "ollama",
                "model_available": False,
            }
