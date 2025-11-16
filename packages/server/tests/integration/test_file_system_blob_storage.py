"""Integration tests for FileSystemBlobStorage with real file operations."""

import tempfile
from collections.abc import Generator
from io import BytesIO
from pathlib import Path

import pytest

from src.infrastructure.storage import FileSystemBlobStorage


@pytest.fixture
def temp_storage_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for storage tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def storage(temp_storage_dir: Path) -> FileSystemBlobStorage:
    """Create a FileSystemBlobStorage instance with temporary directory."""
    return FileSystemBlobStorage(base_path=str(temp_storage_dir))


class TestFileSystemBlobStorageIntegration:
    """Integration tests for FileSystemBlobStorage."""

    def test_full_upload_download_delete_workflow(self, storage: FileSystemBlobStorage) -> None:
        """Test complete workflow: upload, download, verify, delete."""
        # Upload
        file_content = b"Integration test document content"
        file_obj = BytesIO(file_content)
        object_name = "integration/test/document.txt"

        upload_result = storage.upload_file(file_obj, object_name)
        assert upload_result == object_name

        # Verify exists
        assert storage.file_exists(object_name) is True

        # Download
        downloaded_content = storage.download_file(object_name)
        assert downloaded_content == file_content

        # Calculate hash
        file_obj.seek(0)
        hash_before = storage.calculate_hash(file_obj)

        downloaded_obj = BytesIO(downloaded_content)
        hash_after = storage.calculate_hash(downloaded_obj)
        assert hash_before == hash_after

        # Delete
        delete_result = storage.delete_file(object_name)
        assert delete_result is True

        # Verify deleted
        assert storage.file_exists(object_name) is False

    def test_large_file_upload_download(self, storage: FileSystemBlobStorage) -> None:
        """Test uploading and downloading a large file (10 MB)."""
        # Create 10 MB file
        large_content = b"x" * (10 * 1024 * 1024)  # 10 MB
        file_obj = BytesIO(large_content)
        object_name = "large_file.bin"

        # Upload
        storage.upload_file(file_obj, object_name)

        # Download
        downloaded_content = storage.download_file(object_name)

        # Verify size and content match
        assert len(downloaded_content) == len(large_content)
        assert downloaded_content == large_content

    def test_concurrent_operations_on_different_files(self, storage: FileSystemBlobStorage) -> None:
        """Test multiple operations on different files work correctly."""
        files = {
            "file1.txt": b"Content 1",
            "file2.txt": b"Content 2",
            "dir/file3.txt": b"Content 3",
            "dir/subdir/file4.txt": b"Content 4",
        }

        # Upload all files
        for name, content in files.items():
            storage.upload_file(BytesIO(content), name)

        # Verify all exist
        for name in files:
            assert storage.file_exists(name)

        # Download and verify all
        for name, expected_content in files.items():
            downloaded = storage.download_file(name)
            assert downloaded == expected_content

        # Delete one file
        storage.delete_file("file1.txt")

        # Verify only that one is deleted
        assert not storage.file_exists("file1.txt")
        for name in ["file2.txt", "dir/file3.txt", "dir/subdir/file4.txt"]:
            assert storage.file_exists(name)

    def test_special_characters_in_filename(self, storage: FileSystemBlobStorage) -> None:
        """Test handling filenames with special characters."""
        special_names = [
            "file with spaces.txt",
            "file-with-dashes.txt",
            "file_with_underscores.txt",
            "file.multiple.dots.txt",
        ]

        content = b"Special character test"

        for name in special_names:
            storage.upload_file(BytesIO(content), name)
            assert storage.file_exists(name)
            assert storage.download_file(name) == content
            storage.delete_file(name)

    def test_hash_consistency_across_operations(self, storage: FileSystemBlobStorage) -> None:
        """Test that hash calculation is consistent across multiple operations."""
        file_content = b"Consistent hash test content"
        file_obj = BytesIO(file_content)

        # Calculate hash before upload
        hash1 = storage.calculate_hash(file_obj)

        # Upload file
        file_obj.seek(0)
        storage.upload_file(file_obj, "hash_test.txt")

        # Calculate hash again
        file_obj.seek(0)
        hash2 = storage.calculate_hash(file_obj)

        # Download and calculate hash
        downloaded = storage.download_file("hash_test.txt")
        hash3 = storage.calculate_hash(BytesIO(downloaded))

        # All hashes should be identical
        assert hash1 == hash2 == hash3

    def test_directory_structure_preservation(
        self, storage: FileSystemBlobStorage, temp_storage_dir: Path
    ) -> None:
        """Test that directory structure is preserved correctly."""
        nested_path = "level1/level2/level3/file.txt"
        content = b"Nested directory test"

        storage.upload_file(BytesIO(content), nested_path)

        # Verify full directory structure exists
        full_path = temp_storage_dir / "level1" / "level2" / "level3" / "file.txt"
        assert full_path.exists()
        assert full_path.read_bytes() == content

    def test_empty_file_upload_download(self, storage: FileSystemBlobStorage) -> None:
        """Test uploading and downloading an empty file."""
        empty_content = b""
        file_obj = BytesIO(empty_content)
        object_name = "empty_file.txt"

        storage.upload_file(file_obj, object_name)
        assert storage.file_exists(object_name)

        downloaded = storage.download_file(object_name)
        assert downloaded == empty_content

    def test_binary_file_integrity(self, storage: FileSystemBlobStorage) -> None:
        """Test that binary files maintain integrity through upload/download."""
        # Create binary content with various byte values
        binary_content = bytes(range(256))  # All possible byte values
        file_obj = BytesIO(binary_content)
        object_name = "binary_test.bin"

        storage.upload_file(file_obj, object_name)
        downloaded = storage.download_file(object_name)

        # Verify exact byte-for-byte match
        assert downloaded == binary_content
        assert len(downloaded) == 256

    def test_storage_isolation_between_instances(self, temp_storage_dir: Path) -> None:
        """Test that different storage instances with same base path access same files."""
        storage1 = FileSystemBlobStorage(base_path=str(temp_storage_dir))
        storage2 = FileSystemBlobStorage(base_path=str(temp_storage_dir))

        # Upload with first instance
        content = b"Shared content"
        storage1.upload_file(BytesIO(content), "shared.txt")

        # Download with second instance
        downloaded = storage2.download_file("shared.txt")
        assert downloaded == content

        # Delete with second instance
        storage2.delete_file("shared.txt")

        # Verify deleted for first instance
        assert not storage1.file_exists("shared.txt")
