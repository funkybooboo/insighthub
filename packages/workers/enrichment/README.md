# Enrichment Worker

## Overview
The Enrichment Worker fetches external knowledge to enhance RAG quality.

## Responsibilities
- Identify outbound citations or references
- Fetch remote documents via arXiv/OpenAlex
- Summarize references
- Add enriched knowledge to graph/vector pipelines

## Consumes Events
- `document.metadata.extracted`
- `document.graph.build`

## Produces Events
- `enrichment.complete`
- Optional: `document.uploaded` (for recursive ingestion)

## Architecture
Triggered after graph or metadata extraction to augment knowledge.

## Running Locally

task dev
poetry run python src/main.py


## Environment Variables

OPENALEX_API_KEY=
RABBITMQ_URL=


## Testing

pytest


## Extending
Add more data sources or summarization providers.
