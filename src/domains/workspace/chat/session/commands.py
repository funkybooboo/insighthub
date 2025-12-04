"""Chat session CLI commands."""

import argparse
import sys

from returns.result import Failure

from src.context import AppContext
from src.domains.workspace.chat.session.dtos import (
    CreateSessionRequest,
    DeleteSessionRequest,
    ListSessionsRequest,
    SelectSessionRequest,
)
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def cmd_list(ctx: AppContext, args: argparse.Namespace) -> None:
    """List chat sessions in the specified workspace."""
    try:
        # Check workspace exists
        workspace = ctx.workspace_repo.get_by_id(args.workspace_id)
        if not workspace:
            print(f"Error: Workspace {args.workspace_id} not found", file=sys.stderr)
            sys.exit(1)

        # === Create Request DTO ===
        request = ListSessionsRequest(workspace_id=args.workspace_id, skip=0, limit=50)

        # === Call Orchestrator ===
        result = ctx.session_orchestrator.list_sessions(request)

        # === Handle Result (CLI-specific output) ===
        if isinstance(result, Failure):
            error = result.failure()
            print(f"Error: {error.message}", file=sys.stderr)
            sys.exit(1)

        responses, total = result.unwrap()
        if not responses:
            print("No chat sessions found")
            return

        for response in responses:
            title = response.title or "(No title)"
            print(f"[{response.id}] {title}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to list chat sessions: {e}")
        sys.exit(1)


def cmd_new(ctx: AppContext, args: argparse.Namespace) -> None:
    """Create a new chat session (interactive)."""
    try:
        # Check workspace exists
        workspace = ctx.workspace_repo.get_by_id(args.workspace_id)
        if not workspace:
            print(f"Error: Workspace {args.workspace_id} not found", file=sys.stderr)
            sys.exit(1)

        # === CLI Interface: Gather user input ===
        title = input("Session title (optional): ").strip() or None

        # === Create Request DTO ===
        request = CreateSessionRequest(
            workspace_id=args.workspace_id,
            title=title,
            rag_type=workspace.rag_type,
        )

        # === Call Orchestrator ===
        result = ctx.session_orchestrator.create_session(request)

        # === Handle Result (CLI-specific output) ===
        if isinstance(result, Failure):
            error = result.failure()
            print(f"Error: {error.message}", file=sys.stderr)
            sys.exit(1)

        response = result.unwrap()
        print(f"Created chat session [{response.id}] {response.title or '(No title)'}")

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
        # === Create Request DTO ===
        request = SelectSessionRequest(session_id=args.session_id)

        # === Call Orchestrator ===
        result = ctx.session_orchestrator.select_session(request, ctx.state_repo)

        # === Handle Result (CLI-specific output) ===
        if isinstance(result, Failure):
            error = result.failure()
            print(f"Error: {error.message}", file=sys.stderr)
            sys.exit(1)

        response = result.unwrap()
        print(f"Selected [{response.id}] {response.title or f'Session {response.id}'}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to select chat session: {e}")
        sys.exit(1)


def cmd_delete(ctx: AppContext, args: argparse.Namespace) -> None:
    """Delete a chat session."""
    try:
        # Check session exists
        session = ctx.chat_session_service.get_session(args.session_id)
        if not session:
            print(f"Error: Chat session {args.session_id} not found", file=sys.stderr)
            sys.exit(1)

        # Confirm deletion
        confirm = (
            input(f"Delete '{session.title or f'Session {session.id}'}? (yes/no): ").strip().lower()
        )
        if confirm not in ["yes", "y"]:
            print("Cancelled")
            return

        # === Create Request DTO ===
        request = DeleteSessionRequest(session_id=args.session_id)

        # === Call Orchestrator ===
        result = ctx.session_orchestrator.delete_session(request)

        # === Handle Result (CLI-specific output) ===
        if isinstance(result, Failure):
            error = result.failure()
            print(f"Error: {error.message}", file=sys.stderr)
            sys.exit(1)

        deleted = result.unwrap()
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
