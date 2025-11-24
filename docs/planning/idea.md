# Project Proposal and Status

- CS6600 Fall 2025
- Nate Stott (A02386053)
- 11/02/2025 (Updated: 11/24/2025)

## 1. Purpose: 

The thesis work I will be doing for my masters concerns Retrieval Augmented Generation (RAG). I have not started the coding work yet and am in the review papers phase. I would like to play around with RAG for this project so I can be more comfortable, confident, and familiar with RAG. Then when I do start my coding for the thesis I will have a base of knowledge! Now there are two distinct types of RAG, VectorRAG and GraphRAG. VectorRAG being the older of the two is also known as traditional RAG, it uses a Vector Database. VectorRAG has known issues of generalizing groups of the dataset and extracting useful information out. It also has a hard time finding and defining verifying levels of groupings. GraphRAG is the new kid on the block and solves all the issues that VectorRAG has purely from utilizing a Graph Database. There are varies Graph Clustering Algorithms that you can employ on a Graph Database which is why it works so well. Graph Databases are not new, in fact they are quite old, but historically they have found few use cases because they are such a pain to create. With the rise of Graph Database systems such as Neo4j, Cypher, LLMs and MCP have made it possible to create Graph Databases at scale, quickly, and cheaply. This as opened the door for Graphs to take over the RAG business. 

A disclaimer, I will be doing my thesis work with Domo, a software company headquartered in American Fork Utah. What is interesting about Domo is they deal with massive at scale datasets of any type from anywhere on the internet. They want me to use GraphRAG to bring memory to their LLMs which currently do not have a memory. They also want me to implement a decaying memory system on top of the GraphRAG. The project is interesting because of the vastness of the problem and the practical application of it. There are plenty of papers about GraphRAG but they are always about one dataset, to work in Domo, I will need to create a system that can create a GraphRAG from any dataset, no many how large, and no matter what type of data. However, what I have in mind for this project is much more primitive and will not require any help or data from Domo.

I want to build two systems, GraphRAG and VectorRAG for comparison and learning. General flow, and idea:

```txt
Phase 1

Paper + Wikipedia -> API -> MCP -> Embedding Model -> Vector Database

Paper + Wikipedia -> API -> MCP -> LLM -> Graph Database -> Leiden Algorithm

Phase 2

Chatbot -> LLM -> RAG on Vector Database

Chatbot -> LLM -> RAG on Graph Database
```

More of an explanation:

I want to build a system where you can input a paper, article, or whatnot, the system will process that paper, article, etc. build either a graph or vector database from the data, do any post processing steps that need to happen, and provide a api for asking questions about the paper, article, etc. via a LLM infused with RAG, when needed pull reliant information from wikipedia and put it into the database so users can explained their questions past the paper, article, etc. Example "I see the paper talks about x but how does that relate to y" the system will work even if y is not in the Database.

This project uses multiple AI techniques, namely neural networks for encoding, knowledge representation for storage, and search/reasoning for retrieval. This demonstrates how modern AI systems combine approaches we've studied throughout the course.

Further Reading

- https://en.wikipedia.org/wiki/Retrieval-augmented_generation
- https://github.com/microsoft/generative-ai-for-beginners/blob/main/15-rag-and-vector-databases/README.md
- https://cookbook.openai.com/examples/rag_with_graph_db
- https://en.wikipedia.org/wiki/Vector_database
- https://en.wikipedia.org/wiki/Nearest_neighbor_search
- https://en.wikipedia.org/wiki/Graph_database
- https://en.wikipedia.org/wiki/Leiden_algorithm
- https://en.wikipedia.org/wiki/Neo4j
- https://neo4j.com/docs/cypher-manual/current/introduction/cypher-overview/
- https://en.wikipedia.org/wiki/Model_Context_Protocol
- https://github.com/Rudra-ravi/wikipedia-mcp
- https://en.wikipedia.org/wiki/LangChain
- https://github.com/mem0ai/mem0
- https://en.wikipedia.org/wiki/Docker_(software)
- https://github.com/i-am-bee/beeai-framework
- https://github.com/pinecone-io/pinecone-python-client

