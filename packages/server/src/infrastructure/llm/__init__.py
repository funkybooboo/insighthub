"""LLM provider implementations and factory."""

import importlib.util

from src.infrastructure.llm.factory import SUPPORTED_LLM_PROVIDERS, create_llm_provider
from src.infrastructure.llm.llm_provider import LlmProvider
from src.infrastructure.llm.ollama_llm_provider import OllamaLlmProvider

# Check availability of optional providers
_openai_available = importlib.util.find_spec("openai") is not None
_claude_available = importlib.util.find_spec("anthropic") is not None
_huggingface_available = importlib.util.find_spec("transformers") is not None

__all__ = [
    "LlmProvider",
    "OllamaLlmProvider",
    "create_llm_provider",
    "SUPPORTED_LLM_PROVIDERS",
]

# Optional imports for providers that may not be available
if _openai_available:
    from src.infrastructure.llm.openai_llm_provider import OpenAiLlmProvider  # noqa: F401
    __all__.append("OpenAiLlmProvider")

if _claude_available:
    from src.infrastructure.llm.claude_llm_provider import ClaudeLlmProvider  # noqa: F401
    __all__.append("ClaudeLlmProvider")

if _huggingface_available:
    from src.infrastructure.llm.huggingface_llm_provider import HuggingFaceLlmProvider  # noqa: F401
    __all__.append("HuggingFaceLlmProvider")
