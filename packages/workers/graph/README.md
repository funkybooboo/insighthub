# Graph Workers

Knowledge graph-based RAG pipeline workers for structured reasoning and relationship-aware retrieval.

## Overview

Graph workers implement advanced RAG using knowledge graphs and graph algorithms. This approach excels at understanding relationships, performing multi-hop reasoning, and providing structured knowledge retrieval.

## Pipeline Flow

```
+------------------+     +---------+     +-----------------+     +-----------------+
|  Document Flow  | --> | Chunker | --> |  Preprocessor   | --> |  Construction   |
|                 |     |         |     |                 |     |                 |
| Router Output   |     +---------+     | * Entity Ext.   |     | * Graph Build   |
|                 |                    | * Relationship  |     | * Neo4j Store   |
|                 |                    | * Community Det.|     | * Schema Mgmt   |
+------------------+                    +-----------------+     +-----------------+
                                                                |
                                                                v
+------------------+     +-----------------+     +-----------------+
| Graph Traversal | --> |   Query Worker  | --> |   Chat Response |
|                 |     |                 |     |                 |
| * Path Finding  |     | * Search        |     | * Structured    |
| * Relationship  |     | * Retrieval     |     | * Knowledge     |
| * Context       |     | * Ranking       |     | * Response      |
+------------------+     +-----------------+     +-----------------+
```
Document Upload --> Parser --> Chunker --> Entity Extraction --> Relationship Extraction --> Community Detection --> Construction --> [Query Time]
                                                                                                                    |
                                                                                                      Graph Traversal --> Structured Retrieval
```

## Workers

### Entity Extraction (`entity-extraction/`)
**Purpose**: Extract named entities from document chunks
- **Input**: `document.chunked` events with chunk data
- **Output**: `document.entities_extracted` events with entity data
- **Integration**: Uses NER models to identify people, organizations, locations, etc.

### Relationship Extraction (`relationship-extraction/`)
**Purpose**: Identify relationships between extracted entities
- **Input**: `document.entities_extracted` events with entity data
- **Output**: `document.relationships_extracted` events with relationship data
- **Integration**: Applies NLP to find connections like "works for", "located in", etc.

### Community Detection (`community-detection/`)
**Purpose**: Apply clustering algorithms to group related entities
- **Input**: `document.relationships_extracted` events with relationship data
- **Output**: `document.communities_detected` events with community data
- **Integration**: Uses graph algorithms (Leiden, Louvain) to find entity clusters

### Construction (`construction/`)
**Purpose**: Build Neo4j knowledge graphs from extracted data
- **Input**: `document.communities_detected` events with community data
- **Output**: `document.graph_constructed` events with graph statistics
- **Integration**: Creates nodes, relationships, and graph structure in Neo4j

### Query (`query/`)
**Purpose**: Handle graph-based retrieval queries
- **Input**: `chat.graph_query` events with query data
- **Output**: `chat.graph_query_completed` or `chat.graph_query_failed` events
- **Integration**: Performs graph traversal and structured knowledge retrieval

### Connector (`connector/`)
**Purpose**: Graph connectivity utilities and maintenance
- **Input**: Various graph-related events
- **Output**: Graph status and maintenance events
- **Integration**: Provides graph connectivity and utility functions

## Integration with Server & Client

### Server Integration
```
+------------+     +------------+     +-----------------+
|   Server   | --> |   Router   | --> | Graph Workers   |
|            |     |            |     |                 |
| * API Calls|     | * Routing  |     | * Preprocessor  |
| * Config   |     | * Decisions|     | * Construction  |
| * Monitoring|    | * Load Bal.|     | * Query         |
+------------+     +------------+     +-----------------+
```

### Client Integration
```
+------------+     +------------+     +-----------------+
|   Client   | <-> |   Server   | <-> | Graph Workers   |
|            |     |            |     |                 |
| * Upload UI|     | * Progress |     | * Processing    |
| * Chat UI  |     | * Responses|     | * Search        |
| * Graph Viz|     | * Routing  |     | * Knowledge     |
+------------+     +------------+     +-----------------+
```

## Configuration

Graph workers use specialized configuration:

```bash
# Graph Database
NEO4J_URL=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Entity Extraction
NER_MODEL=en_core_web_sm
NER_CONFIDENCE_THRESHOLD=0.7

# Community Detection
COMMUNITY_ALGORITHM=leiden
MIN_COMMUNITY_SIZE=3

# Graph Construction
GRAPH_SCHEMA_VALIDATION=true
RELATIONSHIP_WEIGHTING=confidence
```

## Performance Characteristics

- **Strengths**:
  - Excellent for relationship understanding
  - Multi-hop reasoning capabilities
  - Structured knowledge representation
  - Explainable retrieval paths

- **Limitations**:
  - Higher computational complexity
  - Requires quality entity/relationship extraction
  - May be slower for simple queries
  - Needs sufficient relationship data

## Development

### Running Workers

```bash
# Run all graph workers
docker compose --profile graph-workers up

# Run individual worker
cd packages/workers/graph/construction
docker build -t insighthub-construction .
docker run insighthub-construction
```

### Testing

```bash
# Run worker tests
cd packages/workers/graph/entity-extraction
poetry run pytest tests/

# Graph-specific testing
docker compose --profile graph-testing up
```

## Monitoring & Observability

Graph workers provide:
- **Graph Metrics**: Node/relationship counts, community sizes
- **Query Performance**: Traversal times, path lengths
- **Extraction Quality**: Entity/relationship confidence scores
- **Graph Health**: Connectivity, schema validation

## Scaling Considerations

- **Graph Partitioning**: Handle large graphs through partitioning
- **Query Optimization**: Use graph-specific query optimization
- **Caching**: Cache frequent graph traversals
- **Distributed Processing**: Scale graph algorithms across multiple workers

## Comparison with Vector RAG

```
+-------------+---------------------+---------------------+
|   Aspect    |    Vector RAG       |     Graph RAG       |
+-------------+---------------------+---------------------+
| Query Type  | Similarity search   | Relationship        |
|             |                     | traversal           |
| Reasoning   | Single-hop          | Multi-hop           |
| Structure   | Flat embeddings     | Connected entities  |
| Use Case    | General QA          | Complex             |
|             |                     | relationships       |
| Performance | Fast                | More complex        |
| Accuracy    | Good semantic       | Better relationship |
|             | matching            | understanding       |
+-------------+---------------------+---------------------+
```

## Extending Graph RAG

To add new graph-based capabilities:

1. **New Extraction Workers**: Add specialized entity/relationship extractors
2. **Graph Algorithms**: Implement new community detection or traversal algorithms
3. **Query Types**: Add new graph query patterns and traversal strategies
4. **Visualization**: Enhance client-side graph visualization capabilities