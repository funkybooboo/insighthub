"""Chat session domain exceptions."""

from src.infrastructure.exceptions import NotFoundError, ValidationError


class ChatSessionNotFoundError(NotFoundError):
    """Raised when a chat session is not found."""

    def __init__(self, session_id: int):
        """
        Initialize chat session not found error.

        Args:
            session_id: The session ID that was not found
        """
        super().__init__("ChatSession", session_id)


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
