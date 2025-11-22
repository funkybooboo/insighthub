"""Factory for creating LLM provider instances using server configuration."""

from shared.llm import LlmProvider
from shared.llm import create_llm_provider as shared_create_llm_provider

from src import config


def create_llm_provider() -> LlmProvider:
    """
    Create an LLM provider instance based on server configuration.

    Uses the LLM_PROVIDER environment variable to determine which provider to use.
    Supported providers: ollama, openai

    Returns:
        LlmProvider instance configured based on environment variables
    """
    provider_type = config.LLM_PROVIDER

    if provider_type == "ollama":
        return shared_create_llm_provider(
            provider_type="ollama",
            base_url=config.OLLAMA_BASE_URL,
            model_name=config.OLLAMA_LLM_MODEL,
        )
    elif provider_type == "openai":
        return shared_create_llm_provider(
            provider_type="openai",
            api_key=config.OPENAI_API_KEY,
            model_name=config.OPENAI_MODEL,
        )
    else:
        # Default to ollama
        return shared_create_llm_provider(
            provider_type="ollama",
            base_url=config.OLLAMA_BASE_URL,
            model_name=config.OLLAMA_LLM_MODEL,
        )
