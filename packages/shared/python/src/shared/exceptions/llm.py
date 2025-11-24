"""Exceptions specific to the LLM module."""

from shared.exceptions.base import DomainException


class LlmException(DomainException):
    """Base exception for all LLM-related errors."""

    def __init__(self, message: str, status_code: int = 500):
        """Initialize LLM exception."""
        super().__init__(f"LLM Error: {message}", status_code)


class LlmProviderError(LlmException):
    """Raised when an LLM provider fails."""

    def __init__(self, provider: str, message: str):
        """Initialize LLM provider error."""
        super().__init__(f"{provider} provider failed: {message}", status_code=500)


class LlmGenerationError(LlmException):
    """Raised when text generation fails."""

    def __init__(self, message: str):
        """Initialize text generation error."""
        super().__init__(f"Text generation failed: {message}", status_code=500)
