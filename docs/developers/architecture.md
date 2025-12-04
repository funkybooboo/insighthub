# Architecture Overview

InsightHub follows **Domain-Driven Design (DDD)** principles with clean separation of concerns and strict layer boundaries.

## Core Principles

1. **Domain-Centric**: Business logic lives in domain folders, not infrastructure
2. **Dependency Injection**: Composition over inheritance, all dependencies injected
3. **Railway-Oriented Programming**: Using `returns` library for Result types
4. **Pydantic Validation**: Schema-based validation for all DTOs
5. **Clear Boundaries**: Commands → Orchestrators → Services → Repositories

## Architecture Layers

```
┌─────────────────────────────────────────────┐
│             CLI Layer (cli.py)              │
│         Command routing & parsing           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          Domain Layer (domains/)            │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Commands (commands.py)              │  │
│  │  - Parse CLI arguments               │  │
│  │  - Use IO wrappers for I/O           │  │
│  │  - Call orchestrators only           │  │
│  └──────────────────────────────────────┘  │
│                    ↓                        │
│  ┌──────────────────────────────────────┐  │
│  │  Orchestrators (orchestrator.py)     │  │
│  │  - Coordinate workflow               │  │
│  │  - validation → service → mapper     │  │
│  │  - Return Result types               │  │
│  └──────────────────────────────────────┘  │
│                    ↓                        │
│  ┌──────────────────────────────────────┐  │
│  │  Validation (validation.py)          │  │
│  │  - Business rule validation          │  │
│  │  - Use Pydantic for structure        │  │
│  └──────────────────────────────────────┘  │
│                    ↓                        │
│  ┌──────────────────────────────────────┐  │
│  │  Services (service.py)               │  │
│  │  - Business logic                    │  │
│  │  - Orchestrate workflows             │  │
│  │  - Use data access layer             │  │
│  └──────────────────────────────────────┘  │
│                    ↓                        │
│  ┌──────────────────────────────────────┐  │
│  │  Data Access (data_access.py)        │  │
│  │  - Coordinates cache + repository    │  │
│  │  - Caching logic                     │  │
│  │  - Cache serialization/deserialize   │  │
│  └──────────────────────────────────────┘  │
│                    ↓                        │
│  ┌──────────────────────────────────────┐  │
│  │  Repositories (repositories.py)      │  │
│  │  - Data persistence abstraction      │  │
│  │  - SQL queries                       │  │
│  │  - Return domain models              │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Models (models/)                    │  │
│  │  - Domain entities                   │  │
│  │  - SQLAlchemy models                 │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  DTOs (dtos.py)                      │  │
│  │  - Pydantic request/response models  │  │
│  │  - Validation rules                  │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Mappers (mappers.py)                │  │
│  │  - Model ↔ DTO transformations       │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│    Infrastructure Layer (infrastructure/)   │
│  - Generic utilities (cache, validation)    │
│  - RAG workflows & algorithms               │
│  - LLM providers                            │
│  - Storage adapters                         │
│  - Database connection                      │
└─────────────────────────────────────────────┘
```

## Domain Structure

Each domain is self-contained with all its components:

```
domains/<domain_name>/
├── models.py           # Domain entities (SQLAlchemy)
├── repositories.py     # Data persistence (SQL queries)
├── data_access.py      # Cache + repository coordination
├── service.py          # Business logic
├── orchestrator.py     # Workflow coordination
├── validation.py       # Business rules (Pydantic)
├── mappers.py          # DTO transformations
├── dtos.py             # Pydantic request/response models
└── commands.py         # CLI command handlers
```

**Note**: Not all domains have all components. For example:
- `rag_options` domain has no models/repositories (read-only service)
- `state` domain has no data_access (minimal caching needs)
- Only `workspace` and `document` have data_access layers currently

## Current Domains

### 1. Workspace Domain (`domains/workspace/`)
- **Purpose**: Manage workspaces and their configurations
- **Subdomains**:
  - `document/` - Document management
  - `chat/session/` - Chat sessions
  - `chat/message/` - Chat messages
- **Key Models**: Workspace, VectorRagConfig, GraphRagConfig

### 2. Default RAG Config Domain (`domains/default_rag_config/`)
- **Purpose**: System-wide RAG configuration defaults
- **Key Models**: DefaultRagConfig, DefaultVectorRagConfig, DefaultGraphRagConfig
- **Note**: Single-row configuration table

### 3. State Domain (`domains/state/`)
- **Purpose**: Track current user selections (workspace, session)
- **Key Models**: State
- **Key Operations**: Get current state with resolved names

### 4. RAG Options Domain (`domains/rag_options/`)
- **Purpose**: Query available RAG algorithms and options
- **Key Operations**: List all available algorithms by category
- **Note**: Read-only domain, no models or repositories

## Infrastructure Organization

### Generic Utilities (Reusable Across Domains)

**`infrastructure/cache/cache.py`**
- Generic cache interface (abstract)
- Implementations: RedisCache, InMemoryCache
- Data access layers use Optional[Cache] for caching coordination
- Services with complex caching needs use data_access layer to avoid duplication

**`infrastructure/validation/utils.py`**
- Reusable validation functions
- `validate_positive_id()`, `validate_pagination()`, etc.
- Pure functions, no domain knowledge

**`infrastructure/mappers/utils.py`**
- Reusable mapper utilities
- `format_datetime()`, `map_timestamps()`
- Generic formatting helpers

**`infrastructure/cli_io.py`**
- Generic I/O wrappers
- `IO.print()`, `IO.input()`, `IO.confirm()`
- Replaces domain-specific presenters

### Domain-Specific Infrastructure

**`infrastructure/rag/`**
- RAG algorithms and workflows
- Only `rag_options` domain directly accesses
- Other domains use `rag_options` service

