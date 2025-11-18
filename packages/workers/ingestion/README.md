# Ingestion Worker

## Overview
The Ingestion Worker is responsible for transforming raw uploaded documents into structured, chunked, and normalized text ready for both Vector RAG and Graph RAG pipelines.

It is the first stage of the offline processing pipeline.

## Responsibilities
- Download document from MinIO
- Convert PDF → text
- Clean and normalize text
- Split into semantic chunks
- Extract metadata (title, authors, citations)
- Store processed text in Postgres
- Publish follow-up events to trigger embeddings and graph construction

## Consumes Events
- `document.uploaded`

## Produces Events
- `document.chunks.ready`
- `document.graph.build`
- `embeddings.generate`

## Architecture
1. Server stores uploaded file in MinIO  
2. Worker is triggered via RabbitMQ  
3. Text is extracted and chunked  
4. Chunks saved in Postgres  
5. Subsequent jobs triggered (embeddings + graph)

## Running Locally

task dev
poetry run python src/main.py

## Environment Variables

MINIO_URL=
MINIO_ACCESS_KEY=
MINIO_SECRET_KEY=
RABBITMQ_URL=
DATABASE_URL=

## Testing

pytest

## Extending / Customizing

Add new extractors, PDF parsers, or metadata enrichers in `src/handlers/`.
