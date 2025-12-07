"""Ollama LLM provider implementation."""

import json
from collections.abc import Generator
from typing import Optional

import requests

from .llm_provider import LlmProvider


class OllamaLlmProvider(LlmProvider):
    """
    Ollama LLM provider.

    Connects to a local Ollama instance to generate text responses.

    Example:
        >>> provider = OllamaLlmProvider(
        ...     base_url="http://localhost:11434",
        ...     model_name="llama3.2"
        ... )
        >>> response = provider.generate_response("Hello, world!")
    """

    def __init__(self, base_url: str, model_name: str) -> None:
        """
        Initialize Ollama LLM provider.

        Args:
            base_url: Base URL for Ollama API (e.g., "http://localhost:11434")
            model_name: Name of the LLM model to use (e.g., "llama3.2")
        """
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from Ollama.

        Args:
            prompt: User's message/prompt

        Returns:
            Generated response text
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=60,
            )
            response.raise_for_status()

            result = response.json()
            answer_raw = result.get("response", "")
            answer: str = str(answer_raw).strip() if answer_raw else ""

            return answer

        except requests.exceptions.RequestException as e:
            return (
                f"I apologize, but I'm having trouble connecting to the AI model. Error: {str(e)}"
            )

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
        # Build prompt with conversation history
        if conversation_history:
            prompt_parts = []
            for msg in conversation_history[-10:]:  # Keep last 10 message for context
                role = msg.get("role", "users")
                content = msg.get("content", "")
                if role == "users":
                    prompt_parts.append(f"User: {content}")
                else:
                    prompt_parts.append(f"Assistant: {content}")
            prompt_parts.append(f"User: {message}")
            prompt_parts.append("Assistant:")
            prompt = "\n".join(prompt_parts)
        else:
            prompt = message

        return self.generate_response(prompt)

    def health_check(self) -> dict[str, str | bool]:
        """
        Check if Ollama service is available.

        Returns:
            Dictionary with health status
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            return {
                "status": "healthy",
                "provider": "ollama",
                "base_url": self.base_url,
                "model": self.model_name,
            }
        except requests.exceptions.RequestException:
            return {
                "status": "unhealthy",
                "provider": "ollama",
                "base_url": self.base_url,
                "model": self.model_name,
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
        # Build prompt with conversation history
        if conversation_history:
            prompt_parts = []
            for msg in conversation_history[-10:]:  # Keep last 10 message for context
                role = msg.get("role", "users")
                content = msg.get("content", "")
                if role == "users":
                    prompt_parts.append(f"User: {content}")
                else:
                    prompt_parts.append(f"Assistant: {content}")
            prompt_parts.append(f"User: {message}")
            prompt_parts.append("Assistant:")
            prompt = "\n".join(prompt_parts)
        else:
            prompt = message

        try:
            response = self._make_stream_request(prompt)
            yield from self._process_stream_response(response)
        except requests.exceptions.RequestException as e:
            yield f"I apologize, but I'm having trouble connecting to the AI model. Error: {str(e)}"

    def _make_stream_request(self, prompt: str):
        """Make streaming request to Ollama API."""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": True,
            },
            timeout=60,
            stream=True,
        )
        response.raise_for_status()
        return response

    def _process_stream_response(self, response):
        """Process streaming response from Ollama."""
        for line in response.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            if "response" in chunk:
                yield chunk["response"]
