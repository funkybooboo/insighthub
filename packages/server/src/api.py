"""Flask API application."""

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from src.domains.algorithms.routes import algorithms_bp
from src.domains.auth.routes import auth_bp
from src.domains.health.routes import health_bp
from src.domains.workspaces.chats.messages.routes import messages_bp
from src.domains.workspaces.chats.sessions.routes import sessions_bp
from src.domains.workspaces.documents.routes import documents_bp
from src.domains.workspaces.routes import workspaces_bp
from src.infrastructure.config import config
from src.infrastructure.context import create_app_context, create_database
from src.infrastructure.logger import create_logger
from src.infrastructure.middleware.context_middleware import setup_context_middleware
from src.infrastructure.sockets.handler import SocketHandler

logger = create_logger(__name__)


def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Flask settings
    app.config["SECRET_KEY"] = config.secret_key
    app.config["MAX_CONTENT_LENGTH"] = config.max_content_length

    # Enable CORS
    cors_origins = [origin.strip() for origin in config.cors_origins_str.split(",")]
    CORS(app, origins=cors_origins)

    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins=cors_origins)

    # Initialize socket handler
    socket_handler = SocketHandler(socketio)

    # Initialize workers with SocketIO
    # Create a temporary app context to initialize workers
    db = create_database()
    app_context = create_app_context(db)
    app_context.initialize_workers(socketio)
    logger.info("Background workers initialized successfully")

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


if __name__ == "__main__":
    app = create_app()
    app.run(host=config.host, port=config.port, debug=config.debug)
