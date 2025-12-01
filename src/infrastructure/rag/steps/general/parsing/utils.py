"""Parser utilities for file operations and MIME type detection."""

import hashlib
from typing import BinaryIO


def determine_mime_type(filename: str) -> str:
    """Determine MIME type from filename extension."""
    extension = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    return "application/pdf" if extension == "pdf" else "text/plain"


def calculate_file_hash(file_obj: BinaryIO) -> str:
    """Calculate SHA-256 hash of file content."""
    file_obj.seek(0)
    hash_obj = hashlib.sha256()
    for chunk in iter(lambda: file_obj.read(4096), b""):
        hash_obj.update(chunk)
    return hash_obj.hexdigest()


def extract_text(file_obj: BinaryIO, filename: str) -> str:
    """Extract text content from file."""
    # Simple text extraction - in a real implementation this would use
    # proper parsing libraries for PDFs, DOCX, etc.
    file_obj.seek(0)
    content = file_obj.read()
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        # If not UTF-8, return a placeholder
        return f"Binary file: {filename}"
