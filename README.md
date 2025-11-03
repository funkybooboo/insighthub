# RAG System - Built from First Principles

A fully local Retrieval-Augmented Generation (RAG) system built from scratch with minimal dependencies. Everything runs in Docker - no external APIs or cloud services required!

## Features

- **Fully Local**: Runs entirely on your machine using Docker
- **No External APIs**: Uses Ollama for LLMs and embeddings (free!)
- **Local Vector Database**: Qdrant for fast similarity search
- **Built from First Principles**: Minimal abstraction, educational implementation
- **Multiple Chunking Strategies**: Character, sentence, and word-based chunking
- **Modular Design**: Easy to swap components (embeddings, LLMs, vector stores)

## Architecture

```
Query
  |
  v
Ollama Embeddings (nomic-embed-text)
  |
  v
Qdrant Vector Store (Local similarity search)
  |
  v (Retrieve top-k)
Retrieved Context
  |
  v
Ollama LLM (llama3.2)
(Generate answer)
  |
  v
Final Answer
```

## Components

### Vector RAG (Current)
- **Vector Store**: Qdrant (local Docker container)
- **Embeddings**: Ollama with `nomic-embed-text`
- **LLM**: Ollama with `llama3.2`
- **Chunker**: Pluggable implementations (character, sentence, word-based)

### Graph RAG (Coming Soon)
- Knowledge graph-based retrieval
- Entity extraction and relationship mapping

## Quick Start

### Prerequisites

- Docker & Docker Compose
- ~4GB disk space for models
- ~8GB RAM recommended

### Running the RAG System

Simply run:
```bash
docker-compose up
```

This will:
1. Start Ollama and Qdrant services
2. Automatically pull required models (`nomic-embed-text` and `llama3.2`)
3. Run the demo application

The first run will take longer as it downloads the models (~2.5GB total).

### Development Options

**Option 1: Run the demo (easiest)**
```bash
docker-compose up
```

This runs `main.py` which demonstrates the full RAG pipeline.

**Option 2: Development shell**
```bash
docker-compose --profile dev up shell
```

Then inside the container:
```bash
python src/main.py
```

**Option 3: Jupyter notebook**
```bash
docker-compose --profile dev up jupyter
```

Access at http://localhost:8888

## Usage Examples

### Basic RAG Query

```python
from src.rag.vectorrag import (
    QdrantVectorStore,
    SentenceChunker,
    OllamaEmbeddings,
    RAGSystem,
    ollama_llm_generator
)

# Initialize components
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://ollama:11434"
)

vector_store = QdrantVectorStore(
    host="qdrant",
    port=6333,
    collection_name="my_docs",
    dimension=embeddings.get_dimension()
)

chunker = SentenceChunker(
    chunk_size=500,
    chunk_overlap=50
)

rag = RAGSystem(
    vector_store=vector_store,
    embedding_model=embeddings,
    chunker=chunker
)

# Add documents
documents = [
    {
        "text": "Your document text here...",
        "metadata": {"source": "doc1", "topic": "AI"}
    }
]

rag.add_documents(documents)

# Query
def generator(query, context):
    return ollama_llm_generator(query, context, model="llama3.2")

result = rag.query(
    query="What is RAG?",
    top_k=3,
    llm_generator=generator
)

print(result['answer'])
```

### Custom Chunking

```python
# Character-based chunking
from src.rag.vectorrag import CharacterChunker

chunker = CharacterChunker(
    chunk_size=1000,
    chunk_overlap=100
)

# Sentence-based chunking
from src.rag.vectorrag import SentenceChunker

chunker = SentenceChunker(
    chunk_size=500,
    chunk_overlap=50
)

# Word-based chunking
from src.rag.vectorrag import WordChunker

chunker = WordChunker(
    chunk_size=200,
    chunk_overlap=20
)
```

### Using Different Embedding Models

```python
# Ollama embeddings (local)
from src.rag.vectorrag import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Sentence Transformers (local)
from src.rag.vectorrag import SentenceTransformerEmbeddings

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# OpenAI embeddings (requires API key)
from src.rag.vectorrag import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(api_key="your-key", model="text-embedding-3-small")
```

