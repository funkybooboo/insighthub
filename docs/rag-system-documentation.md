# InsightHub RAG System Documentation

This document describes the Retrieval-Augmented Generation (RAG) implementation in InsightHub, focusing on the actual codebase and architecture rather than general RAG concepts.

## Overview

InsightHub implements a Vector RAG system that enhances LLM responses by retrieving relevant context from user-uploaded documents. The system uses a modular architecture with pluggable components for parsing, chunking, embedding, and vector storage.

## Why RAG Matters

Traditional LLMs have several limitations:
- **Knowledge cutoff**: Limited to training data up to a certain date
- **Domain specificity**: Lack deep knowledge in specialized fields
- **Proprietary data**: Cannot access private or organizational data
- **Hallucinations**: May generate incorrect information confidently

RAG addresses these issues by:
- Providing access to current, domain-specific information
- Enabling use of proprietary or private data
- Reducing hallucinations through grounded responses
- Maintaining LLM's reasoning capabilities

## Core Components

### 1. Document Processing Pipeline

#### Document Parsing
InsightHub supports multiple document formats through a factory pattern:

```python
# packages/shared/python/src/shared/documents/parsing/
from shared.documents.parsing import create_document_parser

# Create parser based on file type
parser = create_document_parser("pdf")  # or "docx", "text", "html"
result = parser.parse(file_stream, metadata)
document = result.ok()  # Document object with text content
```

**Supported Formats**:
- PDF documents (PyPDF)
- Microsoft Word documents (python-docx)
- Plain text files
- HTML content

#### Text Chunking
Documents are split into manageable chunks using configurable strategies:

```python
# packages/shared/python/src/shared/documents/chunking/
from shared.documents.chunking import create_document_chunker

chunker = create_document_chunker("sentence", chunk_size=1000, overlap=200)
chunks = chunker.chunk(document)
# Returns list of Chunk objects with text, metadata, and embeddings
```

**Chunking Best Practices:**
- Use semantic boundaries (paragraphs, sections)
- Maintain overlap for context continuity
- Consider token limits of your LLM
- Preserve document structure when possible

![img.png](chunking_strategies_for_rag.png)

### 2. Vector Embeddings

#### Embedding Generation
InsightHub uses configurable embedding models through a factory pattern:

```python
# packages/shared/python/src/shared/documents/embedding/
from shared.documents.embedding import create_embedding_encoder

# Create encoder (Ollama, OpenAI, or Sentence Transformers)
encoder = create_embedding_encoder("ollama", model_name="nomic-embed-text")

# Encode single text or batch
result = encoder.encode_one("What is machine learning?")
# Returns Result[list[float]] with 768-dimensional vector

batch_result = encoder.encode(["text1", "text2", "text3"])
# Returns Result[list[list[float]]] for batch processing
```

#### Supported Embedding Models
- **Ollama**: `nomic-embed-text` (local, 768 dimensions)
- **OpenAI**: `text-embedding-ada-002` (1536 dimensions)
- **Sentence Transformers**: Various models available

#### Semantic Similarity
Embeddings enable efficient similarity search in vector databases.

#### Visualization
Embeddings can be visualized in reduced dimensions:

```python
from sklearn.manifold import TSNE
import plotly.graph_objs as go

# Reduce 384D embeddings to 3D for visualization
tsne = TSNE(n_components=3, perplexity=10, random_state=42)
reduced_embeddings = tsne.fit_transform(embeddings_matrix)

# Create 3D scatter plot
fig = go.Figure(data=[go.Scatter3d(
    x=reduced_embeddings[:, 0],
    y=reduced_embeddings[:, 1],
    z=reduced_embeddings[:, 2],
    mode='markers+text',
    text=words,
    marker=dict(size=5, opacity=0.7)
)])
```

### 3. Vector Storage (Qdrant)

#### Qdrant Integration
InsightHub uses Qdrant for high-performance vector similarity search:

```python
# packages/shared/python/src/shared/database/vector/
from shared.database.vector import create_vector_database

# Create Qdrant client
vector_db = create_vector_database("qdrant", host="localhost", port=6333)

# Create workspace-specific collection
collection_name = f"workspace_{workspace_id}"
vector_store = vector_db.create_store(collection_name, dimension=768)

# Store document chunks with embeddings
chunks_with_embeddings = [...]  # List of Chunk objects
vector_store.add(chunks_with_embeddings)
```

