# Tutorial 2: Graph RAG

Learn graph-based knowledge retrieval using entity relationships.

**Time**: 20 minutes

## Setup

```bash
task health-check
```

## 1. Configure Graph RAG

View available options:

```bash
task cli -- rag-options list
```

Shows graph-specific options like entity extraction (`spacy`, `llm`), relationship extraction (`dependency-parsing`, `llm`), and clustering (`leiden`, `louvain`).

View current defaults:

```bash
task cli -- default-rag-config show
```

Set graph RAG defaults:

```bash
task cli -- default-rag-config create
```

Input:

```
RAG type [vector]: graph

Available entity extraction algorithms:
  - spacy: Fast and accurate named entity recognition using spaCy's transformer models.  Supports offline operation.
  - llm: Flexible entity extraction using large language models with structured JSON output. Requires LLM provider.

Available relationship extraction algorithms:
  - dependency-parsing: Extract relationships using spaCy's dependency parser to identify subject-verb-object triples. Fast and accurate for well-structured text.
  - llm: Flexible relationship extraction using large language models with structured JSON output. Better for complex relationships. Requires LLM provider.

Available clustering algorithms:
  - leiden: Advanced community detection using the Leiden algorithm. Improved quality over Louvain. Requires python-igraph and leidenalg.
  - louvain: Fast community detection using the Louvain algorithm. Good for large graphs. Requires networkx.

Entity extraction algorithm [spacy]: spacy
Relationship extraction algorithm [dependency-parsing]: dependency-parsing
Clustering algorithm [louvain]: louvain
```

Output:

```
Default RAG config saved
```

## 2. Create Workspace

```bash
task cli -- workspace create
```

Input:

```
Workspace name: Company Knowledge
Description (optional): Organization and team information
RAG type [vector]: graph
```

Output:

```
Created workspace [1] Company Knowledge
```

View configuration:

```bash
task cli -- workspace show 1
```

Output shows inherited graph config:

```
ID: 1
Name: Company Knowledge
RAG Type: graph
Status: active

Graph RAG Configuration:
  Entity Extraction: spacy
  Relationship Extraction: dependency-parsing
  Clustering Algorithm: louvain
```

Select workspace:

```bash
task cli -- workspace select 1
```

## 3. Upload Documents

Create `team-structure.txt`:

```
Alice is the Engineering Manager. She manages the Backend Team.
Bob is a Senior Engineer on the Backend Team. Bob reports to Alice.
Carol is the Product Manager for the Platform product.
Alice and Carol work together on the Platform product.
The Backend Team builds the Platform product.
```

Create `company-info.txt`:

```
The company headquarters is located in San Francisco.
Alice works in the San Francisco office.
Bob works remotely from Austin.
The Backend Team uses Python and Docker for development.
Carol coordinates with the Design Team for product features.
```

Upload:

```bash
task cli -- document add team-structure.txt
task cli -- document add company-info.txt
```

Output:

```
Uploading team-structure.txt...
Uploaded [1] team-structure.txt
```

Documents are processed to extract entities (Alice, Bob, Engineering Manager, Backend Team) and relationships (manages, reports to, works on).

List documents:

```bash
task cli -- document list
```

Output:

```
[1] team-structure.txt
[2] company-info.txt
```

## 4. Query Documents

Create session:

```bash
task cli -- chat create 1
```

Input:

```
Session title (optional): Team Questions
```

Output:

```
Created chat session [1] Team Questions
```

Select session:

```bash
task cli -- chat select 1
```

Output:

```
Selected [1] Team Questions
```

Send query:

```bash
task cli -- chat send "Who does Bob report to?"
```

Output:

```
You: Who does Bob report to?
Assistant: Bob reports to Alice. Bob is a Senior Engineer on the Backend Team,
and Alice is the Engineering Manager who manages the Backend Team.
```

The graph traversed relationships to find Bob -> reports_to -> Alice.

Ask another question:

```bash
task cli -- chat send "What does the Backend Team work on?"
```

Output:

```
You: What does the Backend Team work on?
Assistant: The Backend Team builds the Platform product. They use Python and
Docker for development.
```

The graph connected Backend Team -> builds -> Platform product.

## Commands Covered

- `rag-options list` - View all algorithms
- `default-rag-config show/create` - Configure graph RAG
- `workspace create/show/select` - Manage graph workspaces
- `document add/list` - Handle documents
- `chat create/select/send` - Chat operations
- `state show` - View current state

## Graph RAG vs Vector RAG

**Graph RAG** excels at:
- Entity relationships (who reports to whom, what connects to what)
- Multi-hop reasoning (Alice manages Bob, Bob works on Platform)
- Organizational structures and knowledge graphs
- Explicit connections between concepts

**Vector RAG** excels at:
- Semantic similarity (finding conceptually similar content)
- General document search
- Unstructured text retrieval
- Topic-based queries
