# Graph RAG Architecture

## Overview

Graph RAG uses knowledge graphs and community detection to retrieve structured, relationship-aware context for LLM generation.

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    INGESTION PIPELINE                        │
└─────────────────────────────────────────────────────────────┘

Raw Documents
         │
         ▼
   DocumentParser ──────> Documents
         │
         ▼
      Chunker ──────────> Chunks
         │
         ▼
  EntityExtractor ──────> Named entities (NER/LLM)
         │
         ▼
  RelationExtractor ────> Entity relationships
         │
         ▼
   GraphBuilder ─────────> Knowledge graph
         │
         ▼
  Clustering (Leiden) ──> Communities detected
         │
         ▼
    GraphStore ──────────> Neo4j/PostgreSQL storage


┌─────────────────────────────────────────────────────────────┐
│                     QUERY PIPELINE                           │
└─────────────────────────────────────────────────────────────┘

User Query
         │
         ▼
  GraphRetriever ───────> Relevant nodes/communities
         │
         ▼
  Subgraph Extraction ──> Connected subgraph
         │
         ▼
  ContextBuilder ───────> LLM prompt with graph context
         │
         ▼
       LLM ─────────────> Generated answer
         │
         ▼
  OutputFormatter ──────> Answer + graph provenance
```

## Components

### Ingestion Components

1. **EntityExtractor**
   - Extracts named entities from text
   - Methods: spaCy NER, LLM-based extraction
   - Entity types: Person, Organization, Concept, etc.

2. **RelationExtractor**
   - Identifies relationships between entities
   - Methods: dependency parsing, LLM prompting
   - Relation types: "works_at", "published", "cites"

3. **GraphBuilder**
   - Constructs knowledge graph from entities/relations
   - Merges duplicate entities
   - Applies Leiden clustering for community detection

4. **GraphStore**
   - Stores nodes and edges
   - Databases: Neo4j, ArangoDB, PostgreSQL (with graph extensions)
   - Graph traversal and querying

### Query Components

1. **GraphRetriever**
   - Finds relevant entities/communities
   - Expands to neighboring nodes
   - Returns subgraphs with context

2. **ContextBuilder**
   - Linearizes graph structure for LLM
   - Includes entity descriptions and relationships
   - Formats as natural language or structured data

3. **LLM & OutputFormatter**
   - Same as Vector RAG
   - Adds graph-specific provenance

## Implementation

### Orchestrator: GraphRAGIndexer

```python
from shared.orchestrators import GraphRAGIndexer
from shared.interfaces.graph import *

indexer = GraphRAGIndexer(
    parser=PDFParser(),
    chunker=SentenceChunker(chunk_size=500),
    entity_extractor=LLMEntityExtractor(llm),
    relation_extractor=LLMRelationExtractor(llm),
    graph_builder=LeidenGraphBuilder(),
    graph_store=Neo4jGraphStore(uri="bolt://localhost:7687"),
)

# Ingest documents
stats = indexer.ingest([
    (pdf_bytes, {"title": "Paper 1"}),
])
# stats: {node_count, edge_count, community_count}
```

### Orchestrator: GraphRAG

```python
from shared.orchestrators import GraphRAG

rag = GraphRAG(
    graph_retriever=CommunityGraphRetriever(store),
    context_builder=GraphContextBuilder(),
    llm=OllamaLLM(model="llama3.2:1b"),
    formatter=GraphCitationFormatter(),
)

# Query
result = rag.query("How are RAG and LLMs related?", k=3)
print(result["answer"])
print(result["graph_context"])
```

## Leiden Clustering Algorithm

The Leiden algorithm detects communities in the knowledge graph:

1. **Initial partition**: Each node starts in its own community
2. **Local moves**: Nodes move to neighboring communities if it improves modularity
3. **Refinement**: Communities are refined iteratively
4. **Aggregation**: Graph is coarsened by merging communities

Benefits:
- Identifies thematic clusters in knowledge
- Enables community-level retrieval
- Improves answer quality for complex queries

## Advantages

- **Relationship-aware**: Captures entity connections
- **Structured reasoning**: Understands graph topology
- **Community detection**: Finds thematic clusters
- **Better for complex queries**: "How are X and Y related?"

## Limitations

- **Complex**: Harder to implement and debug
- **Slower**: Entity extraction is expensive (LLM calls)
- **Requires quality NER**: Poor entity extraction degrades results
- **Graph database needed**: Additional infrastructure

## Use Cases

- Multi-hop reasoning
- Relationship queries ("Who works at X?")
- Citation networks
- Knowledge graph exploration

## Comparison to Vector RAG

| Aspect | Vector RAG | Graph RAG |
|--------|-----------|-----------|
| Retrieval | Similarity search | Graph traversal |
| Context | Individual chunks | Entity relationships |
| Complexity | Simple | Complex |
| Speed | Fast | Slower |
| Use case | Factual Q&A | Reasoning, relationships |

## See Also

- [Vector RAG Architecture](./vector-rag-architecture.md)
- [RAG Comparison](./comparison.md)
- Implementation: `packages/shared/python/src/shared/orchestrators/graph_rag.py`
