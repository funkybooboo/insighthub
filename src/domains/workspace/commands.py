"""Workspace CLI commands."""

import argparse
import sys

from pydantic import ValidationError as PydanticValidationError
from returns.result import Failure

from src.context import AppContext
from src.domains.workspace.dtos import (
    CreateWorkspaceRequest,
    DeleteWorkspaceRequest,
    SelectWorkspaceRequest,
    ShowWorkspaceRequest,
    UpdateWorkspaceRequest,
)
from src.infrastructure.cli_io import IO
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def cmd_list(ctx: AppContext, args: argparse.Namespace) -> None:
    """List all workspace."""
    try:
        # Call orchestrator
        result = ctx.workspace_orchestrator.list_workspaces()

        if isinstance(result, Failure):
            error = result.failure()
            message = error.message if hasattr(error, "message") else str(error)
            IO.print_error(f"Error: {message}")
            sys.exit(1)

        responses = result.unwrap()

        if not responses:
            IO.print("No workspace found")
            return

        for ws in responses:
            selected = " (SELECTED)" if ws.id == ctx.current_workspace_id else ""
            IO.print(f"[{ws.id}] {ws.name}{selected}")

    except Exception as e:
        IO.print_error(f"Error: {e}")
        logger.error(f"Failed to list workspaces: {e}")
        sys.exit(1)


def cmd_new(ctx: AppContext, args: argparse.Namespace) -> None:
    """Create a new workspace (interactive)."""
    try:
        # Get default RAG config for default values
        default_config = ctx.default_rag_config_service.get_config()
        if not default_config:
            logger.info("No default RAG config found, creating default configuration")
            default_config = ctx.default_rag_config_service.create_or_update_config(
                rag_type="vector",
                vector_config={},
                graph_config={},
            )

        default_rag_type = default_config.rag_type

        # Get available options from service
        options_result = ctx.rag_options_orchestrator.get_all_options()
        if isinstance(options_result, Failure):
            error = options_result.failure()
            message = error.message if hasattr(error, "message") else str(error)
            IO.print_error(f"Error: {message}")
            sys.exit(1)

        options = options_result.unwrap()

        # Gather input
        name = IO.input("Workspace name: ").strip()
        description = IO.input("Description (optional): ").strip() or None

        # Show available RAG types
        IO.print("\nAvailable RAG types:")
        for opt in options.rag_types:
            IO.print(f"  - {opt.value}: {opt.description}")
        IO.print("")

        rag_type_input = IO.input(f"RAG type [{default_rag_type}]: ").strip() or None

        # Create request DTO (Pydantic validates)
        request = CreateWorkspaceRequest(
            name=name,
            description=description,
            rag_type=rag_type_input,
        )

        # Call orchestrator
        result = ctx.workspace_orchestrator.create_workspace(request, default_rag_type)

        if isinstance(result, Failure):
            error = result.failure()
            message = error.message if hasattr(error, "message") else str(error)
            IO.print_error(f"Error: {message}")
            sys.exit(1)

        response = result.unwrap()
        IO.print(f"Created workspace [{response.id}] {response.name}")

    except KeyboardInterrupt:
        IO.print("\nCancelled")
        sys.exit(0)
    except PydanticValidationError as e:
        IO.print_error("\nValidation errors:")
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            IO.print_error(f"  {field}: {message}")
        sys.exit(1)
    except Exception as e:
        IO.print_error(f"Error: {e}")
        logger.error(f"Failed to create workspace: {e}", exc_info=True)
        sys.exit(1)


def cmd_show(ctx: AppContext, args: argparse.Namespace) -> None:
    """Show detailed information about a workspace."""
    try:
        # Create Request DTO with Pydantic validation
        request = ShowWorkspaceRequest(workspace_id=args.workspace_id)

        # Call orchestrator to get workspace
        workspace_result = ctx.workspace_orchestrator.show_workspace(request)

        if isinstance(workspace_result, Failure):
            error = workspace_result.failure()
            message = error.message if hasattr(error, "message") else str(error)
            IO.print_error(f"Error: {message}")
            sys.exit(1)

        response = workspace_result.unwrap()

        # Present workspace details
        IO.print(f"ID: {response.id}")
        IO.print(f"Name: {response.name}")
        IO.print(f"RAG Type: {response.rag_type}")
        IO.print(f"Status: {response.status}")
        if response.description:
            IO.print(f"Description: {response.description}")
        IO.print(f"Created: {response.created_at}")
        IO.print(f"Updated: {response.updated_at}")

        # Get RAG config via orchestrator
        config_result = ctx.workspace_orchestrator.get_workspace_rag_config(args.workspace_id)

        if isinstance(config_result, Failure):
            # Don't fail if config is missing, just skip display
            pass
        else:
            workspace, rag_config = config_result.unwrap()
            IO.print("")

            if workspace.rag_type == "vector":
                if rag_config:
                    IO.print("Vector RAG Configuration:")
                    IO.print(f"  Chunking Algorithm: {rag_config.chunking_algorithm}")
                    IO.print(f"  Chunk Size: {rag_config.chunk_size}")
                    IO.print(f"  Chunk Overlap: {rag_config.chunk_overlap}")
                    IO.print(f"  Embedding Algorithm: {rag_config.embedding_algorithm}")
                    IO.print(f"  Top K: {rag_config.top_k}")
                    IO.print(f"  Rerank Algorithm: {rag_config.rerank_algorithm}")
                else:
                    IO.print("Vector RAG Configuration: Not configured")
            elif workspace.rag_type == "graph":
                if rag_config:
                    IO.print("Graph RAG Configuration:")
                    IO.print(f"  Entity Extraction: {rag_config.entity_extraction_algorithm}")
                    IO.print(
                        f"  Relationship Extraction: {rag_config.relationship_extraction_algorithm}"
                    )
                    IO.print(f"  Clustering Algorithm: {rag_config.clustering_algorithm}")
                else:
                    IO.print("Graph RAG Configuration: Not configured")

    except PydanticValidationError as e:
        IO.print_error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        IO.print_error(f"Error: {e}")
        logger.error(f"Failed to show workspace: {e}")
        sys.exit(1)


