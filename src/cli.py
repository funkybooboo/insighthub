"""InsightHub CLI - Main entry point and routing."""

import argparse
import atexit
import signal
import sys
from typing import Optional

from src.context import AppContext
from src.domains.default_rag_config import commands as default_rag_config_commands
from src.domains.rag_options import commands as rag_options_commands
from src.domains.state import commands as state_commands
from src.domains.workspace import commands as workspace_commands
from src.domains.workspace.chat.message import commands as chat_message_commands
from src.domains.workspace.chat.session import commands as chat_session_commands
from src.domains.workspace.document import commands as document_commands
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)

# Global context for cleanup
_app_context: Optional[AppContext] = None


def cleanup_handler() -> None:
    """Handle cleanup on application exit."""
    global _app_context
    if _app_context is not None:
        logger.info("Application shutting down...")
        _app_context.cleanup()


def signal_handler(signum: int, frame: object) -> None:
    """Handle interrupt signals for graceful shutdown."""
    signal_name = signal.Signals(signum).name
    logger.info(f"Received signal {signal_name}, shutting down gracefully...")
    cleanup_handler()
    sys.exit(0)


def main() -> None:
    """Main CLI entry point - argument parsing and routing."""
    # Custom help epilog with examples
    epilog = """
Examples:
  # Workspace management
  python -m src.cli workspace list              List all workspace
  python -m src.cli workspace create            Create a new workspace (interactive)
  python -m src.cli workspace select 1          Select workspace with ID 1

  # Document management
  python -m src.cli document list               List document in current workspace
  python -m src.cli document show 1             Show detailed information about document with ID 1
  python -m src.cli document add file.pdf       Add a document to current workspace
  python -m src.cli document remove file.pdf    Remove a document from current workspace

  # Chat operations
  python -m src.cli chat list                   List chat sessions in current workspace
  python -m src.cli chat create                 Create a new chat session in current workspace
  python -m src.cli chat select 1               Select chat session with ID 1
  python -m src.cli chat send "Hello"           Send a message to current session
  python -m src.cli chat history                Show message history for current session
  python -m src.cli chat delete 1               Delete a chat session

  # Configuration
  python -m src.cli default-rag-config show     Show default RAG configuration
  python -m src.cli default-rag-config create   Create/update default RAG config (interactive)

  # State
  python -m src.cli state show                  Show current state (selected workspace/session)

  # RAG Options
  python -m src.cli rag-options list            List all available RAG options

For help on a specific resource, use:
  python -m src.cli <resource> --help
"""

    parser = argparse.ArgumentParser(
        prog="insighthub",
        description="InsightHub CLI - Chat-centric RAG interface",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="resource", help="Resource to manage")

    # ==================== WORKSPACE ====================
    ws_parser = subparsers.add_parser(
        "workspace",
        help="Workspace operations",
        description="Manage workspace for organizing document and chat session",
    )
    ws_subparsers = ws_parser.add_subparsers(dest="action", help="Workspace action")

    ws_subparsers.add_parser("list", help="List all workspace")
    ws_show = ws_subparsers.add_parser("show", help="Show detailed workspace information")
    ws_show.add_argument("workspace_id", type=int, help="Workspace ID")
    ws_subparsers.add_parser("create", help="Create new workspace (interactive)")
    ws_update = ws_subparsers.add_parser("update", help="Update workspace (interactive)")
    ws_update.add_argument("workspace_id", type=int, help="Workspace ID")
    ws_delete = ws_subparsers.add_parser("delete", help="Delete workspace")
    ws_delete.add_argument("workspace_id", type=int, help="Workspace ID")
    ws_select = ws_subparsers.add_parser("select", help="Select a workspace")
    ws_select.add_argument("workspace_id", type=int, help="Workspace ID")

    # ==================== DOCUMENT ====================
    doc_parser = subparsers.add_parser(
        "document",
        help="Document operations",
        description="Manage document within the current workspace",
    )
    doc_subparsers = doc_parser.add_subparsers(dest="action", help="Document action")

    doc_list = doc_subparsers.add_parser("list", help="List document in current workspace")
    doc_list.add_argument(
        "--workspace-id", type=int, help="Workspace ID (overrides selected workspace)"
    )
    doc_show = doc_subparsers.add_parser("show", help="Show detailed document information")
    doc_show.add_argument("document_id", type=int, help="Document ID")
    doc_show.add_argument(
        "--workspace-id", type=int, help="Workspace ID (overrides selected workspace)"
    )
    doc_add = doc_subparsers.add_parser("add", help="Add a document")
    doc_add.add_argument("file", help="Path to document file")
    doc_add.add_argument(
        "--workspace-id", type=int, help="Workspace ID (overrides selected workspace)"
    )
    doc_remove = doc_subparsers.add_parser("remove", help="Remove a document")
    doc_remove.add_argument("filename", help="Document filename to remove")
    doc_remove.add_argument(
        "--workspace-id", type=int, help="Workspace ID (overrides selected workspace)"
    )

    # ==================== CHAT ====================
    chat_parser = subparsers.add_parser(
        "chat",
        help="Chat operations",
        description="Manage chat session and message in the current workspace",
    )
    chat_subparsers = chat_parser.add_subparsers(dest="action", help="Chat action")

    chat_list = chat_subparsers.add_parser("list", help="List chat session in current workspace")
    chat_list.add_argument(
        "--workspace-id", type=int, help="Workspace ID (overrides selected workspace)"
    )
    chat_create = chat_subparsers.add_parser("create", help="Create new chat session in current workspace (interactive)")
    chat_create.add_argument(
        "--workspace-id", type=int, help="Workspace ID (overrides selected workspace)"
    )
    chat_select = chat_subparsers.add_parser("select", help="Select a chat session")
    chat_select.add_argument("session_id", type=int, help="Chat session ID")
    chat_delete = chat_subparsers.add_parser("delete", help="Delete a chat session")
    chat_delete.add_argument("session_id", type=int, help="Chat session ID to delete")
    chat_send = chat_subparsers.add_parser("send", help="Send a message in current session")
    chat_send.add_argument("message", help="Message text to send")
    chat_subparsers.add_parser("history", help="Show message history for current session")

    # ==================== DEFAULT RAG CONFIG ====================
    rag_config_parser = subparsers.add_parser(
        "default-rag-config",
        help="Default RAG configuration",
        description="Manage default RAG configuration settings",
    )
    rag_config_subparsers = rag_config_parser.add_subparsers(
        dest="action", help="RAG config action"
    )

    rag_config_subparsers.add_parser("show", help="Show default RAG config")
    rag_config_subparsers.add_parser(
        "create", help="Create/update default RAG config (interactive)"
    )

    # ==================== STATE ====================
    state_parser = subparsers.add_parser(
        "state",
        help="Application state",
        description="Query current application state (selected workspace/session)",
    )
    state_subparsers = state_parser.add_subparsers(dest="action", help="State action")

    state_subparsers.add_parser("show", help="Show current state")

    # ==================== RAG OPTIONS ====================
    rag_options_parser = subparsers.add_parser(
        "rag-options",
        help="RAG options",
        description="View available RAG algorithms and configurations",
    )
    rag_options_subparsers = rag_options_parser.add_subparsers(
        dest="action", help="RAG options action"
    )

    rag_options_subparsers.add_parser("list", help="List all available RAG options")

    # Parse arguments, but handle help specially
    args = parser.parse_args()

    # Show help if no resource specified
    if not args.resource:
        parser.print_help()
        sys.exit(0)

    # Register cleanup handlers
    atexit.register(cleanup_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize context
    global _app_context
    try:
        logger.info("Initializing InsightHub application...")
        ctx = AppContext()
        _app_context = ctx
        logger.info("Application initialized successfully")

        # Run startup health checks
        if not ctx.startup_checks():
            logger.error("Startup health checks failed")
            print("Error: Critical startup checks failed. Check logs for details.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        print(f"Error: Failed to initialize application: {e}")
        sys.exit(1)

    # Route to command handlers (wrapped in try-catch for proper cleanup)
    try:
        route_command(
            ctx,
            args,
            parser,
            ws_parser,
            doc_parser,
            chat_parser,
            rag_config_parser,
            state_parser,
            rag_options_parser,
        )
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error during command execution: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)


def route_command(
    ctx: AppContext,
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    ws_parser: argparse.ArgumentParser,
    doc_parser: argparse.ArgumentParser,
    chat_parser: argparse.ArgumentParser,
    rag_config_parser: argparse.ArgumentParser,
    state_parser: argparse.ArgumentParser,
    rag_options_parser: argparse.ArgumentParser,
) -> None:
    """Route commands to appropriate handlers."""
    if args.resource == "workspace":
        if not args.action:
            ws_parser.print_help()
            sys.exit(0)
        elif args.action == "list":
            workspace_commands.cmd_list(ctx, args)
        elif args.action == "show":
            workspace_commands.cmd_show(ctx, args)
        elif args.action == "create":
            workspace_commands.cmd_create(ctx, args)
        elif args.action == "update":
            workspace_commands.cmd_update(ctx, args)
        elif args.action == "delete":
            workspace_commands.cmd_delete(ctx, args)
        elif args.action == "select":
            workspace_commands.cmd_select(ctx, args)
        else:
            print(f"Error: Unknown workspace action '{args.action}'\n")
            ws_parser.print_help()
            sys.exit(1)

    elif args.resource == "document":
        if not args.action:
            doc_parser.print_help()
            sys.exit(0)
        elif args.action == "list":
            document_commands.cmd_list(ctx, args)
        elif args.action == "show":
            document_commands.cmd_show(ctx, args)
        elif args.action == "add":
            document_commands.cmd_add(ctx, args)
        elif args.action == "remove":
            document_commands.cmd_remove(ctx, args)
        else:
            print(f"Error: Unknown document action '{args.action}'\n")
            doc_parser.print_help()
            sys.exit(1)

    elif args.resource == "chat":
        if not args.action:
            chat_parser.print_help()
            sys.exit(0)
        elif args.action == "list":
            chat_session_commands.cmd_list(ctx, args)
        elif args.action == "create":
            chat_session_commands.cmd_create(ctx, args)
        elif args.action == "select":
            chat_session_commands.cmd_select(ctx, args)
        elif args.action == "delete":
            chat_session_commands.cmd_delete(ctx, args)
        elif args.action == "send":
            chat_message_commands.cmd_send(ctx, args)
        elif args.action == "history":
            chat_message_commands.cmd_list(ctx, args)
        else:
            print(f"Error: Unknown chat action '{args.action}'\n")
            chat_parser.print_help()
            sys.exit(1)

    elif args.resource == "default-rag-config":
        if not args.action:
            rag_config_parser.print_help()
            sys.exit(0)
        elif args.action == "show":
            default_rag_config_commands.cmd_show(ctx, args)
        elif args.action == "create":
            default_rag_config_commands.cmd_create(ctx, args)
        else:
            print(f"Error: Unknown default-rag-config action '{args.action}'\n")
            rag_config_parser.print_help()
            sys.exit(1)

    elif args.resource == "state":
        if not args.action:
            state_parser.print_help()
            sys.exit(0)
        elif args.action == "show":
            state_commands.cmd_show(ctx, args)
        else:
            print(f"Error: Unknown state action '{args.action}'\n")
            state_parser.print_help()
            sys.exit(1)

    elif args.resource == "rag-options":
        if not args.action:
            rag_options_parser.print_help()
            sys.exit(0)
        elif args.action == "list":
            rag_options_commands.cmd_list(ctx, args)
        else:
            print(f"Error: Unknown rag-options action '{args.action}'\n")
            rag_options_parser.print_help()
            sys.exit(1)

    else:
        print(f"Error: Unknown resource '{args.resource}'\n")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
