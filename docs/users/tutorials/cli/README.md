# InsightHub CLI Tutorials

## Overview

These tutorials teach you how to use InsightHub's RAG (Retrieval-Augmented Generation) system through the command-line interface.

## Tutorials

### 1. Vector RAG Tutorial
**File**: `01-vector-rag-tutorial.md`
**Time**: 20 minutes

Learn how to use vector-based semantic search for retrieving information from documents. This tutorial covers:
- Configuring default vector RAG settings (chunking, embedding, reranking)
- Creating and managing vector workspaces
- Uploading and querying documents
- Understanding how vector similarity search works

**Best for**: General document search, finding semantically similar content, topic-based queries.

### 2. Graph RAG Tutorial
**File**: `02-graph-rag-tutorial.md`
**Time**: 20 minutes

Learn how to use graph-based knowledge retrieval using entity relationships. This tutorial covers:
- Configuring default graph RAG settings (entity extraction, relationship extraction, clustering)
- Creating graph workspaces
- Building knowledge graphs from documents
- Querying relationships and performing multi-hop reasoning

**Best for**: Organizational structures, entity relationships, multi-hop reasoning, knowledge graphs.

## Prerequisites

Before starting the tutorials, ensure services are running:

```bash
task health-check
```

All services (postgres, ollama, qdrant, neo4j, minio, redis) should report healthy.

## Getting Help

For command help:

```bash
task cli -- --help
task cli -- workspace --help
task cli -- document --help
task cli -- chat --help
```

## Key Concepts

- **Workspace**: Container for documents and chat sessions with a specific RAG configuration
- **Default RAG Config**: System-wide defaults that new workspaces inherit
- **Document**: Uploaded file that gets processed (chunked/embedded or entity-extracted)
- **Chat Session**: Conversation thread within a workspace
- **State**: Currently selected workspace and chat session

## Command Reference

See the tutorials for complete command coverage including:
- `rag-options` - View available algorithms
- `default-rag-config` - Configure system defaults
- `workspace` - Manage workspaces
- `document` - Handle documents
- `chat` - Chat operations
- `state` - View current state
