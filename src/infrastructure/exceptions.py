"""Base exceptions for the application."""


class ApplicationError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, code: str = "APPLICATION_ERROR") -> None:
        """Initialize error."""
        self.message = message
        self.code = code
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation."""
        return f"[{self.code}] {self.message}"


class NotFoundError(ApplicationError):
    """Raised when a resource is not found."""

    def __init__(self, resource_type: str, identifier: str | int) -> None:
        """
        Initialize not found error.

        Args:
            resource_type: Type of resource that was not found
            identifier: The identifier that was not found
        """
        message = f"{resource_type} not found: {identifier}"
        super().__init__(message, code="NOT_FOUND")
        self.resource_type = resource_type
        self.identifier = identifier


class AlreadyExistsError(ApplicationError):
    """Raised when attempting to create a resource that already exists."""

    def __init__(self, resource_type: str, identifier: str | int) -> None:
        """
        Initialize already exists error.

        Args:
            resource_type: Type of resource that already exists
            identifier: The identifier that already exists
        """
        message = f"{resource_type} already exists: {identifier}"
        super().__init__(message, code="ALREADY_EXISTS")
        self.resource_type = resource_type
        self.identifier = identifier


class ValidationError(ApplicationError):
    """Raised when validation fails."""

    def __init__(self, message: str) -> None:
        """
        Initialize validation error.

        Args:
            message: The validation error message
        """
        super().__init__(message, code="VALIDATION_ERROR")


class DomainException(ApplicationError):
    """Base exception for domain-specific errors."""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR") -> None:
        """
        Initialize domain exception.

        Args:
            message: The error message
            code: The error code
        """
        super().__init__(message, code=code)
