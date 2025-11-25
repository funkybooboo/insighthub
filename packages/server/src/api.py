"""
Flask application factory for InsightHub RAG system.

This module provides the main Flask application with all routes registered.
"""

import atexit
from typing import Any

from dotenv import load_dotenv
from flask import Flask, g
from flask_cors import CORS
from flask_socketio import SocketIO
from shared.logger import LogLevel, create_logger
from shared.messaging import StatusConsumer
from shared.messaging.status_consumer import create_status_consumer

from src import config
from src.context import AppContext, create_message_publisher
from src.domains.auth.routes import auth_bp
from src.domains.health.routes import health_bp
from src.domains.workspaces.chat.events import (
    WorkspaceStatusData,
    broadcast_workspace_status,
    register_socket_handlers,
    register_status_socket_handlers,
)
from src.domains.workspaces.chat.routes import chat_bp
from src.domains.workspaces.documents.processing_events import (
    handle_document_chunked,
    handle_document_embedded,
    handle_document_indexed,
    handle_document_parsed,
)
from src.domains.workspaces.documents.routes import documents_bp
from src.domains.workspaces.documents.status import DocumentStatusData, broadcast_document_status
from src.domains.workspaces.rag_config.routes import rag_config_bp
from src.domains.workspaces.routes import workspace_bp
from src.infrastructure.database import get_db, init_db
from src.infrastructure.middleware import (
    PerformanceMonitoringMiddleware,
    RateLimitMiddleware,
    RequestCorrelationMiddleware,
    RequestLoggingMiddleware,
    RequestValidationMiddleware,
    SecurityHeadersMiddleware,
)
from src.infrastructure.socket import SocketHandler

# Create logger using shared library
logger = create_logger("api", LogLevel.INFO)


