"""Factory for creating LLM provider instances."""

from src.config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    HUGGINGFACE_API_KEY,
    HUGGINGFACE_MODEL,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_LLM_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

from .claude_provider import ClaudeLlmProvider
from .huggingface_provider import HuggingFaceLlmProvider
from .llm import LlmProvider
from .ollama import OllamaLlmProvider
from .openai_provider import OpenAiLlmProvider


def create_llm_provider(
    provider_name: str | None = None,
    **kwargs: str,
) -> LlmProvider:
    """
    Create an LLM provider instance based on configuration.

    Args:
        provider_name: Name of the provider to use (ollama, openai, claude, huggingface)
                      If None, uses LLM_PROVIDER from config
        **kwargs: Additional provider-specific configuration

    Returns:
        LlmProvider instance

    Raises:
        ValueError: If provider name is not recognized
    """
    provider = provider_name or LLM_PROVIDER

    if provider == "ollama":
        return OllamaLlmProvider(
            base_url=kwargs.get("base_url", OLLAMA_BASE_URL),
            model_name=kwargs.get("model_name", OLLAMA_LLM_MODEL),
        )

    elif provider == "openai":
        return OpenAiLlmProvider(
            api_key=kwargs.get("api_key", OPENAI_API_KEY),
            model_name=kwargs.get("model_name", OPENAI_MODEL),
        )

    elif provider == "claude":
        return ClaudeLlmProvider(
            api_key=kwargs.get("api_key", ANTHROPIC_API_KEY),
            model_name=kwargs.get("model_name", ANTHROPIC_MODEL),
        )

    elif provider == "huggingface":
        return HuggingFaceLlmProvider(
            api_key=kwargs.get("api_key", HUGGINGFACE_API_KEY),
            model_name=kwargs.get("model_name", HUGGINGFACE_MODEL),
            api_url=kwargs.get("api_url"),
        )

    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. "
            f"Supported providers: ollama, openai, claude, huggingface"
        )


def get_available_providers() -> dict[str, dict[str, str | bool]]:
    """
    Get health status of all available LLM providers.

    Returns:
        Dictionary mapping provider names to their health check results
    """
    providers = {
        "ollama": create_llm_provider("ollama"),
        "openai": create_llm_provider("openai"),
        "claude": create_llm_provider("claude"),
        "huggingface": create_llm_provider("huggingface"),
    }

    health_status = {}
    for name, provider in providers.items():
        try:
            health_status[name] = provider.health_check()
        except Exception as e:
            health_status[name] = {
                "status": "error",
                "provider": name,
                "error": str(e),
            }

    return health_status
