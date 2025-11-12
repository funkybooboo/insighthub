"""Chat CLI commands."""

import argparse
import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.context import AppContext

logger = logging.getLogger(__name__)


def send_chat_message(
    context: "AppContext", message: str, session_id: int | None = None
) -> dict[str, str | int | list[dict[str, str | float | dict[str, str]]]]:
    """
    Send a chat message and get a response.

    Args:
        context: Application context with services
        message: The user's message
        session_id: Optional session ID for conversation context

    Returns:
        Dictionary with answer, context, and session info
    """
    logger.info(f"CLI chat message: session_id={session_id}, message_length={len(message)}")
    user = context.user_service.get_or_create_default_user()

    # Process chat message using service orchestration method
    chat_response = context.chat_service.process_chat_message(
        user_id=user.id,
        message=message,
        session_id=session_id,
        rag_type="vector",
    )

    # Get document count
    documents = context.document_service.list_user_documents(user.id)

    logger.info(
        f"CLI chat message processed: session_id={chat_response.session_id}, "
        f"documents_count={len(documents)}, context_chunks={len(chat_response.context)}"
    )

    return {
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


def list_sessions(context: "AppContext") -> dict[str, int | list[dict[str, str | int | None]]]:
    """
    List all chat sessions.

    Args:
        context: Application context with services

    Returns:
        Dictionary with sessions list and count
    """
    logger.info("CLI listing chat sessions")
    user = context.user_service.get_or_create_default_user()
    sessions = context.chat_service.list_user_sessions(user.id)

    logger.info(f"CLI chat sessions listed: count={len(sessions)}")

    return {
        "sessions": [
            {
                "id": session.id,
                "title": session.title if session.title is not None else "",
                "rag_type": session.rag_type,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
            }
            for session in sessions
        ],
        "count": len(sessions),
    }


def cmd_chat(context: "AppContext", args: argparse.Namespace) -> None:
    """Send a chat message."""
    try:
        result = send_chat_message(context, args.message, args.session_id)
        print("\nAnswer:")
        print("-" * 80)
        print(result["answer"])
        print("-" * 80)

        if args.show_context and "context" in result:
            print("\nContext:")
            context_list = result["context"]
            if isinstance(context_list, list):
                for i, ctx in enumerate(context_list, 1):
                    if isinstance(ctx, dict):
                        print(f"\n{i}. Score: {ctx.get('score', 0.0):.2f}")
                        text = ctx.get("text", "")
                        if isinstance(text, str):
                            print(f"   {text[:200]}...")

        print(f"\nDocuments in system: {result.get('documents_count', 0)}")
        print(f"Session ID: {result.get('session_id', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_sessions(context: "AppContext", args: argparse.Namespace) -> None:
    """List all chat sessions."""
    try:
        result = list_sessions(context)
        sessions = result.get("sessions", [])

        if not sessions:
            print("No chat sessions found.")
            return

        print(f"Total sessions: {result.get('count', 0)}\n")
        if isinstance(sessions, list):
            for session in sessions:
                if isinstance(session, dict):
                    print(f"ID: {session.get('id', 'N/A')}")
                    print(f"  Title: {session.get('title', 'N/A')}")
                    print(f"  RAG Type: {session.get('rag_type', 'N/A')}")
                    print(f"  Created: {session.get('created_at', 'N/A')}")
                    print(f"  Updated: {session.get('updated_at', 'N/A')}")
                    print()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_interactive(context: "AppContext", args: argparse.Namespace) -> None:
    """Start an interactive chat session."""
    logger.info("CLI starting interactive chat session")
    print("Interactive Chat Session")
    print("Type 'quit' or 'exit' to end the session")
    print("-" * 80)

    session_id: int | None = None

    while True:
        try:
            message = input("\nYou: ").strip()

            if message.lower() in ["quit", "exit"]:
                logger.info(f"CLI interactive chat session ended: session_id={session_id}")
                print("Goodbye!")
                break

            if not message:
                continue

            result = send_chat_message(context, message, session_id)
            print(f"\nBot: {result['answer']}")

            # Remember session ID for context
            if not session_id:
                result_session_id = result.get("session_id")
                if isinstance(result_session_id, int):
                    session_id = result_session_id
                    logger.debug(f"CLI interactive session established: session_id={session_id}")

        except KeyboardInterrupt:
            logger.info(f"CLI interactive chat session interrupted: session_id={session_id}")
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"CLI interactive chat error: {str(e)}", exc_info=True)
            print(f"Error: {e}", file=sys.stderr)
