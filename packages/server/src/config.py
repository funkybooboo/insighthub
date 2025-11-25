# Minimal config for testing - replace with proper shared config when available
class MockConfig:
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 5000
        self.debug = False
        self.database_url = "postgresql://test:test@localhost:5432/test"
        self.redis_url = None
        self.jwt_secret_key = "test-jwt-secret-key-32-chars-minimum"
        self.jwt_expire_minutes = 1440
        self.cors_origins = ["http://localhost:3000"]
        self.upload_folder = "uploads"
        self.max_content_length = 16777216
        self.rate_limit_enabled = True
        self.rate_limit_per_minute = 60
        self.rate_limit_per_hour = 1000
        self.log_level = "INFO"
        self.log_format = "json"
        self.slow_request_threshold = 1.0
        self.enable_performance_stats = True
        self.blob_storage_type = "filesystem"
        self.file_system_storage_path = "uploads"
        self.s3_endpoint_url = None
        self.s3_access_key = None
        self.s3_secret_key = None
        self.s3_bucket_name = "documents"
        self.llm_provider = "ollama"
        self.ollama_base_url = "http://localhost:11434"
        self.ollama_llm_model = "llama3.2"
        self.ollama_embedding_model = "nomic-embed-text"
        self.openai_api_key = None
        self.openai_model = "gpt-3.5-turbo"
        self.anthropic_api_key = None
        self.anthropic_model = "claude-3-5-sonnet-20241022"
        self.huggingface_api_key = None
        self.huggingface_model = "meta-llama/Llama-3.2-3B-Instruct"
        self.rabbitmq_url = "amqp://guest:guest@localhost:5672/"
        self.rabbitmq_exchange = "insighthub"
        self.qdrant_host = "localhost"
        self.qdrant_port = 6333
        self.qdrant_collection_name = "insighthub"
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.batch_size = 32

    # Properties for compatibility
    @property
    def database(self):
        class DB:
            url = self.database_url
        return DB()

    @property
    def redis(self):
        class Redis:
            url = self.redis_url
            default_ttl = 3600
        return Redis()

    @property
    def security(self):
        class Security:
            jwt_secret_key = self.jwt_secret_key
            jwt_expire_minutes = self.jwt_expire_minutes
            cors_origins = self.cors_origins
        return Security()

    @property
    def storage(self):
        class Storage:
            blob_storage_type = self.blob_storage_type
            file_system_storage_path = self.file_system_storage_path
            s3_endpoint_url = self.s3_endpoint_url
            s3_access_key = self.s3_access_key
            s3_secret_key = self.s3_secret_key
            s3_bucket_name = self.s3_bucket_name
        return Storage()

    @property
    def vector_store(self):
        class VectorStore:
            qdrant_host = self.qdrant_host
            qdrant_port = self.qdrant_port
            qdrant_collection_name = self.qdrant_collection_name
        return VectorStore()

# Create mock config instance
config = MockConfig()