"""
Flask application factory for InsightHub RAG system.

This module provides the main Flask application with all routes registered.
"""

import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, g
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from src.context import AppContext
from src.domains.chat.routes import chat_bp
from src.domains.documents.routes import documents_bp
from src.domains.health.routes import health_bp
from src.infrastructure.database import get_db, init_db

# Load environment variables
load_dotenv()

# Initialize SocketIO instance
socketio = SocketIO(cors_allowed_origins="*")


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

    # Initialize SocketIO with the app
    socketio.init_app(app)

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

    # Socket.IO event handlers
    @socketio.on("connect")
    def handle_connect() -> None:
        """Handle client connection."""
        print("Client connected")
        emit("connected", {"status": "connected"})

    @socketio.on("disconnect")
    def handle_disconnect() -> None:
        """Handle client disconnection."""
        print("Client disconnected")

    @socketio.on("chat_message")
    def handle_chat_message(data: dict[str, Any]) -> None:
        """
        Handle streaming chat messages.

        Expected data:
            {
                "message": "User's question",
                "session_id": "optional-session-id",
                "rag_type": "vector" (optional, defaults to vector)
            }
        """
        from flask import current_app

        with current_app.app_context():
            try:
                # Get database session
                db = next(get_db())
                app_context = AppContext(db)

                user_message = data.get("message", "")
                session_id = data.get("session_id")

                if not user_message:
                    emit("error", {"error": "No message provided"})
                    db.close()
                    return

                # Get user
                user = app_context.user_service.get_or_create_default_user()

                # Get or create session
                session = app_context.chat_service.get_or_create_session(
                    user_id=user.id,
                    session_id=int(session_id) if session_id else None,
                    first_message=user_message,
                )

                # Get conversation history
                messages = app_context.chat_service.list_session_messages(session.id)
                conversation_history = [
                    {"role": msg.role, "content": msg.content} for msg in messages[-10:]
                ]

                # Store user message
                app_context.chat_service.create_message(
                    session_id=session.id, role="user", content=user_message
                )

                # Stream LLM response
                full_response = ""
                for chunk in app_context.llm_provider.chat_stream(
                    user_message, conversation_history
                ):
                    full_response += chunk
                    emit("chat_chunk", {"chunk": chunk})

                # Store assistant response
                app_context.chat_service.create_message(
                    session_id=session.id,
                    role="assistant",
                    content=full_response,
                    metadata={"rag_type": "vector"},
                )

                # Send completion event
                emit("chat_complete", {"session_id": session.id, "full_response": full_response})

                # Close database session
                db.close()

            except Exception as e:
                emit("error", {"error": f"Error processing chat: {str(e)}"})
                if "db" in locals():
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
