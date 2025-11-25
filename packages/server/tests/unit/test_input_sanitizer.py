"""Unit tests for InputSanitizer security utilities."""

import pytest

from src.infrastructure.security.input_sanitizer import InputSanitizer


class TestInputSanitizer:
    """Tests for input sanitization and validation."""

    def test_sanitize_text_basic(self) -> None:
        """Test basic text sanitization."""
        result = InputSanitizer.sanitize_text("Hello World")
        assert result == "Hello World"

    def test_sanitize_text_null_bytes(self) -> None:
        """Test removal of null bytes."""
        result = InputSanizer.sanitize_text("Hello\x00World")
        assert result == "HelloWorld"

    def test_sanitize_text_control_characters(self) -> None:
        """Test removal of control characters."""
        result = InputSanitizer.sanitize_text("Hello\x01\x02World")
        assert result == "HelloWorld"

    def test_sanitize_text_script_tags(self) -> None:
        """Test removal of script tags."""
        result = InputSanitizer.sanitize_text("Hello <script>alert('xss')</script> World")
        assert "<script>" not in result
        assert "alert" not in result

    def test_sanitize_text_iframe_tags(self) -> None:
        """Test removal of iframe tags."""
        result = InputSanitizer.sanitize_text("Hello <iframe src='evil.com'></iframe> World")
        assert "<iframe>" not in result
        assert "evil.com" not in result

    def test_sanitize_text_event_handlers(self) -> None:
        """Test removal of event handlers."""
        result = InputSanitizer.sanitize_text("Hello <div onclick='evil()'>Click me</div> World")
        assert "onclick" not in result
        assert "evil()" not in result

    def test_sanitize_text_max_length(self) -> None:
        """Test max length enforcement."""
        long_text = "A" * 1000
        result = InputSanitizer.sanitize_text(long_text, max_length=100)
        assert len(result) == 100
        assert result == "A" * 100

    def test_sanitize_text_whitespace(self) -> None:
        """Test whitespace trimming."""
        result = InputSanitizer.sanitize_text("  Hello World  ")
        assert result == "Hello World"

    def test_sanitize_text_empty(self) -> None:
        """Test empty input handling."""
        result = InputSanitizer.sanitize_text("")
        assert result == ""

        result = InputSanitizer.sanitize_text(None)
        assert result == ""

    def test_validate_email_valid(self) -> None:
        """Test valid email validation."""
        assert InputSanitizer.validate_email("user@example.com") is True
        assert InputSanitizer.validate_email("test.email+tag@domain.co.uk") is True
        assert InputSanitizer.validate_email("user@localhost") is True

    def test_validate_email_invalid(self) -> None:
        """Test invalid email validation."""
        assert InputSanitizer.validate_email("") is False
        assert InputSanitizer.validate_email("invalid") is False
        assert InputSanitizer.validate_email("user@") is False
        assert InputSanitizer.validate_email("@domain.com") is False
        assert InputSanitizer.validate_email("user@domain") is False
        assert InputSanitizer.validate_email("a" * 255 + "@example.com") is False  # Too long

    def test_validate_username_valid(self) -> None:
        """Test valid username validation."""
        assert InputSanitizer.validate_username("user123") is True
        assert InputSanitizer.validate_username("test_user") is True
        assert InputSanitizer.validate_username("user-name") is True
        assert InputSanitizer.validate_username("a1") is True

    def test_validate_username_invalid(self) -> None:
        """Test invalid username validation."""
        assert InputSanitizer.validate_username("") is False
        assert InputSanitizer.validate_username("a") is False  # Too short
        assert InputSanitizer.validate_username("a" * 51) is False  # Too long
        assert InputSanitizer.validate_username("user@domain") is False  # Invalid chars
        assert InputSanitizer.validate_username("user name") is False  # Spaces
        assert InputSanitizer.validate_username("user.name") is False  # Dots

    def test_validate_password_strength_strong(self) -> None:
        """Test strong password validation."""
        result = InputSanitizer.validate_password_strength("MySecureP@ssw0rd123!")
        assert result["valid"] is True
        assert result["strength"] in ["Good", "Strong"]
        assert result["score"] >= 4
        assert len(result["errors"]) == 0

    def test_validate_password_strength_weak(self) -> None:
        """Test weak password validation."""
        result = InputSanitizer.validate_password_strength("password")
        assert result["valid"] is False
        assert result["strength"] in ["Very Weak", "Weak"]
        assert len(result["errors"]) > 0

    def test_validate_password_strength_too_short(self) -> None:
        """Test password too short."""
        result = InputSanitizer.validate_password_strength("abc")
        assert result["valid"] is False
        assert "at least 8 characters" in str(result["errors"])

    def test_validate_password_strength_no_uppercase(self) -> None:
        """Test password without uppercase."""
        result = InputSanitizer.validate_password_strength("mysecurepassword123!")
        assert result["valid"] is False
        assert any("uppercase" in error for error in result["errors"])

    def test_validate_password_strength_no_lowercase(self) -> None:
        """Test password without lowercase."""
        result = InputSanitizer.validate_password_strength("MYSECUREPASSWORD123!")
        assert result["valid"] is False
        assert any("lowercase" in error for error in result["errors"])

    def test_validate_password_strength_no_numbers(self) -> None:
        """Test password without numbers."""
        result = InputSanitizer.validate_password_strength("MySecurePassword!")
        assert result["valid"] is False
        assert any("number" in error for error in result["errors"])

    def test_validate_password_strength_no_special_chars(self) -> None:
        """Test password without special characters."""
        result = InputSanitizer.validate_password_strength("MySecurePassword123")
        assert result["valid"] is False
        assert any("special character" in error for error in result["errors"])

    def test_validate_password_strength_common_password(self) -> None:
        """Test common password rejection."""
        result = InputSanitizer.validate_password_strength("password123")
        assert result["valid"] is False
        assert any("common" in error.lower() for error in result["errors"])

    def test_sanitize_filename_valid(self) -> None:
        """Test valid filename sanitization."""
        result = InputSanitizer.sanitize_filename("my_document.pdf")
        assert result == "my_document.pdf"

    def test_sanitize_filename_path_traversal(self) -> None:
        """Test path traversal prevention."""
        result = InputSanitizer.sanitize_filename("../../../etc/passwd")
        assert ".." not in result
        assert "/" not in result
        assert "\\" not in result

    def test_sanitize_filename_control_chars(self) -> None:
        """Test control character removal."""
        result = InputSanitizer.sanitize_filename("file\x00\x01.txt")
        assert "\x00" not in result
        assert "\x01" not in result

    def test_sanitize_filename_dots(self) -> None:
        """Test leading/trailing dot removal."""
        result = InputSanitizer.sanitize_filename("...file.txt...")
        assert not result.startswith(".")
        assert not result.endswith(".")

    def test_sanitize_filename_empty(self) -> None:
        """Test empty filename handling."""
        result = InputSanitizer.sanitize_filename("")
        assert result == "unnamed_file"

    def test_sanitize_filename_too_long(self) -> None:
        """Test filename length limiting."""
        long_name = "a" * 300
        result = InputSanitizer.sanitize_filename(long_name)
        assert len(result) <= 255

    def test_validate_file_type_allowed(self) -> None:
        """Test allowed file type validation."""
        assert InputSanitizer.validate_file_type("document.pdf", [".pdf", ".txt"]) is True
        assert InputSanitizer.validate_file_type("file.TXT", [".pdf", ".txt"]) is True

    def test_validate_file_type_not_allowed(self) -> None:
        """Test disallowed file type validation."""
        assert InputSanitizer.validate_file_type("script.exe", [".pdf", ".txt"]) is False
        assert InputSanitizer.validate_file_type("file", [".pdf", ".txt"]) is False
        assert InputSanitizer.validate_file_type("file.", [".pdf", ".txt"]) is False