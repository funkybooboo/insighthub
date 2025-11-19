"""LLM interface for Vector RAG."""

from abc import ABC, abstractmethod
from collections.abc import Iterable


class LLM(ABC):
    """
    Interface for large language models.

    Supports both synchronous and streaming generation.
    """

    @abstractmethod
    def generate(
        self, prompt: str, max_tokens: int = 512, stop: list[str] | None = None
    ) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: Input text prompt
            max_tokens: Maximum number of tokens to generate
            stop: Optional list of stop sequences

        Returns:
            Generated text string
        """
        raise NotImplementedError

    @abstractmethod
    def stream_generate(
        self, prompt: str, max_tokens: int = 512, stop: list[str] | None = None
    ) -> Iterable[str]:
        """
        Stream generation output.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            stop: Optional stop sequences

        Yields:
            Partial text chunks as they are generated
        """
        raise NotImplementedError
