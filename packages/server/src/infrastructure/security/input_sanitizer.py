"""Input sanitization and validation utilities."""

import re
from typing import Any, Dict, Optional, TypedDict, Union


class PasswordValidationResult(TypedDict):
    """Result of password strength validation."""
    valid: bool
    errors: list[str]
    strength: str
    score: int


class InputSanitizer:
    """Utility class for sanitizing and validating user inputs."""

    # Dangerous HTML/script patterns
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript URLs
        r'vbscript:',                  # VBScript URLs
        r'on\w+\s*=',                  # Event handlers
        r'<iframe[^>]*>.*?</iframe>',  # Iframe tags
        r'<object[^>]*>.*?</object>',  # Object tags
        r'<embed[^>]*>.*?</embed>',    # Embed tags
        r'<form[^>]*>.*?</form>',      # Form tags
        r'<input[^>]*>',               # Input tags
        r'<meta[^>]*>',                # Meta tags
    ]

    # SQL injection patterns (basic detection)
    SQL_INJECTION_PATTERNS = [
        r';\s*(drop|delete|update|insert|alter|create|truncate)\s',
        r'union\s+select',
        r'--\s*$',  # SQL comments
        r'/\*.*\*/',  # Block comments
    ]

    @staticmethod
    def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
        """Sanitize text input by removing dangerous content."""
        if not text:
            return ""

        # Convert to string if not already
        text = str(text)

        # Remove null bytes and other control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

        # Remove dangerous HTML/script content
        for pattern in InputSanitizer.DANGEROUS_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

        # Basic SQL injection detection (log but don't modify)
        for pattern in InputSanitizer.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                from src.infrastructure.logging import log_security_event
                from flask import request
                log_security_event(
                    event="potential_sql_injection",
                    details={"pattern": pattern, "input": text[:100]},
                    client_ip=request.remote_addr if request else "unknown"
                )
                break

        # Trim whitespace
        text = text.strip()

        # Apply length limit if specified
        if max_length and len(text) > max_length:
            text = text[:max_length]

        return text

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email or len(email) > 254:  # RFC 5321 limit
            return False

        # Basic email regex (not perfect but covers most cases)
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format."""
        if not username or len(username) < 3 or len(username) > 50:
            return False

        # Only allow alphanumeric, underscore, and hyphen
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', username))

    @staticmethod
    def validate_password_strength(password: str) -> PasswordValidationResult:
        """Validate password strength and return detailed feedback."""
        if not password:
            return {"valid": False, "errors": ["Password cannot be empty"]}

        errors = []
        score = 0

        # Length check
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        elif len(password) >= 12:
            score += 1

        # Character variety checks
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        else:
            score += 1

        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        else:
            score += 1

        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        else:
            score += 1

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            errors.append("Password must contain at least one special character")
        else:
            score += 1

        # Common password check
        common_passwords = [
            "password", "123456", "qwerty", "abc123", "password123",
            "admin", "letmein", "welcome", "monkey", "dragon"
        ]
        if password.lower() in common_passwords:
            errors.append("Password is too common")
            score = max(0, score - 2)

        # Dictionary words (basic check)
        if len(password) <= 20:  # Only check shorter passwords
            with open('/usr/share/dict/words', 'r') as f:
                common_words = {line.strip().lower() for line in f if len(line.strip()) > 3}
                if password.lower() in common_words:
                    errors.append("Password contains common dictionary words")
                    score = max(0, score - 1)

        strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong"]
        strength = strength_levels[min(score, len(strength_levels) - 1)]

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "strength": strength,
            "score": score
        }

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal and other attacks."""
        if not filename:
            return ""

        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename)

        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')

        # Limit length
        if len(filename) > 255:
            filename = filename[:255]

        # Ensure it's not empty after sanitization
        if not filename:
            filename = "unnamed_file"

        return filename

    @staticmethod
    def validate_file_type(filename: str, allowed_extensions: list[str]) -> bool:
        """Validate file extension against allowed types."""
        if not filename or '.' not in filename:
            return False

        extension = filename.rsplit('.', 1)[1].lower()
        return extension in [ext.lower() for ext in allowed_extensions]