"""Chat routes."""

import json

from flask import Blueprint, Response, g, jsonify, request

chat_bp = Blueprint("chat", __name__, url_prefix="/api")


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
        # Get user
        user = g.app_context.user_service.get_or_create_default_user()

        # Process chat message using service orchestration method
        chat_response = g.app_context.chat_service.process_chat_message(
            user_id=user.id,
            message=user_message,
            session_id=int(session_id) if session_id else None,
            rag_type=rag_type,
        )

        # Get document count for response
        documents = g.app_context.document_service.list_user_documents(user.id)

        # Format response
        response = {
            "answer": chat_response.answer,
            "context": [
                {
                    "text": ctx.text,
                    "score": ctx.score,
                    "metadata": ctx.metadata,
                }
                for ctx in chat_response.context
            ],
            "session_id": chat_response.session_id,
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
        user = g.app_context.user_service.get_or_create_default_user()
        sessions = g.app_context.chat_service.list_user_sessions(user.id)

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
        messages = g.app_context.chat_service.list_session_messages(session_id)

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
