# Code Deduplication Refactoring Plan

## Executive Summary

This document outlines the plan to eliminate code duplication between `packages/server/` and `packages/shared/python/`. The goal is to ensure we follow proper OOP principles: program to interfaces (not implementations), use dependency injection, and maintain a single source of truth.

## Current State Analysis

### Duplicate Code Identified

1. **LLM Interface** - `LlmProvider` class exists in both locations (IDENTICAL)
2. **Blob Storage Interface** - `BlobStorage` class exists in both locations (NEARLY IDENTICAL)
3. **RabbitMQ Publisher** - `RabbitMQPublisher` class exists in both locations (NEARLY IDENTICAL)
4. **Chat Models** - `ChatSession` and `ChatMessage` exist in both locations (shared has workspace_id, server does not)
5. **Chat Repositories** - Interface + SQL implementations exist in both locations (IDENTICAL)
6. **Database Base Classes** - `Base`, `TimestampMixin` exist in both locations
7. **LLM Provider Implementations** - Ollama, OpenAI, Claude, HuggingFace all duplicated
8. **Storage Implementations** - MinIO, FileSystem, InMemory all duplicated

### Root Cause

The server was originally developed independently, then the shared library was created to support workers. Code was copied rather than refactored to use the shared library.

## Refactoring Strategy

### Phase 1: Core Interfaces (High Priority)

**Goal**: Remove duplicate interfaces from server, import from shared

#### 1.1 LLM Interface
- **Action**: Delete `server/src/infrastructure/llm/llm.py`
- **Update Imports**:
  - `server/src/domains/chat/service.py`: Change to `from shared.llm import LlmProvider`
  - `server/src/infrastructure/llm/factory.py`: Change to `from shared.llm import LlmProvider`
  - All test files

#### 1.2 Blob Storage Interface
- **Action**: Delete `server/src/infrastructure/storage/blob_storage.py`
- **Update Imports**:
  - `server/src/context.py`: Change to `from shared.storage import BlobStorage`
  - `server/src/domains/documents/service.py`: Change to `from shared.storage import BlobStorage`
  - All factory and test files

#### 1.3 Messaging (RabbitMQ)
- **Action**: Delete `server/src/infrastructure/messaging/publisher.py`
- **Update Imports**:
  - `server/src/context.py`: Change to `from shared.messaging import RabbitMQPublisher`
  - `server/src/domains/documents/service.py`: Change to `from shared.messaging import RabbitMQPublisher`

#### 1.4 Database Base Classes
- **Action**: Delete `server/src/infrastructure/database/base.py`
- **Update Imports**:
  - `server/src/domains/*/models.py`: Change to `from shared.database.base import Base, TimestampMixin`

### Phase 2: Models & Repositories (High Priority)

#### 2.1 Chat Models
- **Issue**: Shared has `workspace_id`, server doesn't
- **Resolution**: Server should use shared models (workspace_id can be nullable for backwards compatibility)
- **Action**: 
  - Delete `server/src/domains/chat/models.py`
  - Update imports to `from shared.models.chat import ChatSession, ChatMessage`
  - Create migration to add `workspace_id` column if not exists

#### 2.2 Chat Repositories
- **Action**: Delete `server/src/domains/chat/repositories.py`
- **Update Imports**: Change to `from shared.repositories.chat import ChatSessionRepository, SqlChatSessionRepository, etc.`

### Phase 3: Implementations (Medium Priority)

#### 3.1 LLM Provider Implementations
Currently duplicated:
- `ollama.py` - OllamaLlmProvider
- `openai_provider.py` - OpenAiLlmProvider
- `claude_provider.py` - ClaudeLlmProvider
- `huggingface_provider.py` - HuggingFaceLlmProvider

**Decision**: Keep in SHARED, server's factory imports from shared
- **Action**:
  - Delete server implementations
  - Update server factory to import from shared
  - Server factory can stay in server (wraps shared implementations with server config)

