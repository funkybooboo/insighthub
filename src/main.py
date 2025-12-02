"""InsightHub CLI - Main entry point and routing."""

import argparse
import sys

from src.context import AppContext
from src.domains.default_rag_configs import commands as default_rag_config_commands
from src.domains.workspaces import commands as workspace_commands
from src.domains.workspaces.chats.messages import commands as chat_message_commands
from src.domains.workspaces.chats.sessions import commands as chat_session_commands
from src.domains.workspaces.documents import commands as document_commands


def main() -> None:
    """Main CLI entry point - argument parsing and routing."""
    # Custom help epilog with examples
    epilog = """
Examples:
  # Workspace management
  python -m src.main workspace list              List all workspaces
  python -m src.main workspace new               Create a new workspace (interactive)
  python -m src.main workspace select 1          Select workspace with ID 1

  # Document management
  python -m src.main document list               List documents in current workspace
  python -m src.main document upload file.pdf    Upload a document
  python -m src.main document remove file.pdf    Remove a document

  # Chat operations
  python -m src.main chat list                   List chat sessions
  python -m src.main chat new                    Create a new chat session
  python -m src.main chat select 1               Select chat session with ID 1
  python -m src.main chat send "Hello"           Send a message to current session
  python -m src.main chat history                Show message history for current session
  python -m src.main chat delete 1               Delete a chat session

  # Configuration
  python -m src.main default-rag-config list     Show default RAG configuration
  python -m src.main default-rag-config new      Create/update default RAG config

For help on a specific resource, use:
  python -m src.main <resource> --help
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
        description="Manage workspaces for organizing documents and chat sessions",
    )
    ws_subparsers = ws_parser.add_subparsers(dest="action", help="Workspace action")

    ws_list = ws_subparsers.add_parser("list", help="List all workspaces")
    ws_show = ws_subparsers.add_parser("show", help="Show detailed workspace information")
    ws_show.add_argument("workspace_id", type=int, help="Workspace ID")
    ws_new = ws_subparsers.add_parser("new", help="Create new workspace (interactive)")
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
        description="Manage documents within the current workspace",
    )
    doc_subparsers = doc_parser.add_subparsers(dest="action", help="Document action")

    doc_list = doc_subparsers.add_parser("list", help="List documents in current workspace")
    doc_upload = doc_subparsers.add_parser("upload", help="Upload a document")
    doc_upload.add_argument("file", help="Path to document file")
    doc_remove = doc_subparsers.add_parser("remove", help="Remove a document")
    doc_remove.add_argument("filename", help="Document filename to remove")

    # ==================== CHAT ====================
    chat_parser = subparsers.add_parser(
        "chat",
        help="Chat operations",
        description="Manage chat sessions and messages within the current workspace",
    )
    chat_subparsers = chat_parser.add_subparsers(dest="action", help="Chat action")

    chat_list = chat_subparsers.add_parser("list", help="List chat sessions in current workspace")
    chat_new = chat_subparsers.add_parser("new", help="Create new chat session (interactive)")
    chat_select = chat_subparsers.add_parser("select", help="Select a chat session")
    chat_select.add_argument("session_id", type=int, help="Chat session ID")
    chat_delete = chat_subparsers.add_parser("delete", help="Delete a chat session")
    chat_delete.add_argument("session_id", type=int, help="Chat session ID to delete")
    chat_send = chat_subparsers.add_parser("send", help="Send a message in current session")
    chat_send.add_argument("message", help="Message text to send")
    chat_history = chat_subparsers.add_parser(
        "history", help="Show message history for current session"
    )

    # ==================== DEFAULT RAG CONFIG ====================
    rag_config_parser = subparsers.add_parser(
        "default-rag-config",
        help="Default RAG configuration",
        description="Manage default RAG configuration settings",
    )
    rag_config_subparsers = rag_config_parser.add_subparsers(
        dest="action", help="RAG config action"
    )

    rag_config_list = rag_config_subparsers.add_parser("list", help="Show default RAG config")
    rag_config_new = rag_config_subparsers.add_parser(
        "new", help="Create/update default RAG config (interactive)"
    )

    # Parse arguments, but handle help specially
    args = parser.parse_args()

    # Show help if no resource specified
    if not args.resource:
        parser.print_help()
        sys.exit(0)

    # Initialize context
    ctx = AppContext()

    # Route to command handlers
    if args.resource == "workspace":
        if not args.action:
            ws_parser.print_help()
            sys.exit(0)
        elif args.action == "list":
            workspace_commands.cmd_list(ctx, args)
        elif args.action == "show":
            workspace_commands.cmd_show(ctx, args)
        elif args.action == "new":
            workspace_commands.cmd_new(ctx, args)
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
        elif args.action == "upload":
            document_commands.cmd_upload(ctx, args)
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
        elif args.action == "new":
            chat_session_commands.cmd_new(ctx, args)
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
        elif args.action == "list":
            default_rag_config_commands.cmd_list(ctx, args)
        elif args.action == "new":
            default_rag_config_commands.cmd_new(ctx, args)
        else:
            print(f"Error: Unknown default-rag-config action '{args.action}'\n")
            rag_config_parser.print_help()
            sys.exit(1)

    else:
        print(f"Error: Unknown resource '{args.resource}'\n")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
