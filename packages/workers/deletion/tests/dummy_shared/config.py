"""Dummy config module for testing."""

from types import SimpleNamespace

# Create dummy config with required attributes
config = SimpleNamespace()
config.rabbitmq_url = "amqp://guest:guest@localhost:5672/"
config.rabbitmq_exchange = "insighthub"
config.database_url = "postgresql://test:test@localhost:5432/test"
config.s3_endpoint_url = "http://localhost:9000"
config.s3_access_key = "minioadmin"
config.s3_secret_key = "minioadmin"
config.s3_bucket_name = "test-bucket"
config.qdrant_host = "localhost"
config.qdrant_port = 6333
config.worker_concurrency = 1
