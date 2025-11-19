# InsightHub Shared Package

Shared types, interfaces, and utilities used across the InsightHub server and worker processes.

## Purpose

This package provides:
- Core data types (Document, Chunk, GraphNode, GraphEdge, etc.)
- Abstract interfaces for RAG components (Chunker, EmbeddingEncoder, VectorStore, etc.)
- Event schemas for RabbitMQ communication
- Shared utilities and helpers

## Structure

```
src/shared/
  types/          # Core data types
  interfaces/     # Abstract base classes for components
    rag/          # RAG-specific interfaces
    vector/       # Vector RAG interfaces
    graph/        # Graph RAG interfaces
  events/         # RabbitMQ event schemas
  utils/          # Shared utilities
```

## Usage

### In Server
```python
from shared.types import Document, Chunk
from shared.interfaces.rag import Chunker, EmbeddingEncoder
```

### In Workers
```python
from shared.types import Document
from shared.events import DocumentUploadedEvent
from shared.interfaces.vector import VectorIndex
```

## Installation

This package is installed as a local dependency in both server and worker packages.

```bash
cd packages/server
poetry add ../shared/python

cd packages/workers/ingestion
poetry add ../../../shared/python
```
