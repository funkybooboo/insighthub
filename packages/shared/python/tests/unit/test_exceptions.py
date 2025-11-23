"""
Unit tests for domain exception classes.

These tests verify the exception classes correctly store input data
and produce expected output through message and status_code properties.
"""

import pytest

from shared.exceptions.base import (
    AlreadyExistsError,
    ConflictError,
    DomainException,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


class TestDomainException:
    """Test DomainException base class input/output."""

    def test_creation_with_message(self) -> None:
        """DomainException stores message."""
        exc = DomainException("Something went wrong")

        assert exc.message == "Something went wrong"
        assert str(exc) == "Something went wrong"

    def test_default_status_code(self) -> None:
        """DomainException has default status code 500."""
        exc = DomainException("Error")

        assert exc.status_code == 500

    def test_custom_status_code(self) -> None:
        """DomainException accepts custom status code."""
        exc = DomainException("Error", status_code=418)

        assert exc.status_code == 418

    def test_inheritance_from_exception(self) -> None:
        """DomainException inherits from Exception."""
        exc = DomainException("Error")

        assert isinstance(exc, Exception)

    def test_can_be_raised(self) -> None:
        """DomainException can be raised and caught."""
        with pytest.raises(DomainException) as exc_info:
            raise DomainException("Test error")

        assert exc_info.value.message == "Test error"
        assert exc_info.value.status_code == 500

    def test_can_be_caught_as_exception(self) -> None:
        """DomainException can be caught as generic Exception."""
        with pytest.raises(Exception):
            raise DomainException("Error")


class TestValidationError:
    """Test ValidationError input/output."""

    def test_creation_with_message(self) -> None:
        """ValidationError stores validation message."""
        exc = ValidationError("Invalid email format")

        assert exc.message == "Invalid email format"
        assert str(exc) == "Invalid email format"

    def test_status_code_is_400(self) -> None:
        """ValidationError has status code 400."""
        exc = ValidationError("Invalid input")

        assert exc.status_code == 400

    def test_inherits_from_domain_exception(self) -> None:
        """ValidationError inherits from DomainException."""
        exc = ValidationError("Error")

        assert isinstance(exc, DomainException)

    def test_can_be_raised(self) -> None:
        """ValidationError can be raised and caught."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Field 'name' is required")

        assert exc_info.value.message == "Field 'name' is required"
        assert exc_info.value.status_code == 400

    def test_can_be_caught_as_domain_exception(self) -> None:
        """ValidationError can be caught as DomainException."""
        with pytest.raises(DomainException):
            raise ValidationError("Error")


class TestNotFoundError:
    """Test NotFoundError input/output."""

    def test_creation_with_string_identifier(self) -> None:
        """NotFoundError stores resource type and string identifier."""
        exc = NotFoundError("Document", "doc-123")

        assert exc.resource_type == "Document"
        assert exc.identifier == "doc-123"
        assert exc.message == "Document with id 'doc-123' not found"

    def test_creation_with_int_identifier(self) -> None:
        """NotFoundError stores resource type and integer identifier."""
        exc = NotFoundError("User", 42)

        assert exc.resource_type == "User"
        assert exc.identifier == 42
        assert exc.message == "User with id '42' not found"

    def test_status_code_is_404(self) -> None:
        """NotFoundError has status code 404."""
        exc = NotFoundError("Resource", "id")

        assert exc.status_code == 404

    def test_message_format(self) -> None:
        """NotFoundError generates correct message format."""
        exc = NotFoundError("Workspace", "ws-abc")

        assert str(exc) == "Workspace with id 'ws-abc' not found"

    def test_inherits_from_domain_exception(self) -> None:
        """NotFoundError inherits from DomainException."""
        exc = NotFoundError("Resource", "id")

        assert isinstance(exc, DomainException)

    def test_can_be_raised(self) -> None:
        """NotFoundError can be raised and caught."""
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError("User", 999)

        assert exc_info.value.resource_type == "User"
        assert exc_info.value.identifier == 999
        assert exc_info.value.status_code == 404


class TestAlreadyExistsError:
    """Test AlreadyExistsError input/output."""

    def test_creation_with_string_identifier(self) -> None:
        """AlreadyExistsError stores resource type and string identifier."""
        exc = AlreadyExistsError("User", "john@example.com")

        assert exc.resource_type == "User"
        assert exc.identifier == "john@example.com"
        assert exc.message == "User with id 'john@example.com' already exists"

    def test_creation_with_int_identifier(self) -> None:
        """AlreadyExistsError stores resource type and integer identifier."""
        exc = AlreadyExistsError("Document", 123)

        assert exc.resource_type == "Document"
        assert exc.identifier == 123
        assert exc.message == "Document with id '123' already exists"

    def test_status_code_is_409(self) -> None:
        """AlreadyExistsError has status code 409."""
        exc = AlreadyExistsError("Resource", "id")

        assert exc.status_code == 409

    def test_message_format(self) -> None:
        """AlreadyExistsError generates correct message format."""
        exc = AlreadyExistsError("Workspace", "main")

        assert str(exc) == "Workspace with id 'main' already exists"

    def test_inherits_from_domain_exception(self) -> None:
        """AlreadyExistsError inherits from DomainException."""
        exc = AlreadyExistsError("Resource", "id")

        assert isinstance(exc, DomainException)

    def test_can_be_raised(self) -> None:
        """AlreadyExistsError can be raised and caught."""
        with pytest.raises(AlreadyExistsError) as exc_info:
            raise AlreadyExistsError("User", "existing_user")

        assert exc_info.value.resource_type == "User"
        assert exc_info.value.identifier == "existing_user"


class TestUnauthorizedError:
    """Test UnauthorizedError input/output."""

    def test_creation_with_default_message(self) -> None:
        """UnauthorizedError uses default message."""
        exc = UnauthorizedError()

        assert exc.message == "Authentication required"

    def test_creation_with_custom_message(self) -> None:
        """UnauthorizedError accepts custom message."""
        exc = UnauthorizedError("Invalid API key")

        assert exc.message == "Invalid API key"

    def test_status_code_is_401(self) -> None:
        """UnauthorizedError has status code 401."""
        exc = UnauthorizedError()

        assert exc.status_code == 401

    def test_inherits_from_domain_exception(self) -> None:
        """UnauthorizedError inherits from DomainException."""
        exc = UnauthorizedError()

        assert isinstance(exc, DomainException)

    def test_can_be_raised(self) -> None:
        """UnauthorizedError can be raised and caught."""
        with pytest.raises(UnauthorizedError) as exc_info:
            raise UnauthorizedError("Token expired")

        assert exc_info.value.message == "Token expired"
        assert exc_info.value.status_code == 401

    def test_str_output(self) -> None:
        """UnauthorizedError str() returns message."""
        exc = UnauthorizedError("Please log in")

        assert str(exc) == "Please log in"


class TestForbiddenError:
    """Test ForbiddenError input/output."""

    def test_creation_with_default_message(self) -> None:
        """ForbiddenError uses default message."""
        exc = ForbiddenError()

        assert exc.message == "Permission denied"

    def test_creation_with_custom_message(self) -> None:
        """ForbiddenError accepts custom message."""
        exc = ForbiddenError("Admin access required")

        assert exc.message == "Admin access required"

    def test_status_code_is_403(self) -> None:
        """ForbiddenError has status code 403."""
        exc = ForbiddenError()

        assert exc.status_code == 403

    def test_inherits_from_domain_exception(self) -> None:
        """ForbiddenError inherits from DomainException."""
        exc = ForbiddenError()

        assert isinstance(exc, DomainException)

    def test_can_be_raised(self) -> None:
        """ForbiddenError can be raised and caught."""
        with pytest.raises(ForbiddenError) as exc_info:
            raise ForbiddenError("You do not own this resource")

        assert exc_info.value.message == "You do not own this resource"
        assert exc_info.value.status_code == 403

    def test_str_output(self) -> None:
        """ForbiddenError str() returns message."""
        exc = ForbiddenError("Access denied")

        assert str(exc) == "Access denied"


class TestConflictError:
    """Test ConflictError input/output."""

    def test_creation_with_message(self) -> None:
        """ConflictError stores message."""
        exc = ConflictError("Resource is locked")

        assert exc.message == "Resource is locked"

    def test_status_code_is_409(self) -> None:
        """ConflictError has status code 409."""
        exc = ConflictError("Conflict")

        assert exc.status_code == 409

    def test_inherits_from_domain_exception(self) -> None:
        """ConflictError inherits from DomainException."""
        exc = ConflictError("Error")

        assert isinstance(exc, DomainException)

    def test_can_be_raised(self) -> None:
        """ConflictError can be raised and caught."""
        with pytest.raises(ConflictError) as exc_info:
            raise ConflictError("Document is being edited by another user")

        assert exc_info.value.message == "Document is being edited by another user"
        assert exc_info.value.status_code == 409

    def test_str_output(self) -> None:
        """ConflictError str() returns message."""
        exc = ConflictError("Version mismatch")

        assert str(exc) == "Version mismatch"


class TestExceptionHierarchy:
    """Test exception class hierarchy and catch behavior."""

    def test_all_exceptions_inherit_from_domain_exception(self) -> None:
        """All custom exceptions inherit from DomainException."""
        exceptions = [
            ValidationError("msg"),
            NotFoundError("Type", "id"),
            AlreadyExistsError("Type", "id"),
            UnauthorizedError(),
            ForbiddenError(),
            ConflictError("msg"),
        ]

        for exc in exceptions:
            assert isinstance(exc, DomainException)

    def test_catch_all_with_domain_exception(self) -> None:
        """All domain exceptions can be caught with DomainException."""

        def raise_validation() -> None:
            raise ValidationError("Error")

        def raise_not_found() -> None:
            raise NotFoundError("User", 1)

        def raise_already_exists() -> None:
            raise AlreadyExistsError("User", 1)

        def raise_unauthorized() -> None:
            raise UnauthorizedError()

        def raise_forbidden() -> None:
            raise ForbiddenError()

        def raise_conflict() -> None:
            raise ConflictError("Error")

        functions = [
            raise_validation,
            raise_not_found,
            raise_already_exists,
            raise_unauthorized,
            raise_forbidden,
            raise_conflict,
        ]

        for func in functions:
            with pytest.raises(DomainException):
                func()

    def test_status_codes_are_unique_per_error_type(self) -> None:
        """Each error type has its appropriate HTTP status code."""
        assert ValidationError("msg").status_code == 400
        assert UnauthorizedError().status_code == 401
        assert ForbiddenError().status_code == 403
        assert NotFoundError("T", "i").status_code == 404
        assert AlreadyExistsError("T", "i").status_code == 409
        assert ConflictError("msg").status_code == 409
        assert DomainException("msg").status_code == 500