#### Retrieval
Find most relevant document chunks for a query:

```python
# packages/shared/python/src/shared/orchestrators/vector_rag.py
from shared.orchestrators import VectorRAG

# Create RAG instance
rag = VectorRAG(embedder=encoder, vector_store=vector_store)

# Query with semantic search
results = rag.query("What is machine learning?", top_k=5)
# Returns List[RetrievalResult] with chunks and similarity scores

for result in results:
    print(f"Score: {result.score:.3f}")
    print(f"Text: {result.chunk.text[:100]}...")
```

## Complete RAG Pipeline

### Architecture Overview

```
User Query --> Chat Service --> Worker --> RAG Pipeline --> LLM --> Response
      |           |           |           |           |           |
   WebSocket --> Store Msg --> RabbitMQ --> Retrieve --> Augment --> Stream Back
```

### Vector RAG Implementation

```python
# packages/shared/python/src/shared/orchestrators/vector_rag.py

class VectorRAGIndexer:
    """Orchestrates document indexing pipeline."""

    def __init__(self, parser, chunker, embedder, vector_store):
        self.parser = parser
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store

    def index(self, file_stream, metadata=None):
        """Index a document through the full pipeline."""
        # 1. Parse document
        doc_result = self.parser.parse(file_stream, metadata)
        document = doc_result.ok()

        # 2. Chunk document
        chunks = self.chunker.chunk(document)

        # 3. Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings_result = self.embedder.encode(texts)
        embeddings = embeddings_result.ok()

        # 4. Store in vector database
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i]
        self.vector_store.add(chunks)

        return document

class VectorRAG:
    """Orchestrates query pipeline."""

    def __init__(self, embedder, vector_store):
        self.embedder = embedder
        self.vector_store = vector_store

    def query(self, query: str, top_k: int = 5):
        """Query the RAG system."""
        # 1. Embed query
        embedding_result = self.embedder.encode_one(query)
        query_embedding = embedding_result.ok()

        # 2. Search vector store
        search_results = self.vector_store.search(query_embedding, top_k)

        # 3. Return retrieval results
        return [
            RetrievalResult(chunk=chunk, score=score)
            for chunk, score in search_results
        ]
```

## Advanced RAG Features

### 1. Configurable RAG Parameters
Workspace-specific RAG configuration through the UI:

```python
# packages/shared/python/src/shared/models/workspace.py
@dataclass
class RagConfig:
    workspace_id: int
    embedding_model: str = "nomic-embed-text"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 8
    retriever_type: str = "vector"  # 'vector' or 'graph'
    # Future: rerank_enabled, rerank_model, etc.
```

### 2. Auto-retry for No Context
When RAG finds no relevant context, the system stores queries for auto-retry:

```python
# packages/server/src/domains/workspaces/chat/service.py
def _store_pending_rag_query(self, workspace_id, session_id, user_id, query, request_id):
    """Store query for potential auto-retry after document upload."""
    # Implementation stores in instance cache for auto-retry

def retry_pending_rag_queries(self, workspace_id, user_id, llm_provider):
    """Retry stored queries with newly available context."""
    # Automatically re-runs queries when documents are processed
```

### 3. Multi-format Document Support
Factory pattern for different document parsers:

```python
# packages/shared/python/src/shared/documents/parsing/
def create_document_parser(format: str):
    """Create appropriate parser based on file format."""
    parsers = {
        "pdf": PdfDocumentParser(),
        "docx": DocxDocumentParser(),
        "txt": TextDocumentParser(),
        "html": HtmlDocumentParser(),
    }
    return parsers.get(format, TextDocumentParser())
```

## Performance Optimization

### Batch Processing
Embeddings are generated in batches for efficiency:

```python
# packages/shared/python/src/shared/documents/embedding/
class OllamaVectorEmbeddingEncoder:
    def encode(self, texts: list[str]) -> Result[list[list[float]]]:
        """Batch encode multiple texts efficiently."""
        # Implementation uses batch processing to optimize API calls
        batch_size = 32
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            # Process batch and collect embeddings
            batch_embeddings = self._encode_batch(batch)
            all_embeddings.extend(batch_embeddings)

        return Ok(all_embeddings)
```

### Workspace Isolation
Each workspace has its own Qdrant collection for data isolation:

```python
# Collections are named by workspace: f"workspace_{workspace_id}"
# This allows parallel processing and data isolation
collection_name = f"workspace_{workspace_id}"
vector_store = qdrant_client.create_store(collection_name, dimension=768)
```

