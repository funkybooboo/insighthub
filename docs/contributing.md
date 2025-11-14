# Contributing to InsightHub

Thank you for contributing! This guide covers standards and workflows.

## Getting Started

### Prerequisites
- Git, Docker, Docker Compose
- Python 3.11+ with Poetry
- Node.js 18+ and Bun
- Basic RAG and LLM knowledge

### Setup

1. Fork and clone:
   ```bash
   git clone https://github.com/yourusername/insighthub.git
   cd insighthub
   ```

2. Backend setup:
   ```bash
   cd packages/server
   poetry install
   cp .env.example .env  # Configure as needed
   ```

3. Frontend setup:
   ```bash
   cd packages/client
   bun install
   ```

4. Start services:
   ```bash
   docker compose up
   ```

## Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

Branch naming:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Refactoring
- `test/description` - Tests

### 2. Make Changes
Make small, focused commits with clear messages.

### 3. Run Quality Checks
```bash
# Python
cd packages/server && task check

# TypeScript
cd packages/client && task check

# Or from root
task server:check && task client:check
```

### 4. Push and Create PR
```bash
git push origin feature/your-feature-name
```

## Code Standards

### Python (Backend)

**Style**:
- Black (line length 100)
- isort (Black-compatible)
- Ruff linting
- Mandatory type hints
- Google-style docstrings

**Type Safety**:
```python
# GOOD: Explicit types
def process_docs(docs: list[Document], max_count: int = 100) -> dict[str, int]:
    results: dict[str, int] = {}
    for doc in docs[:max_count]:
        results[doc.id] = len(doc.text)
    return results

# BAD: Missing types or Any
def process_docs(docs, max_count=100):
    results: dict[str, Any] = {}  # Any forbidden!
    return results
```

**Architecture**:
- Dependency injection via constructors
- Interface-based design (no "Base" prefix)
- No direct instantiation of concrete classes

```python
# GOOD: Dependency injection
class VectorRag(Rag):
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_model: EmbeddingModel,
        chunker: Chunker
    ):
        self.vector_store = vector_store

# BAD: Direct instantiation
class VectorRag:
    def __init__(self):
        self.vector_store = QdrantVectorStore(...)  # Tightly coupled!
```

**Testing**:
- Use dummy implementations, not mocks
- Unit tests: isolated, fast, no external dependencies
- Integration tests: testcontainers with real services

```python
# GOOD: Dummy implementation
def test_vector_rag():
    rag = VectorRag(
        vector_store=InMemoryVectorStore(),
        embedding_model=DummyEmbeddings(),
        chunker=CharacterChunker(chunk_size=10)
    )
    count = rag.add_documents([{"text": "test"}])
    assert count > 0

# BAD: Mocking
def test_vector_rag():
    mock_store = Mock()  # Don't use mocks!
```

### TypeScript (Frontend)

**Style**:
- Prettier for formatting
- ESLint React rules
- TypeScript strict mode
- PascalCase for components, camelCase for utilities

**Component Pattern**:
```typescript
// GOOD: Typed props
interface ChatMessageProps {
  message: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, role, timestamp }) => {
  return <div className={`message ${role}`}>{message}</div>;
};

// BAD: Untyped
export const ChatMessage = ({ message, role, timestamp }) => {
  return <div>{message}</div>;
};
```

### General Standards

**Character Encoding**:
- ASCII only - no emojis or special Unicode characters
- Standard punctuation only

**Documentation**:
- Lowercase filenames in docs/
- Code examples with language tags
- Table of contents for long docs
- 80-100 character line length

## Testing Requirements

### Python Tests
- **Unit** (`tests/unit/`): Isolated, dummy implementations, fast
- **Integration** (`tests/integration/`): Testcontainers, real services

```bash
cd packages/server
poetry run pytest tests/unit/ -v           # Fast
poetry run pytest tests/integration/ -v    # Slower
poetry run pytest --cov=src                # Coverage
```

### TypeScript Tests
```bash
cd packages/client
bun test
```

## Documentation

Update docs when you:
- Add features or endpoints
- Change configuration
- Modify architecture
- Fix documented behavior

**Locations**:
- `README.md` - Overview
- `docs/` - General docs
- `packages/server/docs/` - Backend
- `packages/client/README.md` - Frontend
- `CLAUDE.md` - Architecture (major changes only)

## Pull Request Process

### Before Submitting
1. Install Task (see `docs/taskfile-setup.md`)
2. Run all checks: `task check`
3. Write tests
4. Update documentation
5. Write clear commit messages

### Commit Format
```
type: brief description

Longer explanation if needed.

Fixes #issue-number
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### PR Template
```markdown
## Description
Brief description

## Type
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing done

## Checklist
- [ ] Code follows style
- [ ] Tests added/updated
- [ ] Docs updated
- [ ] CI checks pass
```

### Review Process
1. **CI**: All checks pass (format, lint, type-check, test)
2. **Code Review**: Maintainer approval
3. **Merge**: Squash and merge to main

## Common Tasks

### Add RAG Component
1. Create interface in `src/infrastructure/rag/`
2. Implement concrete class
3. Add to factory
4. Unit tests with dummies
5. Integration tests
6. Update docs

### Add API Endpoint
1. Define route in `src/domains/*/routes.py`
2. Service logic in `src/domains/*/service.py`
3. Database models if needed
4. Unit + integration tests
5. Update API docs

### Add React Component
1. Create in `src/components/`
2. Define TypeScript interfaces
3. Add to parent component
4. Write tests
5. Update docs if needed

## Getting Help
- Check `docs/` directory
- Review similar code
- GitHub issues/discussions

Thank you for contributing!
