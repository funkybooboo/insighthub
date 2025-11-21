# Project 2 Proposal

- CS6600 Fall 2025
- Nate Stott (A02386053)
- 11/02/2025

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
- Pinecone
- Beeai-framework
- MCP
- Leiden Algorithm
- LangChain
- Mem0
- RAG
- Docker
- Wikipedia

## 3. Deliverables: 

A software system where you can ask questions to a chatbot and get up reliant information from provided papers and wikipedia with citations. The chatbot will remember past conversations so you can pick up from where you left off!

To run it will be a simple `docker compose up` so the only dependency you need to worry about is docker and an internet connection.

## 4. Schedule: 

I used chatgpt to generate the following schedule, I read through it, made my edits and it seems reasonable.

### Week 1 (Nov 8-14): Infrastructure & VectorRAG ✅ COMPLETED
- **Nov 8-9**: Set up development environment
  - Docker containers for Qdrant, Ollama, PostgreSQL
  - Configure Python environment with Poetry
  - Set up modular RAG architecture with dependency injection

- **Nov 10-12**: Build VectorRAG pipeline
  - Implement document ingestion and chunking strategies
  - Create embedding pipeline with Ollama (nomic-embed-text)
  - Set up Qdrant vector database integration
  - Implement retrieval and generation with multiple LLM providers

- **Nov 13-14**: Test VectorRAG
  - Load test documents into system
  - Verify embeddings and retrieval quality
  - Debug and optimize performance

**Deliverable**: Complete VectorRAG system with CLI, API, and streaming chat

### Week 2 (Nov 15-21): GraphRAG & Wikipedia Integration 🚧 IN PROGRESS
- **Nov 15-17**: Build GraphRAG pipeline
  - Implement LLM-based entity extraction
  - Set up Neo4j graph database
  - Create graph construction from extracted entities
  - Apply Leiden clustering algorithm

- **Nov 18-19**: Wikipedia MCP integration
  - Connect Wikipedia MCP server
  - Implement dynamic knowledge retrieval
  - Add fetched content to both databases

- **Nov 20-21**: Test GraphRAG
  - Compare retrieval quality with VectorRAG
  - Verify graph structure and clustering
  - Debug and optimize

**Deliverable**: Working GraphRAG system with Wikipedia integration

### Week 3 (Nov 22-28): Chatbot Interface & Comparison
- **Nov 22-24**: Build chatbot interface
  - Implement conversation history with Mem0
  - Create dual-mode chatbot (Vector vs Graph)
  - Add citation tracking and display
  
- **Nov 25-26**: Testing and comparison
  - Run identical queries on both systems
  - Document performance differences
  - Create comparison report with examples
  
- **Nov 27-28**: Documentation and wrap-up
  - Write README with setup instructions
  - Document architecture and design decisions
  - Prepare final deliverables and demo

**Deliverable**: Complete system with both RAG approaches, chatbot interface, and comparative analysis

## 5. Risks & Challenges

**Technical Challenges**:
- Graph RAG implementation complexity (entity extraction, graph construction)
- Neo4j integration and Cypher query optimization
- MCP server setup and Wikipedia API integration
- Performance comparison between Vector vs Graph approaches

**Timeline Risks**:
- Learning curve for graph databases and clustering algorithms
- Integration complexity with multiple new components
- Potential scope creep with advanced features

**Mitigation**:
- Modular architecture allows incremental development
- Existing Vector RAG provides working baseline
- Docker simplifies dependency management
- Comprehensive testing ensures stability
