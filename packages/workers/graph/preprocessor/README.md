# Graph Preprocessor Worker

Consolidated worker for graph RAG preprocessing: entity extraction, relationship extraction, and community detection.

## Responsibility

- Consume `document.chunked` events
- Extract named entities from document chunks
- Identify relationships between entities
- Apply community detection algorithms
- Store entities, relationships, and communities
- Publish `document.communities_detected` events

## Processing Pipeline

```
+-----------------+
| document.chunked |
+-----------------+
         |
         v
+-----------------+     +-----------------+
| Entity Extraction| --> |   NER Models    |
|                 |     |                 |
| * PERSON        |     | * spaCy         |
| * ORG           |     | * LLM-based     |
| * GPE           |     | * Confidence     |
+-----------------+     +-----------------+
         |
         v
+-----------------+     +-----------------+
|Relationship Ext.| --> |  Pattern Match  |
|                 |     |                 |
| * WORKS_FOR     |     | * Co-occurrence |
| * LOCATED_IN    |     | * LLM Analysis  |
| * PART_OF       |     | * Scoring       |
+-----------------+     +-----------------+
         |
         v
+-----------------+     +-----------------+
|Community Detect.| --> | Graph Algorithms|
|                 |     |                 |
| * Clusters      |     | * Leiden        |
| * Groups        |     | * Louvain       |
| * Relationships |     | * Connectivity  |
+-----------------+     +-----------------+
         |
         v
+-----------------+
|communities_detected|
+-----------------+
```

## Events

| Direction | Event                      | Description                          |
|-----------|----------------------------|--------------------------------------|
| Consumes  | document.chunked           | Triggered after document chunking    |
| Produces  | document.communities_detected | Emitted after full preprocessing     |

## Environment Variables

| Variable           | Default                                           | Description            |
|--------------------|---------------------------------------------------|------------------------|
| RABBITMQ_URL       | amqp://insighthub:insighthub_dev@rabbitmq:5672/   | RabbitMQ connection    |
| RABBITMQ_EXCHANGE  | insighthub                                        | Exchange name          |
| DATABASE_URL       | postgresql://insighthub:dev@localhost:5432/insights | Database connection    |
| OLLAMA_BASE_URL    | http://ollama:11434                               | Ollama API endpoint    |
| WORKER_CONCURRENCY | 2                                                 | Concurrent processing  |

## Development

```bash
# Install dependencies
poetry install

# Run worker
poetry run python -m src.main

# Run tests
poetry run pytest tests/
```