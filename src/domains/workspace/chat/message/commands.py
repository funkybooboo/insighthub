"""Chat message CLI commands."""

import argparse
import sys

from returns.result import Failure

from src.context import AppContext
from src.domains.workspace.chat.message.dtos import ListMessagesRequest, SendMessageRequest
from src.infrastructure.logger import create_logger
from src.infrastructure.types.errors import NotFoundError

logger = create_logger(__name__)


def format_error(error: object) -> str:
    """Format error object into a user-friendly message."""
    if isinstance(error, NotFoundError):
        return f"{error.resource} {error.id} not found"
    return getattr(error, "message", str(error))


def cmd_list(ctx: AppContext, args: argparse.Namespace) -> None:
    """List message history in the current chat session."""
    try:
        if not ctx.current_session_id:
            print("Error: No chat session selected. Use 'chat select <id>' first", file=sys.stderr)
            sys.exit(1)

        # === Create Request DTO ===
        request = ListMessagesRequest(session_id=ctx.current_session_id, skip=0, limit=50)

        # === Call Orchestrator ===
        result = ctx.message_orchestrator.list_messages(request)

        # === Handle Result (CLI-specific output) ===
        if isinstance(result, Failure):
            error = result.failure()
            print(f"Error: {format_error(error)}", file=sys.stderr)
            sys.exit(1)

        responses, total = result.unwrap()

        if not responses:
            print("No messages in this session")
            return

        print(f"\nChat History ({total} messages):\n")
        for response in responses:
            role = "You" if response.role == "user" else "Assistant"
            print(f"{role}: {response.content}\n")

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

        # Stream callback to print chunks
        def print_chunk(chunk: str) -> None:
            print(chunk, end="", flush=True)

        # === Create Request DTO ===
        request = SendMessageRequest(
            session_id=ctx.current_session_id,
            content=args.message,
            stream_callback=print_chunk,
        )

        # Print user message
        print(f"\nYou: {request.content}\n")

        # === Call Orchestrator ===
        print("Assistant: ", end="", flush=True)
        result = ctx.message_orchestrator.send_message(request)

        print()  # New line after streaming completes

        # === Handle Result (CLI-specific output) ===
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
