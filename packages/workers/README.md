# Workers

This folder contains all the **workers** responsible for processing documents, embeddings, chat messages, and graph structures in the InsightHub RAG system. Workers are **action-focused** and communicate via RabbitMQ events, allowing for **scalable, decoupled pipelines**.

The design supports:

- **User-uploaded documents**
- **External knowledge retrieval** (Wikipedia, URLs)
- **Vector-based RAG**
- **Graph-based RAG**
- **Hybrid RAG**
- **Chat interactions with streaming responses**
- **Workspace provisioning and management**
- **Large document handling** through chunking and streaming

---

## Worker List

| Worker        | Responsibility                                            | Status        | Events Consumed                     | Events Produced                                                                        |
|---------------|-----------------------------------------------------------|---------------|-------------------------------------|----------------------------------------------------------------------------------------|
| `parser`      | Extract text/content from PDFs, DOCX, HTML, and TXT files | [x] Implemented | `document.uploaded`                 | `document.parsed`                                                                      |
| `chucker`     | Split documents into smaller chunks for embeddings        | [x] Implemented | `document.parsed`                   | `document.chunked`                                                                     |
| `embedder`    | Generate embeddings from document chunks                  | [x] Implemented | `document.chunked`                  | `document.embedded`                                                                    |
| `indexer`     | Store embeddings into Qdrant vector database              | [x] Implemented | `document.embedded`                 | `document.indexed`                                                                     |
| `connector`   | Build graph nodes and edges in Neo4j (Graph RAG)          | [x] Implemented | `document.embedded`                 | `graph.updated`                                                                        |
| `enricher`    | Add metadata, summaries, classifications                  | [x] Implemented | `document.indexed`, `graph.updated` | `document.enriched`                                                                    |
| `chat`        | Process chat messages with RAG and LLM streaming          | [x] Implemented | `chat.message_received`             | `chat.response_chunk`, `chat.response_complete`, `chat.error`, `chat.no_context_found` |
| `wikipedia`   | Fetch content from Wikipedia and create documents         | [x] Implemented | `wikipedia.fetch_requested`         | `document.uploaded`, `wikipedia.fetch_completed`                                       |
| `provisioner` | Workspace infrastructure provisioning                     | [x] Implemented | `workspace.provision_requested`     | `workspace.provision_status`                                                           |
| `deletion`    | Workspace and document cleanup/deletion                   | [x] Implemented | `workspace.deletion_requested`, `document.deleted` | `workspace.deletion_status` |

---

## Complete Event Flow

### Document Processing Pipeline (Vector + Graph RAG)

```
document.uploaded --> Parser --> document.parsed --> Chucker --> document.chunked --> Embedder --> document.embedded
                                                                                      |
                                                                      Indexer --> document.indexed
                                                                                      |
                                                                Enricher --> document.enriched
                                                                                      ^
document.embedded --> Connector --> graph.updated ------------------------------^
```

### Wikipedia Content Pipeline

```
wikipedia.fetch_requested --> Wikipedia --> document.uploaded --> [Document Processing Pipeline]
```

### Chat Interaction Pipeline

```
chat.message_received --> Chat --> chat.response_chunk/chat.response_complete/chat.error/chat.no_context_found
```

### Workspace Management Pipelines

```
workspace.provision_requested --> Provisioner --> workspace.provision_status

workspace.deletion_requested --> Deletion --> workspace.deletion_status
```

---

## Detailed Worker Descriptions

### Core Document Processing Workers

#### Parser Worker (`packages/workers/parser/`)
**Purpose**: Extract clean text content from various document formats
- **Input**: `document.uploaded` events with file metadata
- **Output**: `document.parsed` events with extracted text
- **Responsibilities**:
  - Retrieve files from MinIO object storage
  - Parse PDFs, DOCX, HTML, and plain text files
  - Clean and normalize extracted text
  - Store parsed text in PostgreSQL database
  - Update document processing status

