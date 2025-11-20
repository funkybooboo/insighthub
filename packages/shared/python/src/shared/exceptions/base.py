"""Base exception classes for domain-driven error handling."""


class DomainException(Exception):
    """
    Base exception for all domain-specific errors.

    All domain exceptions should inherit from this class to enable
    centralized error handling and HTTP status code mapping.
    """

    def __init__(self, message: str, status_code: int = 500):
        """
        Initialize domain exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code to return
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(DomainException):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        """
        Initialize validation error.

        Args:
            message: Description of validation failure
        """
        super().__init__(message, status_code=400)


class NotFoundError(DomainException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, identifier: str | int):
        """
        Initialize not found error.

        Args:
            resource_type: Type of resource (e.g., "Document", "User")
            identifier: Resource identifier
        """
        message = f"{resource_type} with id '{identifier}' not found"
        super().__init__(message, status_code=404)
        self.resource_type = resource_type
        self.identifier = identifier


class AlreadyExistsError(DomainException):
    """Raised when attempting to create a resource that already exists."""

    def __init__(self, resource_type: str, identifier: str | int):
        """
        Initialize already exists error.

        Args:
            resource_type: Type of resource (e.g., "Document", "User")
            identifier: Resource identifier
        """
        message = f"{resource_type} with id '{identifier}' already exists"
        super().__init__(message, status_code=409)
        self.resource_type = resource_type
        self.identifier = identifier


class UnauthorizedError(DomainException):
    """Raised when user lacks authentication."""

    def __init__(self, message: str = "Authentication required"):
        """
        Initialize unauthorized error.

        Args:
            message: Description of authentication requirement
        """
        super().__init__(message, status_code=401)


class ForbiddenError(DomainException):
    """Raised when user lacks permission for an action."""

    def __init__(self, message: str = "Permission denied"):
        """
        Initialize forbidden error.

        Args:
            message: Description of permission requirement
        """
        super().__init__(message, status_code=403)


class ConflictError(DomainException):
    """Raised when operation conflicts with current state."""

    def __init__(self, message: str):
        """
        Initialize conflict error.

        Args:
            message: Description of conflict
        """
        super().__init__(message, status_code=409)
