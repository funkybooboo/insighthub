"""Claude LLM provider implementation."""

import os
from collections.abc import Generator
from typing import cast

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
        api_key: str | None = None,
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
                messages=[{"role": "user", "content": prompt}],
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

    def chat(self, message: str, conversation_history: list[dict[str, str]] | None = None) -> str:
        """
        Generate a chat response with optional conversation history.

        Args:
            message: Current user message
            conversation_history: Optional list of previous messages

        Returns:
            Generated response text
        """
        if not ANTHROPIC_AVAILABLE:
            return "Anthropic library not installed. Please run: pip install anthropic"

        if not self.client:
            return "Anthropic API key not configured. Please set ANTHROPIC_API_KEY in environment."

        try:
            # Build messages array
            messages: list[MessageParam] = []

            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages
                    role_str = msg.get("role", "user")
                    content_str = msg.get("content", "")
                    if role_str in ("user", "assistant"):
                        messages.append(
                            cast(MessageParam, {"role": role_str, "content": content_str})
                        )

            # Add current message
            messages.append(cast(MessageParam, {"role": "user", "content": message}))

            # Call Claude
            response = self.client.messages.create(
                model=self.model_name, max_tokens=1024, messages=messages
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
                messages=[{"role": "user", "content": "Hi"}],
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
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ) -> Generator[str, None, None]:
        """
        Generate a streaming chat response with optional conversation history.

        Args:
            message: Current user message
            conversation_history: Optional list of previous messages

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
            # Build messages array
            messages: list[MessageParam] = []

            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:
                    role_str = msg.get("role", "user")
                    content_str = msg.get("content", "")
                    if role_str in ("user", "assistant"):
                        messages.append(
                            cast(MessageParam, {"role": role_str, "content": content_str})
                        )

            # Add current message
            messages.append(cast(MessageParam, {"role": "user", "content": message}))

            # Call Claude with streaming
            with self.client.messages.stream(
                model=self.model_name, max_tokens=1024, messages=messages
            ) as stream:
                yield from stream.text_stream

        except Exception as e:
            yield f"Error connecting to Claude: {str(e)}"
