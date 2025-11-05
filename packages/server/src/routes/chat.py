"""Chat routes."""

import json
from typing import Any

from flask import Blueprint, Response, g, jsonify, request

from src.services.chat_service import ChatService
from src.services.document_service import DocumentService
from src.services.user_service import UserService
from src.storage.blob_storage import get_blob_storage

chat_bp = Blueprint("chat", __name__, url_prefix="/api")


def get_db_session() -> Any:
    """Get database session from Flask g object."""
    return g.db


@chat_bp.route("/chat", methods=["POST"])
def chat() -> tuple[Response, int]:
    """
    Handle chat messages and return responses from the RAG system.

    Expected JSON payload:
        {
            "message": "User's question",
            "session_id": "optional-session-id",
            "rag_type": "vector" (optional, defaults to vector)
        }

    Returns:
        JSON response with answer and relevant context
    """
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"]
    session_id = data.get("session_id")
    rag_type = data.get("rag_type", "vector")

    try:
        # Get services
        db = get_db_session()
        user_service = UserService(db)
        chat_service = ChatService(db)
        blob_storage = get_blob_storage()
        doc_service = DocumentService(db, blob_storage)

        # Get user
        user = user_service.get_or_create_default_user()

        # Get or create chat session
        if session_id:
            session = chat_service.get_session_by_id(int(session_id))
            if not session:
                return jsonify({"error": "Session not found"}), 404
        else:
            # Create new session with first message as title
            session = chat_service.create_session(
                user_id=user.id, first_message=user_message, rag_type=rag_type
            )

        # Store user message
        chat_service.create_message(session_id=session.id, role="user", content=user_message)

        # TODO: Integrate with RAG system here
        # from rag.factory import create_rag
        # rag = create_rag(rag_type="vector", ...)
        # results = rag.query(user_message, top_k=5)
        # answer = results["answer"]
        # context = results["context"]

        # For now, return a mock response
        mock_answer = f"This is a mock response to: {user_message}"
        mock_context = [
            {
                "text": "Sample context chunk 1",
                "score": 0.85,
                "metadata": {"source": "document_1"},
            },
            {
                "text": "Sample context chunk 2",
                "score": 0.78,
                "metadata": {"source": "document_2"},
            },
        ]

        # Store assistant response with metadata
        chat_service.create_message(
            session_id=session.id,
            role="assistant",
            content=mock_answer,
            metadata={"context_chunks": len(mock_context), "rag_type": rag_type},
        )

        # Get document count
        documents = doc_service.list_user_documents(user.id)

        response = {
            "answer": mock_answer,
            "context": mock_context,
            "session_id": session.id,
            "documents_count": len(documents),
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Error processing chat: {str(e)}"}), 500


@chat_bp.route("/sessions", methods=["GET"])
def list_sessions() -> tuple[Response, int]:
    """
    List all chat sessions for the current user.

    Returns:
        JSON response with list of chat sessions
    """
    try:
        db = get_db_session()
        user_service = UserService(db)
        chat_service = ChatService(db)

        user = user_service.get_or_create_default_user()
        sessions = chat_service.list_user_sessions(user.id)

        sessions_list = [
            {
                "id": session.id,
                "title": session.title,
                "rag_type": session.rag_type,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
            }
            for session in sessions
        ]

        return jsonify({"sessions": sessions_list, "count": len(sessions_list)}), 200

    except Exception as e:
        return jsonify({"error": f"Error listing sessions: {str(e)}"}), 500


@chat_bp.route("/sessions/<int:session_id>/messages", methods=["GET"])
def get_session_messages(session_id: int) -> tuple[Response, int]:
    """
    Get all messages for a specific chat session.

    Args:
        session_id: The chat session ID

    Returns:
        JSON response with list of messages
    """
    try:
        db = get_db_session()
        chat_service = ChatService(db)

        messages = chat_service.list_session_messages(session_id)

        messages_list = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "metadata": json.loads(msg.extra_metadata) if msg.extra_metadata else None,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]

        return jsonify({"messages": messages_list, "count": len(messages_list)}), 200

    except Exception as e:
        return jsonify({"error": f"Error getting messages: {str(e)}"}), 500
