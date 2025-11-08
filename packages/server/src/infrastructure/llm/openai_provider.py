"""OpenAI LLM provider implementation."""

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.config import OPENAI_API_KEY

from .llm import LlmProvider


class OpenAiLlmProvider(LlmProvider):
    """OpenAI LLM provider implementation."""

    def __init__(
        self,
        api_key: str = OPENAI_API_KEY,
        model_name: str = "gpt-3.5-turbo",
    ):
        """
        Initialize OpenAI LLM provider.

        Args:
            api_key: OpenAI API key
            model_name: Name of the OpenAI model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from OpenAI.

        Args:
            prompt: User's message/prompt

        Returns:
            Generated response text
        """
        if not self.client:
            return "OpenAI API key not configured. Please set OPENAI_API_KEY in environment."

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )

            answer = response.choices[0].message.content
            return answer.strip() if answer else ""

        except Exception as e:
            return f"Error connecting to OpenAI: {str(e)}"

    def chat(self, message: str, conversation_history: list[dict[str, str]] | None = None) -> str:
        """
        Generate a chat response with optional conversation history.

        Args:
            message: Current user message
            conversation_history: Optional list of previous messages

        Returns:
            Generated response text
        """
        if not self.client:
            return "OpenAI API key not configured. Please set OPENAI_API_KEY in environment."

        try:
            # Build messages array
            messages: list[ChatCompletionMessageParam] = []

            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages
                    role_str = msg.get("role", "user")
                    content_str = msg.get("content", "")
                    # OpenAI expects specific role types - create properly typed messages
                    if role_str == "user":
                        messages.append({"role": "user", "content": content_str})
                    elif role_str == "assistant":
                        messages.append({"role": "assistant", "content": content_str})
                    elif role_str == "system":
                        messages.append({"role": "system", "content": content_str})

            # Add current message
            messages.append({"role": "user", "content": message})

            # Call OpenAI
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
        if not self.client:
            return {
                "status": "unhealthy",
                "provider": "openai",
                "error": "API key not configured",
            }

        try:
            # Try to list models as a health check
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
