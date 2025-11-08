"""
Command-line interface for the InsightHub RAG system.

This CLI uses the service layer (via AppContext) to avoid code duplication.
Both CLI and API use the same business logic.
"""

import argparse
import sys

from src.context import AppContext
from src.domains.chat import commands as chat_commands
from src.domains.documents import commands as doc_commands
from src.infrastructure.database import get_db, init_db


class CLIClient:
    """CLI client for interacting with InsightHub using the service layer."""

    def __init__(self) -> None:
        """Initialize the CLI client with application context."""
        # Initialize database
        init_db()

        # Create database session
        self.db = next(get_db())

        # Create application context with services
        self.context = AppContext(self.db)

    def close(self) -> None:
        """Close database session."""
        if self.db:
            self.db.close()


# Command handlers (delegate to domain command modules)


def cmd_upload(client: CLIClient, args: argparse.Namespace) -> None:
    """Upload a document."""
    doc_commands.cmd_upload(client.context, args)


def cmd_list(client: CLIClient, args: argparse.Namespace) -> None:
    """List all documents."""
    doc_commands.cmd_list(client.context, args)


def cmd_delete(client: CLIClient, args: argparse.Namespace) -> None:
    """Delete a document."""
    doc_commands.cmd_delete(client.context, args)


def cmd_chat(client: CLIClient, args: argparse.Namespace) -> None:
    """Send a chat message."""
    chat_commands.cmd_chat(client.context, args)


def cmd_sessions(client: CLIClient, args: argparse.Namespace) -> None:
    """List all chat sessions."""
    chat_commands.cmd_sessions(client.context, args)


def cmd_interactive(client: CLIClient, args: argparse.Namespace) -> None:
    """Start an interactive chat session."""
    chat_commands.cmd_interactive(client.context, args)


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="InsightHub RAG CLI")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a document to the system")
    upload_parser.add_argument("file", help="Path to the file to upload (PDF or TXT)")

    # List documents command
    subparsers.add_parser("list", help="List all documents in the system")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a document")
    delete_parser.add_argument("doc_id", type=int, help="Document ID to delete")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Send a chat message")
    chat_parser.add_argument("message", help="The question or message to send")
    chat_parser.add_argument("--session-id", type=int, help="Optional session ID for context")
    chat_parser.add_argument(
        "--show-context", action="store_true", help="Show retrieved context chunks"
    )

    # List sessions command
    subparsers.add_parser("sessions", help="List all chat sessions")

    # Interactive command
    subparsers.add_parser("interactive", help="Start an interactive chat session")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Create client
    client = CLIClient()

    try:
        # Execute command
        commands = {
            "upload": cmd_upload,
            "list": cmd_list,
            "delete": cmd_delete,
            "chat": cmd_chat,
            "sessions": cmd_sessions,
            "interactive": cmd_interactive,
        }

        command_func = commands.get(args.command)
        if command_func:
            command_func(client, args)
        else:
            parser.print_help()
            sys.exit(1)
    finally:
        # Always close database session
        client.close()


if __name__ == "__main__":
    main()
