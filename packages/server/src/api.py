"""
Flask application factory for InsightHub RAG system.

This module provides the main Flask application with all routes registered.
"""

import logging
import os

from dotenv import load_dotenv
from flask import Flask, g
from flask_cors import CORS
from flask_socketio import SocketIO
from shared.messaging import StatusConsumer
from shared.messaging.status_consumer import create_status_consumer

from src import config
from src.context import AppContext
from src.domains.auth.routes import auth_bp
from src.domains.chat.routes import chat_bp
from src.domains.chat.socket_handlers import (
    register_socket_handlers as register_chat_socket_handlers,
)
from src.domains.documents.routes import documents_bp
from src.domains.health.routes import health_bp
from src.domains.status.socket_handlers import (
    DocumentStatusData,
    WorkspaceStatusData,
    broadcast_document_status,
    broadcast_workspace_status,
    register_status_socket_handlers,
)
from src.infrastructure.database import get_db, init_db
from src.infrastructure.middleware import (
    PerformanceMonitoringMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    RequestValidationMiddleware,
    SecurityHeadersMiddleware,
)
from src.infrastructure.socket import SocketHandler


class InsightHubApp(Flask):
    """Typed Flask subclass with custom InsightHub attributes."""

    performance_monitoring: PerformanceMonitoringMiddleware
    status_consumer: StatusConsumer | None


# Load environment variables
load_dotenv()

# Initialize SocketIO instance
socketio = SocketIO(cors_allowed_origins="*")


def create_app() -> InsightHubApp:
    """
    Create and configure the Flask application.

    Returns:
        InsightHubApp: Configured Flask application with custom attributes
    """
    app = InsightHubApp(__name__)

    # CORS configuration
    CORS(
        app,
        origins=config.CORS_ORIGINS.split(","),
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    # Configuration from environment variables
    app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
    app.config["DEBUG"] = config.FLASK_DEBUG

    # Set up logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO))
    app.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Initialize middleware (order matters!)
    # 1. Security headers (first, to add headers to all responses)
    SecurityHeadersMiddleware(app)

    # 2. Request validation (validate before processing)
    RequestValidationMiddleware(
        app,
        max_content_length=config.MAX_CONTENT_LENGTH,
    )

    # 3. Rate limiting (after validation, before business logic)
    rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RateLimitMiddleware(
        app,
        requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
        requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000")),
        enabled=rate_limit_enabled,
    )

    # 4. Request logging (log after rate limiting)
    RequestLoggingMiddleware(app)

    # 5. Performance monitoring (monitor everything)
    performance_monitoring = PerformanceMonitoringMiddleware(
        app,
        slow_request_threshold=float(os.getenv("SLOW_REQUEST_THRESHOLD", "1.0")),
        enable_stats=os.getenv("ENABLE_PERFORMANCE_STATS", "true").lower() == "true",
    )

    # Store performance monitoring instance for access in routes
    app.performance_monitoring = performance_monitoring

    # Initialize database
    try:
        init_db()
        app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.error(f"Could not initialize database: {e}")

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(chat_bp)
    app.logger.info("All blueprints registered")

    # Initialize SocketIO with the app
    socketio.init_app(app)

    # Initialize socket handler (registers base connect/disconnect handlers)
    SocketHandler(socketio)

    # Register domain-specific socket handlers
    register_chat_socket_handlers(socketio)

    # Register status socket handlers
    register_status_socket_handlers(socketio)

    # Start status update consumer if RabbitMQ is configured
    def on_document_status(event_data: DocumentStatusData) -> None:
        """Handle document status update from RabbitMQ."""
        broadcast_document_status(event_data, socketio)

    def on_workspace_status(event_data: WorkspaceStatusData) -> None:
        """Handle workspace status update from RabbitMQ."""
        broadcast_workspace_status(event_data, socketio)

    status_consumer = create_status_consumer(
        on_document_status=on_document_status,
        on_workspace_status=on_workspace_status,
    )

    if status_consumer:
        app.logger.info("Status update consumer started")
        # Store consumer reference for graceful shutdown
        app.status_consumer = status_consumer
    else:
        app.logger.info("Status update consumer disabled (RabbitMQ not configured)")

    app.logger.info("Socket.IO initialized")

    # Database session and application context management
    @app.before_request
    def before_request() -> None:
        """Set up database session and application context before each request."""
        g.db = next(get_db())
        g.app_context = AppContext(g.db)

    @app.teardown_appcontext
    def teardown_db(error: BaseException | None) -> None:
        """Close database session at the end of the request."""
        db = g.pop("db", None)
        if db is not None:
            db.close()

    return app


def run_server(host: str | None = None, port: int | None = None, debug: bool | None = None) -> None:
    """
    Run the Flask development server with Socket.IO support.

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

    socketio.run(
        app, host=server_host, port=server_port, debug=server_debug, allow_unsafe_werkzeug=True
    )


if __name__ == "__main__":
    run_server()
