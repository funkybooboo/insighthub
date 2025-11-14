# InsightHub Documentation

Documentation for the InsightHub dual RAG system.

## Quick Start

- [Project Proposal](idea.md) - Original proposal and timeline
- [Quick Start Guide](../packages/server/docs/quick-start.md) - Get running in 5 minutes

## Architecture

- [Project Overview](../README.md) - System overview
- [Architecture](architecture.md) - System design and patterns
- [CLAUDE.md](../CLAUDE.md) - Detailed design principles
- [Streaming](streaming.md) - WebSocket implementation

## Development

### Build System
- [Docker Guide](docker.md) - Container workflows
- [Task Setup](taskfile-setup.md) - Task runner commands

### Backend (Python)
Server docs in `packages/server/docs/`:
- [API Documentation](../packages/server/docs/api.md)
- [Quick Start](../packages/server/docs/quick-start.md)
- [Server README](../packages/server/README.md)

### Frontend (React)
- [Client README](../packages/client/README.md)

### Contributing
- [Contributing Guide](contributing.md) - Code standards and workflow
- [GitHub Actions](github-actions.md) - CI/CD workflows

## Project Status

### Phase 1: Vector RAG - Complete
- Modular architecture with dependency injection
- Multiple chunking strategies
- Ollama + Qdrant integration
- Real-time streaming chat
- Document management
- CLI and REST API

### Phase 2: Graph RAG - In Progress
- Neo4j integration (planned)
- Leiden clustering (planned)
- React chatbot with memory
- Wikipedia MCP integration (planned)
- Vector vs Graph comparison

### Phase 3: Advanced Features - Planned
- Hybrid search
- Evaluation metrics
- Multi-modal content

## Tech Stack

**Frontend**: React 19, TypeScript, Vite, TailwindCSS, Redux Toolkit, Socket.IO

**Backend**: Python 3.11+, Flask, SQLAlchemy, PostgreSQL, Qdrant, Ollama

**Infrastructure**: Docker, GitHub Actions, Poetry, Bun

## Architecture Principles

- **Clean Architecture**: Domain and infrastructure layer separation
- **Dependency Injection**: Pluggable components
- **Interface-Based Design**: Program to interfaces
- **Type Safety**: Strict typing in Python and TypeScript
- **ASCII Only**: No emojis or special characters

## Documentation Standards

- Lowercase filenames (e.g., `docker.md`, `idea.md`)
- ASCII characters only
- Clear section headers
- Code examples with language tags
- 80-100 character line length

## Quick Links

- [Main README](../README.md)
- [Project Proposal](idea.md)
- [Server Docs](../packages/server/docs/)
- [Client Docs](../packages/client/README.md)

## Support

- Review documentation
- Check testing guide for examples
- Create GitHub issue for bugs/features
