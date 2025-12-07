"""OpenAI LLM provider implementation."""

from collections.abc import Generator
from typing import Optional

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from .llm_provider import LlmProvider


class OpenAiLlmProvider(LlmProvider):
    """
    OpenAI LLM provider.

    Connects to OpenAI's API to generate text responses.

    Example:
        >>> provider = OpenAiLlmProvider(
        ...     api_key="sk-...",
        ...     model_name="gpt-4"
        ... )
        >>> response = provider.generate_response("Hello, world!")
    """

    def __init__(self, api_key: str, model_name: str) -> None:
        """
        Initialize OpenAI LLM provider.

        Args:
            api_key: OpenAI API key
            model_name: Name of the OpenAI model to use (e.g., "gpt-4", "gpt-3.5-turbo")
        """
        self.api_key = api_key
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key)

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from OpenAI.

        Args:
            prompt: User's message/prompt

        Returns:
            Generated response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "users", "content": prompt}],
                temperature=0.7,
            )

            answer = response.choices[0].message.content
            return answer.strip() if answer else ""

        except Exception as e:
            return f"Error connecting to OpenAI: {str(e)}"

    def chat(
        self, message: str, conversation_history: Optional[list[dict[str, str]]] = None
    ) -> str:
        """
        Generate a chat response with optional conversation history.

        Args:
            message: Current users message
            conversation_history: Optional list of previous message

        Returns:
            Generated response text
        """
        try:
            messages = self._build_messages(message, conversation_history)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
            )

            answer = response.choices[0].message.content
            return answer.strip() if answer else ""

        except Exception as e:
            return f"Error connecting to OpenAI: {str(e)}"

    def health_check(self) -> dict[str, str | bool]:
        """
        Check if OpenAI service is available.

        Returns:
            Dictionary with health status
        """
        try:
            self.client.models.list()
            return {
                "status": "healthy",
                "provider": "openai",
                "model": self.model_name,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "openai",
                "error": str(e),
            }

    def get_model_name(self) -> str:
        """Get the name of the model being used."""
        return self.model_name

    def chat_stream(
        self, message: str, conversation_history: Optional[list[dict[str, str]]] = None
    ) -> Generator[str, None, None]:
        """
        Generate a streaming chat response with optional conversation history.

        Args:
            message: Current users message
            conversation_history: Optional list of previous message

        Yields:
            Chunks of generated response text
        """
        try:
            messages = self._build_messages(message, conversation_history)

            stream = self.client.chat.completions.create(
                model=self.model_name, messages=messages, temperature=0.7, stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"Error connecting to OpenAI: {str(e)}"

    def _build_messages(
        self, message: str, conversation_history: Optional[list[dict[str, str]]]
    ) -> list[ChatCompletionMessageParam]:
        """Build message array from conversation history and current message."""
        messages: list[ChatCompletionMessageParam] = []

        if conversation_history:
            for msg in conversation_history[-10:]:
                role_str = msg.get("role", "users")
                content_str = msg.get("content", "")
                message_dict = self._create_message_dict(role_str, content_str)
                if message_dict:
                    messages.append(message_dict)

        messages.append({"role": "users", "content": message})
        return messages

    def _create_message_dict(
        self, role_str: str, content_str: str
    ) -> Optional[ChatCompletionMessageParam]:
        """Create a properly typed message dict for the given role."""
        if role_str == "users":
            return {"role": "users", "content": content_str}
        elif role_str == "assistant":
            return {"role": "assistant", "content": content_str}
        elif role_str == "system":
            return {"role": "system", "content": content_str}
        return None