#### 3.2 Storage Implementations
Currently duplicated:
- `minio_blob_storage.py` / `minio_storage.py`
- `file_system_blob_storage.py`
- `in_memory_blob_storage.py`

**Decision**: Keep in SHARED
- **Action**:
  - Delete server implementations
  - Update server factory to import from shared

### Phase 4: Clean Up (Medium Priority)

#### 4.1 Folder Structure
After removing duplicates, server infrastructure should be:

```
server/src/infrastructure/
├── auth/              # Server-specific: JWT, middleware
├── database/          # Server-specific: session management, schema
├── errors/            # Server-specific: Flask error handlers
├── factories/         # Server-specific: Factories that wire up shared components
├── rag/               # Server-specific: RAG factory (being deprecated)
├── repositories/      # Server-specific: Non-standard repos (default_rag_config, workspace)
├── middleware/        # Server-specific: Flask middleware
├── socket/            # Server-specific: Socket.IO handlers
└── logging_config.py  # Server-specific: Flask logging
```

#### 4.2 Update Factories
Server factories should import implementations from shared and inject server-specific config:

```python
# server/src/infrastructure/factories/repository_factory.py
from shared.repositories.chat import SqlChatSessionRepository, SqlChatMessageRepository
from shared.repositories.document import SqlDocumentRepository
from shared.repositories.user import SqlUserRepository

def create_chat_session_repository(db: Session) -> ChatSessionRepository:
    return SqlChatSessionRepository(db)
```

### Phase 5: Verification (High Priority)

#### 5.1 Tests
- Run server unit tests: `cd packages/server && task test:unit`
- Run server integration tests: `cd packages/server && task test:integration`
- Ensure no imports broken

#### 5.2 Type Checking
- Run mypy: `cd packages/server && task check`
- Fix any type errors

#### 5.3 Runtime Testing
- Start development environment: `task up-dev`
- Test API endpoints
- Test WebSocket chat
- Test document upload

## Implementation Order

1. ✅ LLM Interface (simplest, least dependencies)
2. ✅ Blob Storage Interface
3. ✅ RabbitMQ Publisher
4. Database Base Classes
5. Chat Models (requires migration)
6. Chat Repositories
7. LLM Implementations
8. Storage Implementations
9. Clean up folder structure
10. Verification & testing

## Benefits

1. **Single Source of Truth**: All core logic in shared library
2. **Proper OOP**: Programming to interfaces, dependency injection
3. **Easier Maintenance**: Changes only needed in one place
4. **Better Testing**: Can test shared components once, reuse across server/workers
5. **Consistency**: Server and workers use identical implementations
6. **Reduced Codebase Size**: ~2000-3000 lines of duplicate code removed

## Risks & Mitigation

| Risk | Mitigation |
|------|-----------|
| Breaking existing functionality | Comprehensive test suite, phase-by-phase approach |
| Import errors | Update all imports systematically, verify with mypy |
| Database model incompatibility | Migrations for model changes, backwards compatibility |
| Circular dependencies | Careful structuring, keep server-specific code in server |

## Success Criteria

- [ ] Zero duplicate interfaces between server and shared
- [ ] All server tests pass
- [ ] Mypy type checking passes
- [ ] Development environment runs without errors
- [ ] API endpoints functional
- [ ] WebSocket chat functional
- [ ] Document upload/retrieval functional
- [ ] Code review confirms OOP principles followed

## Timeline

- **Phase 1-3**: 2-3 hours
- **Phase 4**: 1 hour
- **Phase 5**: 1 hour
- **Total**: ~5 hours of focused work

## Notes

- The `factory.py` pattern in server is GOOD - it wraps shared components with server-specific config
- Server-specific code (Flask routes, middleware, auth) should stay in server
- Shared code (interfaces, models, repositories, implementations) should be in shared
- Workers will benefit from this refactoring as they can import from shared directly
