"""Security headers middleware."""

import logging

from flask import Flask, Response

from src import config

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    """
    Middleware for adding security headers to all responses.

    Implements OWASP security best practices:
    - Content Security Policy (CSP)
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Strict-Transport-Security (HSTS)
    - Referrer-Policy
    """

    def __init__(self, app: Flask, config: dict[str, str] | None = None) -> None:
        """
        Initialize security headers middleware.

        Args:
            app: Flask application instance
            config: Optional custom security header configuration
        """
        self.app = app
        self.config = config or self._default_config()
        self.setup_security_headers(app)
        logger.info("Security headers middleware initialized")

    def _default_config(self) -> dict[str, str]:
        """Get default security headers configuration."""
        # Allow connections to configured CORS origins for WebSocket and API calls
        connect_src = "'self'"
        if config.CORS_ORIGINS != "*":
            connect_src += " " + " ".join(config.CORS_ORIGINS.split(","))
        else:
            # In development, allow connections to common localhost ports
            connect_src += " http://localhost:* ws://localhost:* wss://localhost:*"

        return {
            # Prevent clickjacking attacks
            "X-Frame-Options": "DENY",
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            # Enable XSS filter in older browsers
            "X-XSS-Protection": "1; mode=block",
            # Content Security Policy - adjust as needed
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                f"connect-src {connect_src}"
            ),
            # Control referrer information
            "Referrer-Policy": "strict-origin-when-cross-origin",
            # Prevent browser feature abuse
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "accelerometer=()"
            ),
        }

    def setup_security_headers(self, app: Flask) -> None:
        """Set up security headers on all responses."""

        @app.after_request
        def add_security_headers(response: Response) -> Response:
            """Add security headers to response."""
            for header, value in self.config.items():
                response.headers[header] = value

            # Add HSTS only in production (when using HTTPS)
            if not app.config.get("DEBUG", False):
                response.headers["Strict-Transport-Security"] = (
                    "max-age=31536000; includeSubDomains"
                )

            return response
