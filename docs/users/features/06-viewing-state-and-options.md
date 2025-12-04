# Viewing State and RAG Options

InsightHub provides commands to view your current application state and available RAG configuration options.

## Viewing Current State

The `state show` command displays your currently selected workspace and chat session:

```bash
task cli -- state show
```

**Output:**
```
Current State:

  Workspace: [1] My Project
  Session: [5] Technical Discussion
```

This is useful when you:
- Want to confirm which workspace you're working in
- Need to verify which chat session is active
- Are switching between multiple projects

If no workspace or session is selected, you'll see:
```
Current State:

  Workspace: None selected
  Session: None selected
```

## Viewing Available RAG Options

The `rag-options list` command shows all available RAG algorithms and configurations:

```bash
task cli -- rag-options list
```

**Output:**
```
Available RAG Options:

RAG Types:
  - vector: Vector-based semantic search using embeddings
  - graph: Graph-based knowledge retrieval
  - hybrid: Combination of vector and graph approaches

Chunking Algorithms:
  - semantic: Split text based on semantic meaning
  - sliding_window: Fixed-size chunks with overlap
  - paragraph: Split by paragraphs

Embedding Algorithms:
  - sentence_transformers: Local embedding models
  - openai: OpenAI embedding API
  - cohere: Cohere embedding API

Rerank Algorithms:
  - cross_encoder: Re-rank using cross-encoder models
  - bm25: BM25 lexical ranking
  - none: No reranking

Entity Extraction Algorithms:
  - spacy: SpaCy NER extraction
  - llm: LLM-based extraction
  - none: No entity extraction

Relationship Extraction Algorithms:
  - dependency_parsing: Extract relationships from syntax
  - llm: LLM-based extraction
  - none: No relationship extraction

Clustering Algorithms:
  - louvain: Louvain community detection
  - leiden: Leiden algorithm
  - none: No clustering
```

## When to Use These Commands

### Use `state show` when:
- You're unsure which workspace is currently active
- You need to verify your chat session before sending messages
- You're documenting your workflow or troubleshooting

### Use `rag-options list` when:
- You're configuring a new workspace
- You want to know what algorithms are available
- You're deciding which RAG strategy to use for your project
- You need to reference valid option values for the `default-rag-config` command

## Integration with Other Commands

These viewing commands complement the configuration commands:

```bash
# Check current state
task cli -- state show

# View available options
task cli -- rag-options list

# Configure defaults based on available options
task cli -- default-rag-config new

# Create a workspace with those defaults
task cli -- workspace new
```

## Tips

- Run `state show` regularly to stay oriented in your workflow
- Use `rag-options list` before configuring RAG settings to see all valid choices
- These commands are read-only and don't modify any data
- You can run them at any time without affecting your workspaces or sessions
