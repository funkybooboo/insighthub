"""State CLI commands."""

import argparse
import sys

from returns.result import Failure

from src.context import AppContext
from src.infrastructure.cli_io import IO
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def cmd_show(ctx: AppContext, args: argparse.Namespace) -> None:
    """Show current state (selected workspace and session)."""
    try:
        # Call orchestrator
        result = ctx.state_orchestrator.get_current_state()

        if isinstance(result, Failure):
            error = result.failure()
            message = error.message if hasattr(error, "message") else str(error)
            IO.print_error(f"Error: {message}")
            sys.exit(1)

        response = result.unwrap()

        # Present state
        IO.print("Current State:")
        IO.print("")

        if response.current_workspace_id:
            workspace_info = f"[{response.current_workspace_id}]"
            if response.current_workspace_name:
                workspace_info += f" {response.current_workspace_name}"
            IO.print(f"  Workspace: {workspace_info}")
        else:
            IO.print("  Workspace: None selected")

        if response.current_session_id:
            session_info = f"[{response.current_session_id}]"
            if response.current_session_title:
                session_info += f" {response.current_session_title}"
            IO.print(f"  Session: {session_info}")
        else:
            IO.print("  Session: None selected")

    except Exception as e:
        IO.print_error(f"Error: {e}")
        logger.error(f"Failed to show state: {e}")
        sys.exit(1)
