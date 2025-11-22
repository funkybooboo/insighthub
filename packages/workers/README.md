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
| `chucker`   | Split documents into smaller chunks for embeddings               |
| `embedder`  | Generate embeddings from document chunks                         |
| `indexer`   | Store embeddings into a vector database (Vector RAG)             |
| `connector` | Build graph nodes and edges in a graph database (Graph RAG)      |
| `enricher`  | Add metadata, summaries, classifications, or post-processing     |
| `notifier`  | Publish events or notifications to downstream systems or UIs     |

---

## Worker Pipeline

### User-uploaded documents

```

user.upload → ingester → parser → chucker → embedder → indexer
→ connector
→ enricher → notifier

```

### External knowledge augmentation (Wikipedia, URL)

```

user.question → retriever → ingester → parser → chucker → embedder → indexer
→ connector
→ enricher → notifier

```

> The `embedder` output is fanned out to both `indexer` (Vector RAG) and `connector` (Graph RAG).

---

## Event Flow (RabbitMQ)

| Event               | Produced By | Consumed By        |
|---------------------|-------------|--------------------|
| `document.uploaded` | ingester    | parser             |
| `document.ingested` | parser      | chucker            |
| `document.parsed`   | chucker     | embedder           |
| `document.chunked`  | embedder    | indexer, connector |
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

Perfect! I can create a clear **worker flow diagram** for your README showing how documents move through the system, branching for Vector RAG and Graph RAG, and including external retrieval.

Here’s a textual/ASCII-style version you can embed in Markdown:

---

## Worker Pipeline Diagram

```
            ┌────────────┐
            │  Retriever │
            │(Wikipedia,│
            │ URLs, APIs)│
            └─────┬──────┘
                  │
                  ▼
            ┌────────────┐
            │  Ingester  │
            │(Uploads,   │
            │ retrieved) │
            └─────┬──────┘
                  │
                  ▼
            ┌────────────┐
            │   Parser   │
            │ (extract   │
            │  text)    │
            └─────┬──────┘
                  │
                  ▼
            ┌────────────┐
            │  Chucker   │
            │(split into │
            │  chunks)   │
            └─────┬──────┘
                  │
                  ▼
            ┌────────────┐
            │  Embedder  │
            │(create     │
            │ embeddings)│
            └─────┬──────┘
         ┌─────────┴─────────┐
         ▼                   ▼
  ┌────────────┐       ┌────────────┐
  │  Indexer   │       │ Connector  │
  │(Vector DB) │       │(Graph DB) │
  └─────┬──────┘       └─────┬──────┘
         │                    │
         └───────┬────────────┘
                 ▼
            ┌────────────┐
            │ Enricher   │
            │(metadata,  │
            │ summaries, │
            │ classifications) │
            └─────┬──────┘
                  ▼
            ┌────────────┐
            │ Notifier   │
            │(events/UI) │
            └────────────┘
```

---

# **Explanation**

- **Retriever → Ingester**: Handles external content (Wikipedia, URLs) or uploaded files.  
- **Parser → Chucker → Embedder**: Standard preprocessing pipeline for all content.  
- **Embedder → Indexer / Connector**: Branches for Vector RAG (`Indexer`) and Graph RAG (`Connector`).  
- **Enricher → Notifier**: Post-processing and notifications.  

This diagram makes it clear how **both user-uploaded and external content** can feed **Vector and Graph RAG pipelines simultaneously**.
