"""Workspace CLI commands."""

import argparse
import sys

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.workflows.factory import create_provision_workflow

logger = create_logger(__name__)


def cmd_list(ctx: object, args: argparse.Namespace) -> None:
    """List all workspaces."""
    try:
        workspaces = ctx.workspace_repo.get_all()
        if not workspaces:
            print("No workspaces found")
            return

        print("\nWorkspaces:")
        print("=" * 80)
        for ws in workspaces:
            selected = " (SELECTED)" if ws.id == ctx.current_workspace_id else ""
            print(f"[{ws.id}] {ws.name}{selected}")
            print(f"    Status: {ws.status} | RAG Type: {ws.rag_type}")
            if ws.description:
                print(f"    Description: {ws.description}")
            print(f"    Created: {ws.created_at}")
            print("-" * 80)

    except Exception as e:
        logger.error(f"Failed to list workspaces: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def cmd_new(ctx: object, args: argparse.Namespace) -> None:
    """Create a new workspace (interactive)."""
    try:
        # Interactive prompts
        name = input("Workspace name: ").strip()
        if not name:
            print("Error: Name cannot be empty")
            sys.exit(1)

        description = input("Description (optional): ").strip() or None

        rag_type = input("RAG type (vector/graph) [vector]: ").strip() or "vector"
        if rag_type not in ["vector", "graph"]:
            print("Error: RAG type must be 'vector' or 'graph'")
            sys.exit(1)

        # Create workspace
        print(f"\nCreating workspace '{name}'...")
        workspace = ctx.workspace_repo.create(
            name=name,
            description=description,
            rag_type=rag_type,
            rag_config=None,
            status="provisioning",
        )

        logger.info(f"Workspace created: id={workspace.id}")

        # Provision RAG resources
        print("Provisioning RAG resources...")
        provision_workflow = create_provision_workflow(
            rag_type=rag_type, rag_config=workspace.rag_config or {}
        )

        result = provision_workflow.execute(
            workspace_id=str(workspace.id),
            rag_config=workspace.rag_config or {},
        )

        if result.is_ok():
            ctx.workspace_repo.update(workspace.id, status="ready")
            logger.info(f"Workspace {workspace.id} ready")
            print(f"\nWorkspace created successfully!")
            print(f"  ID: {workspace.id}")
            print(f"  Name: {name}")
            print(f"  Status: ready")
        else:
            ctx.workspace_repo.update(workspace.id, status="failed")
            error = result.unwrap_err()
            logger.error(f"Provisioning failed: {error}")
            print(f"Error: Provisioning failed - {error}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to create workspace: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)


def cmd_select(ctx: object, args: argparse.Namespace) -> None:
    """Select a workspace as the current workspace."""
    try:
        workspace = ctx.workspace_repo.get_by_id(args.workspace_id)
        if not workspace:
            print(f"Error: Workspace {args.workspace_id} not found")
            sys.exit(1)

        ctx.current_workspace_id = workspace.id
        print(f"Selected workspace: [{workspace.id}] {workspace.name}")

    except Exception as e:
        logger.error(f"Failed to select workspace: {e}")
        print(f"Error: {e}")
        sys.exit(1)
