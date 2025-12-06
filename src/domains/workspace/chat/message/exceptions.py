"""Chat message domain exceptions."""

from typing import Optional

from src.infrastructure.exceptions import DomainException, NotFoundError, ValidationError


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
        super().__init__("Message content cannot be empty")


class InvalidMessageRoleError(ValidationError):
    """Raised when an invalid message role is specified."""

    def __init__(self, role: str, valid_roles: list[str]):
        """
        Initialize invalid message role error.

        Args:
            role: The invalid role provided
            valid_roles: List of valid roles
        """
        valid_roles_str = ", ".join(valid_roles)
        message = f"Invalid message role '{role}'. Valid roles: {valid_roles_str}"
        super().__init__(message)
        self.role = role
        self.valid_roles = valid_roles


class LlmProviderError(DomainException):
    """Raised when an LLM provider operation fails."""

    def __init__(
        self, message: str, provider: Optional[str]= None, original_error: Optional[Exception]= None
    ):
        """
        Initialize LLM provider error.

        Args:
            message: The error message
            provider: The name of the LLM provider (e.g., "ollama", "openai")
            original_error: The original exception that caused this error
        """
        super().__init__(message, code="LLM_PROVIDER_ERROR")
        self.provider = provider
        self.original_error = original_error
