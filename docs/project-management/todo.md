# **Project Roadmap / Todo**

## 0. High-Level Goal

Build a configurable RAG platform where users create **Workspaces**, upload documents, configure RAG settings, and start chat sessions that operate over those documents.
System includes:

* Client (React)
* Server (API + RAG orchestration)
* Workers (document processing, retrieval, background tasks)
* CLI
* Shared code libraries
* Containerized deployment (Docker, Swarm, K8s-ready)
* Strong testing, CI, and code quality practices

---

# **1. Workspaces & RAG System**

## 1.1 Workspace Architecture

### *Purpose*

Group documents and chat sessions. Each workspace has its own RAG configuration.

### *Data Model*

* **Workspace** `1:N` Documents
* **Workspace** `1:1` RAG Config
* **Workspace** `1:N` Chat Sessions

### *Entities*

* **Workspace:** id, name, timestamps
* **Document:** id, workspace_id, filename, path/content, uploaded_at
* **RAG Config:** id, workspace_id (unique), embedding_model, retriever_type, chunk_size, timestamps
* **Chat Session:** id, workspace_id, history JSONB, timestamps

### *API Requirements*

* Workspaces: create, update, delete, list
* Documents: upload, delete, list
* RAG Config: create, update, validate, retrieve
* Chat Sessions: create, delete, list, fetch history
* RAG operations: load workspace config, load document embeddings, run retrieval + LLM response

### *DB Schema Cleanup*

Ensure: sensible naming, foreign keys, cascading deletes, indexing.

---

# **2. Client (React)**

## 2.1 Storybook

* Story for each main component

## 2.2 Cypress Tests

Replace Playwright. Cover main workflows:

* Sign up / sign in
* Change background/theme
* Create workspace
* Create chat
* Upload/delete documents
* Delete workspace/chat
* Chat with bot

## 2.3 UI/UX Features

* Workspaces UI
* Chats UI
* Document uploads & status
* Theme system
* Settings & Preferences
* RAG Config (global + workspace-level)

## 2.4 Folder Restructure (Recursive Feature Structure)

Use recursive feature-based architecture:

```
src/features/<feature>/{components/hooks/api/...}
```

Sub-features follow same structure.

---

# **3. Server**

## 3.1 Endpoints & Services

* Workspace CRUD
* Document upload + storage
* Chat session CRUD
* RAG pipeline
* Authentication
* Preferences
* Worker coordination (RabbitMQ)

## 3.2 Stateless Processes

* Server should be horizontally scalable
* No local state — use DB, Redis, and object storage

## 3.3 Cache

* Redis for:

  * embeddings cache
  * chat history cache
  * document metadata
  * rate limiting

## 3.4 Security

* Validate all user inputs
* Enforce permissions
* Sanitization
* JWT or session handling
* Pass all security middleware
* Ensure RCE-safe document processing pipeline

---

# **4. Workers**

## 4.1 Purpose

Background processing for:

* Document ingestion
* Chunking
* Embedding generation
* Retrieval pipelines
* Web-scraping & external information pulling
* Preparing data for user queries

## 4.2 Architecture

* RabbitMQ-based event-driven system
* Observer—not polling
* Could be separate packages next to server or nested inside server monorepo

## 4.3 Shared Library

Move logic shared by:

* Server
* Workers
* CLI

Into one **shared/js** and/or **shared/ts** lib.

It seems like we need to move some of the types declared in types to a more appropriate places.

We need to remove all reading from the configs in the shared library.

---

# **5. CLI**

## 5.1 Goals

* Typescript-based
* Uses shared codebase
* Provide parity with core features of client
* Clean commands, good UX
* Test coverage

## 5.2 Tasks

* Implement CLI
* Add CI for CLI
* Share code between client/server/workers

---

# **6. DevOps / Deployment**

## **6.1 Environment & Configuration Management**

We need a **Configuration Manager** responsible for loading, validating, and merging config values across:

* Client
* Server
* Workers
* CLI

### **Requirements**

* Support plain `.env` files (preferred default)
* Provide structured typed config access inside code
* Support environment layering:

  * `.env.local`
  * `.env.test`
  * `.env.production`
  * Worker-specific `.env.worker`
  * CLI environment overrides
* Ensure strong validation & schema enforcement (Zod, Valibot, Yup, or custom)
* Allow fallback logic (ENV → defaults → secrets → runtime overrides)
* Possibly support future advanced config systems:

  * Consul
  * Vault
  * SSM / Parameter Store
  * etc.
* Prevent secrets from being committed or baked into images
* Provide a centralized “config entrypoint” for each process

### **Implementation Outline**

* A shared `@shared/config` package
* Loads `.env` + `.env.<env>`
* Merges configs based on NODE_ENV / RUN_MODE
* Validates with schema before app starts
* Exposes a stable API:

```ts
import { config } from '@shared/config';

config.server.databaseUrl
config.rag.defaultEmbeddingModel
config.client.theme
config.worker.queueNames
```

* Supports “dynamic config” resolution for workers (e.g., queue names, worker limits)

### **Goals**

* Safe defaults
* Strong validation
* No ambiguity between environments
* Consistent config across server, client, CLI, workers
* Future extensibility without breaking plain `.env` workflows

## 6.2 Docker & Secrets

* Do not bake secrets into images
* Use Docker secrets or external secret manager

## 6.3 Audit in CI

Extend CI:

* Install Trivy
* Run `task security`
* Add scanning and auditing steps

## 6.4 Orchestrations

Be deployable to:

* Docker Compose
* Docker Swarm
* Kubernetes

Swarm compatibility implies easy k8s migration.

---

# **7. Documentation**

## 7.1 Codebase Docs

* Features
* Tests
* Architecture overview
* Deployment
* Shared libraries
* Worker processes
* Environment handling

## 7.2 RAG & Design Docs

* Design-driven documentation
* UML diagrams
* Explanation of stateless architecture
* User guide/manual

---

# **8. Testing**

## 8.1 General

* Improve global test coverage
* Unit tests for all libraries
* Integration tests for server
* Worker tests

## 8.2 Bruno Tests

* Fix: ensure they pass security middleware

---

# **9. Project Management Workflow**

* Create a *plain-text Kanban-style system* for organizing project tasks
* Possibly use Markdown-based columns or folders

---

# **10. General Code Quality**

* Clean up types
* Global vs local types
* Remove duplication
* Simplify where possible
* Ensure strong validation everywhere

---

# **11. Final Milestones**

### A. Get Server Working

* Authentication
* CRUD for all resources
* RAG endpoints

### B. Get Client Working

* Layout & style system
* Workspaces + Chats
* Documents
* Theming
* Settings & Preferences
* RAG Config UI

### C. Get CLI Working

### D. Implement Workers & Shared Lib