def create_chat_event_consumer(socketio: SocketIO) -> Any | None:
    """
    Create a chat event consumer that forwards worker events to WebSocket clients.

    The chat worker publishes events to RabbitMQ with routing keys like:
    - chat.response_chunk
    - chat.response_complete
    - chat.no_context_found
    - chat.error

    This consumer listens for these events and forwards them to WebSocket clients.
    """
    try:
        from shared.messaging import RabbitMQConsumer

        from src.domains.workspaces.chat.events import (
            handle_chat_error,
            handle_chat_no_context_found,
            handle_chat_response_chunk,
            handle_chat_response_complete,
        )

        def on_chat_response_chunk(event_data: dict) -> None:
            """Handle chat.response_chunk events from chat worker."""
            handle_chat_response_chunk(event_data)

        def on_chat_response_complete(event_data: dict) -> None:
            """Handle chat.response_complete events from chat worker."""
            handle_chat_response_complete(event_data)

        def on_chat_no_context_found(event_data: dict) -> None:
            """Handle chat.no_context_found events from chat worker."""
            handle_chat_no_context_found(event_data)

        def on_chat_error(event_data: dict) -> None:
            """Handle chat.error events from chat worker."""
            handle_chat_error(event_data)

        def on_wikipedia_fetch_completed(event_data: dict) -> None:
            """Handle wikipedia.fetch_completed event from wikipedia worker."""
            # Auto-retry any pending RAG queries for this workspace
            workspace_id = event_data.get("workspace_id")
            user_id = event_data.get("user_id")

            if workspace_id and user_id:
                try:
                    from src.context import create_llm

                    llm_provider = create_llm()

                    # Get chat service from app context
                    from flask import g

                    if hasattr(g, "app_context") and hasattr(g.app_context, "chat_service"):
                        chat_service = g.app_context.chat_service
                        chat_service.retry_pending_rag_queries(
                            workspace_id=int(workspace_id),
                            user_id=int(user_id),
                            llm_provider=llm_provider,
                        )
                except Exception as retry_error:
                    print(
                        f"Failed to retry pending RAG queries after Wikipedia fetch: {retry_error}"
                    )

            # Emit completion status
            from src.domains.workspaces.documents.events import emit_wikipedia_fetch_status

            emit_wikipedia_fetch_status(
                workspace_id=int(workspace_id) if workspace_id else 0,
                query=event_data.get("query", ""),
                status="completed",
                document_ids=event_data.get("document_ids", []),
                message="Wikipedia article fetched and processed",
            )

        # Create consumer with event handlers
        consumer = RabbitMQConsumer(
            queue_name="server_events",
            exchange_name="server_events",
            routing_keys=[
                "chat.response_chunk",
                "chat.response_complete",
                "chat.no_context_found",
                "chat.error",
                "wikipedia.fetch_completed",
            ],
            event_handlers={
                "chat.response_chunk": on_chat_response_chunk,
                "chat.response_complete": on_chat_response_complete,
                "chat.no_context_found": on_chat_no_context_found,
                "chat.error": on_chat_error,
                "wikipedia.fetch_completed": on_wikipedia_fetch_completed,
            },
        )

        logger.info("Chat event consumer created")
        return consumer

    except Exception as e:
        logger.error(f"Failed to create chat event consumer: {e}")
        return None


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
    # Configure logging first
    from src.infrastructure.logging import configure_logging

    configure_logging()

    # Initialize database (run migrations in development)

    if config.FLASK_DEBUG:  # Only run migrations automatically in development
        logger.info("Running database migrations (development mode)")
        init_db()
    else:
        logger.info("Skipping automatic migrations (production mode)")

    app = InsightHubApp(__name__)

    # CORS configuration
    CORS(
        app,
        origins=config.CORS_ORIGINS,
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

    # 2. Request correlation (generate IDs for tracking)
    RequestCorrelationMiddleware(app)

    # 3. Request validation (validate before processing)
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
        redis_url=config.REDIS_URL if config.REDIS_URL else None,
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

    def on_document_parsed(event_data: dict) -> None:
        """Handle document parsed event from parser worker."""
        handle_document_parsed(event_data, socketio)

    def on_document_chunked(event_data: dict) -> None:
        """Handle document chunked event from chucker worker."""
        handle_document_chunked(event_data, socketio)

    def on_document_embedded(event_data: dict) -> None:
        """Handle document embedded event from embedder worker."""
        handle_document_embedded(event_data, socketio)

    def on_document_indexed(event_data: dict) -> None:
        """Handle document indexed event from indexer worker."""
        handle_document_indexed(event_data, socketio)

        def on_wikipedia_fetch_completed(event_data: dict) -> None:
            """Handle wikipedia.fetch_completed event from wikipedia worker."""
            # Auto-retry any pending RAG queries for this workspace
            workspace_id = event_data.get("workspace_id")
            user_id = event_data.get("user_id")

            if workspace_id and user_id:
                try:
                    from src.context import create_llm

                    llm_provider = create_llm()

                    # Get chat service from app context
                    from flask import g

                    if hasattr(g, "app_context") and hasattr(g.app_context, "chat_service"):
                        chat_service = g.app_context.chat_service
                        chat_service.retry_pending_rag_queries(
                            workspace_id=int(workspace_id),
                            user_id=int(user_id),
                            llm_provider=llm_provider,
                        )
                except Exception as retry_error:
                    print(
                        f"Failed to retry pending RAG queries after Wikipedia fetch: {retry_error}"
                    )

            # Emit completion status
            from src.domains.workspaces.documents.events import emit_wikipedia_fetch_status

            emit_wikipedia_fetch_status(
                workspace_id=int(workspace_id) if workspace_id else 0,
                query=event_data.get("query", ""),
                status="completed",
                document_ids=event_data.get("document_ids", []),
                message="Wikipedia article fetched and processed",
            )

    def on_workspace_provision_status(event_data: dict) -> None:
        """Handle workspace provision status from provision worker."""
        from src.domains.workspaces.events import handle_workspace_provision_status

        handle_workspace_provision_status(event_data, socketio)

    def on_workspace_deletion_status(event_data: dict) -> None:
        """Handle workspace deletion status from deletion worker."""
        from src.domains.workspaces.events import handle_workspace_deletion_status

        handle_workspace_deletion_status(event_data, socketio)

    app.status_consumer = create_status_consumer(
        on_document_status=on_document_status,
        on_workspace_status=on_workspace_status,
        on_document_parsed=on_document_parsed,
        on_document_chunked=on_document_chunked,
        on_document_embedded=on_document_embedded,
        on_document_indexed=on_document_indexed,
        on_workspace_provision_status=on_workspace_provision_status,
    )

    # Create a simple chat event consumer for async chat processing
    # This listens for chat events from the chat worker and emits them via WebSocket
    chat_event_consumer = create_chat_event_consumer(socketio)
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