#### Chucker Worker (`packages/workers/chucker/`)
**Purpose**: Split large documents into manageable chunks for embedding
- **Input**: `document.parsed` events with document text
- **Output**: `document.chunked` events with chunk metadata
- **Responsibilities**:
  - Retrieve parsed text from database
  - Apply configurable chunking strategies (character, word, sentence)
  - Handle chunk overlap for context preservation
  - Store chunks in database with metadata
  - Generate unique chunk IDs

#### Embedder Worker (`packages/workers/embedder/`)
**Purpose**: Generate vector embeddings from text chunks
- **Input**: `document.chunked` events with chunk IDs
- **Output**: `document.embedded` events with embedding metadata
- **Responsibilities**:
  - Retrieve text chunks from database
  - Generate embeddings using Sentence Transformers
  - Batch processing for performance
  - Store embeddings in database
  - Handle GPU/CPU selection automatically

#### Indexer Worker (`packages/workers/indexer/`)
**Purpose**: Store embeddings in vector database for similarity search
- **Input**: `document.embedded` events with embedding data
- **Output**: `document.indexed` events confirming storage
- **Responsibilities**:
  - Connect to Qdrant vector database
  - Create/manage collections as needed
  - Upsert vectors with metadata
  - Handle batch operations efficiently
  - Update document processing status

#### Connector Worker (`packages/workers/connector/`)
**Purpose**: Build knowledge graphs from document embeddings
- **Input**: `document.embedded` events with chunk data
- **Output**: `graph.updated` events with graph statistics
- **Responsibilities**:
  - Extract entities and relationships from chunks
  - Connect to Neo4j graph database
  - Create/update nodes and relationships
  - Apply graph algorithms (Leiden clustering)
  - Generate graph statistics

#### Enricher Worker (`packages/workers/enricher/`)
**Purpose**: Enhance documents with metadata and insights
- **Input**: `document.indexed` and `graph.updated` events
- **Output**: `document.enriched` events with enhanced metadata
- **Responsibilities**:
  - Aggregate data from vector and graph databases
  - Generate document summaries and keywords
  - Extract entities and topics
  - Calculate document importance scores
  - Store enrichment data

### Specialized Workers

#### Chat Worker (`packages/workers/chat/`)
**Purpose**: Handle conversational AI interactions with RAG
- **Input**: `chat.message_received` events with user messages
- **Output**: Streaming `chat.response_chunk` events, final `chat.response_complete`
- **Responsibilities**:
  - Retrieve relevant context from vector/graph databases
  - Generate responses using LLM (Ollama)
  - Stream responses in real-time chunks
  - Handle conversation memory and context
  - Provide fallback responses when no context found

#### Wikipedia Worker (`packages/workers/wikipedia/`)
**Purpose**: Fetch and process Wikipedia content for knowledge augmentation
- **Input**: `wikipedia.fetch_requested` events with article titles
- **Output**: `document.uploaded` events for each fetched article
- **Responsibilities**:
  - Query Wikipedia API for article content
  - Parse and clean Wikipedia markup
  - Store content in MinIO and database
  - Trigger document processing pipeline
  - Handle rate limiting and errors

#### Provisioner Worker (`packages/workers/provisioner/`)
**Purpose**: Set up infrastructure for new workspaces
- **Input**: `workspace.provision_requested` events
- **Output**: `workspace.provision_status` events with progress
- **Responsibilities**:
  - Create Qdrant collections for new workspaces
  - Initialize Neo4j graph structures
  - Set up MinIO buckets
  - Configure workspace-specific settings
  - Report provisioning progress

#### Deletion Worker (`packages/workers/deletion/`)
**Purpose**: Clean up workspaces and documents when deleted
- **Input**: `workspace.deletion_requested` and `document.deleted` events
- **Output**: `workspace.deletion_status` events with progress
- **Responsibilities**:
  - Delete all documents in a workspace
  - Remove vectors from Qdrant collections
  - Clean up graph data from Neo4j
  - Delete files from MinIO storage
  - Remove database records
  - Provide progress updates during deletion

---

## Design Principles

