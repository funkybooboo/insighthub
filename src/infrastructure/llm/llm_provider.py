"""LLM provider interface for text generation."""

from abc import ABC, abstractmethod
from collections.abc import Generator


class LlmProvider(ABC):
    """
    Abstract interface for LLM provider operations.

    Implementations: OllamaLlmProvider, OpenAiLlmProvider, ClaudeLlmProvider, HuggingFaceLlmProvider
    """

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: User's message/prompt

        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    def chat(self, message: str, conversation_history: list[dict[str, str]] | None = None) -> str:
        """
        Generate a chat response with optional conversation history.

        Args:
            message: Current users message
            conversation_history: Optional list of previous message
                                 Each message is {"role": "users"|"assistant", "content": "..."}

        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    def chat_stream(
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ) -> Generator[str, None, None]:
        """
        Generate a streaming chat response with optional conversation history.

        Args:
            message: Current users message
            conversation_history: Optional list of previous message
                                 Each message is {"role": "users"|"assistant", "content": "..."}

        Yields:
            Chunks of generated response text
        """
        pass

    @abstractmethod
    def health_check(self) -> dict[str, str | bool]:
        """
        Check if the LLM service is available.

        Returns:
            Dictionary with health status
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the model being used.

        Returns:
            Model name string
        """
        pass
