"""MinIO (S3-compatible) blob storage implementation."""

import hashlib
from io import BytesIO
from typing import BinaryIO

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from .blob_storage import BlobStorage


class MinioBlobStorage(BlobStorage):
    """S3-compatible blob storage implementation (works with MinIO)."""

    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        region: str = "us-east-1",
    ):
        """
        Initialize S3 blob storage.

        Args:
            endpoint_url: S3 endpoint URL (e.g., http://localhost:9000 for MinIO)
            access_key: S3 access key
            secret_key: S3 secret key
            bucket_name: S3 bucket name
            region: AWS region (default: us-east-1)
        """
        self.bucket_name = bucket_name

        # Create S3 client
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=Config(signature_version="s3v4"),
        )

        # Create bucket if it doesn't exist
        self._create_bucket_if_not_exists()

    def _create_bucket_if_not_exists(self) -> None:
        """Create the bucket if it doesn't already exist."""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            try:
                self.client.create_bucket(Bucket=self.bucket_name)
            except ClientError as e:
                print(f"Error creating bucket: {e}")

    def upload_file(self, file_obj: BinaryIO, object_name: str) -> str:
        """
        Upload a file to S3.

        Args:
            file_obj: File-like object to upload
            object_name: Name/key for the object in S3

        Returns:
            str: Object name/key
        """
        try:
            self.client.upload_fileobj(file_obj, self.bucket_name, object_name)
            return object_name
        except ClientError as e:
            raise Exception(f"Error uploading file: {e}") from e

    def download_file(self, object_name: str) -> bytes:
        """
        Download a file from S3.

        Args:
            object_name: Name/key of the object to download

        Returns:
            bytes: File content
        """
        try:
            buffer = BytesIO()
            self.client.download_fileobj(self.bucket_name, object_name, buffer)
            buffer.seek(0)
            return buffer.read()
        except ClientError as e:
            raise Exception(f"Error downloading file: {e}") from e

    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from S3.

        Args:
            object_name: Name/key of the object to delete

        Returns:
            bool: True if successful
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            print(f"Error deleting file: {e}")
            return False

    def file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in S3.

        Args:
            object_name: Name/key of the object to check

        Returns:
            bool: True if file exists
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError:
            return False

    def calculate_hash(self, file_obj: BinaryIO) -> str:
        """
        Calculate SHA-256 hash of a file.

        Args:
            file_obj: File-like object

        Returns:
            str: SHA-256 hash hex digest
        """
        sha256_hash = hashlib.sha256()
        file_obj.seek(0)
        for byte_block in iter(lambda: file_obj.read(4096), b""):
            sha256_hash.update(byte_block)
        file_obj.seek(0)
        return sha256_hash.hexdigest()
