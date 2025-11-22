# Workers

This folder contains all the **workers** responsible for processing documents, embeddings, and graph structures in the InsightHub RAG system. Workers are **action-focused** and communicate via RabbitMQ events, allowing for **scalable, decoupled pipelines**.

The design supports:

- **User-uploaded documents**
- **External knowledge retrieval** (e.g., Wikipedia, URLs)
- **Vector-based RAG**
- **Graph-based RAG**
- **Hybrid RAG**
- **Large document handling** through chunking and streaming

---

## Worker List

| Worker      | Responsibility                                                   |
|-------------|------------------------------------------------------------------|
| `retriever` | Fetch external content from Wikipedia, URLs, or APIs             |
| `ingester`  | Receive raw documents (user-uploaded files or retrieved content) |
| `parser`    | Extract text/content from PDFs, DOCX, HTML, and TXT files        |
| `chunker`   | Split documents into smaller chunks for embeddings               |
| `embedder`  | Generate embeddings from document chunks                         |
| `indexer`   | Store embeddings into a vector database (Vector RAG)             |
| `connector` | Build graph nodes and edges in a graph database (Graph RAG)      |
| `enricher`  | Add metadata, summaries, classifications, or post-processing     |
| `notifier`  | Publish events or notifications to downstream systems or UIs     |

---

## Worker Pipeline

### User-uploaded documents

```
user.upload -> ingester -> parser -> chunker -> embedder -> indexer
                                                        \-> connector
                                                        \-> enricher -> notifier
```

### External knowledge augmentation (Wikipedia, URL)

```
user.question -> retriever -> ingester -> parser -> chunker -> embedder -> indexer
                                                                       \-> connector
                                                                       \-> enricher -> notifier
```

> The `embedder` output is fanned out to both `indexer` (Vector RAG) and `connector` (Graph RAG).

---

## Event Flow (RabbitMQ)

| Event               | Produced By | Consumed By        |
|---------------------|-------------|--------------------|
| `document.uploaded` | user/system | ingester           |
| `document.ingested` | ingester    | parser             |
| `document.parsed`   | parser      | chunker            |
| `document.chunked`  | chunker     | embedder           |
| `embedding.created` | embedder    | indexer, connector |
| `document.enriched` | enricher    | notifier           |

Workers communicate exclusively via **events**, allowing multiple pipelines (Vector, Graph, or Hybrid) to run **in parallel and independently**.

---

## Design Principles

1. **Action-focused workers**: each worker performs a single, clear task.
2. **Source-agnostic**: works for both user uploads and external data.
3. **Scalable**: each worker can scale horizontally independently.
4. **RAG-agnostic**: the same workers can support Vector RAG, Graph RAG, or Hybrid RAG.
5. **Large document support**: text is streamed, chunked, and processed incrementally to handle arbitrarily large files.

---

## Adding a New Worker

1. Create a new folder in `workers/` with the worker name (verb-style).
2. Implement the worker logic inside `main.py`.
3. Define input and output **RabbitMQ events** in line with the existing pipeline.
4. Add the worker to the orchestration system (Docker, Taskfile, etc.).

---

## Notes

- All workers are **decoupled**; any downstream change will not affect upstream workers.
- Workers can be **added, removed, or replaced** independently.
- The pipeline supports **dynamic augmentation** of the knowledge base for both Vector and Graph RAG systems.

---

## Worker Pipeline Diagram

```
                +------------+
                |  Retriever |
                | (Wikipedia,|
                |  URLs, APIs)|
                +-----+------+
                      |
                      v
                +------------+
                |  Ingester  |
                | (Uploads,  |
                |  retrieved)|
                +-----+------+
                      |
                      v
                +------------+
                |   Parser   |
                |  (extract  |
                |   text)    |
                +-----+------+
                      |
                      v
                +------------+
                |  Chunker   |
                | (split into|
                |   chunks)  |
                +-----+------+
                      |
                      v
                +------------+
                |  Embedder  |
                | (create    |
                | embeddings)|
                +-----+------+
           +----------+----------+
           |                     |
           v                     v
    +------------+         +------------+
    |  Indexer   |         | Connector  |
    | (Vector DB)|         | (Graph DB) |
    +-----+------+         +-----+------+
           |                     |
           +----------+----------+
                      |
                      v
                +------------+
                |  Enricher  |
                | (metadata, |
                | summaries, |
                | classify)  |
                +-----+------+
                      |
                      v
                +------------+
                |  Notifier  |
                | (events/UI)|
                +------------+
```

---

## Explanation

- **Retriever -> Ingester**: Handles external content (Wikipedia, URLs) or uploaded files.
- **Parser -> Chunker -> Embedder**: Standard preprocessing pipeline for all content.
- **Embedder -> Indexer / Connector**: Branches for Vector RAG (`Indexer`) and Graph RAG (`Connector`).
- **Enricher -> Notifier**: Post-processing and notifications.

This diagram shows how **both user-uploaded and external content** can feed **Vector and Graph RAG pipelines simultaneously**.
