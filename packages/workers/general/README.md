# General Workers

Shared workers that provide core functionality across all RAG pipelines and handle infrastructure operations.

## Overview

General workers handle the foundational operations that support both Vector RAG and Graph RAG pipelines. These workers manage document ingestion, preprocessing, routing, enrichment, user interaction, external data sources, and infrastructure lifecycle.

## Workers

### Document Processing Pipeline

#### Parser (`parser/`)
**Purpose**: Entry point for document processing - handles multiple file formats
- **Input**: `document.uploaded` events with file metadata
- **Output**: `document.parsed` events with extracted text
- **Integration**: First worker in the pipeline, supports PDF, DOCX, HTML, TXT

#### Chucker (`chunker/`)
**Purpose**: Split documents into manageable chunks for processing
- **Input**: `document.parsed` events with document text
- **Output**: `document.chunked` events with chunk metadata
- **Integration**: Shared preprocessing step used by both vector and graph pipelines

#### Router (`router/`)
**Purpose**: Route documents to appropriate RAG pipelines based on configuration
- **Input**: `document.chunked` events after chunking
- **Output**: Routes events to vector and/or graph pipelines
- **Integration**: Decision point enabling hybrid RAG (vector + graph simultaneously)

### Content & Data Management

#### Wikipedia (`wikipedia/`)
**Purpose**: Fetch and process external content from Wikipedia
- **Input**: `wikipedia.fetch_requested` events with article titles
- **Output**: `document.uploaded` events for processed articles
- **Integration**: External knowledge augmentation, feeds into main document pipeline

#### Enricher (`enricher/`)
**Purpose**: Enhance documents with aggregated metadata and insights
- **Input**: `document.indexed` and `graph.updated` events
- **Output**: `document.enriched` events with enhanced metadata
- **Integration**: Post-processing step that combines data from multiple pipelines

### User Interaction & Orchestration

#### Chat (`chat/`)
**Purpose**: Handle conversational AI interactions and query orchestration
- **Input**: `chat.message_received` events with user messages
- **Output**: Streaming `chat.response_chunk` events and final responses
- **Integration**: Main user interface, coordinates between vector and graph query workers

### Infrastructure Management

#### Infrastructure Manager (`infrastructure-manager/`)
**Purpose**: Handle workspace lifecycle operations (provisioning and cleanup)
- **Input**: `workspace.provision_requested` and `workspace.deletion_requested`
- **Output**: `workspace.provision_status` and `workspace.deletion_status`
- **Integration**: Manages database collections, graph schemas, and storage buckets

## Integration with Other Components

### Server Integration
```
+------------+     +------------+     +------------+
|   Client   | --> |   Server   | --> |  Workers   |
|            |     |            |     |            |
| * Uploads  |     | * API Layer|     | * Parser   |
| * Chat     |     | * Routing  |     | * Chat     |
| * Settings |     | * Monitoring|    | * Router   |
+------------+     +------------+     +------------+
```

### Pipeline Integration
```
Vector Pipeline:     Router --> Chunker --> Vector Processor --> Vector Query --> Chat
Graph Pipeline:      Router --> Chunker --> Graph Preprocessor --> Graph Construction --> Graph Query --> Chat
Hybrid Pipeline:     Router --> Chunker --> [Both Vector & Graph Pipelines] --> Chat
```

### Client Integration
```
+------------+     +------------+     +------------+
|   Client   | <-> |   Server   | <-> |  Workers   |
|            |     |            |     |            |
| * Upload UI|     | * Progress |     | * Streaming|
| * Chat UI  |     | * Responses|     | * Status   |
| * Settings |     | * Routing  |     | * Events   |
+------------+     +------------+     +------------+
```

## Configuration

General workers use shared configuration:

```bash
# Document Processing
SUPPORTED_FILE_TYPES=pdf,docx,html,txt
MAX_FILE_SIZE=50MB
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# External Services
WIKIPEDIA_API_TIMEOUT=30
WIKIPEDIA_RATE_LIMIT=10

# Chat Configuration
MAX_CHAT_HISTORY=50
STREAM_CHUNK_SIZE=100
RESPONSE_TIMEOUT=60

# Infrastructure
DEFAULT_VECTOR_DIMENSION=768
GRAPH_SCHEMA_VERSION=v1.0
```

## Development

### Running Workers

```bash
# Run all general workers
docker compose --profile general up

# Run individual worker
cd packages/workers/general/parser
docker build -t insighthub-parser .
docker run insighthub-parser
```

### Testing

```bash
# Run worker tests
cd packages/workers/general/chat
poetry run pytest tests/

# Integration testing
docker compose --profile general-testing up
```

## Architecture Role

General workers serve as the **backbone of the InsightHub system**:

- **Document Pipeline**: Parser --> Chunker --> Router (foundation for all RAG)
- **User Interface**: Chat worker (main interaction point)
- **Data Enhancement**: Wikipedia + Enricher (knowledge augmentation)
- **Infrastructure**: Infrastructure Manager (system lifecycle)

These workers are **pipeline-agnostic** and support both Vector RAG and Graph RAG approaches, enabling the system's flexibility and extensibility.