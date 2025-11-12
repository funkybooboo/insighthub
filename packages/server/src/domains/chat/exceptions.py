"""Chat domain exceptions."""

from src.infrastructure.errors.base import DomainException, NotFoundError, ValidationError


class ChatSessionNotFoundError(NotFoundError):
    """Raised when a chat session is not found."""

    def __init__(self, session_id: int):
        """
        Initialize chat session not found error.

        Args:
            session_id: The session ID that was not found
        """
        super().__init__("ChatSession", session_id)


class ChatMessageNotFoundError(NotFoundError):
    """Raised when a chat message is not found."""

    def __init__(self, message_id: int):
        """
        Initialize chat message not found error.

        Args:
            message_id: The message ID that was not found
        """
        super().__init__("ChatMessage", message_id)


class EmptyMessageError(ValidationError):
    """Raised when an empty message is provided."""

    def __init__(self) -> None:
        """Initialize empty message error."""
        super().__init__("Message cannot be empty")


class InvalidRagTypeError(ValidationError):
    """Raised when an invalid RAG type is specified."""

    def __init__(self, rag_type: str, valid_types: list[str]):
        """
        Initialize invalid RAG type error.

        Args:
            rag_type: The invalid RAG type provided
            valid_types: List of valid RAG types
        """
        valid_types_str = ", ".join(valid_types)
        message = f"Invalid RAG type '{rag_type}'. Valid types: {valid_types_str}"
        super().__init__(message)
        self.rag_type = rag_type
        self.valid_types = valid_types


class LlmProviderError(DomainException):
    """Raised when LLM provider fails."""

    def __init__(self, provider_name: str, reason: str):
        """
        Initialize LLM provider error.

        Args:
            provider_name: Name of the LLM provider
            reason: Reason for failure
        """
        message = f"LLM provider '{provider_name}' failed: {reason}"
        super().__init__(message, status_code=503)
        self.provider_name = provider_name
        self.reason = reason
