# Chat Worker

Chat orchestrator worker that processes chat messages with RAG and LLM.

## Environment Variables

- `RABBITMQ_URL`: RabbitMQ connection URL
- `RABBITMQ_EXCHANGE`: RabbitMQ exchange name
- `DATABASE_URL`: PostgreSQL connection URL
- `OLLAMA_BASE_URL`: Ollama API base URL
- `OLLAMA_LLM_MODEL`: LLM model name for chat
- `OLLAMA_EMBEDDING_MODEL`: Embedding model name
- `QDRANT_URL`: Qdrant vector database URL
- `QDRANT_COLLECTION`: Qdrant collection name
- `WORKER_CONCURRENCY`: Number of concurrent workers

## Events

### Consumes
- `chat.message_received`: Triggers chat processing

### Produces
- `chat.response_chunk`: Streaming response chunks
- `chat.response_complete`: Complete response
- `chat.no_context_found`: When no RAG context available
- `chat.error`: Processing errors