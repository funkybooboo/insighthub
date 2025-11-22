# Embeddings Worker

## Overview

The Embeddings Worker generates vector embeddings for all document chunks and inserts them into Qdrant.

## Responsibilities
- Read prepared chunks from Postgres
- Generate embeddings via Ollama / OpenAI / HF models
- Upsert embeddings into Qdrant
- Attach metadata (doc_id, chunk_id, title)

## Consumes Events
- `embeddings.generate`

## Produces Events
- `vector.index.updated`

## Architecture
Ingestion → Embeddings Worker → Qdrant index

## Running Locally

task dev
poetry run python src/main.py

## Environment Variables

QDRANT_URL=
OLLAMA_BASE_URL=
RABBITMQ_URL=
DATABASE_URL=

## Testing

pytest

## Extending

Add new embedding models or batching logic.

