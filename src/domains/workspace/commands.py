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
from src.infrastructure.types import ResultHandler

logger = create_logger(__name__)


def cmd_list(ctx: AppContext, args: argparse.Namespace) -> None:
    """List all workspace."""
    try:
        # Call orchestrator
        result = ctx.workspace_orchestrator.list_workspaces()
        responses = ResultHandler.unwrap_or_exit(result, "list workspaces")

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


def cmd_create(ctx: AppContext, args: argparse.Namespace) -> None:
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
        options = ResultHandler.unwrap_or_exit(options_result, "get RAG options")

        # Gather input
        name = IO.input("Workspace name: ").strip()
        description = IO.input("Description (optional): ").strip() or None

        # Show available RAG types
        IO.print("\nAvailable RAG types:")
        for opt in options.rag_types:
            IO.print(f"  - {opt.value}: {opt.description}")
        IO.print("")

        rag_type_input = IO.input(f"RAG type [{default_rag_type}]: ").strip() or None
        rag_type = rag_type_input if rag_type_input else default_rag_type

        # Initialize RAG config fields
        chunking_algorithm = None
        chunk_size = None
        chunk_overlap = None
        embedding_algorithm = None
        top_k = None
        rerank_algorithm = None
        entity_extraction = None
        relationship_extraction = None
        clustering = None

        # Collect vector config if needed
        if rag_type == "vector":
            # Show available options
            IO.print("\nAvailable chunking algorithms:")
            for opt in options.chunking_algorithms:
                IO.print(f"  - {opt.value}: {opt.description}")

            IO.print("\nAvailable embedding algorithms:")
            for opt in options.embedding_algorithms:
                IO.print(f"  - {opt.value}: {opt.description}")

            IO.print("\nAvailable reranking algorithms:")
            for opt in options.rerank_algorithms:
                IO.print(f"  - {opt.value}: {opt.description}")
            IO.print("")

            # Prompt for vector RAG configuration with defaults from default config
            default_chunking = default_config.vector_config.chunking_algorithm
            chunking_algorithm = IO.input(f"Chunking algorithm [{default_chunking}]: ").strip() or None

            default_chunk_size = default_config.vector_config.chunk_size
            chunk_size_str = IO.input(f"Chunk size [{default_chunk_size}]: ").strip()
            chunk_size = int(chunk_size_str) if chunk_size_str else None

            default_chunk_overlap = default_config.vector_config.chunk_overlap
            chunk_overlap_str = IO.input(f"Chunk overlap [{default_chunk_overlap}]: ").strip()
            chunk_overlap = int(chunk_overlap_str) if chunk_overlap_str else None

            default_embedding = default_config.vector_config.embedding_algorithm
            embedding_algorithm = IO.input(f"Embedding algorithm [{default_embedding}]: ").strip() or None

            default_top_k = default_config.vector_config.top_k
            top_k_str = IO.input(f"Top K [{default_top_k}]: ").strip()
            top_k = int(top_k_str) if top_k_str else None

            default_reranking = default_config.vector_config.rerank_algorithm
            rerank_algorithm = IO.input(f"Rerank algorithm [{default_reranking}]: ").strip() or None

        else:  # graph
            # Show available options
            IO.print("\nAvailable entity extraction algorithms:")
            for opt in options.entity_extraction_algorithms:
                IO.print(f"  - {opt.value}: {opt.description}")

            IO.print("\nAvailable relationship extraction algorithms:")
            for opt in options.relationship_extraction_algorithms:
                IO.print(f"  - {opt.value}: {opt.description}")

            IO.print("\nAvailable clustering algorithms:")
            for opt in options.clustering_algorithms:
                IO.print(f"  - {opt.value}: {opt.description}")
            IO.print("")

            # Prompt for graph RAG configuration with defaults from default config
            default_entity = default_config.graph_config.entity_extraction_algorithm
            entity_extraction = (
                IO.input(f"Entity extraction algorithm [{default_entity}]: ").strip() or None
            )

            default_relationship = default_config.graph_config.relationship_extraction_algorithm
            relationship_extraction = (
                IO.input(f"Relationship extraction algorithm [{default_relationship}]: ").strip()
                or None
            )

            default_clustering = default_config.graph_config.clustering_algorithm
            clustering = IO.input(f"Clustering algorithm [{default_clustering}]: ").strip() or None

        # Create request DTO (Pydantic validates)
        request = CreateWorkspaceRequest(
            name=name,
            description=description,
            rag_type=rag_type_input,
            chunking_algorithm=chunking_algorithm,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            embedding_algorithm=embedding_algorithm,
            top_k=top_k,
            rerank_algorithm=rerank_algorithm,
            entity_extraction_algorithm=entity_extraction,
            relationship_extraction_algorithm=relationship_extraction,
            clustering_algorithm=clustering,
        )

        # Call orchestrator
        result = ctx.workspace_orchestrator.create_workspace(request, default_rag_type)
        response = ResultHandler.unwrap_or_exit(result, "create workspace")
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
        response = ResultHandler.unwrap_or_exit(workspace_result, "show workspace")

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
        workspace = ResultHandler.unwrap_or_exit(workspace_result, "get workspace")

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
        response = ResultHandler.unwrap_or_exit(result, "update workspace")
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
        workspace = ResultHandler.unwrap_or_exit(workspace_result, "get workspace")

        # Confirm deletion
        if not IO.confirm(f"Delete workspace [{workspace.id}] {workspace.name}? (yes/no): "):
            IO.print("Cancelled")
            return

        # Create Request DTO with Pydantic validation
        request = DeleteWorkspaceRequest(workspace_id=args.workspace_id)

        # Call orchestrator
        result = ctx.workspace_orchestrator.delete_workspace(request)
        deleted = ResultHandler.unwrap_or_exit(result, "delete workspace")
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
        response = ResultHandler.unwrap_or_exit(result, "select workspace")
        IO.print(f"Selected [{response.id}] {response.name}")

    except PydanticValidationError as e:
        IO.print_error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        IO.print_error(f"Error: {e}")
        logger.error(f"Failed to select workspace: {e}")
        sys.exit(1)
