"""
Integration tests for storage module.

These tests verify that storage implementations work correctly
with complete file lifecycle operations.
"""

import io

import pytest

from shared.storage.in_memory_blob_storage import InMemoryBlobStorage


class TestStorageFullWorkflow:
    """Integration tests for complete storage workflows."""

    def test_upload_download_delete_workflow(self) -> None:
        """Test complete file lifecycle: upload, download, delete."""
        storage = InMemoryBlobStorage()
        content = b"Complete workflow test content"
        filename = "workflow/test.txt"

        # Upload
        upload_result = storage.upload_file(io.BytesIO(content), filename)
        assert upload_result.is_ok()
        assert upload_result.unwrap() == filename

        # Verify exists
        assert storage.file_exists(filename) is True

        # Download
        download_result = storage.download_file(filename)
        assert download_result.is_ok()
        assert download_result.unwrap() == content

        # Delete
        delete_result = storage.delete_file(filename)
        assert delete_result.is_ok()
        assert delete_result.unwrap() is True

        # Verify deleted
        assert storage.file_exists(filename) is False
        download_after_delete = storage.download_file(filename)
        assert download_after_delete.is_err()

    def test_multiple_files_management(self) -> None:
        """Test managing multiple files simultaneously."""
        storage = InMemoryBlobStorage()

        files = {
            "documents/doc1.pdf": b"PDF content 1",
            "documents/doc2.pdf": b"PDF content 2",
            "images/image1.png": b"PNG data",
            "data/config.json": b'{"setting": "value"}',
        }

        # Upload all files
        for path, content in files.items():
            result = storage.upload_file(io.BytesIO(content), path)
            assert result.is_ok()

        # Verify all exist
        for path in files.keys():
            assert storage.file_exists(path) is True

        # Download and verify content
        for path, expected_content in files.items():
            result = storage.download_file(path)
            assert result.is_ok()
            assert result.unwrap() == expected_content

        # Delete some files
        storage.delete_file("documents/doc1.pdf")
        storage.delete_file("images/image1.png")

        # Verify selective deletion
        assert storage.file_exists("documents/doc1.pdf") is False
        assert storage.file_exists("documents/doc2.pdf") is True
        assert storage.file_exists("images/image1.png") is False
        assert storage.file_exists("data/config.json") is True


class TestStorageHashIntegration:
    """Integration tests for storage hash functionality."""

    def test_hash_before_and_after_upload(self) -> None:
        """Hash is consistent before and after upload."""
        storage = InMemoryBlobStorage()
        content = b"Content for hashing test"
        file_obj = io.BytesIO(content)

        # Calculate hash before upload
        hash_before = storage.calculate_hash(file_obj)

        # Upload file
        storage.upload_file(file_obj, "test.txt")

        # Calculate hash of same content again
        hash_after = storage.calculate_hash(io.BytesIO(content))

        assert hash_before == hash_after

    def test_hash_uniquely_identifies_content(self) -> None:
        """Different content produces different hashes."""
        storage = InMemoryBlobStorage()

        contents = [
            b"Content version 1",
            b"Content version 2",
            b"Completely different content",
            b"",
        ]

        hashes = []
        for content in contents:
            h = storage.calculate_hash(io.BytesIO(content))
            hashes.append(h)

        # All hashes should be unique
        assert len(hashes) == len(set(hashes))


class TestStorageOverwrite:
    """Integration tests for file overwrite behavior."""

    def test_overwrite_preserves_latest_content(self) -> None:
        """Overwriting a file keeps the latest content."""
        storage = InMemoryBlobStorage()
        filename = "overwrite_test.txt"

        # Upload version 1
        storage.upload_file(io.BytesIO(b"Version 1"), filename)
        result1 = storage.download_file(filename)
        assert result1.unwrap() == b"Version 1"

        # Upload version 2
        storage.upload_file(io.BytesIO(b"Version 2"), filename)
        result2 = storage.download_file(filename)
        assert result2.unwrap() == b"Version 2"

        # Upload version 3
        storage.upload_file(io.BytesIO(b"Version 3"), filename)
        result3 = storage.download_file(filename)
        assert result3.unwrap() == b"Version 3"

    def test_overwrite_with_different_size(self) -> None:
        """Can overwrite with content of different size."""
        storage = InMemoryBlobStorage()
        filename = "size_test.txt"

        # Start with small content
        storage.upload_file(io.BytesIO(b"Small"), filename)
        assert len(storage.download_file(filename).unwrap()) == 5

        # Overwrite with large content
        large_content = b"X" * 10000
        storage.upload_file(io.BytesIO(large_content), filename)
        assert len(storage.download_file(filename).unwrap()) == 10000

        # Overwrite back to small
        storage.upload_file(io.BytesIO(b"Tiny"), filename)
        assert len(storage.download_file(filename).unwrap()) == 4


class TestStorageErrorHandling:
    """Integration tests for storage error handling."""

    def test_download_nonexistent_returns_error(self) -> None:
        """Downloading nonexistent file returns proper error."""
        storage = InMemoryBlobStorage()

        result = storage.download_file("does/not/exist.txt")

        assert result.is_err()
        error = result.error
        assert error.code == "NOT_FOUND"
        assert "does/not/exist.txt" in error.message

    def test_delete_nonexistent_returns_false(self) -> None:
        """Deleting nonexistent file returns Ok(False)."""
        storage = InMemoryBlobStorage()

        result = storage.delete_file("does/not/exist.txt")

        assert result.is_ok()
        assert result.unwrap() is False


class TestStorageBinaryContent:
    """Integration tests for binary content handling."""

    def test_binary_pdf_roundtrip(self) -> None:
        """Binary PDF-like content survives upload/download."""
        storage = InMemoryBlobStorage()

        # Simulated PDF header and content
        pdf_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\n%%EOF"

        storage.upload_file(io.BytesIO(pdf_content), "test.pdf")
        result = storage.download_file("test.pdf")

        assert result.is_ok()
        assert result.unwrap() == pdf_content

    def test_all_byte_values_roundtrip(self) -> None:
        """All 256 byte values survive upload/download."""
        storage = InMemoryBlobStorage()

        all_bytes = bytes(range(256))

        storage.upload_file(io.BytesIO(all_bytes), "all_bytes.bin")
        result = storage.download_file("all_bytes.bin")

        assert result.is_ok()
        assert result.unwrap() == all_bytes
        assert len(result.unwrap()) == 256
