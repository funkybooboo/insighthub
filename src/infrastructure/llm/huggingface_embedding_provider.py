"""Hugging Face Embedding provider implementation."""

import os
from collections.abc import Iterable
from typing import Optional

import requests
from returns.result import Failure, Result, Success

from src.infrastructure.rag.steps.vector_rag.embedding.vector_embedder import (
    EmbeddingError,
    VectorEmbeddingEncoder,
)


class HuggingFaceEmbeddingProvider(VectorEmbeddingEncoder):
    """
    Hugging Face Embedding provider.

    Connects to Hugging Face's API to generate embeddings.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        api_url: Optional[str] = None,
    ) -> None:
        """
        Initialize Hugging Face Embedding provider.

        Args:
            api_key: Hugging Face API key (defaults to HUGGINGFACE_API_KEY env var)
            model_name: Name of the Hugging Face embedding model to use (default: "sentence-transformers/all-MiniLM-L6-v2")
            api_url: Optional custom API URL for the embedding endpoint.
        """
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY", "")
        self.model_name = model_name
        self.api_url = api_url or f"https://api-inference.huggingface.co/models/{model_name}"

    def encode(self, texts: Iterable[str]) -> Result[list[list[float]], EmbeddingError]:
        """
        Encode a list of texts into embeddings.

        Args:
            texts: An iterable of strings to encode.

        Returns:
            Result containing a list of lists of floats, where each inner list is an embedding for the corresponding text.
        """
        texts_list = list(texts)

        if not self.api_key:
            return Failure(
                EmbeddingError(
                    "Hugging Face API key not configured. Please set HUGGINGFACE_API_KEY in environment.",
                    "MISSING_API_KEY",
                )
            )

        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "inputs": texts_list,
                "options": {"wait_for_model": True},
            }  # wait_for_model can be slow

            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            embeddings = response.json()
            return Success(embeddings)

        except requests.exceptions.RequestException as e:
            return Failure(
                EmbeddingError(f"Error generating Hugging Face embeddings: {e}", "REQUEST_ERROR")
            )
        except Exception as e:
            return Failure(
                EmbeddingError(f"Error processing Hugging Face response: {e}", "PROCESSING_ERROR")
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

        This is a placeholder. A proper implementation would dynamically determine this.
        For 'sentence-transformers/all-MiniLM-L6-v2', it's typically 384.
        """
        return 384

    def get_model_name(self) -> str:
        """
        Get the name of the embedding model.

        Returns:
            Model name
        """
        return self.model_name
