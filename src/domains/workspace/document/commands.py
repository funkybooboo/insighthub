"""Document CLI commands."""

import argparse
import sys
from io import BytesIO
from pathlib import Path

from src.context import AppContext
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def cmd_list(ctx: AppContext, args: argparse.Namespace) -> None:
    """List documents in the current workspace."""
    try:
        if not ctx.current_workspace_id:
            print("Error: No workspace selected. Use 'workspace select <id>' first", file=sys.stderr)
            sys.exit(1)

        documents = ctx.document_service.list_documents_by_workspace(ctx.current_workspace_id)
        if not documents:
            print("No documents found")
            return

        for doc in documents:
            print(f"[{doc.id}] {doc.filename}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to list documents: {e}")
        sys.exit(1)


def cmd_show(ctx: AppContext, args: argparse.Namespace) -> None:
    """Show detailed information about a document."""
    try:
        if not ctx.current_workspace_id:
            print("Error: No workspace selected. Use 'workspace select <id>' first", file=sys.stderr)
            sys.exit(1)

        document = ctx.document_service.get_document_by_id(args.document_id)
        if not document:
            print(f"Error: Document {args.document_id} not found", file=sys.stderr)
            sys.exit(1)

        # Verify document belongs to current workspace
        if document.workspace_id != ctx.current_workspace_id:
            print(f"Error: Document {args.document_id} not in current workspace", file=sys.stderr)
            sys.exit(1)

        print(f"ID: {document.id}")
        print(f"Filename: {document.filename}")
        print(f"Status: {document.status}")
        print(f"Size: {document.file_size} bytes")
        print(f"MIME Type: {document.mime_type}")
        print(f"Chunks: {document.chunk_count if document.chunk_count else 0}")
        print(f"Hash: {document.content_hash}")
        print(f"Uploaded: {document.created_at}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to show document: {e}")
        sys.exit(1)


def cmd_upload(ctx: AppContext, args: argparse.Namespace) -> None:
    """Upload a document to the current workspace."""
    try:
        if not ctx.current_workspace_id:
            print("Error: No workspace selected. Use 'workspace select <id>' first", file=sys.stderr)
            sys.exit(1)

        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)

        print(f"Uploading {file_path.name}...")

        # Read file content
        with open(file_path, "rb") as f:
            file_content = f.read()

        # Upload and process document through service
        document = ctx.document_service.upload_and_process_document(
            workspace_id=ctx.current_workspace_id,
            filename=file_path.name,
            file_content=file_content,
        )

        print(f"Uploaded [{document.id}] {document.filename}")

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
            print("Error: No workspace selected. Use 'workspace select <id>' first", file=sys.stderr)
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

        # Delete through service
        deleted = ctx.document_service.remove_document(doc_to_remove.id)
        if deleted:
            print(f"Deleted [{doc_to_remove.id}] {doc_to_remove.filename}")
        else:
            print(f"Error: Failed to delete document", file=sys.stderr)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to remove document: {e}")
        sys.exit(1)
