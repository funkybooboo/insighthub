# Database Setup

This document describes the PostgreSQL database integration for InsightHub.

## Architecture

The codebase follows a clean layered architecture:

```
rag/                    # RAG library (vector/graph implementations)
db/
  +-- base.py           # Base classes and mixins
  +-- session.py        # Database connection and session management
  +-- repository.py     # Data access layer (repositories)
  +-- models/           # SQLAlchemy models
      +-- user.py
      +-- document.py
      +-- chat_session.py
      +-- chat_message.py
services/               # Business logic layer
  +-- user_service.py
  +-- document_service.py
  +-- chat_service.py
routes/                 # API endpoints
  +-- health.py
  +-- documents.py
  +-- chat.py
app.py                  # Flask application factory
```

## Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email
- `full_name` - Optional full name
- `created_at`, `updated_at` - Timestamps

### Documents Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `filename` - Original filename
- `file_path` - Path to stored file
- `file_size` - File size in bytes
- `mime_type` - MIME type (application/pdf or text/plain)
- `content_hash` - SHA-256 hash for deduplication
- `chunk_count` - Number of chunks created by RAG system
- `rag_collection` - Vector store collection name
- `created_at`, `updated_at` - Timestamps

### Chat Sessions Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `title` - Session title (auto-generated from first message)
- `rag_type` - Type of RAG used (vector/graph)
- `created_at`, `updated_at` - Timestamps

### Chat Messages Table
- `id` - Primary key
- `session_id` - Foreign key to chat_sessions
- `role` - Message role (user/assistant/system)
- `content` - Message content
- `metadata` - JSON string for additional data (context chunks, scores, etc.)
- `created_at`, `updated_at` - Timestamps

## Setup Instructions

### 1. Start PostgreSQL

Using Docker Compose (recommended):
```bash
docker compose up postgres
```

Or run locally on port 5432.

### 2. Configure Environment

Copy `.env.example` to `.env` and update:
```bash
DATABASE_URL=postgresql://insighthub:insighthub_dev@localhost:5432/insighthub
```

### 3. Create Initial Migration

Generate the initial migration:
```bash
poetry run alembic revision --autogenerate -m "Initial schema"
```

### 4. Run Migrations

Apply migrations to create tables:
```bash
poetry run alembic upgrade head
```

## Common Operations

### Create New Migration

After modifying models:
```bash
poetry run alembic revision --autogenerate -m "Description of changes"
poetry run alembic upgrade head
```

### View Migration History

```bash
poetry run alembic history
```

### Rollback Migration

```bash
poetry run alembic downgrade -1  # Rollback one migration
poetry run alembic downgrade base  # Rollback all migrations
```

### Reset Database

```bash
poetry run alembic downgrade base
poetry run alembic upgrade head
```

## Testing

Integration tests use testcontainers to spin up temporary PostgreSQL instances:

```python
@pytest.fixture(scope="function")
def db_session(postgres_container):
    # Automatic setup/teardown of test database
    ...
```

Run tests:
```bash
poetry run pytest tests/integration/
```

## Service Layer Usage

The service layer encapsulates business logic and can be used by both API routes and CLI:

```python
from sqlalchemy.orm import Session
from services.document_service import DocumentService

# In API route or CLI
db = get_db_session()
doc_service = DocumentService(db)

# Create document
doc = doc_service.create_document(
    user_id=1,
    filename="paper.pdf",
    file_path="/uploads/paper.pdf",
    file_size=1024,
    mime_type="application/pdf",
    content_hash="abc123..."
)

# List documents
docs = doc_service.list_user_documents(user_id=1)
```

## RAG Integration

The RAG library remains independent and is used by the service layer:

```python
from rag.factory import create_rag
from services.document_service import DocumentService

# Create RAG instance
rag = create_rag(
    rag_type="vector",
    chunking_strategy="sentence",
    embedding_type="ollama",
    vector_store_type="qdrant"
)

# Process document
text = doc_service.extract_text(file_path, filename)
chunk_count = rag.add_documents([{"text": text, "metadata": {"doc_id": doc.id}}])

# Update document with RAG info
doc_service.update_document(doc.id, chunk_count=chunk_count, rag_collection="insighthub")
```