## Data Access Layer Pattern

The data access layer coordinates caching and persistence operations to avoid duplicating caching logic in services.

### When to Use Data Access Layer

**Use data_access.py when**:
- Domain has complex caching requirements (workspace, document)
- Multiple service methods need the same caching patterns
- Need to coordinate cache invalidation across related entities

**Don't use when**:
- Service has simple/no caching needs (chat session, message)
- Service only has a few operations
- Would create unnecessary indirection

### Data Access Layer Responsibilities

```python
class WorkspaceDataAccess:
    """Coordinates cache + repository for Workspace."""

    def __init__(self, repository: WorkspaceRepository, cache: Optional[Cache] = None):
        self.repository = repository  # Exposed for special operations
        self.cache = cache

    def get_by_id(self, workspace_id: int) -> Workspace | None:
        """Get with caching."""
        # Try cache first
        cached = self._get_from_cache(workspace_id)
        if cached:
            return cached

        # Cache miss - fetch from database
        workspace = self.repository.get_by_id(workspace_id)

        if workspace and self.cache:
            self._cache_workspace(workspace)

        return workspace

    def update(self, workspace_id: int, **updates) -> bool:
        """Update and invalidate cache."""
        result = self.repository.update(workspace_id, **updates)
        if result:
            self._invalidate_cache(workspace_id)
        return result
```

**Key Points**:
- Data access handles ALL caching logic
- Service just calls data_access methods
- Repository is exposed via `self.repository` for operations not yet in data_access
- Cache is Optional - data access gracefully handles None

## Data Flow Example: Create Workspace

```
1. CLI Command (commands.py)
   ↓
   - Parse args
   - Get options from rag_options_orchestrator
   - Display options using IO.print()
   - Gather input using IO.input()
   - Create Pydantic DTO (validates automatically)

2. Orchestrator (orchestrator.py)
   ↓
   - Call validation layer
   - Call service layer
   - Map result to response DTO
   - Return Result[WorkspaceResponse, Error]

3. Validation (validation.py)
   ↓
   - Apply business rules
   - Check defaults
   - Return Result[ValidatedRequest, ValidationError]

4. Service (service.py)
   ↓
   - Execute business logic
   - Create RAG resources (domain-specific workflow)
   - Use data_access for persistence
   - Data access handles caching automatically
   - Return Result[Workspace, Error]

5. Data Access (data_access.py)
   ↓
   - Check cache first
   - Call repository if cache miss
   - Cache result before returning
   - Handle cache invalidation on updates

6. Repository (repositories.py)
   ↓
   - Execute SQL queries
   - Map rows to domain models
   - Return domain models

7. Mapper (mappers.py)
   ↓
   - Transform Workspace → WorkspaceResponse
   - Use generic mapper utils for dates
   - Return response DTO
```

## Key Design Decisions

### Why Models in Domains?
Models are domain-specific entities. Moving them to domains ensures:
- Clear ownership (each domain owns its models)
- No circular dependencies
- Models are colocated with their business logic

### Why Repositories in Domains?
Repositories are domain-specific data access layers:
- Each domain knows how to persist its own models
- Repository queries reflect domain operations
- Infrastructure only provides database connection

### Why Only `rag_options` Accesses RAG Infrastructure?
Clear separation of concerns:
- `rag_options` is the **only** domain that directly reads algorithm options
- All other domains use `rag_options` service
- Prevents duplication and ensures consistency

### Why Generic Validation/Mapper Utilities?
Eliminate duplication without coupling:
- Pure functions, no side effects
- No domain-specific knowledge
- Easy to test and reuse

### Why Pydantic for DTOs?
Declarative validation:
- Schema-based validation at runtime
- Automatic parsing and type coercion
- Self-documenting API contracts

## Adding a New Domain

1. Create domain directory structure:
```bash
mkdir -p src/domains/my_domain/{models,repositories}
touch src/domains/my_domain/{__init__.py,service.py,orchestrator.py,validation.py,mappers.py,dtos.py,commands.py}
```

2. Define models in `models/`
3. Implement repository in `repositories/`
4. Define Pydantic DTOs in `dtos.py`
5. Implement validation in `validation.py`
6. Implement business logic in `service.py`
7. Orchestrate workflow in `orchestrator.py`
8. Create CLI commands in `commands.py`
9. Wire into `context.py` and `cli.py`

## Testing Strategy

- **Unit Tests**: Test services, validation, mappers in isolation
- **Integration Tests**: Test repositories with real database
- **E2E Tests**: Test complete CLI workflows

Each domain's tests mirror its structure:
```
tests/
├── unit/
│   └── domains/
│       └── my_domain/
│           ├── test_service.py
│           ├── test_validation.py
│           └── test_mappers.py
├── integration/
│   └── domains/
│       └── my_domain/
│           └── test_repository.py
└── e2e/
    └── cli/
        └── test_my_domain_commands.py
```

## Best Practices

1. **Commands**: Only call orchestrators, never services or repositories directly
2. **Orchestrators**: Coordinate, don't contain business logic
3. **Services**: Business logic only, no I/O or presentation concerns
4. **Repositories**: Data access only, return domain models
5. **Validation**: Business rules, not just structure (Pydantic handles structure)
6. **DTOs**: Request = input validation, Response = output formatting
7. **Mappers**: Transformations only, no business logic

## Anti-Patterns to Avoid

❌ Commands directly accessing repositories
❌ Services containing validation logic (should be in validation layer)
❌ DTOs as domain models (separate concerns)
❌ Infrastructure code in domain services (inject dependencies)
❌ Domain-specific code in infrastructure utilities
❌ Skipping orchestrators for "simple" operations
❌ Using raw dict instead of Pydantic models for DTOs
