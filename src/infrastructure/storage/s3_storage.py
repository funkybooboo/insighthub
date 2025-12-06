"""S3-compatible blob storage implementation using boto3."""

from typing import Optional

try:
    import boto3
    from botocore.exceptions import ClientError

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from .storage import BlobStorage


class S3BlobStorage(BlobStorage):
    """S3-compatible blob storage using boto3 client."""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool = True,
        region: Optional[str] = None,
    ):
        """
        Initialize S3 blob storage.

        Args:
            endpoint: S3 endpoint URL (e.g., "localhost:9000" for MinIO)
            access_key: S3 access key
            secret_key: S3 secret key
            bucket_name: S3 bucket name
            secure: Whether to use HTTPS (default: True)
            region: S3 region (optional, defaults to us-east-1)
        """
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 package is required for S3BlobStorage")

        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.secure = secure

        # Build endpoint URL with protocol
        protocol = "https" if secure else "http"
        endpoint_url = f"{protocol}://{endpoint}"

        # Initialize boto3 client (lazy - connection happens on first use)
        self._client: Optional[boto3.client] = None
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._region = region or "us-east-1"

    @property
    def client(self) -> boto3.client:
        """Lazy initialization of boto3 S3 client."""
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=self._endpoint_url,
                aws_access_key_id=self._access_key,
                aws_secret_access_key=self._secret_key,
                region_name=self._region,
            )
            self._ensure_bucket()
        return self._client

    def _ensure_bucket(self) -> None:
        """Ensure the bucket exists, create it if it doesn't."""
        if not self._client:
            return

        try:
            self._client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            self._handle_bucket_error(e)

    def _handle_bucket_error(self, e: ClientError) -> None:
        """Handle bucket access errors."""
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code != "404":
            raise RuntimeError(f"Failed to access bucket {self.bucket_name}: {e}")

        self._create_bucket()

    def _create_bucket(self) -> None:
        """Create S3 bucket."""
        try:
            if self._region == "us-east-1":
                self._client.create_bucket(Bucket=self.bucket_name)
            else:
                self._client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": self._region},
                )
        except ClientError as create_error:
            raise RuntimeError(
                f"Failed to create bucket {self.bucket_name}: {create_error}"
            )

    def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """
        Upload data to S3 storage.

        Args:
            key: Unique identifier for the blob
            data: Binary data to store
            content_type: MIME type of the data

        Returns:
            str: URL to access the uploaded blob
        """
        from io import BytesIO

        try:
            # Upload data
            data_stream = BytesIO(data)
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data_stream,
                ContentType=content_type,
            )

            # Return the URL
            return self.get_url(key)

        except ClientError as e:
            raise RuntimeError(f"Failed to upload {key}: {e}")

    def download(self, key: str) -> bytes:
        """
        Download data from S3 storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            bytes: Binary data from storage

        Raises:
            FileNotFoundError: If blob doesn't exist
        """
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read()

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "NoSuchKey":
                raise FileNotFoundError(f"Blob {key} not found")
            raise RuntimeError(f"Failed to download {key}: {e}")

    def delete(self, key: str) -> bool:
        """
        Delete a blob from S3 storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "NoSuchKey":
                return False  # Already doesn't exist
            raise RuntimeError(f"Failed to delete {key}: {e}")

    def exists(self, key: str) -> bool:
        """
        Check if a blob exists in S3 storage.

        Args:
            key: Unique identifier for the blob

        Returns:
            bool: True if blob exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "404":
                return False
            raise RuntimeError(f"Failed to check existence of {key}: {e}")

    def get_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Get a signed URL for accessing the blob.

        Args:
            key: Unique identifier for the blob
            expires_in: URL expiration time in seconds

        Returns:
            str: Signed URL for blob access
        """
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in,
            )
            return url

        except ClientError as e:
            raise RuntimeError(f"Failed to generate URL for {key}: {e}")
