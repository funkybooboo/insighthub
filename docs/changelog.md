# Changelog Guidelines

This document explains how to maintain the `CHANGELOG.md` file for the InsightHub project.

## Purpose

The changelog documents **all notable changes** in the project.  
It is intended for developers, contributors, and users to see what has changed between versions.

## Location

The main changelog file is located at the root of the project:

```
/CHANGELOG.md
```

## Structure

The file follows the [Common Changelog](https://common-changelog.org/) style:

- **Latest release at the top**
- **Version headings:** `## [VERSION] - YYYY-MM-DD`
- **Unreleased section:** `## [Unreleased]` for ongoing changes
- **Grouped changes:** `Added`, `Changed`, `Fixed`, `Removed`

Example:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Add support for vector RAG module.
- Implement Flask backend with clean architecture.

### Changed
- Updated from FastAPI to Flask 3.0+
- Migrated from MinIO to filesystem storage
- Switched from Pinecone to Qdrant vector database

### Fixed
- Fix bug in filebeat Docker configuration.
- Resolve WebSocket connection issues in React 19

## [1.0.0] - 2025-11-18
- Initial release with Flask backend and React 19 frontend.
```

## How to Add Entries

1. **Always add new changes under `## [Unreleased]`.**

2. **Group by type**:

   * **Added:** new features
   * **Changed:** updates to existing functionality
   * **Fixed:** bug fixes
   * **Removed:** removed functionality

3. **Use concise, clear language**.

4. **Reference relevant issues or PRs** if applicable:

```
- Fix crash when uploading document (#42)
- Add caching for RAG queries (#37)
- Implement JWT authentication with Flask (#45)
```

5. **When releasing a version**:

   * Move items from `Unreleased` to a new version heading.
   * Add the release date.
   * Tag the Git repository with the version number (e.g., `git tag v1.0.0`).

## Commit Messages

While not mandatory, following **conventional commits** helps keep the changelog consistent:

```
feat: add vector RAG support
fix: correct filebeat Docker config
docs: update changelog instructions
refactor: migrate from FastAPI to Flask
test: add integration tests for Flask endpoints
```

## Current Technology Stack

This project uses:

- **Backend**: Flask 3.0+ with SQLAlchemy
- **Frontend**: React 19 with TypeScript and Redux
- **Database**: PostgreSQL with Alembic migrations
- **Vector DB**: Qdrant for vector storage
- **Graph DB**: Neo4j for graph-based RAG
- **Storage**: Local filesystem (changed from MinIO)
- **Message Queue**: RabbitMQ for worker communication
- **Cache**: Redis for session and performance
- **LLM**: Ollama for local inference
- **Containerization**: Docker Compose for orchestration

## Summary

* Keep `CHANGELOG.md` human-readable.
* Add only **notable changes**.
* Update `Unreleased` regularly.
* Tag releases in Git to match changelog versions.
* Reference current technology stack when documenting changes.
* Include both backend (Flask) and frontend (React 19) changes.