def cmd_update(ctx: AppContext, args: argparse.Namespace) -> None:
    """Update a workspace (interactive)."""
    try:
        # Get workspace model via orchestrator for input gathering
        workspace_result = ctx.workspace_orchestrator.get_workspace_model(args.workspace_id)

        if isinstance(workspace_result, Failure):
            error = workspace_result.failure()
            message = error.message if hasattr(error, "message") else str(error)
            IO.print_error(f"Error: {message}")
            sys.exit(1)

        workspace = workspace_result.unwrap()

        # Gather input
        IO.print(f"Current name: {workspace.name}")
        name = IO.input("New name (press Enter to keep): ").strip() or None

        IO.print(f"Current description: {workspace.description or '(none)'}")
        description = IO.input("New description (press Enter to keep): ").strip() or None

        # Create request DTO (Pydantic validates)
        request = UpdateWorkspaceRequest(
            workspace_id=workspace.id,
            name=name,
            description=description,
        )

        # Call orchestrator
        result = ctx.workspace_orchestrator.update_workspace(request)

        if isinstance(result, Failure):
            error = result.failure()
            message = error.message if hasattr(error, "message") else str(error)
            IO.print_error(f"Error: {message}")
            sys.exit(1)

        response = result.unwrap()
        IO.print(f"Updated [{response.id}] {response.name}")

    except KeyboardInterrupt:
        IO.print("\nCancelled")
        sys.exit(0)
    except PydanticValidationError as e:
        IO.print_error("\nValidation errors:")
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            IO.print_error(f"  {field}: {message}")
        sys.exit(1)
    except Exception as e:
        IO.print_error(f"Error: {e}")
        logger.error(f"Failed to update workspace: {e}")
        sys.exit(1)


def cmd_delete(ctx: AppContext, args: argparse.Namespace) -> None:
    """Delete a workspace."""
    try:
        # Get workspace via orchestrator
        workspace_result = ctx.workspace_orchestrator.get_workspace_model(args.workspace_id)

        if isinstance(workspace_result, Failure):
            error = workspace_result.failure()
            message = error.message if hasattr(error, "message") else str(error)
            IO.print_error(f"Error: {message}")
            sys.exit(1)

        workspace = workspace_result.unwrap()

        # Confirm deletion
        if not IO.confirm(f"Delete workspace [{workspace.id}] {workspace.name}? (yes/no): "):
            IO.print("Cancelled")
            return

        # Create Request DTO with Pydantic validation
        request = DeleteWorkspaceRequest(workspace_id=args.workspace_id)

        # Call orchestrator
        result = ctx.workspace_orchestrator.delete_workspace(request)

        if isinstance(result, Failure):
            error = result.failure()
            message = error.message if hasattr(error, "message") else str(error)
            IO.print_error(f"Error: {message}")
            sys.exit(1)

        deleted = result.unwrap()
        if deleted:
            IO.print(f"Deleted [{workspace.id}] {workspace.name}")
        else:
            IO.print_error("Error: Failed to delete workspace")
            sys.exit(1)

    except PydanticValidationError as e:
        IO.print_error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        IO.print_error(f"Error: {e}")
        logger.error(f"Failed to delete workspace: {e}")
        sys.exit(1)


def cmd_select(ctx: AppContext, args: argparse.Namespace) -> None:
    """Select a workspace as the current workspace."""
    try:
        # Create Request DTO with Pydantic validation
        request = SelectWorkspaceRequest(workspace_id=args.workspace_id)

        # Call orchestrator
        result = ctx.workspace_orchestrator.select_workspace(request, ctx.state_repo)

        if isinstance(result, Failure):
            error = result.failure()
            message = error.message if hasattr(error, "message") else str(error)
            IO.print_error(f"Error: {message}")
            sys.exit(1)

        response = result.unwrap()
        IO.print(f"Selected [{response.id}] {response.name}")

    except PydanticValidationError as e:
        IO.print_error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        IO.print_error(f"Error: {e}")
        logger.error(f"Failed to select workspace: {e}")
        sys.exit(1)
