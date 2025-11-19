# Vector RAG Architecture

## Overview

Vector RAG (Retrieval-Augmented Generation) uses dense vector embeddings and similarity search to retrieve relevant context for LLM generation.

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    INGESTION PIPELINE                        │
└─────────────────────────────────────────────────────────────┘

Raw Documents (PDF, Text, HTML)
         │
         ▼
   DocumentParser ──────> Document objects
         │
         ▼
      Chunker ──────────> Chunks (semantic segments)
         │
         ▼
  MetadataEnricher ─────> Enriched chunks (token count, etc.)
         │
         ▼
  EmbeddingEncoder ─────> Vector embeddings
         │
         ▼
    VectorIndex ────────> Qdrant/Pinecone storage


┌─────────────────────────────────────────────────────────────┐
│                     QUERY PIPELINE                           │
└─────────────────────────────────────────────────────────────┘

User Query
         │
         ▼
  EmbeddingEncoder ─────> Query vector
         │
         ▼
  VectorRetriever ──────> Top-K similar chunks
         │
         ▼
      Ranker ───────────> Re-ranked results
         │
         ▼
  ContextBuilder ───────> LLM prompt with context
         │
         ▼
       LLM ─────────────> Generated answer
         │
         ▼
  OutputFormatter ──────> Final answer + citations
```

## Components

### Ingestion Components

1. **DocumentParser**
   - Parses raw bytes (PDF, HTML, text)
   - Extracts clean text
   - Preserves metadata (title, author, etc.)

2. **Chunker**
   - Splits text into semantic segments
   - Strategies: sentence, paragraph, character-based
   - Configurable chunk size and overlap

3. **MetadataEnricher**
   - Adds token count, language, hash
   - Attaches document provenance
   - Custom metadata fields

4. **EmbeddingEncoder**
   - Generates dense vector embeddings
   - Models: Ollama, OpenAI, Sentence Transformers
   - Batch processing for efficiency

5. **VectorIndex**
   - Stores vectors with metadata
   - Databases: Qdrant, Pinecone, Weaviate
   - Nearest-neighbor search

### Query Components

1. **VectorRetriever**
   - Encodes query to vector
   - Performs similarity search
   - Returns top-K chunks with scores

2. **Ranker**
   - Re-ranks results for relevance
   - Methods: cross-encoders, BM25, score fusion
   - Improves retrieval quality

3. **ContextBuilder**
   - Assembles chunks into LLM context
   - Respects token limits
   - Adds instructions and formatting

4. **LLM**
   - Generates answer from context
   - Models: Ollama, OpenAI, Claude
   - Streaming support

5. **OutputFormatter**
   - Formats final response
   - Adds citations and provenance
   - Structured JSON output

## Implementation

### Orchestrator: VectorRAGIndexer

```python
from shared.orchestrators import VectorRAGIndexer
from shared.interfaces.vector import *

indexer = VectorRAGIndexer(
    parser=PDFParser(),
    chunker=SentenceChunker(chunk_size=500, overlap=50),
    enricher=DefaultEnricher(),
    embedder=OllamaEmbeddings(model="nomic-embed-text"),
    vector_index=QdrantVectorStore(url="http://localhost:6333"),
)

# Ingest documents
ids = indexer.ingest([
    (pdf_bytes, {"title": "Paper 1", "workspace_id": "ws_123"}),
])
```

### Orchestrator: VectorRAG

```python
from shared.orchestrators import VectorRAG

rag = VectorRAG(
    embedder=OllamaEmbeddings(model="nomic-embed-text"),
    vector_retriever=QdrantRetriever(store),
    ranker=CrossEncoderRanker(),
    context_builder=DefaultContextBuilder(max_tokens=2000),
    llm=OllamaLLM(model="llama3.2:1b"),
    formatter=CitationFormatter(),
)

# Query
result = rag.query("What is RAG?", k=5)
print(result["answer"])
for source in result["provenance"]:
    print(f"- {source['document_id']}: {source['score']}")
```

## Advantages

- **Simple**: Easy to understand and implement
- **Fast**: Efficient vector similarity search
- **Scalable**: Handles millions of vectors
- **Accurate**: Good for factual retrieval

## Limitations

- **No reasoning**: Cannot infer relationships
- **Limited context**: Fixed-size chunks
- **No graph structure**: Misses entity connections
- **Query dependent**: Relies on query-document similarity

## Use Cases

- Document Q&A
- Semantic search
- FAQ systems
- Knowledge base retrieval

## See Also

- [Graph RAG Architecture](./graph-rag-architecture.md)
- [RAG Comparison](./comparison.md)
- Implementation: `packages/shared/python/src/shared/orchestrators/vector_rag.py`
