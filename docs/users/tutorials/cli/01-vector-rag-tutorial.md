# Tutorial 1: Vector RAG

Learn vector-based semantic search for document retrieval.

**Time**: 20 minutes

## Setup

```bash
task health-check
```

## 1. Configure Vector RAG

View available options:

```bash
task cli -- rag-options list
```

View current defaults:

```bash
task cli -- default-rag-config show
```

Output:

```
RAG Type: vector
Chunking Algorithm: sentence
Chunk Size: 1000
Chunk Overlap: 200
Embedding Algorithm: nomic-embed-text
Top K: 5
Rerank Algorithm: none
```

Set defaults:

```bash
task cli -- default-rag-config create
```

Input:

```
RAG type [vector]:
Chunking algorithm [sentence]: semantic
Chunk size [1000]: 800
Chunk overlap [200]: 150
Embedding algorithm [nomic-embed-text]:
Top K [5]: 5
Rerank algorithm [none]: cross-encoder
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
Workspace name: Tech Docs
Description (optional): Technical documentation
RAG type [vector]:
```

Output:

```
Created workspace [1] Tech Docs
```

View configuration:

```bash
task cli -- workspace show 1
```

Output shows inherited vector config:

```
ID: 1
Name: Tech Docs
RAG Type: vector
Status: active

Vector RAG Configuration:
  Chunking Algorithm: semantic
  Chunk Size: 800
  Chunk Overlap: 150
  Embedding Algorithm: nomic-embed-text
  Top K: 5
  Rerank Algorithm: cross-encoder
```

Select workspace:

```bash
task cli -- workspace select 1
```

## 3. Upload Documents

Create `python.txt`:

```
Python handles errors using try-except blocks. Place code that might raise
exceptions in the try block. Catch specific exceptions in except blocks.
Python has built-in exceptions like ValueError, TypeError, and KeyError.
```

Create `docker.txt`:

```
Docker containers package applications with dependencies. Images are templates,
containers are running instances. Dockerfile contains instructions: FROM (base),
RUN (commands), COPY (files), CMD (default command). Docker Compose defines
multi-container apps in docker-compose.yml.
```

Upload:

```bash
task cli -- document upload python.txt
task cli -- document upload docker.txt
```

Output:

```
Uploading python.txt...
Uploaded [1] python.txt
```

List documents:

```bash
task cli -- document list
```

Output:

```
[1] python.txt
[2] docker.txt
```

View details:

```bash
task cli -- document show 1
```

## 4. Query Documents

Create session:

```bash
task cli -- chat create 1
```

Input:

```
Session title (optional): Questions
```

Output:

```
Created chat session [1] Questions
```

Select session:

```bash
task cli -- chat select 1
```

Output:

```
Selected [1] Questions
```

Check state:

```bash
task cli -- state show
```

Output:

```
Current State:

  Workspace: [1] Tech Docs
  Session: [1] Questions
```

Send query:

```bash
task cli -- chat send "How does Python handle errors?"
```

Output:

```
You: How does Python handle errors?
Assistant: Python uses try-except blocks for error handling. Place risky code
in the try block and catch specific exceptions in except blocks.
```

View history:

```bash
task cli -- chat history
```

## Commands Covered

- `rag-options list` - View algorithms
- `default-rag-config show/create` - Configure defaults
- `workspace create/show/select` - Manage workspaces
- `document upload/list/show` - Handle documents
- `chat create/select/send/history` - Chat operations
- `state show` - View current state