1. **Single Responsibility**: Each worker performs one clear, focused task
2. **Event-Driven**: Workers communicate exclusively through RabbitMQ events
3. **Horizontally Scalable**: Each worker can scale independently
4. **Fault Tolerant**: Robust error handling with retry logic and dead letter queues
5. **Stateless**: Workers don't maintain state between operations
6. **Configurable**: Environment-based configuration for different environments
7. **Observable**: Comprehensive logging and health checks

---

## Technology Stack

- **Language**: Python 3.11+ with Poetry dependency management
- **Messaging**: RabbitMQ with AMQP protocol and topic exchanges
- **Vector Database**: Qdrant for high-performance similarity search
- **Graph Database**: Neo4j for knowledge graph operations
- **Object Storage**: MinIO for document storage
- **LLM Integration**: Ollama for local AI processing
- **Containerization**: Docker with health checks and resource limits
- **Monitoring**: Structured JSON logging with correlation IDs

---

## Configuration

All workers share common configuration via environment variables:

```bash
# RabbitMQ
RABBITMQ_URL=amqp://insighthub:insighthub_dev@rabbitmq:5672/
RABBITMQ_EXCHANGE=insighthub

# Databases
DATABASE_URL=postgresql://insighthub:insighthub_dev@postgres:5432/insighthub
QDRANT_URL=http://qdrant:6333
NEO4J_URL=bolt://neo4j:7687

# Object Storage
MINIO_ENDPOINT_URL=http://minio:9000
MINIO_ACCESS_KEY=insighthub
MINIO_SECRET_KEY=insighthub_dev_secret

# AI/ML
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=llama3.2

# Worker Settings
WORKER_CONCURRENCY=4
```

---

## Development and Deployment

### Adding a New Worker

1. Create a new folder in `packages/workers/` with a verb-based name
2. Implement the worker inheriting from `BaseWorker`
3. Define input/output events following the established patterns
4. Add Docker configuration and health checks
5. Update this README with the new worker documentation

### Running Workers

```bash
# Run all workers with Docker Compose
docker compose --profile workers up

# Run individual worker
cd packages/workers/parser
docker build -t insighthub-parser .
docker run insighthub-parser

# Development with hot reload
cd packages/workers/parser
poetry install
poetry run python src/main.py
```

---

## Monitoring and Observability

All workers include:

- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Health Checks**: HTTP endpoints for container orchestration
- **Metrics**: Processing latency, queue depth, error rates
- **Error Handling**: Automatic retries with exponential backoff
- **Dead Letter Queues**: Failed messages routed for manual inspection

---

## Current Implementation Status

### Fully Implemented Workers
- **Base Worker Infrastructure**: Shared `BaseWorker` class with RabbitMQ integration
- **Parser Worker**: Document parsing with MinIO integration
- **Chucker Worker**: Multi-strategy text chunking
- **Embedder Worker**: Sentence Transformer embeddings
- **Indexer Worker**: Qdrant vector storage
- **Connector Worker**: Neo4j graph construction
- **Enricher Worker**: Metadata enrichment framework
- **Chat Worker**: Streaming LLM responses with RAG
- **Wikipedia Worker**: External content fetching
- **Provisioner Worker**: Workspace infrastructure setup
- **Deletion Worker**: Workspace and document cleanup

### Ready for Implementation
All workers have complete scaffolding with TODO comments for complex operations. The heavy lifting (database operations, external service integrations, complex algorithms) remains to be implemented in each worker's TODO sections.

---

## Architecture Benefits

- **Scalability**: Workers can scale independently based on load
- **Reliability**: Fault isolation prevents cascade failures
- **Maintainability**: Single responsibility makes workers easy to understand and modify
- **Testability**: Event-driven design enables comprehensive testing
- **Flexibility**: Easy to add new workers or modify existing pipelines
- **Observability**: Complete event tracing through the entire pipeline

This architecture supports both **Vector RAG** and **Graph RAG** simultaneously, with the ability to add new RAG approaches (hybrid, multi-modal, etc.) without disrupting existing functionality.