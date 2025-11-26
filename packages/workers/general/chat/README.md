# Chat Worker

Chat orchestrator worker that coordinates RAG queries and LLM generation for chat messages.

## Architecture

The chat worker implements proper separation of concerns by delegating RAG retrieval to specialized query workers:

1. **Receives** `chat.message_received` events
2. **Determines** RAG type from chat session (`vector`, `graph`, or `none`)
3. **Delegates** to appropriate query worker:
   - Vector RAG → `chat.vector_query` → Vector Query Worker
   - Graph RAG → `chat.graph_query` → Graph Query Worker
4. **Waits** for query completion events
5. **Generates** LLM response with retrieved context

## Environment Variables

- `RABBITMQ_URL`: RabbitMQ connection URL
- `RABBITMQ_EXCHANGE`: RabbitMQ exchange name
- `DATABASE_URL`: PostgreSQL connection URL
- `OLLAMA_BASE_URL`: Ollama API base URL
- `OLLAMA_LLM_MODEL`: LLM model name for chat
- `WORKER_CONCURRENCY`: Number of concurrent workers

## Events

### Consumes
- `chat.message_received`: Triggers chat processing
- `chat.vector_query_completed`: Vector query results
- `chat.graph_query_completed`: Graph query results
- `chat.vector_query_failed`: Vector query errors
- `chat.graph_query_failed`: Graph query errors

### Produces
- `chat.vector_query`: Requests vector-based retrieval
- `chat.graph_query`: Requests graph-based retrieval
- `chat.response_chunk`: Streaming response chunks
- `chat.response_complete`: Complete response
- `chat.no_context_found`: When no RAG context available
- `chat.error`: Processing errors