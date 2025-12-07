"""HuggingFace LLM provider implementation."""

import os
from collections.abc import Generator
from typing import Optional

import requests

from .llm_provider import LlmProvider


class HuggingFaceLlmProvider(LlmProvider):
    """HuggingFace LLM provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "meta-llama/Llama-3.2-3B-Instruct",
        api_url: Optional[str] = None,
    ):
        """
        Initialize Hugging Face LLM provider.

        Args:
            api_key: Hugging Face API key (defaults to HUGGINGFACE_API_KEY env var)
            model_name: Name of the Hugging Face model to use
            api_url: Optional custom API URL (for inference endpoints)
        """
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY", "")
        self.model_name = model_name
        self.api_url = api_url or f"https://api-inference.huggingface.co/models/{model_name}"

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from Hugging Face.

        Args:
            prompt: User's message/prompt

        Returns:
            Generated response text
        """
        if not self.api_key:
            return "Hugging Face API key not configured. Please set HUGGINGFACE_API_KEY in environment."

        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 512,
                    "temperature": 0.7,
                    "return_full_text": False,
                },
            }

            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()
            return self._parse_response(result)

        except requests.exceptions.RequestException as e:
            return f"Error connecting to Hugging Face: {str(e)}"
        except Exception as e:
            return f"Error processing Hugging Face response: {str(e)}"

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
            for msg in conversation_history[-10:]:  # Keep last 10 message
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
        Check if Hugging Face service is available.

        Returns:
            Dictionary with health status
        """
        if not self.api_key:
            return {
                "status": "unhealthy",
                "provider": "huggingface",
                "error": "API key not configured",
            }

        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(
                f"https://huggingface.co/api/models/{self.model_name}", headers=headers, timeout=5
            )
            response.raise_for_status()
            return {
                "status": "healthy",
                "provider": "huggingface",
                "model": self.model_name,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "huggingface",
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
        # HuggingFace doesn't support streaming in the same way
        # Fall back to returning the full response as a single chunk
        full_response = self.chat(message, conversation_history)
        yield full_response

    def _parse_response(self, result) -> str:
        """Parse HuggingFace API response and extract generated text."""
        list_response = self._try_parse_list_response(result)
        if list_response is not None:
            return list_response

        dict_response = self._try_parse_dict_response(result)
        if dict_response is not None:
            return dict_response

        return str(result)

    def _try_parse_list_response(self, result) -> Optional[str]:
        """Try to parse response as a list format."""
        if not isinstance(result, list) or len(result) == 0:
            return None

        if isinstance(result[0], dict) and "generated_text" in result[0]:
            text_raw = result[0]["generated_text"]
            return str(text_raw).strip() if text_raw else ""

        return None

    def _try_parse_dict_response(self, result) -> Optional[str]:
        """Try to parse response as a dict format."""
        if isinstance(result, dict) and "generated_text" in result:
            text_raw = result["generated_text"]
            return str(text_raw).strip() if text_raw else ""
        return None
