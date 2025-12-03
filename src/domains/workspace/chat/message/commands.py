"""Chat message CLI commands."""

import argparse
import sys

from returns.result import Failure

from src.context import AppContext
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def cmd_list(ctx: AppContext, args: argparse.Namespace) -> None:
    """List message history in the current chat session."""
    try:
        if not ctx.current_session_id:
            print("Error: No chat session selected. Use 'chat select <id>' first", file=sys.stderr)
            sys.exit(1)

        session = ctx.chat_session_service.get_session(ctx.current_session_id)
        if not session:
            print(f"Error: Chat session {ctx.current_session_id} not found", file=sys.stderr)
            sys.exit(1)

        # List message for the session
        messages, total = ctx.chat_message_service.get_session_messages(
            session_id=session.id, skip=0, limit=50
        )

        if not messages:
            print("No messages in this session")
            return

        print(f"\nChat History ({total} messages):\n")
        for message in messages:
            role = "You" if message.role == "user" else "Assistant"
            print(f"{role}: {message.content}\n")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to list messages: {e}")
        sys.exit(1)


def cmd_send(ctx: AppContext, args: argparse.Namespace) -> None:
    """Send a message and get streaming response from LLM with RAG context."""
    try:
        if not ctx.current_session_id:
            print("Error: No chat session selected. Use 'chat select <id>' first", file=sys.stderr)
            sys.exit(1)

        # Get the message content
        message_content = args.message

        # Print user message
        print(f"\nYou: {message_content}\n")

        # Stream callback to print chunks
        print("Assistant: ", end="", flush=True)

        def print_chunk(chunk: str) -> None:
            print(chunk, end="", flush=True)

        # Send message with RAG and streaming (all logic in service)
        result = ctx.chat_message_service.send_message_with_rag(
            session_id=ctx.current_session_id,
            message_content=message_content,
            stream_callback=print_chunk,
        )

        print()  # New line after streaming completes

        if isinstance(result, Failure):
            error = result.failure()
            print(f"\nError: {error.message}", file=sys.stderr)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nCancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to send message: {e}")
        sys.exit(1)
