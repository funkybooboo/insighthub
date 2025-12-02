"""Chat message CLI commands."""

import argparse
import sys

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
    """Send a message and get streaming response from LLM."""
    try:
        if not ctx.current_session_id:
            print("Error: No chat session selected. Use 'chat select <id>' first", file=sys.stderr)
            sys.exit(1)

        session = ctx.chat_session_service.get_session(ctx.current_session_id)
        if not session:
            print(f"Error: Chat session {ctx.current_session_id} not found", file=sys.stderr)
            sys.exit(1)

        # Get the message content
        message_content = args.message

        # Create user message
        user_message = ctx.chat_message_service.create_message(
            session_id=session.id,
            role="user",
            content=message_content,
        )

        print(f"\nYou: {user_message.content}\n")

        # Get conversation history for context
        messages, _ = ctx.chat_message_service.get_session_messages(
            session_id=session.id, skip=0, limit=50
        )

        # Build conversation history (excluding the message we just created)
        conversation_history = []
        for msg in messages[:-1]:  # Exclude last message (the one we just created)
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })

        # Stream response from LLM
        print("Assistant: ", end="", flush=True)
        response_chunks = []

        try:
            for chunk in ctx.llm_provider.chat_stream(message_content, conversation_history):
                print(chunk, end="", flush=True)
                response_chunks.append(chunk)
            print()  # New line after streaming completes

            # Save assistant response
            full_response = "".join(response_chunks)
            if full_response.strip():
                ctx.chat_message_service.create_message(
                    session_id=session.id,
                    role="assistant",
                    content=full_response.strip(),
                )

        except Exception as e:
            print(f"\nError generating response: {e}", file=sys.stderr)
            logger.error(f"Failed to generate LLM response: {e}")

    except KeyboardInterrupt:
        print("\n\nCancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to send message: {e}")
        sys.exit(1)