## Evaluation Metrics

### Retrieval Quality
- **Precision@K**: Fraction of retrieved documents that are relevant
- **Recall@K**: Fraction of relevant documents that are retrieved
- **Mean Reciprocal Rank (MRR)**: Average of reciprocal ranks
- **Normalized Discounted Cumulative Gain (NDCG)**: Ranking quality metric

### Generation Quality
- **Faithfulness**: Does the answer contradict the context?
- **Relevance**: Does the answer address the question?
- **Completeness**: Does the answer fully address the question?
- **Groundedness**: Is the answer supported by the context?

## Production Considerations

### Scalability
- **Qdrant**: Chosen for high-performance vector search with horizontal scaling
- **Worker Pool**: Configurable concurrency for document processing workers
- **Workspace Isolation**: Separate vector collections prevent cross-contamination
- **Async Processing**: RabbitMQ enables decoupling of request/response flow

### Monitoring
Health checks and structured logging are implemented:

```python
# packages/server/src/domains/health/routes.py
@app.route('/health')
def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.route('/health/rag')
def rag_health_check():
    """Check RAG system components."""
    # Verify Qdrant, Ollama, and worker connectivity
    return check_rag_system_health()
```

### Security
- **JWT Authentication**: Secure API access with token-based auth
- **Workspace Scoping**: Users can only access their own workspaces/documents
- **Input Validation**: Comprehensive validation using domain services
- **Rate Limiting**: Configurable per-endpoint rate limits

## Common Pitfalls

### 1. Chunk Size Issues
- **Too small**: Loss of context and meaning
- **Too large**: Exceeds LLM context window
- **Solution**: Experiment with different sizes (500-2000 tokens)

### 2. Embedding Model Mismatch
- **Problem**: Using different models for indexing vs. querying
- **Solution**: Always use the same embedding model

### 3. Poor Retrieval Quality
- **Problem**: Irrelevant chunks retrieved
- **Solutions**:
  - Improve chunking strategy
  - Use re-ranking
  - Implement query expansion
  - Fine-tune embedding model

### 4. Hallucinations
- **Problem**: LLM generates incorrect information despite context
- **Solutions**:
  - Improve prompt engineering
  - Add confidence scoring
  - Implement fact-checking mechanisms

## Future Directions

### Advanced RAG Techniques
- **Graph-based Retrieval**: Use knowledge graphs for complex relationships
- **Multi-modal RAG**: Handle images, audio, and video content
- **Conversational RAG**: Maintain context across multiple interactions
- **Self-improving RAG**: Learn from user feedback to improve retrieval

### Integration Patterns
- **API-first Design**: Expose RAG as microservice
- **Streaming Responses**: Real-time generation for better UX
- **Hybrid Approaches**: Combine RAG with fine-tuned models
- **Federated RAG**: Query across multiple knowledge bases

## Implementation Status

### Currently Implemented
- **Vector RAG Pipeline**: Complete document processing and querying
- **Multi-format Support**: PDF, DOCX, text, HTML document parsing
- **Configurable Chunking**: Sentence-based chunking with overlap
- **Embedding Models**: Ollama (local), OpenAI, Sentence Transformers
- **Vector Storage**: Qdrant with workspace isolation
- **Real-time Processing**: Async workers with WebSocket status updates
- **Auto-retry Logic**: Queries without context are retried when documents are added

### Planned Enhancements
- **Graph RAG**: Neo4j-based entity relationship analysis
- **Re-ranking**: Cross-encoder models for improved retrieval quality
- **Query Expansion**: Multiple query variations for better results
- **Hybrid Retrieval**: Combine vector and graph-based approaches
- **Advanced Chunking**: Semantic chunking and hierarchical strategies

## Conclusion

InsightHub's RAG implementation demonstrates a production-ready approach to document analysis with LLMs. The modular architecture using factory patterns allows for easy extension and customization. Key success factors include:

1. **Clean Architecture**: Separation of concerns with domain-driven design
2. **Async Processing**: Worker-based pipeline prevents blocking operations
3. **Real-time Feedback**: WebSocket updates keep users informed of progress
4. **Workspace Isolation**: Multi-tenant architecture with data separation
5. **Extensible Design**: Factory patterns enable easy addition of new components

The system successfully combines LLM reasoning with efficient document retrieval, providing contextually relevant responses for academic research and document analysis tasks.