# Configuration Guide

This document explains how configuration works in the InsightHub server application.

## Environment Files

### File Structure

```
.env.example          # Template file (committed to git)
.env.local.example    # Local-only setup template (committed to git)
.env                  # Local development config (gitignored)
.env.local            # Local-only config (gitignored)
.env.test             # Test config (gitignored)
```

### Setup Instructions

1. **Development Setup** (General):
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

2. **Local-Only Setup** (No external services):
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your local-only settings
   # Uses local file storage, local Ollama, local Qdrant, etc.
   ```

3. **Test Setup**:
   ```bash
   cp .env.example .env.test
   # Edit .env.test with test-specific settings
   ```

4. **Production**:
   - DO NOT use .env files in production
   - Set environment variables directly via:
     - Docker environment variables
     - Kubernetes secrets/configmaps
     - Cloud platform environment configuration

## How Config Loading Works

The `src/config.py` module automatically loads the correct environment file:

```python
if os.getenv("PYTEST_CURRENT_TEST"):
    # Running tests -> load .env.test
    load_dotenv(".env.test", override=True)
elif os.path.exists(".env"):
    # Development -> load .env
    load_dotenv(".env")
# Production -> use environment variables (no file)
```

**Priority Order**:
1. `.env.local` (if it exists, highest priority)
2. `.env` (standard development config)
3. Environment variables (production)

To use local-only config:
```bash
cp .env.local.example .env.local
# Now .env.local takes precedence over .env
```

## Configuration Sections

### Service Implementation Types

Control which implementation to use for each service:

```bash
USER_SERVICE_TYPE=default
DOCUMENT_SERVICE_TYPE=default
CHAT_SERVICE_TYPE=default
```

**Available Options**: `default`

### Repository Implementation Types

Control which implementation to use for each repository:

```bash
USER_REPOSITORY_TYPE=sql
DOCUMENT_REPOSITORY_TYPE=sql
CHAT_SESSION_REPOSITORY_TYPE=sql
CHAT_MESSAGE_REPOSITORY_TYPE=sql
```

**Available Options**: `sql`

### Blob Storage Type

Control where files are stored:

```bash
BLOB_STORAGE_TYPE=file_system
```

**Available Options**:
- `file_system` - Store files on local filesystem (good for development)
- `s3` - Store files in S3-compatible storage (MinIO, AWS S3, etc.)
- `in_memory` - Store files in memory (testing only)

### File System Storage

When using `BLOB_STORAGE_TYPE=file_system`:

```bash
FILE_SYSTEM_STORAGE_PATH=uploads
```

Files will be stored in the specified directory.

### S3 Storage

When using `BLOB_STORAGE_TYPE=s3`:

```bash
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
S3_BUCKET_NAME=documents
```

**Compatible with**:
- MinIO (self-hosted S3-compatible storage)
- AWS S3
- DigitalOcean Spaces
- Cloudflare R2
- Any S3-compatible storage

### Database

PostgreSQL connection string:

```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

**Examples**:
- Development: `postgresql://insighthub:insighthub_dev@localhost:5432/insighthub`
- Testing: `sqlite:///:memory:` (unit tests) or testcontainer (integration tests)
- Production: Use managed database URL from cloud provider

### RAG Configuration

```bash
RAG_TYPE=vector
CHUNKING_STRATEGY=sentence
CHUNK_SIZE=512
CHUNK_OVERLAP=50
RAG_TOP_K=5
```

### Ollama Configuration

For local LLM inference:

```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### Qdrant Configuration

Vector database for RAG:

```bash
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=insighthub
```

## Environment-Specific Recommendations

### Development (.env)

```bash
# Use file system storage for simplicity
BLOB_STORAGE_TYPE=file_system
FILE_SYSTEM_STORAGE_PATH=uploads

# Use local PostgreSQL
DATABASE_URL=postgresql://insighthub:insighthub_dev@localhost:5432/insighthub

# Enable debug mode
FLASK_DEBUG=True
```

### Local-Only (.env.local)

For a completely local setup with no external dependencies:

```bash
# Local file storage
BLOB_STORAGE_TYPE=file_system
FILE_SYSTEM_STORAGE_PATH=uploads

# Local PostgreSQL
DATABASE_URL=postgresql://insighthub:insighthub_dev@localhost:5432/insighthub

# Local Ollama (run: ollama serve)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Local Qdrant (run: docker run -p 6333:6333 qdrant/qdrant)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# No cloud/external services needed
FLASK_DEBUG=True
```

### Testing (.env.test)

```bash
# Use in-memory storage for speed
BLOB_STORAGE_TYPE=in_memory

# Tests use SQLite or testcontainers
DATABASE_URL=sqlite:///:memory:

# Disable debug for cleaner test output
FLASK_DEBUG=False
```

### Production (Environment Variables)

```bash
# Use S3 for scalability
BLOB_STORAGE_TYPE=s3
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=<from secrets manager>
S3_SECRET_KEY=<from secrets manager>
S3_BUCKET_NAME=insighthub-prod-documents

# Use managed PostgreSQL
DATABASE_URL=<from cloud provider>

# Disable debug
FLASK_DEBUG=False
```

## Adding New Configuration

To add a new configuration variable:

1. **Add to `.env.example`** with documentation
2. **Add to `src/config.py`** with type annotation:
   ```python
   MY_NEW_CONFIG: Final[str] = os.getenv("MY_NEW_CONFIG", "default_value")
   ```
3. **Use in code**:
   ```python
   from src import config

   value = config.MY_NEW_CONFIG
   ```

## Security Best Practices

1. **Never commit `.env` or `.env.test`** - They're in `.gitignore`
2. **Never commit secrets** - Use placeholder values in `.env.example`
3. **Use different secrets** for development, testing, and production
4. **In production**, use:
   - Cloud provider secret managers (AWS Secrets Manager, GCP Secret Manager)
   - Kubernetes secrets
   - Encrypted environment variables
5. **Rotate secrets regularly**
