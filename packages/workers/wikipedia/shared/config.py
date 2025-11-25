class Config:
    rabbitmq_url = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange = "insighthub"
    database_url = "postgresql://test:test@localhost:5432/test"
    worker_concurrency = 1
    s3_endpoint_url = "http://localhost:9000"
    s3_access_key = "minioadmin"
    s3_secret_key = "minioadmin"
    s3_bucket_name = "wiki-bucket"

config = Config()