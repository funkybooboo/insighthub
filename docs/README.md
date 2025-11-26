# InsightHub Documentation

This directory contains comprehensive documentation for the InsightHub project.

## Directory Structure

### setup/
Setup and installation guides:
- **docker.md** - Container deployment with Docker Compose
- **python-workspace.md** - Python monorepo workspace configuration
- **docker-workspace-update.md** - Changes for Docker workspace compatibility
- **taskfile-setup.md** - Task automation setup and usage

### architecture/
System architecture and design:
- **architecture.md** - Overall system architecture and design principles
- **project-structure.md** - Codebase organization and conventions
- **rag-system-documentation.md** - RAG implementation details (Vector/Graph)
- **streaming.md** - Real-time streaming architecture with WebSockets
- **worker-consolidation-analysis.md** - Worker service analysis

### development/
Development guides and processes:
- **contributing.md** - Contribution guidelines and standards
- **testing.md** - Testing strategies and best practices
- **github-actions.md** - CI/CD workflow documentation

### user-guides/
User-facing documentation:
- **client-user-flows.md** - Detailed user interaction flows

### planning/
Project planning documents:
- **idea.md** - Original project concept
- **requirements.md** - Project requirements
- **high-level-design.md** - High-level design overview
- **low-level-design.md** - Detailed design specifications

### project-management/
Project management resources:
- **todo.md** - Project task tracking

### rag/
RAG system specific documentation:
- **comparison.md** - Vector RAG vs Graph RAG comparison
- **vector-rag-architecture.md** - Vector RAG implementation
- **graph-rag-architecture.md** - Graph RAG implementation

## Quick Links

### Getting Started
1. [Docker Setup](setup/docker.md) - Start here for deployment
2. [Python Workspace](setup/python-workspace.md) - Local development setup
3. [Contributing Guide](development/contributing.md) - Development workflow

### Understanding the System
1. [System Architecture](architecture/architecture.md) - Overall architecture
2. [Project Structure](architecture/project-structure.md) - Code organization
3. [RAG System](architecture/rag-system-documentation.md) - Core RAG implementation

### Development
1. [Testing Guide](development/testing.md) - Testing strategies
2. [GitHub Actions](development/github-actions.md) - CI/CD workflows
3. [Taskfile Setup](setup/taskfile-setup.md) - Task automation

## Additional Documentation

### Root Level Files
- **README.md** - Main project README
- **CHANGELOG.md** - Version history and changes
- **CLAUDE.md** - Claude AI assistant instructions
- **GEMINI.md** - Gemini AI assistant instructions

### Package-Specific Docs
- **packages/server/docs/** - Server API documentation
- **packages/client/docs/** - Client-specific documentation (if any)

## Documentation Standards

All documentation in this project follows these standards:
- ASCII-only characters (no emojis or special Unicode)
- Lowercase filenames for markdown files
- Clear, concise language
- Code examples where applicable
- Links to related documentation
