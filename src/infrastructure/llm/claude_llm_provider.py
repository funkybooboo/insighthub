"""Claude LLM provider implementation."""

import os
from typing import cast, Generator, Optional

from .llm_provider import LlmProvider

try:
    from anthropic import Anthropic
    from anthropic.types import MessageParam

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ClaudeLlmProvider(LlmProvider):
    """Claude (Anthropic) LLM provider."""

    def __init__(
        self,
        api_key: Optional[str]= None,
        model_name: str = "claude-3-5-sonnet-20241022",
    ):
        """
        Initialize Claude LLM provider.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model_name: Name of the Claude model to use
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model_name = model_name
        self.client = (
            Anthropic(api_key=self.api_key) if ANTHROPIC_AVAILABLE and self.api_key else None
        )

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from Claude.

        Args:
            prompt: User's message/prompt

        Returns:
            Generated response text
        """
        if not ANTHROPIC_AVAILABLE:
            return "Anthropic library not installed. Please run: pip install anthropic"

        if not self.client:
            return "Anthropic API key not configured. Please set ANTHROPIC_API_KEY in environment."

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=1024,
                messages=[{"role": "users", "content": prompt}],
            )

            # Extract text content from response
            if response.content and len(response.content) > 0:
                content_block = response.content[0]
                if hasattr(content_block, "text"):
                    text = str(content_block.text).strip()
                    return text
            return ""

        except Exception as e:
            return f"Error connecting to Claude: {str(e)}"

    def chat(self, message: str, conversation_history: Optional[list[dict[str, str]]] = None) -> str:
        """
        Generate a chat response with optional conversation history.

        Args:
            message: Current users message
            conversation_history: Optional list of previous message

        Returns:
            Generated response text
        """
        if not ANTHROPIC_AVAILABLE:
            return "Anthropic library not installed. Please run: pip install anthropic"

        if not self.client:
            return "Anthropic API key not configured. Please set ANTHROPIC_API_KEY in environment."

        try:
            messages = self._build_messages(message, conversation_history)
            response = self.client.messages.create(
                model=self.model_name, max_tokens=1024, messages=messages
            )
            return self._extract_text_from_response(response)

        except Exception as e:
            return f"Error connecting to Claude: {str(e)}"

    def _build_messages(
        self, message: str, conversation_history: Optional[list[dict[str, str]]]
    ) -> list[MessageParam]:
        """Build message array from history and current message."""
        messages: list[MessageParam] = []

        if conversation_history:
            for msg in conversation_history[-10:]:
                role_str = msg.get("role", "users")
                content_str = msg.get("content", "")
                if role_str in ("users", "assistant"):
                    messages.append(
                        cast(MessageParam, {"role": role_str, "content": content_str})
                    )

        messages.append(cast(MessageParam, {"role": "users", "content": message}))
        return messages

    def _extract_text_from_response(self, response) -> str:
        """Extract text content from Claude response."""
        if not response.content or len(response.content) == 0:
            return ""

        content_block = response.content[0]
        if not hasattr(content_block, "text"):
            return ""

        return str(content_block.text).strip()

    def health_check(self) -> dict[str, str | bool]:
        """
        Check if Claude service is available.

        Returns:
            Dictionary with health status
        """
        if not ANTHROPIC_AVAILABLE:
            return {
                "status": "unhealthy",
                "provider": "claude",
                "error": "Anthropic library not installed",
            }

        if not self.client:
            return {
                "status": "unhealthy",
                "provider": "claude",
                "error": "API key not configured",
            }

        try:
            # Try a minimal request as health check
            self.client.messages.create(
                model=self.model_name,
                max_tokens=10,
                messages=[{"role": "users", "content": "Hi"}],
            )
            return {
                "status": "healthy",
                "provider": "claude",
                "model": self.model_name,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "claude",
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
        if not ANTHROPIC_AVAILABLE:
            yield "Anthropic library not installed. Please run: pip install anthropic"
            return

        if not self.client:
            yield "Anthropic API key not configured. Please set ANTHROPIC_API_KEY in environment."
            return

        try:
            messages = self._build_messages(message, conversation_history)
            with self.client.messages.stream(
                model=self.model_name, max_tokens=1024, messages=messages
            ) as stream:
                yield from stream.text_stream

        except Exception as e:
            yield f"Error connecting to Claude: {str(e)}"
