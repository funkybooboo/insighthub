"""
Flask application factory for InsightHub RAG system.

This module provides the main Flask application with all routes registered.
"""

import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, g
from flask_cors import CORS

from src.context import AppContext
from src.domains.chat.routes import chat_bp
from src.domains.documents.routes import documents_bp
from src.domains.health.routes import health_bp
from src.infrastructure.database import get_db, init_db

# Load environment variables
load_dotenv()


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    CORS(app)

    # Configuration from environment variables
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))

    # Initialize database
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(chat_bp)

    # Database session and application context management
    @app.before_request
    def before_request() -> None:
        """Set up database session and application context before each request."""
        g.db = next(get_db())
        g.app_context = AppContext(g.db)

    @app.teardown_appcontext
    def teardown_db(error: Any) -> None:
        """Close database session at the end of the request."""
        db = g.pop("db", None)
        if db is not None:
            db.close()

    return app


def run_server(host: str | None = None, port: int | None = None, debug: bool | None = None) -> None:
    """
    Run the Flask development server.

    Args:
        host: Host to bind to (defaults to FLASK_HOST env var or 0.0.0.0)
        port: Port to listen on (defaults to FLASK_PORT env var or 5000)
        debug: Enable debug mode (defaults to FLASK_DEBUG env var or True)
    """
    app = create_app()

    server_host = host or os.getenv("FLASK_HOST", "0.0.0.0")
    server_port = port or int(os.getenv("FLASK_PORT", "5000"))
    server_debug = (
        debug if debug is not None else os.getenv("FLASK_DEBUG", "True").lower() == "true"
    )

    app.run(host=server_host, port=server_port, debug=server_debug)


if __name__ == "__main__":
    run_server()
