# InsightHub Refactoring Plan

This document outlines the file system reorganization to establish a clean, maintainable architecture.

## Goals

1. Create shared Python package for types and interfaces used by server and workers
2. Refactor client to feature-based structure
3. Move RAG notes to documentation
4. Implement foundational RAG interfaces
5. Add TODOs for future implementation work

---

## Status: IN PROGRESS

### Completed ✅

1. **Shared Python Package Structure**
   - Created `packages/shared/python/` with Poetry configuration
   - Implemented core data types:
     - `shared.types.common` - PrimitiveValue, MetadataValue
     - `shared.types.document` - Document, Chunk
     - `shared.types.graph` - GraphNode, GraphEdge
     - `shared.types.rag` - ChunkerConfig, RagConfig, SearchResult
     - `shared.types.retrieval` - RetrievalResult

2. **Vector RAG Interfaces** (based on `vector_rag_notes.py`)
   - `shared.interfaces.vector.parser.DocumentParser` - Parse raw bytes to Document
   - `shared.interfaces.vector.chunker.Chunker` - Split documents into chunks
   - `shared.interfaces.vector.chunker.MetadataEnricher` - Enrich chunk metadata
   - `shared.interfaces.vector.embedder.EmbeddingEncoder` - Generate embeddings
   - `shared.interfaces.vector.store.VectorIndex` - Vector storage abstraction
   - `shared.interfaces.vector.retriever.VectorRetriever` - High-level retrieval
   - `shared.interfaces.vector.ranker.Ranker` - Rerank results
   - `shared.interfaces.vector.context.ContextBuilder` - Build LLM context
   - `shared.interfaces.vector.llm.LLM` - LLM generation interface
   - `shared.interfaces.vector.formatter.OutputFormatter` - Format responses

### In Progress 🚧

3. **Graph RAG Interfaces** (based on `graph_rag_notes.py`)
   - TODO: Entity extraction interfaces
   - TODO: Relation extraction interfaces
   - TODO: Graph builder interfaces
   - TODO: Graph store interfaces
   - TODO: Graph retrieval interfaces
   - TODO: Hybrid retriever interfaces

### Pending ⏳

4. **Orchestrators**
   - TODO: `shared.orchestrators.VectorRAGIndexer` - Ingestion pipeline
   - TODO: `shared.orchestrators.VectorRAG` - Query pipeline
   - TODO: `shared.orchestrators.GraphRAGIndexer` - Graph ingestion
   - TODO: `shared.orchestrators.GraphRAG` - Graph query

5. **Event Schemas** (for RabbitMQ)
   - TODO: `shared.events.document` - Document events
   - TODO: `shared.events.embedding` - Embedding events
   - TODO: `shared.events.graph` - Graph events
   - TODO: `shared.events.query` - Query events

6. **Move RAG Notes to Docs**
   - TODO: Move `graph_rag_notes.py` to `docs/rag/graph-rag-architecture.md`
   - TODO: Move `vector_rag_notes.py` to `docs/rag/vector-rag-architecture.md`
   - TODO: Create `docs/rag/comparison.md`

7. **Client Refactoring**
   - TODO: Reorganize to feature-based structure (OPTIONAL - current structure is good)
   - Current structure (domain-based) works well, only refactor if needed

8. **Server Updates**
   - TODO: Update server to depend on `insighthub-shared`
   - TODO: Migrate existing RAG types to use shared types
   - TODO: Update imports throughout server codebase

9. **Worker Implementation**
   - TODO: Add shared package dependency to all workers
   - TODO: Implement ingestion worker using shared interfaces
   - TODO: Implement embeddings worker
   - TODO: Implement graph worker

---

## New File Structure

