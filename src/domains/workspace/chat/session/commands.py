"""Chat session CLI commands."""

import argparse
import sys

from src.context import AppContext
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def cmd_list(ctx: AppContext, args: argparse.Namespace) -> None:
    """List chat session in the specified workspace."""
    try:
        workspace = ctx.workspace_repo.get_by_id(args.workspace_id)
        if not workspace:
            print(f"Error: Workspace {args.workspace_id} not found", file=sys.stderr)
            sys.exit(1)

        # List session for the workspace
        sessions, total = ctx.chat_session_service.list_workspace_sessions(
            workspace_id=workspace.id, skip=0, limit=50
        )

        if not sessions:
            print("No chat sessions found")
            return

        for session in sessions:
            title = session.title or "(No title)"
            print(f"[{session.id}] {title}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to list chat sessions: {e}")
        sys.exit(1)


def cmd_new(ctx: AppContext, args: argparse.Namespace) -> None:
    """Create a new chat session (interactive)."""
    try:
        workspace = ctx.workspace_repo.get_by_id(args.workspace_id)
        if not workspace:
            print(f"Error: Workspace {args.workspace_id} not found", file=sys.stderr)
            sys.exit(1)

        # Interactive prompts
        title = input("Session title (optional): ").strip() or None

        # Create session
        session = ctx.chat_session_service.create_session(
            title=title,
            workspace_id=workspace.id,
            rag_type=workspace.rag_type,
        )

        print(f"Created chat session [{session.id}] {session.title or '(No title)'}")

    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to create chat session: {e}")
        sys.exit(1)


def cmd_select(ctx: AppContext, args: argparse.Namespace) -> None:
    """Select a chat session as the current session."""
    try:
        session = ctx.chat_session_service.get_session(args.session_id)

        if not session:
            print(f"Error: Chat session {args.session_id} not found", file=sys.stderr)
            sys.exit(1)

        ctx.state_repo.set_current_session(session.id)
        print(f"Selected [{session.id}] {session.title or f'Session {session.id}'}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to select chat session: {e}")
        sys.exit(1)


def cmd_delete(ctx: AppContext, args: argparse.Namespace) -> None:
    """Delete a chat session."""
    try:
        session = ctx.chat_session_service.get_session(args.session_id)

        if not session:
            print(f"Error: Chat session {args.session_id} not found", file=sys.stderr)
            sys.exit(1)

        # Confirm deletion
        confirm = input(f"Delete '{session.title or f'Session {session.id}'}? (yes/no): ").strip().lower()
        if confirm not in ["yes", "y"]:
            print("Cancelled")
            return

        deleted = ctx.chat_session_service.delete_session(args.session_id)
        if deleted:
            print(f"Deleted [{session.id}] {session.title or f'Session {session.id}'}")
        else:
            print("Error: Failed to delete session", file=sys.stderr)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to delete chat session: {e}")
        sys.exit(1)
