"""Chat message domain exceptions."""

from src.infrastructure.exceptions import NotFoundError, ValidationError


class ChatMessageNotFoundError(NotFoundError):
    """Raised when a chats message is not found."""

    def __init__(self, message_id: int):
        """
        Initialize chats message not found error.

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
