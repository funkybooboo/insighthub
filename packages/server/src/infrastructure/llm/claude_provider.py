"""Anthropic Claude LLM provider implementation."""

import os

from .llm import LlmProvider

try:
    from anthropic import Anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ClaudeLlmProvider(LlmProvider):
    """Anthropic Claude LLM provider implementation."""

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
        self.client = Anthropic(api_key=self.api_key) if ANTHROPIC_AVAILABLE and self.api_key else None

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
                return response.content[0].text.strip()
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
            messages = []

            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    messages.append({"role": role, "content": content})

            # Add current message
            messages.append({"role": "user", "content": message})

            # Call Claude
            response = self.client.messages.create(
                model=self.model_name, max_tokens=1024, messages=messages
            )

            # Extract text content from response
            if response.content and len(response.content) > 0:
                return response.content[0].text.strip()
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
