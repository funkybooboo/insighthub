"""Document CLI commands."""

import argparse
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.context import AppContext

logger = logging.getLogger(__name__)


def upload_document(context: "AppContext", file_path: Path) -> dict[str, str | int]:
    """
    Upload a document to the system.

    Args:
        context: Application context with services
        file_path: Path to the file to upload

    Returns:
        Dictionary with document information

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file type is unsupported
    """
    logger.info(f"CLI document upload initiated: file_path={file_path}")

    if not file_path.exists():
        logger.warning(f"CLI document upload failed: file not found (path={file_path})")
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = file_path.suffix.lower().lstrip(".")
    if extension not in ["pdf", "txt"]:
        logger.warning(f"CLI document upload failed: unsupported file type (extension={extension})")
        raise ValueError(f"Unsupported file type: {extension}. Only PDF and TXT allowed.")

    # Get user
    user = context.user_service.get_or_create_default_user()

    # Process document upload using service orchestration method
    with open(file_path, "rb") as f:
        result = context.document_service.process_document_upload(
            user_id=user.id,
            filename=file_path.name,
            file_obj=f,
        )

    logger.info(
        f"CLI document upload completed: doc_id={result.document.id}, filename={result.document.filename}, "
        f"file_size={result.document.file_size}, is_duplicate={result.is_duplicate}"
    )

    return {
        "id": result.document.id,
        "filename": result.document.filename,
        "file_size": result.document.file_size,
        "text_length": result.text_length,
        "status": "already_exists" if result.is_duplicate else "uploaded",
    }


def list_documents(context: "AppContext") -> dict[str, int | list[dict[str, str | int | None]]]:
    """
    List all documents in the system.

    Args:
        context: Application context with services

    Returns:
        Dictionary with documents list and count
    """
    logger.info("CLI listing documents")
    user = context.user_service.get_or_create_default_user()
    documents = context.document_service.list_user_documents(user.id)

    logger.info(f"CLI documents listed: count={len(documents)}")

    return {
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "file_size": doc.file_size,
                "mime_type": doc.mime_type,
                "chunk_count": doc.chunk_count,
                "created_at": doc.created_at.isoformat(),
            }
            for doc in documents
        ],
        "count": len(documents),
    }


def delete_document(context: "AppContext", doc_id: int) -> dict[str, str]:
    """
    Delete a document from the system.

    Args:
        context: Application context with services
        doc_id: Document ID to delete

    Returns:
        Dictionary with success message

    Raises:
        ValueError: If document not found
    """
    logger.info(f"CLI document deletion initiated: doc_id={doc_id}")

    # Check if document exists
    document = context.document_service.get_document_by_id(doc_id)
    if not document:
        logger.warning(f"CLI document deletion failed: document not found (doc_id={doc_id})")
        raise ValueError(f"Document with ID {doc_id} not found")

    # Delete document (including from blob storage)
    context.document_service.delete_document(doc_id, delete_from_storage=True)

    # TODO: Remove from RAG system
    # rag.remove_document(doc_id)

    logger.info(f"CLI document deleted: doc_id={doc_id}, filename={document.filename}")

    return {"message": f"Document {doc_id} deleted successfully"}


def cmd_upload(context: "AppContext", args: argparse.Namespace) -> None:
    """Upload a document."""
    try:
        file_path = Path(args.file)
        result = upload_document(context, file_path)

        if result["status"] == "already_exists":
            print("Document already exists in the system!")
        else:
            print("Document uploaded successfully!")

        print(f"Document ID: {result['id']}")
        print(f"Filename: {result['filename']}")
        print(f"File Size: {result['file_size']} bytes")
        if "text_length" in result:
            print(f"Text Length: {result['text_length']} characters")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(context: "AppContext", args: argparse.Namespace) -> None:
    """List all documents."""
    try:
        result = list_documents(context)
        documents = result.get("documents", [])

        if not documents:
            print("No documents found.")
            return

        print(f"Total documents: {result.get('count', 0)}\n")
        if isinstance(documents, list):
            for doc in documents:
                if isinstance(doc, dict):
                    print(f"ID: {doc.get('id', 'N/A')}")
                    print(f"  Filename: {doc.get('filename', 'N/A')}")
                    print(f"  Size: {doc.get('file_size', 'N/A')} bytes")
                    print(f"  MIME Type: {doc.get('mime_type', 'N/A')}")
                    print(f"  Chunks: {doc.get('chunk_count') or 'N/A'}")
                    print(f"  Created: {doc.get('created_at', 'N/A')}")
                    print()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_delete(context: "AppContext", args: argparse.Namespace) -> None:
    """Delete a document."""
    try:
        result = delete_document(context, args.doc_id)
        print(result["message"])
    except (ValueError, Exception) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