## 2. Resources: 

- Neo4j
- Qdrant (changed from Pinecone)
- Flask (changed from Beeai-framework)
- MCP
- Leiden Algorithm
- React 19 (changed from LangChain)
- Mem0
- RAG
- Docker
- Wikipedia
- PostgreSQL
- Redis
- RabbitMQ

## 3. Deliverables: 

A software system where you can ask questions to a chatbot and get reliant information from provided papers and wikipedia with citations. The chatbot will remember past conversations so you can pick up from where you left off!

To run it will be a simple `docker compose up` so the only dependency you need to worry about is docker and an internet connection.

## 4. Schedule: 

### Week 1 (Nov 8-14): Infrastructure & VectorRAG [x] COMPLETED
- **Nov 8-9**: Set up development environment
  - [x] Docker containers for Qdrant, Ollama, PostgreSQL
  - [x] Configure Python environment with Poetry
  - [x] Set up modular RAG architecture with dependency injection

- **Nov 10-12**: Build VectorRAG pipeline
  - [x] Implement document ingestion and chunking strategies
  - [x] Create embedding pipeline with Ollama (nomic-embed-text)
  - [x] Set up Qdrant vector database integration
  - [x] Implement retrieval and generation with multiple LLM providers

- **Nov 13-14**: Test VectorRAG
  - [x] Load test documents into system
  - [x] Verify embeddings and retrieval quality
  - [x] Debug and optimize performance

**Deliverable**: [x] Complete VectorRAG system with CLI, API, and streaming chat

### Week 2 (Nov 15-21): GraphRAG & Wikipedia Integration [WIP] IN PROGRESS
- **Nov 15-17**: Build GraphRAG pipeline
  - [x] Set up Neo4j graph database
  - [WIP] Implement LLM-based entity extraction
  - [WIP] Create graph construction from extracted entities
  - [WIP] Apply Leiden clustering algorithm

- **Nov 18-19**: Wikipedia MCP integration
  - [WIP] Connect Wikipedia MCP server
  - [WIP] Implement dynamic knowledge retrieval
  - [WIP] Add fetched content to both databases

- **Nov 20-21**: Test GraphRAG
  - [WIP] Compare retrieval quality with VectorRAG
  - [WIP] Verify graph structure and clustering
  - [WIP] Debug and optimize

**Deliverable**: [WIP] Working GraphRAG system with Wikipedia integration

### Week 3 (Nov 22-28): Chatbot Interface & Comparison
- **Nov 22-24**: Build chatbot interface
  - [x] Implement conversation history with PostgreSQL
  - [x] Create dual-mode chatbot (Vector vs Graph)
  - [x] Add citation tracking and display
  - [x] Real-time streaming via Socket.IO
  
- **Nov 25-26**: Testing and comparison
  - [WIP] Run identical queries on both systems
  - [WIP] Document performance differences
  - [WIP] Create comparison report with examples
  
- **Nov 27-28**: Documentation and wrap-up
  - [x] Write README with setup instructions
  - [x] Document architecture and design decisions
  - [WIP] Prepare final deliverables and demo

**Deliverable**: [WIP] Complete system with both RAG approaches, chatbot interface, and comparative analysis

## 5. Current Implementation Status

### [x] Completed Features

**Core Infrastructure:**
- Flask 3.0+ backend with clean architecture
- React 19 frontend with TypeScript and Redux
- PostgreSQL for application data
- Qdrant vector database for VectorRAG
- Neo4j graph database for GraphRAG
- Redis for caching and session management
- RabbitMQ for background job processing
- Docker Compose orchestration

**VectorRAG Implementation:**
- Document upload and parsing (PDF, DOCX, HTML, TXT)
- Multiple chunking strategies (character, sentence, word)
- Ollama integration for embeddings (nomic-embed-text)
- Vector similarity search with configurable top-k
- Real-time chat with streaming responses
- Source citation and metadata tracking