## Development

### Project Structure

```
rag/
  src/
    rag/
      types.py              # Common type definitions
      rag.py                # Base RAG interface
      vectorrag/
        __init__.py
        vector_rag.py       # Main RAG orchestration
        chunkers/           # Document chunking implementations
          chunker.py        # Abstract base class
          character_chunker.py
          sentence_chunker.py
          word_chunker.py
        embeddings/         # Embedding model wrappers
          embedding.py
          ollama_embedding.py
          open_api_embedding.py
          sentence_transformer_embedding.py
        stores/             # Vector store implementations
          store.py
          qdrant_store.py
          pinecone_store.py
        example.py
      graphrag/             # Graph RAG (coming soon)
    main.py                 # Demo application
  docker-compose.yml        # Docker services
  Dockerfile                # Python app container
  requirements.txt          # Python dependencies
  pyproject.toml            # Code quality configuration
  README.md                 # This file
```

### Code Quality

This project uses modern Python tooling:

```bash
# Format code
make format

# Run linter
make lint

# Type check
make type-check

# Run all checks
make check
```

### Adding New Features

The modular design makes it easy to extend:

1. **Custom Chunking Strategy**: Extend `DocumentChunker` in `chunkers/chunker.py`
2. **New Embedding Model**: Implement `EmbeddingModel` interface in `embeddings/embedding.py`
3. **Different Vector Store**: Create a new store with the same interface as `QdrantVectorStore`
4. **Custom LLM Generator**: Write a function with signature `(query: str, context: str) -> str`

## Configuration

### Environment Variables

Configuration is managed via `.env` file. See `.env.example` for all available options:

```bash
# Ollama configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Qdrant configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=rag_collection

# Chunking configuration
CHUNK_SIZE=500
CHUNK_OVERLAP=50
CHUNK_STRATEGY=sentence

# RAG configuration
RAG_TOP_K=5

# Optional: Only if using OpenAI
# OPENAI_API_KEY=your-openai-key

# Optional: Only if using Pinecone instead of Qdrant
# PINECONE_API_KEY=your-pinecone-key
```

### Docker Services

- **Ollama**: http://localhost:11434
- **Qdrant**: http://localhost:6333 (UI: http://localhost:6334)
- **Jupyter**: http://localhost:8888 (dev profile)

## Performance

### Model Sizes
- `nomic-embed-text`: ~275MB
- `llama3.2`: ~2GB
- Total: ~2.5GB

### Speed (typical on M1 Mac)
- Embedding: ~50 docs/sec
- Retrieval: ~1ms for top-5
- Generation: ~20 tokens/sec

## Contributing

This is an educational project built from first principles. Contributions welcome!

Areas for improvement:
- [ ] Graph RAG implementation
- [ ] Advanced chunking strategies
- [ ] Hybrid search (vector + keyword)
- [ ] Query optimization
- [ ] Caching layer
- [ ] Evaluation metrics

## Learning Resources

This implementation is designed to be educational. Key concepts:

1. **Embeddings**: Converting text to numerical vectors
2. **Vector Databases**: Efficient similarity search
3. **Chunking**: Splitting documents for better retrieval
4. **RAG**: Combining retrieval with generation

## Troubleshooting

### "Ollama connection refused"
```bash
# Restart Ollama
docker-compose restart ollama
# Wait 10 seconds, then try again
```

### "Model not found"

The models should be pulled automatically on first run. If you encounter issues:

```bash
# Check if ollama-setup ran successfully
docker-compose logs ollama-setup

# Pull models manually if needed
docker exec ollama ollama pull nomic-embed-text
docker exec ollama ollama pull llama3.2
```

### "Out of memory"
```bash
# Use smaller models
docker exec ollama ollama pull phi3  # Smaller alternative to llama3.2
```

## License

MIT License - Feel free to use this for learning and projects!

## Acknowledgments

- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Qdrant](https://qdrant.tech/) - Vector database
- [Nomic AI](https://www.nomic.ai/) - Embedding models

---

Built for learning and experimentation!
