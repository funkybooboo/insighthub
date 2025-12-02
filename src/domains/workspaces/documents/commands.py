"""Document CLI commands."""

import argparse
import sys
from io import BytesIO
from pathlib import Path

from src.context import AppContext
from src.infrastructure.logger import create_logger
from src.infrastructure.models import Workspace
from src.infrastructure.rag.steps.general.parsing.utils import (
    calculate_file_hash,
    determine_mime_type,
)
from src.infrastructure.rag.workflows.factory import WorkflowFactory

logger = create_logger(__name__)


def _build_rag_config(workspace: Workspace) -> dict:
    """Build RAG configuration dictionary from workspace model with defaults."""
    return {
        "rag_type": getattr(workspace, "rag_type", "vector"),
        "embedder_type": getattr(workspace, "embedder_type", "ollama"),
        "embedder_config": getattr(
            workspace,
            "embedder_config",
            {
                "base_url": "http://localhost:11434",
                "model_name": "nomic-embed-text",
            },
        ),
        "vector_store_type": getattr(workspace, "vector_store_type", "qdrant"),
        "vector_store_config": getattr(
            workspace,
            "vector_store_config",
            {
                "host": "localhost",
                "port": 6333,
                "collection_name": f"workspace_{workspace.id}",
            },
        ),
        "enable_reranking": getattr(workspace, "enable_reranking", False),
        "reranker_type": getattr(workspace, "reranker_type", "dummy"),
        "reranker_config": getattr(workspace, "reranker_config", {}),
    }


def cmd_list(ctx: AppContext, args: argparse.Namespace) -> None:
    """List documents in the current workspace."""
    try:
        if not ctx.current_workspace_id:
            logger.error(f"Error: No workspace selected. Use 'workspace select <id>' first")
            sys.exit(1)

        documents = ctx.document_repo.get_by_workspace(ctx.current_workspace_id)
        if not documents:
            print(f"No documents in workspace {ctx.current_workspace_id}")
            return

        print(f"\nDocuments in workspace {ctx.current_workspace_id}:")
        print("=" * 80)
        for doc in documents:
            print(f"[{doc.id}] {doc.filename}")
            print(f"    Status: {doc.status} | Size: {doc.file_size} bytes")
            print(f"    MIME: {doc.mime_type}")
            print(f"    Uploaded: {doc.created_at}")
            print("-" * 80)

    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_upload(ctx: AppContext, args: argparse.Namespace) -> None:
    """Upload a document to the current workspace."""
    try:
        if not ctx.current_workspace_id:
            logger.error(f"Error: No workspace selected. Use 'workspace select <id>' first")
            sys.exit(1)

        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"Error: File not found: {file_path}")
            sys.exit(1)

        # Read file
        print(f"Reading file: {file_path.name}")
        with open(file_path, "rb") as f:
            file_content = f.read()

        # Calculate hash and mime type
        content_hash = calculate_file_hash(BytesIO(file_content))
        mime_type = determine_mime_type(file_path.name, BytesIO(file_content))

        # Upload document
        print("Uploading...")
        document = ctx.document_service.upload_document(
            workspace_id=ctx.current_workspace_id,
            filename=file_path.name,
            file_obj=BytesIO(file_content),
            mime_type=mime_type,
            content_hash=content_hash,
            file_size=len(file_content),
        )

        ctx.document_repo.update(document.id, status="processing")
        print(f"Document uploaded: ID={document.id}")

        # Get workspace and process
        workspace = ctx.workspace_repo.get_by_id(ctx.current_workspace_id)
        rag_config = _build_rag_config(workspace)

        print("Processing (parsing, chunking, embedding, indexing)...")
        consume_workflow = WorkflowFactory.create_consume_workflow(
            rag_config=rag_config
        )

        blob_key = f"{content_hash}/{file_path.name}"
        blob_content = ctx.blob_storage.download(blob_key)

        result = consume_workflow.execute(
            raw_document=BytesIO(blob_content),
            document_id=str(document.id),
            workspace_id=str(workspace.id),
            metadata={
                "filename": file_path.name,
                "mime_type": mime_type,
                "file_size": str(len(file_content)),
            },
        )

        if result.is_ok():
            chunks_indexed = result.unwrap()
            ctx.document_repo.update(document.id, status="ready")
            print(f"\nDocument indexed successfully!")
            print(f"  ID: {document.id}")
            print(f"  Chunks: {chunks_indexed}")
        else:
            ctx.document_repo.update(document.id, status="failed")
            error = result.unwrap_err()
            logger.error(f"Error: Processing failed - {error}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Failed to upload document: {e}", exc_info=True)
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_remove(ctx: AppContext, args: argparse.Namespace) -> None:
    """Remove a document by filename."""
    try:
        if not ctx.current_workspace_id:
            logger.error(f"Error: No workspace selected. Use 'workspace select <id>' first")
            sys.exit(1)

        # Find document by filename
        documents = ctx.document_repo.get_by_workspace(ctx.current_workspace_id)
        doc_to_remove = None
        for doc in documents:
            if doc.filename == args.filename:
                doc_to_remove = doc
                break

        if not doc_to_remove:
            logger.error(f"Error: Document '{args.filename}' not found in workspace")
            sys.exit(1)

        # Confirm deletion
        confirm = input(f"Delete '{args.filename}' (ID={doc_to_remove.id})? [y/N]: ")
        if confirm.lower() != "y":
            print("Cancelled")
            return

        # Delete document
        ctx.document_repo.delete(doc_to_remove.id)
        print(f"Document '{args.filename}' deleted")

    except KeyboardInterrupt:
        print("\nCancelled")
    except Exception as e:
        logger.error(f"Failed to remove document: {e}")
        logger.error(f"Error: {e}")
        sys.exit(1)
