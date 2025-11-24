"""Tests for blob storage implementations."""

import unittest
from io import BytesIO
import os
import shutil

from shared.storage.in_memory_blob_storage import InMemoryBlobStorage
from shared.storage.file_system_blob_storage import FileSystemBlobStorage


class TestInMemoryBlobStorage(unittest.TestCase):
    """Tests for InMemoryBlobStorage."""

    def setUp(self):
        """Set up the test case."""
        self.storage = InMemoryBlobStorage()

    def test_upload_and_download_file(self):
        """Test uploading and downloading a file."""
        file_content = b"Hello, World!"
        file_obj = BytesIO(file_content)
        object_name = "hello.txt"

        upload_result = self.storage.upload_file(file_obj, object_name)
        self.assertTrue(upload_result.is_ok())
        self.assertEqual(upload_result.unwrap(), object_name)

        download_result = self.storage.download_file(object_name)
        self.assertTrue(download_result.is_ok())
        self.assertEqual(download_result.unwrap(), file_content)

    def test_file_exists(self):
        """Test checking if a file exists."""
        file_content = b"Hello, World!"
        file_obj = BytesIO(file_content)
        object_name = "hello.txt"

        self.assertFalse(self.storage.file_exists(object_name))

        self.storage.upload_file(file_obj, object_name)

        self.assertTrue(self.storage.file_exists(object_name))

    def test_delete_file(self):
        """Test deleting a file."""
        file_content = b"Hello, World!"
        file_obj = BytesIO(file_content)
        object_name = "hello.txt"

        self.storage.upload_file(file_obj, object_name)

        self.assertTrue(self.storage.file_exists(object_name))

        delete_result = self.storage.delete_file(object_name)
        self.assertTrue(delete_result.is_ok())
        self.assertTrue(delete_result.unwrap())

        self.assertFalse(self.storage.file_exists(object_name))

    def test_calculate_hash(self):
        """Test calculating the hash of a file."""
        file_content = b"Hello, World!"
        file_obj = BytesIO(file_content)

        hash_result = self.storage.calculate_hash(file_obj)
        self.assertEqual(hash_result, "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f") # SHA256 hash for "Hello, World!"


class TestFileSystemBlobStorage(unittest.TestCase):
    """Tests for FileSystemBlobStorage."""

    def setUp(self):
        """Set up the test case."""
        self.test_dir = "test_storage"
        self.storage = FileSystemBlobStorage(base_path=self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """Tear down the test case."""
        shutil.rmtree(self.test_dir)

    def test_upload_and_download_file(self):
        """Test uploading and downloading a file."""
        file_content = b"Hello, World!"
        file_obj = BytesIO(file_content)
        object_name = "hello.txt"

        upload_result = self.storage.upload_file(file_obj, object_name)
        self.assertTrue(upload_result.is_ok())
        self.assertEqual(upload_result.unwrap(), object_name)

        download_result = self.storage.download_file(object_name)
        self.assertTrue(download_result.is_ok())
        self.assertEqual(download_result.unwrap(), file_content)

    def test_file_exists(self):
        """Test checking if a file exists."""
        file_content = b"Hello, World!"
        file_obj = BytesIO(file_content)
        object_name = "hello.txt"

        self.assertFalse(self.storage.file_exists(object_name))

        self.storage.upload_file(file_obj, object_name)

        self.assertTrue(self.storage.file_exists(object_name))

    def test_delete_file(self):
        """Test deleting a file."""
        file_content = b"Hello, World!"
        file_obj = BytesIO(file_content)
        object_name = "hello.txt"

        self.storage.upload_file(file_obj, object_name)

        self.assertTrue(self.storage.file_exists(object_name))

        delete_result = self.storage.delete_file(object_name)
        self.assertTrue(delete_result.is_ok())
        self.assertTrue(delete_result.unwrap())

        self.assertFalse(self.storage.file_exists(object_name))

    def test_calculate_hash(self):
        """Test calculating the hash of a file."""
        file_content = b"Hello, World!"
        file_obj = BytesIO(file_content)

        hash_result = self.storage.calculate_hash(file_obj)
        self.assertEqual(hash_result, "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f") # SHA256 hash for "Hello, World!"


if __name__ == "__main__":
    unittest.main()
