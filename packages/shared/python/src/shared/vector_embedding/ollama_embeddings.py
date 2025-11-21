"""Ollama embedding implementation."""

from typing import Iterable

from .encoder import EmbeddingEncoder


class OllamaEmbeddings(EmbeddingEncoder):
    """Generates embeddings using Ollama."""

    def __init__(self, model: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def encode(self, texts: Iterable[str]) -> list[list[float]]:
        """Batch encode texts."""
        # TODO: Implement actual API call to Ollama
        return [[0.1] * 768 for _ in texts]

    def encode_one(self, text: str) -> list[float]:
        """Encode a single text."""
        # TODO: Implement actual API call to Ollama
        return [0.1] * 768