```
packages/
  shared/
    python/
      src/
        shared/
          __init__.py
          types/                    # ✅ DONE
            __init__.py
            common.py              # PrimitiveValue, MetadataValue
            document.py            # Document, Chunk
            graph.py               # GraphNode, GraphEdge
            rag.py                 # RagConfig, ChunkerConfig, SearchResult
            retrieval.py           # RetrievalResult
          interfaces/              # ✅ Vector DONE, Graph TODO
            __init__.py
            vector/                # ✅ DONE
              __init__.py
              parser.py            # DocumentParser
              chunker.py           # Chunker, MetadataEnricher
              embedder.py          # EmbeddingEncoder
              store.py             # VectorIndex
              retriever.py         # VectorRetriever
              ranker.py            # Ranker
              context.py           # ContextBuilder
              llm.py               # LLM
              formatter.py         # OutputFormatter
            graph/                 # TODO
              __init__.py
              entity.py            # EntityExtractor
              relation.py          # RelationExtractor
              builder.py           # GraphBuilder
              store.py             # GraphStore
              retriever.py         # GraphRetriever
            hybrid/                # TODO
              __init__.py
              retriever.py         # HybridRetriever
              fusion.py            # FusionScorer
          orchestrators/           # TODO
            __init__.py
            vector_rag.py          # VectorRAGIndexer, VectorRAG
            graph_rag.py           # GraphRAGIndexer, GraphRAG
          events/                  # TODO
            __init__.py
            document.py
            embedding.py
            graph.py
            query.py
          utils/                   # Future
            __init__.py
      pyproject.toml               # ✅ DONE
      README.md                    # ✅ DONE

  server/
    src/
      infrastructure/
        rag/
          # TODO: Update to use shared.interfaces instead of local interfaces
          # TODO: Keep concrete implementations (QdrantVectorStore, OllamaEmbeddings, etc.)
      domains/
        # No changes needed

  workers/
    ingestion/
      src/
        # TODO: Implement using shared.interfaces
    embeddings/
      src/
        # TODO: Implement using shared.interfaces
    graph/
      src/
        # TODO: Implement using shared.interfaces
    # ... other workers

  client/
    # Current structure is fine (domain-based)
    # OPTIONAL: Refactor to feature-based only if project grows significantly
```

---

## Migration Steps

### Phase 1: Shared Package Setup (COMPLETED)

1. ✅ Create shared package structure
2. ✅ Implement core types
3. ✅ Implement Vector RAG interfaces
4. ⏳ Implement Graph RAG interfaces
5. ⏳ Implement orchestrators
6. ⏳ Add event schemas

### Phase 2: Server Migration (TODO)

1. Add shared package to server dependencies:
   ```bash
   cd packages/server
   poetry add ../shared/python
   ```

2. Update imports:
   ```python
   # OLD
   from src.infrastructure.rag.types import Chunk, Document
   
   # NEW
   from shared.types import Chunk, Document
   ```

3. Update RAG implementations to use shared interfaces:
   ```python
   # OLD
   from src.infrastructure.rag.embeddings.embedding import EmbeddingModel
   
   # NEW
   from shared.interfaces.vector import EmbeddingEncoder
   ```

4. Remove duplicate type definitions from server

### Phase 3: Worker Implementation (TODO)

1. Add shared package to worker dependencies
2. Implement workers using shared interfaces
3. Add Dockerfiles for each worker
4. Add workers to docker-compose.yml
5. Implement RabbitMQ integration

### Phase 4: Documentation (TODO)

1. Move `graph_rag_notes.py` → `docs/rag/graph-rag-architecture.md`
2. Move `vector_rag_notes.py` → `docs/rag/vector-rag-architecture.md`
3. Create `docs/rag/comparison.md`
4. Update `docs/architecture.md` with new structure
5. Create `docs/shared-package.md` explaining the shared package

### Phase 5: Client (OPTIONAL)

- Current domain-based structure works well
- Only refactor if project grows to 20+ features
- Defer this to future work

---

## Key Decisions

### ✅ Keep Current Client Structure
The current domain-based organization (`src/components/`, `src/services/`, `src/store/`) works well for the current project size. Feature-based restructuring adds complexity without clear benefit at this scale.

### ✅ Use Shared Package for Types and Interfaces
All common types and abstract interfaces go in `shared/`. Concrete implementations stay in `server/` or `workers/`. This enables code reuse without duplication.

### ✅ Workers Use Same Interfaces as Server
Both server and workers implement the same RAG interfaces. This allows workers to be extracted from server logic without breaking compatibility.

