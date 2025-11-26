"""Main application setup and configuration."""

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from src.config import config
from src.context import create_app_context
from src.domains.algorithms.routes import algorithms_bp
from src.domains.auth.routes import auth_bp
from src.domains.health.routes import health_bp
from src.domains.workspaces.chats.messages.routes import messages_bp
from src.domains.workspaces.chats.sessions.routes import sessions_bp
from src.domains.workspaces.documents.routes import documents_bp
from src.domains.workspaces.routes import workspaces_bp
from src.infrastructure.database import create_database_from_config
from src.infrastructure.logger import create_logger
from src.infrastructure.middleware.context_middleware import setup_context_middleware

logger = create_logger(__name__)


class App:
    """Main application class containing all core components."""

    def __init__(self):
        """Initialize the application with all core components."""
        logger.info("Initializing InsightHub application")

        # Initialize database
        self.db = create_database_from_config()

        # Initialize SocketIO (will be configured with Flask app later)
        self.socketio = SocketIO()

        # Create application context with all services
        self.context = create_app_context(self.db, self.socketio)

        logger.info("Application initialized successfully")

    def get_context(self):
        """Get the application context."""
        return self.context

    def get_db(self):
        """Get the database instance."""
        return self.db

    def get_socketio(self):
        """Get the SocketIO instance."""
        return self.socketio


# Global application instance
_app_instance: App | None = None


def create_app() -> App:
    """Create and return the singleton application instance."""
    global _app_instance

    if _app_instance is None:
        _app_instance = App()

    return _app_instance


def reset_app() -> None:
    """Reset the application instance (primarily for testing)."""
    global _app_instance
    _app_instance = None


def create_flask_app(app_instance: App) -> Flask:
    """Create and configure Flask application using the app instance."""
    app = Flask(__name__)

    # Flask settings
    app.config["SECRET_KEY"] = config.secret_key
    app.config["MAX_CONTENT_LENGTH"] = config.max_content_length

    # Enable CORS
    cors_origins = [origin.strip() for origin in config.cors_origins_str.split(",")]
    CORS(app, origins=cors_origins)

    # Configure SocketIO with the Flask app
    app_instance.socketio.init_app(app, cors_allowed_origins=cors_origins)

    # Register domain event handlers for event-driven architecture
    from src.infrastructure.events import register_domain_event_handlers

    register_domain_event_handlers(app_instance.socketio)

    # Set up context middleware for requests
    setup_context_middleware(app)

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(algorithms_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(workspaces_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(sessions_bp)

    @app.route("/")
    def index() -> dict[str, str]:
        return {"message": "InsightHub API", "version": "2.0.0"}

    logger.info("Flask application created successfully")
    return app
