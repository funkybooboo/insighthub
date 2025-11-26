"""Middleware to inject application context into Flask g object."""

from flask import Flask, g

from src.infrastructure.context import create_app_context, create_database


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
            # Create database connection for this request
            db = create_database()
            # Create application context with services
            g.app_context = create_app_context(db)

    @app.teardown_appcontext
    def teardown_appcontext(exception: Exception | None = None) -> None:
        """Clean up app context after request."""
        if hasattr(g, "app_context"):
            # Close database connection
            if hasattr(g.app_context, "db"):
                g.app_context.db.close()
