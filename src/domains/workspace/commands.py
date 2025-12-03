"""Workspace CLI commands."""

import argparse
import sys

from returns.result import Failure

from src.context import AppContext
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def cmd_list(ctx: AppContext, args: argparse.Namespace) -> None:
    """List all workspace."""
    try:
        workspaces = ctx.workspace_repo.get_all()
        if not workspaces:
            print("No workspace found")
            return

        for ws in workspaces:
            selected = " (SELECTED)" if ws.id == ctx.current_workspace_id else ""
            print(f"[{ws.id}] {ws.name}{selected}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to list workspace: {e}")
        sys.exit(1)


def cmd_new(ctx: AppContext, args: argparse.Namespace) -> None:
    """Create a new workspace (interactive)."""
    try:
        # Get default RAG config
        default_config = ctx.default_rag_config_service.get_config()

        # Auto-create default config if it doesn't exist
        if not default_config:
            logger.info("No default RAG config found, creating default configuration")
            default_config = ctx.default_rag_config_service.create_or_update_config(
                rag_type="vector",
                vector_config={},
                graph_config={},
            )

        default_rag_type = default_config.rag_type

        # Interactive prompts
        name = input("Workspace name: ").strip()
        if not name:
            print("Error: Name cannot be empty", file=sys.stderr)
            sys.exit(1)

        description = input("Description (optional): ").strip() or None

        rag_type = (
            input(f"RAG type (vector/graph) [{default_rag_type}]: ").strip() or default_rag_type
        )
        if rag_type not in ["vector", "graph"]:
            print("Error: RAG type must be 'vector' or 'graph'", file=sys.stderr)
            sys.exit(1)

        # Create workspace using service
        result = ctx.workspace_service.create_workspace(
            name=name,
            description=description,
            rag_type=rag_type,
        )

        if isinstance(result, Failure):
            error = result.failure()
            print(f"Error: {error.message}", file=sys.stderr)
            sys.exit(1)

        workspace = result.unwrap()
        print(f"Created workspace [{workspace.id}] {workspace.name}")

    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to create workspace: {e}", exc_info=True)
        sys.exit(1)


def cmd_show(ctx: AppContext, args: argparse.Namespace) -> None:
    """Show detailed information about a workspace."""
    try:
        workspace = ctx.workspace_service.get_workspace(args.workspace_id)
        if not workspace:
            print(f"Error: Workspace {args.workspace_id} not found", file=sys.stderr)
            sys.exit(1)

        print(f"ID: {workspace.id}")
        print(f"Name: {workspace.name}")
        print(f"RAG Type: {workspace.rag_type}")
        print(f"Status: {workspace.status}")
        if workspace.description:
            print(f"Description: {workspace.description}")
        print(f"Created: {workspace.created_at}")
        print(f"Updated: {workspace.updated_at}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to show workspace: {e}")
        sys.exit(1)


def cmd_update(ctx: AppContext, args: argparse.Namespace) -> None:
    """Update a workspace (interactive)."""
    try:
        workspace = ctx.workspace_service.get_workspace(args.workspace_id)
        if not workspace:
            print(f"Error: Workspace {args.workspace_id} not found", file=sys.stderr)
            sys.exit(1)

        # Show current values and prompt for new ones
        print(f"Current name: {workspace.name}")
        name = input("New name (press Enter to keep): ").strip()

        print(f"Current description: {workspace.description or '(none)'}")
        description = input("New description (press Enter to keep): ").strip()

        # Only update if values were provided
        if not name and not description:
            print("No changes made")
            return

        result = ctx.workspace_service.update_workspace(
            args.workspace_id,
            name=name if name else None,
            description=description if description else None,
        )

        if isinstance(result, Failure):
            error = result.failure()
            print(f"Error: {error.message}", file=sys.stderr)
            sys.exit(1)

        updated = result.unwrap()
        print(f"Updated [{updated.id}] {updated.name}")

    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to update workspace: {e}")
        sys.exit(1)


def cmd_delete(ctx: AppContext, args: argparse.Namespace) -> None:
    """Delete a workspace."""
    try:
        workspace = ctx.workspace_service.get_workspace(args.workspace_id)
        if not workspace:
            print(f"Error: Workspace {args.workspace_id} not found", file=sys.stderr)
            sys.exit(1)

        # Confirm deletion
        confirm = (
            input(f"Delete workspace [{workspace.id}] {workspace.name}? (yes/no): ").strip().lower()
        )
        if confirm not in ["yes", "y"]:
            print("Cancelled")
            return

        deleted = ctx.workspace_service.delete_workspace(args.workspace_id)
        if deleted:
            print(f"Deleted [{workspace.id}] {workspace.name}")
        else:
            print("Error: Failed to delete workspace", file=sys.stderr)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to delete workspace: {e}")
        sys.exit(1)


def cmd_select(ctx: AppContext, args: argparse.Namespace) -> None:
    """Select a workspace as the current workspace."""
    try:
        workspace = ctx.workspace_repo.get_by_id(args.workspace_id)
        if not workspace:
            print(f"Error: Workspace {args.workspace_id} not found", file=sys.stderr)
            sys.exit(1)

        ctx.state_repo.set_current_workspace(workspace.id)
        print(f"Selected [{workspace.id}] {workspace.name}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to select workspace: {e}")
        sys.exit(1)
