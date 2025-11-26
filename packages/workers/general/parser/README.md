# Parser Worker

Document parser worker - extracts text from various file formats (PDF, DOCX, HTML, TXT).

## Responsibility

- Consume document.uploaded events
- Fetch documents from MinIO storage
- Extract text content based on file type
- Store parsed text in PostgreSQL
- Publish document.parsed events

## Events

| Direction | Event             | Description                         |
|-----------|-------------------|-------------------------------------|
| Consumes  | document.uploaded | Triggered when document is uploaded |
| Produces  | document.parsed   | Emitted after text is extracted     |

## Environment Variables

| Variable           | Default                                                   | Description            |
|--------------------|-----------------------------------------------------------|------------------------|
| RABBITMQ_URL       | amqp://insighthub:insighthub_dev@rabbitmq:5672/           | RabbitMQ connection    |
| RABBITMQ_EXCHANGE  | insighthub                                                | Exchange name          |
| DATABASE_URL       | postgresql://insighthub:insighthub_dev@postgres:5432/insighthub | PostgreSQL connection  |
| MINIO_ENDPOINT_URL | http://minio:9000                                         | MinIO endpoint         |
| MINIO_ACCESS_KEY   | insighthub                                                | MinIO access key       |
| MINIO_SECRET_KEY   | insighthub_dev_secret                                     | MinIO secret key       |
| MINIO_BUCKET_NAME  | documents                                                 | Storage bucket         |
| WORKER_CONCURRENCY | 4                                                         | Concurrent processing  |

## Development

```bash
# Install dependencies
poetry install

# Run worker
poetry run python -m src.main
```
