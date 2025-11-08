"""Hugging Face LLM provider implementation."""

import os

import requests

from .llm import LlmProvider


class HuggingFaceLlmProvider(LlmProvider):
    """Hugging Face LLM provider implementation."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "meta-llama/Llama-3.2-3B-Instruct",
        api_url: str | None = None,
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

            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and "generated_text" in result[0]:
                    return result[0]["generated_text"].strip()
            elif isinstance(result, dict) and "generated_text" in result:
                return result["generated_text"].strip()

            return str(result)

        except requests.exceptions.RequestException as e:
            return f"Error connecting to Hugging Face: {str(e)}"
        except Exception as e:
            return f"Error processing Hugging Face response: {str(e)}"

    def chat(self, message: str, conversation_history: list[dict[str, str]] | None = None) -> str:
        """
        Generate a chat response with optional conversation history.

        Args:
            message: Current user message
            conversation_history: Optional list of previous messages

        Returns:
            Generated response text
        """
        # Build prompt with conversation history
        if conversation_history:
            prompt_parts = []
            for msg in conversation_history[-10:]:  # Keep last 10 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
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