### ⏳ Event-Driven Architecture with RabbitMQ
Workers communicate via RabbitMQ events. Event schemas are defined in `shared.events` to ensure consistency.

---

## TODOs Added to Codebase

### Server TODOs

```python
# packages/server/src/infrastructure/rag/factory.py
# TODO: Migrate to use shared.interfaces.vector.* instead of local interfaces
# TODO: Update create_rag() to return shared.orchestrators.VectorRAG instance

# packages/server/src/domains/chat/service.py
# TODO: Integrate RAG query pipeline using shared.orchestrators.VectorRAG
# TODO: Add support for GraphRAG alongside VectorRAG

# packages/server/src/domains/documents/service.py
# TODO: Trigger RabbitMQ events for async worker processing
# TODO: Use shared.orchestrators.VectorRAGIndexer for document ingestion
```

### Worker TODOs

```python
# packages/workers/ingestion/src/main.py
# TODO: Implement DocumentParser using shared.interfaces.vector.parser
# TODO: Implement Chunker using shared.interfaces.vector.chunker
# TODO: Listen for document.uploaded events
# TODO: Publish embeddings.generate and document.graph.build events

# packages/workers/embeddings/src/main.py
# TODO: Implement EmbeddingEncoder using shared.interfaces.vector.embedder
# TODO: Implement VectorIndex integration for Qdrant
# TODO: Listen for embeddings.generate events
# TODO: Publish vector.index.updated events

# packages/workers/graph/src/main.py
# TODO: Implement EntityExtractor using shared.interfaces.graph.entity
# TODO: Implement RelationExtractor using shared.interfaces.graph.relation
# TODO: Implement GraphBuilder using shared.interfaces.graph.builder
# TODO: Implement GraphStore integration for Neo4j
# TODO: Listen for document.graph.build events
# TODO: Publish graph.build.complete events
```

---

## Testing Strategy

### Shared Package Tests

```bash
cd packages/shared/python
poetry run pytest tests/
```

Tests should cover:
- Type validation and serialization
- Interface contracts (using dummy implementations)
- Event schema validation

### Server Integration Tests

After migration, ensure:
- Existing RAG tests still pass
- Types are compatible
- Imports resolve correctly

### Worker Tests

Each worker should have:
- Unit tests with dummy implementations
- Integration tests with testcontainers (Qdrant, Neo4j, RabbitMQ)

---

## Next Steps

1. **Complete Graph RAG interfaces** (in `shared/interfaces/graph/`)
2. **Create orchestrators** (in `shared/orchestrators/`)
3. **Move RAG notes to documentation** (`docs/rag/`)
4. **Add shared package to server** (`poetry add ../shared/python`)
5. **Migrate server imports** (update all imports to use `shared.*`)
6. **Implement ingestion worker** (using shared interfaces)
7. **Add RabbitMQ integration** (event publishing/consuming)
8. **Update documentation** (architecture diagrams, API docs)

---

## Questions to Resolve

1. **Neo4j vs PostgreSQL for Graph Store?**
   - Neo4j is more powerful for graph operations
   - PostgreSQL is simpler, already in stack
   - Decision: Start with PostgreSQL, migrate to Neo4j if needed

2. **Synchronous vs Async Document Processing?**
   - Current: Synchronous in server
   - Future: Async with workers
   - Decision: Keep synchronous for now, add async as optimization

3. **Client Refactoring Priority?**
   - Current structure works well
   - Feature-based adds complexity
   - Decision: Defer client refactoring

---

## Success Criteria

- ✅ Shared package installed and importable in server and workers
- ✅ No duplicate type definitions between packages
- ✅ All interfaces documented with examples
- ⏳ Server migrated to use shared types/interfaces
- ⏳ At least 2 workers implemented (ingestion, embeddings)
- ⏳ RAG notes moved to markdown documentation
- ⏳ All tests passing after refactoring
- ⏳ Docker Compose can run full stack (server + workers)

---

*Last Updated: 2025-11-18*
*Status: Phase 1 Complete, Phase 2 In Progress*
