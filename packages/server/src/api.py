"""Flask API application."""

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from src.infrastructure import config
from src.infrastructure.logger import create_logger
from src.infrastructure.sockets.handler import SocketHandler
from src.domains.algorithms.routes import algorithms_bp
from src.domains.auth.routes import auth_bp
from src.domains.workspaces.chat.routes import chat_bp
from src.domains.workspaces.documents.routes import documents_bp
from src.domains.health.routes import health_bp
from src.domains.workspaces.routes import workspaces_bp

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

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(algorithms_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(workspaces_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(chat_bp)

    @app.route("/")
    def index() -> dict[str, str]:
        return {"message": "InsightHub API", "version": "2.0.0"}

    logger.info("Flask application created successfully")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=config.host, port=config.port, debug=config.debug)