**Chat System:**
- WebSocket-based real-time communication
- Conversation history persistence
- User authentication with JWT
- Workspace-based organization
- Multi-session support

**Development Tools:**
- Comprehensive testing setup (Pytest, Vitest, Playwright)
- CI/CD with GitHub Actions
- ELK stack for monitoring
- Task-based build system
- Bruno for API testing

### [WIP] In Progress

**GraphRAG Implementation:**
- Entity extraction using LLMs
- Relationship extraction and graph construction
- Leiden clustering algorithm implementation
- Graph-based retrieval strategies

**External Knowledge:**
- Wikipedia MCP integration
- Dynamic content fetching
- Knowledge graph enrichment

### [TODO] Planned Features

**Advanced RAG:**
- Hybrid Vector + Graph retrieval
- Context-aware chunking
- Query expansion and reformulation
- Multi-modal document support

**User Experience:**
- Advanced search and filtering
- Document visualization
- Analytics and usage metrics
- Mobile-responsive design

## 6. Architecture Decisions Made

### Technology Stack Changes

| Original | Current | Reason |
|----------|---------|--------|
| FastAPI | Flask | Better Socket.IO integration, simpler for this use case |
| Pinecone | Qdrant | Open-source, Docker-friendly, better control |
| LangChain | Custom implementation | More control over RAG pipeline, educational value |
| BeeAI | Flask + custom services | Better ecosystem support, more flexible |

### Key Architectural Patterns

- **Clean Architecture**: Clear separation between domain, infrastructure, and presentation
- **Event-Driven**: RabbitMQ for asynchronous document processing
- **Microservices**: Workers scale independently based on queue depth
- **CQRS**: Separate read/write models for chat and document processing
- **Repository Pattern**: Data access abstraction for testability

## 7. Risks & Challenges

### Technical Challenges - Status

**Completed:**
- [x] Vector RAG implementation complexity
- [x] Real-time streaming architecture
- [x] Multi-document processing pipeline
- [x] Authentication and authorization

**In Progress:**
- [WIP] Graph RAG implementation (entity extraction, graph construction)
- [WIP] Neo4j integration and Cypher query optimization
- [WIP] MCP server setup and Wikipedia API integration

**Remaining:**
- [TODO] Performance comparison between Vector vs Graph approaches
- [TODO] Memory management for large document sets
- [TODO] Scalability testing and optimization

### Timeline Risks - Mitigation

**Mitigated:**
- [x] Learning curve for Flask and React - resolved through incremental development
- [x] Docker complexity - resolved with comprehensive compose files
- [x] Testing strategy - resolved with multiple testing frameworks

**Monitoring:**
- [WIP] Graph database implementation complexity
- [WIP] Integration testing with external services
- [TODO] Performance optimization for large datasets

## 8. Success Metrics

### Technical Metrics
- **VectorRAG Performance**: < 100ms retrieval time for top-10 results
- **Chat Latency**: < 2 seconds for first token
- **Document Processing**: < 30 seconds for 10MB files
- **System Uptime**: > 99.5% availability

### Educational Metrics
- **RAG Comparison**: Clear performance and quality differences between Vector and Graph approaches
- **Architecture Learning**: Understanding of clean architecture and microservices
- **Technology Integration**: Successful integration of multiple AI/ML technologies

### Project Completion
- **MVP**: [x] Fully functional VectorRAG system with chat interface
- **Full System**: [WIP] Dual RAG system with Wikipedia integration
- **Documentation**: [x] Comprehensive setup and architecture guides

## 9. Next Steps

### Immediate (This Week)
1. Complete GraphRAG entity extraction implementation
2. Integrate Wikipedia MCP for external knowledge
3. Implement Leiden clustering for graph communities
4. Test and compare RAG approaches

### Final Week
1. Performance optimization and load testing
2. Final documentation and demo preparation
3. Code review and cleanup
4. Project presentation preparation

This project serves as both a learning platform for RAG technologies and a foundation for my master's thesis work on GraphRAG systems at scale.