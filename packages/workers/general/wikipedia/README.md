# Wikipedia Worker

## Overview
The Wikipedia Worker fetches and processes Wikipedia content for knowledge augmentation.

## Responsibilities
- Query Wikipedia API for article content
- Parse and clean Wikipedia markup
- Store content in MinIO and database
- Trigger document processing pipeline

## Events

| Direction | Event                      | Description                          |
|-----------|----------------------------|--------------------------------------|
| Consumes  | wikipedia.fetch_requested  | Triggered with article titles        |
| Produces  | document.uploaded          | Emitted for each fetched article     |
| Produces  | wikipedia.fetch_completed  | Emitted when fetch is complete       |

## Environment Variables

| Variable           | Default                                           | Description            |
|--------------------|---------------------------------------------------|------------------------|
| RABBITMQ_URL       | amqp://insighthub:insighthub_dev@rabbitmq:5672/   | RabbitMQ connection    |
| RABBITMQ_EXCHANGE  | insighthub                                        | Exchange name          |
| DATABASE_URL       | postgresql://insighthub:dev@localhost:5432/insights | Database connection    |
| MINIO_ENDPOINT_URL | http://minio:9000                                 | MinIO endpoint         |
| MINIO_ACCESS_KEY   | insighthub                                        | MinIO access key       |
| MINIO_SECRET_KEY   | insighthub_dev_secret                             | MinIO secret key       |
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