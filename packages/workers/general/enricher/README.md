# Enricher Worker

## Overview
The Enricher Worker enhances documents with metadata, summaries, and insights by aggregating data from vector and graph databases.

## Responsibilities
- Aggregate data from vector and graph databases
- Generate document summaries and keywords
- Extract entities and topics
- Calculate document importance scores
- Store enrichment data

## Events

| Direction | Event              | Description                          |
|-----------|--------------------|--------------------------------------|
| Consumes  | document.indexed   | Triggered after vector processing    |
| Consumes  | graph.updated      | Triggered after graph processing     |
| Produces  | document.enriched  | Emitted after enrichment is complete |

## Environment Variables

| Variable           | Default                                           | Description            |
|--------------------|---------------------------------------------------|------------------------|
| RABBITMQ_URL       | amqp://insighthub:insighthub_dev@rabbitmq:5672/   | RabbitMQ connection    |
| RABBITMQ_EXCHANGE  | insighthub                                        | Exchange name          |
| DATABASE_URL       | postgresql://insighthub:dev@localhost:5432/insights | Database connection    |
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
