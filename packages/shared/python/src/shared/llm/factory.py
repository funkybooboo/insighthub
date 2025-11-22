"""Factory for creating LLM provider instances."""

from typing import Any

from .llm_provider import LlmProvider
from .ollama_llm_provider import OllamaLlmProvider
from .openai_llm_provider import OpenAiLlmProvider
from .claude_llm_provider import ClaudeLlmProvider
from .huggingface_llm_provider import HuggingFaceLlmProvider


SUPPORTED_LLM_PROVIDERS = ["ollama", "openai", "claude", "huggingface"]


def create_llm_provider(
    provider_type: str,
    **kwargs: Any,
) -> LlmProvider:
    """
    Create an LLM provider instance.

    Args:
        provider_type: Type of provider (ollama, openai, claude, huggingface)
        **kwargs: Provider-specific configuration:
            - ollama: base_url, model_name
            - openai: api_key, model_name
            - claude: api_key, model_name
            - huggingface: api_key, model_name, api_url

    Returns:
        LlmProvider instance

    Raises:
        ValueError: If provider type is not recognized or required params missing

    Examples:
        >>> provider = create_llm_provider(
        ...     "ollama",
        ...     base_url="http://localhost:11434",
        ...     model_name="llama3.2"
        ... )

        >>> provider = create_llm_provider(
        ...     "openai",
        ...     api_key="sk-...",
        ...     model_name="gpt-4"
        ... )
    """
    if provider_type == "ollama":
        base_url = kwargs.get("base_url")
        model_name = kwargs.get("model_name")
        if not base_url or not model_name:
            raise ValueError("Ollama requires: base_url, model_name")
        return OllamaLlmProvider(base_url=base_url, model_name=model_name)

    elif provider_type == "openai":
        api_key = kwargs.get("api_key")
        model_name = kwargs.get("model_name")
        if not api_key or not model_name:
            raise ValueError("OpenAI requires: api_key, model_name")
        return OpenAiLlmProvider(api_key=api_key, model_name=model_name)

    elif provider_type == "claude":
        api_key = kwargs.get("api_key")
        model_name = kwargs.get("model_name")
        if not api_key or not model_name:
            raise ValueError("Claude requires: api_key, model_name")
        return ClaudeLlmProvider(api_key=api_key, model_name=model_name)

    elif provider_type == "huggingface":
        api_key = kwargs.get("api_key")
        model_name = kwargs.get("model_name")
        if not api_key or not model_name:
            raise ValueError("HuggingFace requires: api_key, model_name")
        return HuggingFaceLlmProvider(
            api_key=api_key,
            model_name=model_name,
            api_url=kwargs.get("api_url"),
        )

    else:
        raise ValueError(
            f"Unknown LLM provider type: {provider_type}. "
            f"Supported: {', '.join(SUPPORTED_LLM_PROVIDERS)}"
        )
