"""LLM interface for text generation with streaming support."""

from abc import ABC, abstractmethod
from typing import Any, Generator

from shared.types.rag import RagConfig


class LLM(ABC):
    """
    Interface for large language model text generation.
    
    Implementations should support different LLM providers:
    - Ollama (local)
    - OpenAI (API)
    - Claude (API)
    - HuggingFace (local)
    """

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512, stop: list[str] | None = None, temperature: float = 0.7, rag_config: RagConfig | None = None) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: Input prompt for generation
            max_tokens: Maximum number of tokens to generate
            stop: Optional stop sequences
            temperature: Sampling temperature (0.0-1.0)
            rag_config: Optional RAG configuration

        Returns:
            str: Generated text

        Raises:
            LLMError: If generation fails
        """
        pass

    @abstractmethod
    def stream_generate(self, prompt: str, max_tokens: int = 512, stop: list[str] | None = None, temperature: float = 0.7, rag_config: RagConfig | None = None) -> Generator[str, None, None]:
        """
        Generate text with streaming output.

        Args:
            prompt: Input prompt for generation
            max_tokens: Maximum number of tokens to generate
            stop: Optional stop sequences
            temperature: Sampling temperature (0.0-1.0)
            rag_config: Optional RAG configuration

        Yields:
            str: Partial text chunks as they're generated

        Raises:
            LLMError: If generation fails
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the LLM model.

        Returns:
            str: Model name
        """
        pass

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        """
        Check if the LLM service is available.

        Returns:
            dict[str, Any]: Health status information
        """
        pass