# InsightHub Shared Package

Shared types, interfaces, and utilities used across the InsightHub Flask server, workers, and CLI applications.

## Purpose

This package provides:

- **Core data types** (Document, Chunk, GraphNode, GraphEdge, Result, Option, etc.)
- **Abstract interfaces** for RAG components (Chunker, VectorEmbeddingEncoder, VectorDatabase, etc.)
- **Event schemas** for RabbitMQ communication
- **LLM provider interfaces** and implementations (Ollama, OpenAI, Claude)
- **Database interfaces** (vector and graph databases)
- **Repository interfaces** for data access layer
- **Shared utilities** and helpers
- **Worker base classes** for background processing

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
from shared.documents.chunking import Chunker, SentenceChunker
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

This package is installed as a local dependency in server, workers, and CLI packages:

```bash
cd packages/server
poetry add ../shared/python

cd packages/workers/parser
poetry add ../../../shared/python

cd packages/cli
poetry add ../../shared/python
```

## Current Implementation Status

### [x] Completed Components

- **Core Types**: All basic types and utility functions
- **Document Processing**: 
  - Chunking strategies (sentence, character, word)
  - Vector embedding generation with Ollama
  - File parsing (PDF, DOCX, HTML, TXT)
  - External content retrieval (Wikipedia)
- **Database Interfaces**:
  - Vector database abstraction (Qdrant implementation)
  - Graph database abstraction (Neo4j implementation)
- **LLM Integration**: Ollama provider with streaming support
- **Messaging**: Complete RabbitMQ event system
- **Storage**: Filesystem, S3, and in-memory implementations
- **Caching**: Redis and in-memory cache implementations

### [WIP] In Progress

- **Graph Database**: Neo4j integration for GraphRAG
- **Advanced Document Processing**: 
  - Entity extraction for graph construction
  - Relationship extraction
  - Document enrichment and summarization

### [TODO] Planned

- **Additional LLM Providers**: OpenAI, Claude, HuggingFace integration
- **Advanced Caching**: Distributed caching strategies
- **Performance Monitoring**: Metrics and tracing
- **Testing Utilities**: Mock implementations for testing

## Key Features

- **Type Safety**: Full type annotations throughout
- **Modular Design**: Clear separation of concerns
- **Extensibility**: Easy to add new implementations
- **Testing Support**: Dummy implementations for unit testing
- **Error Handling**: Comprehensive exception hierarchy
- **Configuration**: Environment-based configuration
- **Logging**: Structured logging with correlation IDs

## Integration with Flask Backend

The shared package integrates seamlessly with the Flask backend:

```python
# In Flask application
from shared.database.vector import QdrantVectorDatabase
from shared.llm import OllamaLlmProvider
from shared.documents.chunking import SentenceChunker

# Factory pattern for easy configuration
vector_db = create_vector_database("qdrant", host="localhost", port=6333)
llm_provider = create_llm_provider("ollama", base_url="http://localhost:11434")
```

## Worker Integration

All workers use the shared package for consistent behavior:

```python
# In worker main.py
from shared.worker import BaseWorker
from shared.messaging.consumer import MessageConsumer
from shared.documents.parser import DocumentParser
```

This shared foundation ensures consistency across the entire InsightHub ecosystem while maintaining clean architecture principles.