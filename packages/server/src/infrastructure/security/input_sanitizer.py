
"""Input sanitization utilities for security."""

import html
import re
from typing import Any, Union


class InputSanitizer:
    """
    Input sanitization utilities to prevent security vulnerabilities.

    Provides methods to sanitize user input for different contexts:
    - HTML content (XSS prevention)
    - SQL queries (basic protection)
    - File paths (path traversal prevention)
    - General text input
    """

    # Dangerous HTML tags that should be removed
    DANGEROUS_HTML_TAGS = {
        'script', 'iframe', 'object', 'embed', 'form', 'input', 'button',
        'link', 'meta', 'style', 'applet', 'param', 'base', 'bgsound'
    }

    # Dangerous HTML attributes
    DANGEROUS_HTML_ATTRS = {
        'onload', 'onerror', 'onclick', 'onmouseover', 'onmouseout',
        'onkeydown', 'onkeyup', 'onkeypress', 'onsubmit', 'onreset',
        'onselect', 'onchange', 'onfocus', 'onblur', 'onabort',
        'javascript:', 'data:', 'vbscript:'
    }

    # SQL injection patterns to detect/remove
    SQL_INJECTION_PATTERNS = [
        r';\s*(drop|delete|update|insert|alter|create|truncate)\s',
        r';\s*(union|select)\s.*\sfrom\s',
        r'--',  # SQL comments
        r'/\*.*\*/',  # Block comments
        r';\s*exec\s',
        r';\s*execute\s',
    ]

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\./',  # Parent directory
        r'\.\.\\',  # Windows parent directory
        r'%2e%2e%2f',  # URL encoded ../
        r'%2e%2e%5c',  # URL encoded ..\
    ]

    @staticmethod
    def sanitize_html(input_text: str) -> str:
        """
        Sanitize HTML content to prevent XSS attacks.

        Removes dangerous tags and attributes, escapes remaining HTML.

        Args:
            input_text: Raw HTML input

        Returns:
            Sanitized HTML-safe string
        """
        if not isinstance(input_text, str):
            return str(input_text)

        # Remove dangerous tags
        for tag in InputSanitizer.DANGEROUS_HTML_TAGS:
            pattern = rf'<{tag}[^>]*>.*?</{tag}>|<{tag}[^>]*/?>'
            input_text = re.sub(pattern, '', input_text, flags=re.IGNORECASE | re.DOTALL)

        # Remove dangerous attributes
        for attr in InputSanitizer.DANGEROUS_HTML_ATTRS:
            pattern = rf'\s{re.escape(attr)}\s*=\s*["\'][^"\']*["\']'
            input_text = re.sub(pattern, '', input_text, flags=re.IGNORECASE)

        # Escape remaining HTML
        return html.escape(input_text, quote=True)

    @staticmethod
    def sanitize_sql(input_text: str) -> str:
        """
        Basic SQL input sanitization.

        This is NOT a complete SQL injection prevention solution.
        Always use parameterized queries for database operations.

        Args:
            input_text: Raw SQL input

        Returns:
            Sanitized string safe for basic SQL contexts
        """
        if not isinstance(input_text, str):
            return str(input_text)

        # Remove/replace dangerous patterns
        for pattern in InputSanitizer.SQL_INJECTION_PATTERNS:
            input_text = re.sub(pattern, '', input_text, flags=re.IGNORECASE)

        # Escape single quotes
        input_text = input_text.replace("'", "''")

        return input_text

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other issues.

        Args:
            filename: Raw filename

        Returns:
            Sanitized filename
        """
        if not isinstance(filename, str):
            return str(filename)

        # Remove path traversal patterns
        for pattern in InputSanitizer.PATH_TRAVERSAL_PATTERNS:
            filename = re.sub(pattern, '', filename, flags=re.IGNORECASE)

        # Remove dangerous characters
        filename = re.sub(r'[<>:"|?*]', '', filename)

        # Limit length
        filename = filename[:255]

        # Ensure not empty
        if not filename.strip():
            filename = "unnamed_file"

        return filename

    @staticmethod
    def sanitize_text(input_text: str, max_length: int = 10000) -> str:
        """
        Sanitize general text input.

        Args:
            input_text: Raw text input
            max_length: Maximum allowed length

        Returns:
            Sanitized text
        """
        if not isinstance(input_text, str):
            input_text = str(input_text)

        # Remove null bytes
        input_text = input_text.replace('\x00', '')

        # Remove control characters except newlines and tabs
        input_text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', input_text)

        # Limit length
        input_text = input_text[:max_length]

        return input_text.strip()

    @staticmethod
    def sanitize_email(email: str) -> str:
        """
        Sanitize email address.

        Args:
            email: Raw email input

        Returns:
            Sanitized email or empty string if invalid
        """
        if not isinstance(email, str):
            return ""

        email = email.strip().lower()

        # Basic email validation pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if re.match(email_pattern, email):
            return email
        else:
            return ""

    @staticmethod
    def sanitize_url(url: str) -> str:
        """
        Sanitize URL input.

        Args:
            url: Raw URL input

        Returns:
            Sanitized URL or empty string if invalid
        """
        if not isinstance(url, str):
            return ""

        url = url.strip()

        # Basic URL validation
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'

        if re.match(url_pattern, url):
            return url
        else:
            return ""

    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validate username format and constraints.

        Username must be 3-50 characters and contain only letters, numbers, underscores, and hyphens.

        Args:
            username: Username to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(username, str):
            return False

        # Check length
        if not 3 <= len(username) <= 50:
            return False

        # Check allowed characters (letters, numbers, underscores, hyphens)
        username_pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(username_pattern, username))

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid format, False otherwise
        """
        if not isinstance(email, str):
            return False

        email = email.strip()

        # RFC 5322 compliant email pattern (simplified)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        return bool(re.match(email_pattern, email))

    @staticmethod
    def validate_password_strength(password: str) -> dict[str, Any]:
        """
        Validate password strength and return detailed analysis.

        Args:
            password: Password to validate

        Returns:
            Dict with keys:
            - valid: bool - whether password meets minimum requirements
            - errors: list[str] - list of validation error messages
            - strength: str - "weak", "medium", or "strong"
        """
        if not isinstance(password, str):
            return {
                "valid": False,
                "errors": ["Password must be a string"],
                "strength": "weak"
            }

        errors = []
        score = 0

        # Length check
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        else:
            score += 1

        # Uppercase check
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        else:
            score += 1

        # Lowercase check
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        else:
            score += 1

        # Number check
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        else:
            score += 1

        # Special character check (optional but recommended)
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            # Don't add to errors, but don't increase score
            pass
        else:
            score += 1

        # Check for common weak passwords
        weak_passwords = [
            "password", "123456", "qwerty", "abc123", "password123",
            "admin", "letmein", "welcome", "monkey", "123456789"
        ]
        if password.lower() in weak_passwords:
            errors.append("Password is too common, please choose a stronger password")
            score = min(score, 1)  # Cap score for weak passwords

        # Determine strength
        if score <= 2 or errors:
            strength = "weak"
        elif score <= 4:
            strength = "medium"
        else:
            strength = "strong"

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "strength": strength
        }

    @classmethod
    def sanitize_all(cls, data: Any) -> Any:
        """
        Recursively sanitize all string values in a data structure.

        Args:
            data: Data structure to sanitize (dict, list, etc.)

        Returns:
            Sanitized data structure
        """
        if isinstance(data, dict):
            return {key: cls.sanitize_all(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [cls.sanitize_all(item) for item in data]
        elif isinstance(data, str):
            return cls.sanitize_text(data)
        else:
            return data
