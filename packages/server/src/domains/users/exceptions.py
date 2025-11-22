"""User domain exceptions."""

from shared.exceptions import AlreadyExistsError, NotFoundError, ValidationError


class UserNotFoundError(NotFoundError):
    """Raised when a user is not found."""

    def __init__(self, identifier: str | int):
        """
        Initialize user not found error.

        Args:
            identifier: The user ID, username, or email that was not found
        """
        super().__init__("User", identifier)


class UserAlreadyExistsError(AlreadyExistsError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, identifier: str):
        """
        Initialize user already exists error.

        Args:
            identifier: The username or email that already exists
        """
        super().__init__("User", identifier)


class InvalidEmailError(ValidationError):
    """Raised when an invalid email address is provided."""

    def __init__(self, email: str):
        """
        Initialize invalid email error.

        Args:
            email: The invalid email address
        """
        super().__init__(f"Invalid email address: {email}")
        self.email = email


class InvalidUsernameError(ValidationError):
    """Raised when an invalid username is provided."""

    def __init__(self, username: str, reason: str):
        """
        Initialize invalid username error.

        Args:
            username: The invalid username
            reason: Reason for invalidity
        """
        super().__init__(f"Invalid username '{username}': {reason}")
        self.username = username
        self.reason = reason


class UserAuthenticationError(ValidationError):
    """Raised when user authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        """
        Initialize user authentication error.

        Args:
            message: The error message
        """
        super().__init__(message)
