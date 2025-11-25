"""
Flask application factory for InsightHub RAG system.

This module provides the main Flask application with all routes registered.
"""

import atexit
import os
from typing import Any, Callable

from dotenv import load_dotenv
from flask import Flask, g
from flask_cors import CORS
from flask_socketio import SocketIO
from shared.logger import LogLevel, create_logger, create_status_consumer
from shared.messaging import StatusConsumer
from shared.messaging.status_consumer import create_status_consumer

from src import config

# Create logger using shared library
logger = create_logger("api", LogLevel.INFO)
from src.context import AppContext, create_message_publisher
from src.domains.auth.routes import auth_bp
from src.domains.health.routes import health_bp
from src.domains.workspaces.routes import workspace_bp
from src.domains.workspaces.chat.routes import chat_bp
from src.domains.workspaces.chat.events import register_socket_handlers
from src.domains.workspaces.documents.routes import documents_bp
from src.domains.workspaces.rag_config.routes import rag_config_bp
from src.domains.workspaces.chat.events import (
    WorkspaceStatusData,
    broadcast_workspace_status,
    register_status_socket_handlers,
)
from src.domains.workspaces.documents.status import (
    DocumentStatusData,
    broadcast_document_status,
    emit_wikipedia_fetch_status,
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


def create_simple_chat_consumer(socketio: SocketIO) -> Any | None:
    """
    Create a simple chat event consumer.

    For now, this is a placeholder that will be implemented when the
    chat worker is fully integrated. The chat worker will publish events
    to RabbitMQ, and this consumer will forward them to WebSocket clients.
    """
    # TODO: Implement proper chat event consumer
    # For now, chat events are handled synchronously
    logger.info("Simple chat consumer placeholder created")
    return "chat_consumer_placeholder"


class InsightHubApp(Flask):
    """Typed Flask subclass with custom InsightHub attributes."""

    from shared.messaging import RabbitMQPublisher

    performance_monitoring: PerformanceMonitoringMiddleware
    status_consumer: StatusConsumer | None
    message_publisher: RabbitMQPublisher | None


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

    # Set up logging using shared logger
    log_level_map = {
        "DEBUG": LogLevel.DEBUG,
        "INFO": LogLevel.INFO,
        "WARNING": LogLevel.WARNING,
        "ERROR": LogLevel.ERROR,
        "CRITICAL": LogLevel.CRITICAL,
    }
    log_level = log_level_map.get(config.LOG_LEVEL.upper(), LogLevel.INFO)
    logger.set_level(log_level)

    # Initialize middleware (order matters!)
    # 1. Security headers (first, to add headers to all responses)
    SecurityHeadersMiddleware(app)

    # 2. Request validation (validate before processing)
    RequestValidationMiddleware(
        app,
        max_content_length=config.MAX_CONTENT_LENGTH,
    )

    # 3. Rate limiting (after validation, before business logic)
    RateLimitMiddleware(
        app,
        requests_per_minute=config.RATE_LIMIT_PER_MINUTE,
        requests_per_hour=config.RATE_LIMIT_PER_HOUR,
        enabled=config.RATE_LIMIT_ENABLED,
    )

    # 4. Request logging (log after rate limiting)
    RequestLoggingMiddleware(app)

    # 5. Performance monitoring (monitor everything)
    performance_monitoring = PerformanceMonitoringMiddleware(
        app,
        slow_request_threshold=config.SLOW_REQUEST_THRESHOLD,
        enable_stats=config.ENABLE_PERFORMANCE_STATS,
    )

    # Store performance monitoring instance for access in routes
    app.performance_monitoring = performance_monitoring

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Could not initialize database", error=str(e))

    # Initialize message publisher (singleton for the app lifetime)
    app.message_publisher = create_message_publisher()
    if app.message_publisher:
        logger.info("Message publisher initialized and connected to RabbitMQ")

        # Register cleanup handler for graceful shutdown
        def cleanup_publisher() -> None:
            if app.message_publisher:
                try:
                    app.message_publisher.disconnect()
                    logger.info("Message publisher disconnected")
                except Exception as e:
                    logger.warning(f"Error disconnecting message publisher: {e}")

        atexit.register(cleanup_publisher)
    else:
        logger.info("Message publisher disabled (RabbitMQ not configured)")

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(rag_config_bp)
    app.register_blueprint(workspace_bp)
    logger.info("All blueprints registered")

    # Initialize SocketIO with the app
    socketio.init_app(app)

    # Initialize socket handler (registers base connect/disconnect handlers)
    SocketHandler(socketio)

    # Register domain-specific socket handlers
    register_socket_handlers(socketio)

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

    # Create a simple chat event consumer for async chat processing
    # This listens for chat events from the chat worker and emits them via WebSocket
    chat_event_consumer = create_simple_chat_consumer(socketio)
    if chat_event_consumer:
        logger.info("Chat event consumer started")
        app.chat_event_consumer = chat_event_consumer
    else:
        logger.info("Chat event consumer disabled")

    logger.info("Socket.IO initialized")

    # Database session and application context management
    @app.before_request
    def before_request() -> None:
        """Set up database session and application context before each request."""
        g.db = next(get_db())
        g.app_context = AppContext(g.db, message_publisher=app.message_publisher)

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
        host: Host to bind to (defaults to config.FLASK_HOST)
        port: Port to listen on (defaults to config.FLASK_PORT)
        debug: Enable debug mode (defaults to config.FLASK_DEBUG)
    """
    app = create_app()

    server_host = host or config.FLASK_HOST
    server_port = port or config.FLASK_PORT
    server_debug = debug if debug is not None else config.FLASK_DEBUG

    socketio.run(
        app, host=server_host, port=server_port, debug=server_debug, allow_unsafe_werkzeug=True
    )


if __name__ == "__main__":
    run_server()
