"""Document CLI commands."""

import argparse
import sys
from pathlib import Path

from src.context import AppContext
from src.domains.workspace.document.dtos import (
    DeleteDocumentRequest,
    ShowDocumentRequest,
    UploadDocumentRequest,
)
from src.infrastructure.logger import create_logger
from src.infrastructure.types import ResultHandler

logger = create_logger(__name__)


def cmd_list(ctx: AppContext, args: argparse.Namespace) -> None:
    """List documents in the current workspace."""
    try:
        if not ctx.current_workspace_id:
            print(
                "Error: No workspace selected. Use 'workspace select <id>' first", file=sys.stderr
            )
            sys.exit(1)

        # === Call Orchestrator ===
        result = ctx.document_orchestrator.list_documents(ctx.current_workspace_id)

        # === Handle Result (CLI-specific output) ===
        responses = ResultHandler.unwrap_or_exit(result, "list documents")
        if not responses:
            print("No documents found")
            return

        for response in responses:
            print(f"[{response.id}] {response.filename}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to list documents: {e}")
        sys.exit(1)


def cmd_show(ctx: AppContext, args: argparse.Namespace) -> None:
    """Show detailed information about a document."""
    try:
        if not ctx.current_workspace_id:
            print(
                "Error: No workspace selected. Use 'workspace select <id>' first", file=sys.stderr
            )
            sys.exit(1)

        # === Create Request DTO ===
        request = ShowDocumentRequest(
            document_id=args.document_id, workspace_id=ctx.current_workspace_id
        )

        # === Call Orchestrator ===
        result = ctx.document_orchestrator.show_document(request)

        # === Handle Result (CLI-specific output) ===
        response = ResultHandler.unwrap_or_exit(result, "show document")

        print(f"ID: {response.id}")
        print(f"Filename: {response.filename}")
        print(f"Status: {response.status}")
        print(f"Size: {response.file_size} bytes")
        print(f"MIME Type: {response.mime_type}")
        print(f"Chunks: {response.chunk_count if response.chunk_count else 0}")
        print(f"Hash: {response.content_hash}")
        print(f"Uploaded: {response.created_at}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to show document: {e}")
        sys.exit(1)


def cmd_upload(ctx: AppContext, args: argparse.Namespace) -> None:
    """Upload a document to the current workspace."""
    try:
        if not ctx.current_workspace_id:
            print(
                "Error: No workspace selected. Use 'workspace select <id>' first", file=sys.stderr
            )
            sys.exit(1)

        file_path = Path(args.file)

        # === Create Request DTO ===
        request = UploadDocumentRequest(
            workspace_id=ctx.current_workspace_id,
            filename=file_path.name,
            file_path=str(file_path),
        )

        print(f"Uploading {file_path.name}...")

        # === Call Orchestrator ===
        result = ctx.document_orchestrator.upload_document(request)

        # === Handle Result (CLI-specific output) ===
        response = ResultHandler.unwrap_or_exit(result, "upload document")
        print(f"Uploaded [{response.id}] {response.filename}")

    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to upload document: {e}", exc_info=True)
        sys.exit(1)


def cmd_remove(ctx: AppContext, args: argparse.Namespace) -> None:
    """Remove a document by filename."""
    try:
        if not ctx.current_workspace_id:
            print(
                "Error: No workspace selected. Use 'workspace select <id>' first", file=sys.stderr
            )
            sys.exit(1)

        # Find document by filename
        documents = ctx.document_service.list_documents_by_workspace(ctx.current_workspace_id)
        doc_to_remove = None
        for doc in documents:
            if doc.filename == args.filename:
                doc_to_remove = doc
                break

        if not doc_to_remove:
            print(f"Error: Document '{args.filename}' not found", file=sys.stderr)
            sys.exit(1)

        # Confirm deletion
        confirm = input(f"Delete '{args.filename}'? (yes/no): ").strip().lower()
        if confirm not in ["yes", "y"]:
            print("Cancelled")
            return

        # === Create Request DTO ===
        request = DeleteDocumentRequest(
            document_id=doc_to_remove.id, workspace_id=ctx.current_workspace_id
        )

        # === Call Orchestrator ===
        result = ctx.document_orchestrator.delete_document(request)

        # === Handle Result (CLI-specific output) ===
        deleted = ResultHandler.unwrap_or_exit(result, "delete document")
        if deleted:
            print(f"Deleted [{doc_to_remove.id}] {args.filename}")
        else:
            print("Error: Failed to delete document", file=sys.stderr)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to remove document: {e}")
        sys.exit(1)
