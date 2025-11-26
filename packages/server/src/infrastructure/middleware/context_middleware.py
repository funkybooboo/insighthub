"""Middleware to inject application context into Flask g object."""

from flask import Flask, g

from src.context import get_app_context


def setup_context_middleware(app: Flask) -> None:
    """
    Set up middleware to inject app context into Flask g.

    This makes the application context available to all routes
    via g.app_context.

    Args:
        app: Flask application instance
    """

    @app.before_request
    def before_request() -> None:
        """Inject app context before each request."""
        if not hasattr(g, "app_context"):
            g.app_context = get_app_context()

    @app.teardown_appcontext
    def teardown_appcontext(exception: Exception | None = None) -> None:
        """Clean up app context after request."""
        # Note: Database connection is now a singleton and should not be closed per request
        # The singleton database connection will be closed when the application shuts down
        pass
