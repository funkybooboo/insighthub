# InsightHub Shared Package

Shared types, interfaces, and utilities used across the InsightHub server and worker processes.

## Purpose

This package provides:

- Core data types (Document, Chunk, GraphNode, GraphEdge, Result, Option, etc.)
- Abstract interfaces for RAG components (Chunker, VectorEmbeddingEncoder, VectorDatabase, etc.)
- Event schemas for RabbitMQ communication
- LLM provider interfaces and implementations
- Database interfaces (vector and graph)
- Repository interfaces for data access
- Shared utilities and helpers

## Structure

```
src/shared/
  types/                    # Core data types (Result, Option, Document, Chunk, etc.)
  models/                   # SQLAlchemy ORM models
  exceptions/               # Domain exception classes
  documents/                # Document processing
    chunking/               # Text chunking (Chunker interface, SentenceChunker)
    embedding/              # Vector embeddings (VectorEmbeddingEncoder, Ollama)
    parsing/                # File parsing (PDF, DOCX, HTML, TXT)
    retrieving/             # External content retrieval (Wikipedia, URLs)
  database/                 # Database interfaces
    vector/                 # Vector databases (VectorDatabase, Qdrant)
    graph/                  # Graph databases (GraphDatabase, Neo4j)
  messaging/                # RabbitMQ messaging
    events/                 # Event schemas (document, embedding, graph, query)
    consumer/               # Message consumers
    publisher/              # Message publishers
  llm/                      # LLM providers (Ollama, OpenAI, Claude, HuggingFace)
  repositories/             # Data access layer interfaces
    user/                   # User repository
    document/               # Document repository
    chat_session/           # Chat session repository
    chat_message/           # Chat message repository
    status/                 # Status repository
  storage/                  # Blob storage (S3, FileSystem, InMemory)
  cache/                    # Caching (Redis, InMemory, NoOp)
  logger/                   # Structured logging
  worker/                   # Worker base class
```

## Usage

### Core Types
```python
from shared.types import Document, Chunk, Result, Ok, Err, Option, Some, Nothing
```

### Document Processing
```python
from shared.documents.chunking import Chunker, SentenceDocumentChunker
from shared.documents.embedding import VectorEmbeddingEncoder, OllamaVectorEmbeddingEncoder
from shared.documents.retrieving import Retriever, WikipediaRetriever
```

### Databases
```python
from shared.database.vector import VectorDatabase, QdrantVectorDatabase
from shared.database.graph import GraphDatabase, Neo4jGraphDatabase
```

### LLM Providers
```python
from shared.llm import LlmProvider, create_llm_provider
provider = create_llm_provider("ollama", base_url="http://localhost:11434", model_name="llama3.2")
```

### Events
```python
from shared.messaging.events import DocumentUploadedEvent, DocumentChunksReadyEvent
```

### Factories
```python
from shared.cache.factory import create_cache
from shared.storage.factory import create_blob_storage
from shared.database.vector.factory import create_vector_database
```

## Installation

This package is installed as a local dependency in both server and worker packages.

```bash
cd packages/server
poetry add ../shared/python

cd packages/workers/ingestion
poetry add ../../../shared/python
```
