# Vector Workers

Vector-based RAG pipeline workers for similarity search and retrieval.

## Overview

Vector workers implement the traditional RAG (Retrieval-Augmented Generation) approach using dense vector embeddings and similarity search. This pipeline is optimized for semantic similarity and works well for general-purpose question answering.

## Pipeline Flow

```
+------------------+     +---------+     +-------------+     +-------------+
|  Document Flow  | --> | Chunker | --> | Processor  | --> |   Query     |
|                 |     |         |     |             |     |             |
| Router Output   |     +---------+     | * Embedding |     | * Search    |
|                 |                    | * Indexing  |     | * Retrieval |
+------------------+                    +-------------+     +-------------+
                                                               |
                                                               v
+------------------+     +-----------------+     +-----------------+
|   Similarity    | --> |    Context      | --> |   Chat Response |
|   Search        |     |  Retrieval      |     |                 |
+------------------+     +-----------------+     +-----------------+
```
Document Upload --> Parser --> Chunker --> Embedder --> Indexer --> [Query Time]
                                                            |
                                                    Similarity Search --> Context Retrieval
```

## Workers

### Document Parser (`parser/`)
**Purpose**: Extract clean text content from various document formats
- **Input**: `document.uploaded` events with file metadata
- **Output**: `document.parsed` events with extracted text
- **Integration**: Triggered by client document uploads via server API

### Text Chunker (`chunker/`)
**Purpose**: Split large documents into manageable chunks for embedding
- **Input**: `document.parsed` events with document text
- **Output**: `document.chunked` events with chunk metadata
- **Integration**: Prepares content for efficient embedding and retrieval

### Vector Embedder (`embedder/`)
**Purpose**: Generate dense vector embeddings from text chunks
- **Input**: `document.chunked` events with chunk IDs
- **Output**: `document.embedded` events with embedding data
- **Integration**: Uses Sentence Transformers for high-quality embeddings

### Vector Indexer (`indexer/`)
**Purpose**: Store embeddings in vector database for similarity search
- **Input**: `document.embedded` events with embedding data
- **Output**: `document.indexed` events confirming storage
- **Integration**: Stores vectors in Qdrant for fast similarity search

## Integration with Server & Client

### Server Integration
```
+------------+     +------------+     +-----------------+
|   Server   | --> |   Router   | --> | Vector Workers  |
|            |     |            |     |                 |
| * API Calls|     | * Routing  |     | * Processor     |
| * Config   |     | * Decisions|     | * Query         |
| * Monitoring|    | * Load Bal.|     | * Health Checks |
+------------+     +------------+     +-----------------+
```

### Client Integration
```
+------------+     +------------+     +-----------------+
|   Client   | <-> |   Server   | <-> | Vector Workers  |
|            |     |            |     |                 |
| * Upload UI|     | * Progress |     | * Processing    |
| * Chat UI  |     | * Responses|     | * Search        |
| * Settings |     | * Routing  |     | * Results       |
+------------+     +------------+     +-----------------+
```

## Configuration

Vector workers use environment variables for configuration:

```bash
# Embedding Model
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Vector Database
QDRANT_URL=http://qdrant:6333
VECTOR_DIMENSION=768

# Chunking Strategy
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Performance Characteristics

- **Strengths**:
  - Fast similarity search
  - Good for general QA
  - Low latency retrieval
  - Scalable for large document collections

- **Limitations**:
  - Limited reasoning about relationships
  - May miss complex multi-hop connections
  - Semantic similarity doesn't capture structured knowledge

## Development

### Running Workers

```bash
# Run all vector workers
docker compose --profile vector-workers up

# Run individual worker
cd packages/workers/vector/embedder
docker build -t insighthub-embedder .
docker run insighthub-embedder
```

### Testing

```bash
# Run worker tests
cd packages/workers/vector/embedder
poetry run pytest tests/

# Integration testing
docker compose --profile testing up
```

## Monitoring & Observability

Vector workers provide:
- **Latency Metrics**: Embedding generation and indexing times
- **Throughput Monitoring**: Documents processed per minute
- **Error Tracking**: Failed embeddings or indexing operations
- **Resource Usage**: Memory and CPU utilization

## Scaling Considerations

- **Horizontal Scaling**: Multiple embedder/indexer instances
- **Batch Processing**: Group small documents for efficient processing
- **Caching**: Cache frequent queries and embeddings
- **Load Balancing**: Distribute work across worker instances