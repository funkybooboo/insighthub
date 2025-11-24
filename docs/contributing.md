# Contributing to InsightHub

Thank you for your interest in contributing to InsightHub! This guide provides comprehensive standards, workflows, and best practices for contributing to our dual RAG system.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Pull Request Process](#pull-request-process)
- [Common Tasks](#common-tasks)
- [Getting Help](#getting-help)

---

## Getting Started

### Prerequisites

**Required Tools**:
- **Git**: Version control
- **Docker & Docker Compose**: Containerization
- **Task**: Task runner (install with `sh -c "$(curl --location https://taskfile.dev/install.sh)"`)
- **Python 3.11+**: Backend development
- **Poetry**: Python dependency management
- **Node.js 18+**: Frontend development
- **Bun**: JavaScript runtime (recommended)

**Knowledge Areas**:
- Basic understanding of RAG (Retrieval-Augmented Generation) systems
- Familiarity with LLMs (Large Language Models)
- React and TypeScript knowledge
- Python and Flask knowledge

### Initial Setup

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/yourusername/insighthub.git
   cd insighthub
   ```

2. **Backend Setup**:
   ```bash
   cd packages/server
   poetry install
   cp .env.example .env  # Configure as needed
   ```

3. **Frontend Setup**:
   ```bash
   cd packages/client
   bun install
   ```

4. **CLI Setup** (if needed):
   ```bash
   cd packages/cli
   bun install
   ```

5. **Start Development Environment**:
   ```bash
   # Start infrastructure services
   task up-infra
   
   # Terminal 1: Start backend
   cd packages/server
   poetry shell
   task server
   
   # Terminal 2: Start frontend
   cd packages/client
   task dev
   ```

---

## Development Workflow

### 1. Create Feature Branch

```bash
# Create a new feature branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

**Branch Naming Conventions**:
- `feature/description` - New features and functionality
- `fix/description` - Bug fixes and error corrections
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring and improvements
- `test/description` - Test additions and improvements
- `chore/description` - Maintenance tasks and dependencies

### 2. Make Changes

**Development Principles**:
- Make small, focused commits
- Write clear, descriptive commit messages
- Test your changes thoroughly
- Follow the established code standards
- Update documentation as needed

### 3. Run Quality Checks

```bash
# From project root - run all checks
task check

# Or run package-specific checks
cd packages/server && task check  # Python checks
cd packages/client && task check  # TypeScript checks
```

**Quality Check Components**:
- **Code Formatting**: Automatic formatting with Black/Prettier
- **Linting**: Code quality and style checks
- **Type Checking**: Static type analysis
- **Testing**: Unit and integration test execution
- **Build Verification**: Ensure code builds successfully

### 4. Test Your Changes

**Local Testing**:
```bash
# Server tests
cd packages/server
task test

# Client tests
cd packages/client
task test

# E2E tests (if applicable)
cd packages/client
task test:e2e
```

**Manual Testing**:
- Test the application in the browser
- Verify new functionality works as expected
- Test edge cases and error conditions
- Ensure existing functionality isn't broken

### 5. Submit Changes

```bash
# Stage and commit changes
git add .
git commit -m "feat: add new feature description"

# Push to your fork
git push origin feature/your-feature-name
```

---

## Code Standards

### Python (Backend)

#### Code Style

**Formatting Tools**:
- **Black**: Code formatting (line length 100)
- **isort**: Import sorting (Black-compatible)
- **Ruff**: Fast linting and code quality

**Configuration**:
```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.ruff]
line-length = 100
target-version = "py311"
```

#### Type Safety

**Strict Type Checking**:
```python
# GOOD: Explicit types with no Any
def process_documents(
    docs: list[Document], 
    max_count: int = 100
) -> dict[str, int]:
    results: dict[str, int] = {}
    for doc in docs[:max_count]:
        results[doc.id] = len(doc.text)
    return results

# BAD: Missing types or using Any
def process_documents(docs, max_count=100):
    results: dict[str, Any] = {}  # Any is forbidden!
    return results
```

**Type Hints Requirements**:
- All function parameters must have type hints
- All return values must have type hints
- All variables must have type hints when not immediately obvious
- Use `| None` for optional types
- Never use `Any` type

#### Architecture Patterns

**Dependency Injection**:
```python
# GOOD: Dependencies injected via constructor
class VectorRag(Rag):
    def __init__(
        self,
        vector_store: VectorStore,      # Interface, not concrete
        embedding_model: EmbeddingModel, # Interface, not concrete
        chunker: Chunker              # Interface, not concrete
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.chunker = chunker

# BAD: Direct instantiation of concrete classes
class VectorRag:
    def __init__(self):
        self.vector_store = QdrantVectorStore(...)  # Tightly coupled!
```

**Interface-Based Design**:
```python
# GOOD: Program to interfaces
class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,  # Abstract interface
        storage: BlobStorage,          # Abstract interface
        rag: Rag                      # Abstract interface
    ):
        self.repository = repository
        self.storage = storage
        self.rag = rag

# BAD: Depend on concrete implementations
class DocumentService:
    def __init__(self):
        self.repository = PostgresDocumentRepository(...)  # Coupled!
```

#### Documentation

**Docstring Format**:
```python
def create_workspace(
    name: str, 
    description: str, 
    rag_config: RagConfig
) -> Workspace:
    """Create a new workspace with the given configuration.
    
    Args:
        name: The name of the workspace to create.
        description: Human-readable description of the workspace purpose.
        rag_config: RAG configuration for the workspace.
        
    Returns:
        The created Workspace object with ID and metadata.
        
    Raises:
        WorkspaceExistsError: If a workspace with the same name already exists.
        ValidationError: If the rag_config is invalid.
    """
    # Implementation...
```

### TypeScript (Frontend)

#### Code Style

**Formatting Tools**:
- **Prettier**: Code formatting
- **ESLint**: Code quality and React rules

**Configuration**:
```json
// .eslintrc.json
{
  "extends": [
    "@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "react/prop-types": "off"
  }
}
```

#### Component Patterns

**Typed Components**:
```typescript
// GOOD: Properly typed props
interface ChatMessageProps {
  message: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  onReply?: (message: string) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ 
  message, 
  role, 
  timestamp, 
  onReply 
}) => {
  return (
    <div className={`message ${role}`}>
      <div className="content">{message}</div>
      <div className="timestamp">{timestamp.toLocaleString()}</div>
      {onReply && (
        <button onClick={() => onReply(message)}>
          Reply
        </button>
      )}
    </div>
  );
};

// BAD: Untyped components
export const ChatMessage = ({ message, role, timestamp, onReply }) => {
  return <div>{message}</div>;  // No type safety!
};
```

**Custom Hooks**:
```typescript
// GOOD: Properly typed custom hook
interface UseChatReturn {
  messages: ChatMessage[];
  sendMessage: (content: string) => Promise<void>;
  isLoading: boolean;
}

export const useChat = (sessionId: string): UseChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const sendMessage = useCallback(async (content: string) => {
    setIsLoading(true);
    // Implementation...
    setIsLoading(false);
  }, [sessionId]);
  
  return { messages, sendMessage, isLoading };
};
```

#### State Management

**Redux Toolkit Pattern**:
```typescript
// GOOD: Properly typed Redux slice
interface ChatState {
  messages: ChatMessage[];
  activeSessionId: string | null;
  isLoading: boolean;
}

const initialState: ChatState = {
  messages: [],
  activeSessionId: null,
  isLoading: false,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload);
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
});

export const { addMessage, setLoading } = chatSlice.actions;
```

### General Standards

#### Character Encoding

**ASCII-Only Policy**:
- Use only ASCII characters in all code, comments, and documentation
- No emojis in code, commit messages, or documentation
- Use standard ASCII punctuation (-, ", ', etc.)
- Avoid special Unicode characters (smart quotes, em dashes)

**Examples**:
```python
# GOOD: ASCII only
# Run all quality checks (format, lint, type-check, test)
def check_code_quality():
    pass

# BAD: Contains emoji and special characters
# Run all quality checks [x] (format * lint * type-check * test)
def check_code_quality():  # [rocket]
    pass
```

#### Naming Conventions

**Python**:
- **Classes**: PascalCase (`VectorRag`, `DocumentService`)
- **Functions/Variables**: snake_case (`process_documents`, `user_id`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_CHUNK_SIZE`, `DEFAULT_TIMEOUT`)
- **Files**: snake_case (`document_service.py`, `vector_rag.py`)

**TypeScript**:
- **Components**: PascalCase (`ChatMessage`, `WorkspaceSelector`)
- **Functions/Variables**: camelCase (`processDocuments`, `userId`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_CHUNK_SIZE`, `DEFAULT_TIMEOUT`)
- **Files**: PascalCase for components (`ChatMessage.tsx`), camelCase for utilities (`apiClient.ts`)

---

## Testing Requirements

### Testing Philosophy

**Core Principles**:
1. **Test Isolation**: Each test should be independent
2. **Real over Mock**: Use dummy implementations instead of mocks when possible
3. **Fast Feedback**: Unit tests should execute in under 100ms
4. **Comprehensive Coverage**: Test happy paths, edge cases, and error conditions
5. **Maintainability**: Tests should be as maintainable as production code

### Python Testing

#### Unit Tests

**Location**: `packages/server/tests/unit/`

**Framework**: Pytest with dummy implementations

**Example Structure**:
```python
# tests/unit/test_document_service.py
import pytest
from src.domains.documents.service import DocumentService
from src.infrastructure.storage import InMemoryBlobStorage
from shared.types import Document

def test_document_service_create_document():
    """Test document creation with valid data."""
    # Arrange
    storage = InMemoryBlobStorage()
    service = DocumentService(storage=storage)
    
    document_data = {
        "filename": "test.pdf",
        "content": "Test content",
        "workspace_id": "test-workspace"
    }
    
    # Act
    result = service.create_document(document_data)
    
    # Assert
    assert isinstance(result, Document)
    assert result.filename == "test.pdf"
    assert result.workspace_id == "test-workspace"
```

#### Integration Tests

**Location**: `packages/server/tests/integration/`

**Framework**: Pytest with testcontainers

**Example Structure**:
```python
# tests/integration/test_document_endpoints.py
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.qdrant import QdrantContainer

@pytest.fixture(scope="function")
def postgres_container():
    """Spin up temporary PostgreSQL container."""
    with PostgresContainer("postgres:16") as container:
        yield container

def test_document_upload_integration(postgres_container):
    """Test document upload with real database."""
    # Use real services running in Docker
    # Test actual database operations
    pass
```

### TypeScript Testing

#### Unit Tests

**Location**: `packages/client/src/**/*.test.{ts,tsx}`

**Framework**: Vitest + React Testing Library + MSW

**Example Structure**:
```typescript
// src/components/ChatMessage.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatMessage } from './ChatMessage';

describe('ChatMessage', () => {
  test('renders user message correctly', () => {
    render(
      <ChatMessage 
        message="Hello world" 
        role="user" 
        timestamp={new Date()} 
      />
    );
    
    expect(screen.getByText('Hello world')).toBeInTheDocument();
    expect(screen.getByTestId('message-user')).toBeInTheDocument();
  });

  test('calls onReply when reply button is clicked', async () => {
    const onReplyMock = vi.fn();
    render(
      <ChatMessage 
        message="Hello" 
        role="assistant" 
        timestamp={new Date()}
        onReply={onReplyMock}
      />
    );
    
    const replyButton = screen.getByRole('button', { name: /reply/i });
    await userEvent.click(replyButton);
    
    expect(onReplyMock).toHaveBeenCalledWith('Hello');
  });
});
```

#### E2E Tests

**Location**: `packages/client/e2e/**/*.spec.ts`

**Framework**: Playwright

**Example Structure**:
```typescript
// e2e/chat/complete-flow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Chat Flow', () => {
  test('should send and receive messages', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Login
    await page.fill('[data-testid="username"]', 'testuser');
    await page.fill('[data-testid="password"]', 'password');
    await page.click('[data-testid="login-button"]');
    
    // Create workspace
    await page.click('[data-testid="create-workspace"]');
    await page.fill('[data-testid="workspace-name"]', 'Test Workspace');
    await page.click('[data-testid="create-button"]');
    
    // Send chat message
    await page.fill('[data-testid="chat-input"]', 'Hello, how are you?');
    await page.click('[data-testid="send-button"]');
    
    // Verify response
    await expect(page.locator('[data-testid="chat-response"]')).toBeVisible();
  });
});
```

### Coverage Requirements

**Minimum Coverage Thresholds**:
- **Lines**: > 80%
- **Functions**: > 80%
- **Branches**: > 75%
- **Statements**: > 80%

**Coverage Commands**:
```bash
# Python
cd packages/server
task test:coverage

# TypeScript
cd packages/client
task test:coverage
```

---

## Documentation Standards

### Documentation Structure

**File Organization**:
```
docs/
- planning/          # Project planning documents
- project-management/ # Project management docs
- rag/              # RAG system documentation
- architecture.md    # System architecture
- client-user-flows.md # User interaction flows
- project-structure.md # Code organization
- testing.md        # Testing guide
- docker.md         # Docker setup
- contributing.md    # This file
- changelog.md      # Project changelog
```

### Writing Guidelines

**Markdown Standards**:
- Use lowercase filenames (e.g., `testing.md`, not `Testing.md`)
- Include table of contents for longer documents
- Use 80-100 character line length
- Use proper markdown syntax for headers, lists, and code blocks

**Code Examples**:
- Include language tags for syntax highlighting
```python
# Python example
def example_function():
    pass
```

```typescript
// TypeScript example
const example = () => {
  // code
};
```

**Documentation Updates**:
Update documentation when you:
- Add new features or endpoints
- Change configuration options
- Modify architecture significantly
- Fix documented behavior
- Add new development workflows

---

## Pull Request Process

### Before Submitting

**Pre-Submission Checklist**:
1. **Install Task**: `sh -c "$(curl --location https://taskfile.dev/install.sh)"`
2. **Run Quality Checks**: `task check`
3. **Write Tests**: Ensure adequate test coverage
4. **Update Documentation**: Update relevant documentation
5. **Write Clear Commit Messages**: Follow conventional commit format

### Commit Message Format

**Conventional Commits**:
```
type(scope): brief description

Longer explanation if needed.

Fixes #issue-number
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic changes)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

**Examples**:
```
feat(chat): add message streaming support

Add real-time streaming for chat responses using WebSocket
connection. Messages now appear token-by-token as they're
generated by the LLM.

Fixes #123

fix(auth): resolve JWT token expiration issue

Update token refresh logic to handle expired tokens gracefully
and automatically request new tokens when needed.

Fixes #124
```

### Pull Request Template

**PR Description Structure**:
```markdown
## Description
Brief description of the change and its purpose.

## Type
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring
- [ ] Other

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Self-review completed
- [ ] CI checks pass
```

### Review Process

**Review Criteria**:
1. **Code Quality**: Follows all style and architecture guidelines
2. **Test Coverage**: Adequate tests for new functionality
3. **Documentation**: Updated and accurate
4. **Performance**: No significant performance regressions
5. **Security**: No security vulnerabilities introduced

**Review Workflow**:
1. **Automated Checks**: CI/CD pipeline validates code quality
2. **Peer Review**: At least one maintainer approval required
3. **Integration Testing**: Verify changes work in full system
4. **Documentation Review**: Ensure documentation is accurate

---

## Common Tasks

### Adding New RAG Component

1. **Create Interface**:
   ```python
   # src/infrastructure/rag/interfaces/new_component.py
   from abc import ABC, abstractmethod
   
   class NewComponent(ABC):
       @abstractmethod
       def process(self, data: Any) -> Any:
           pass
   ```

2. **Implement Concrete Class**:
   ```python
   # src/infrastructure/rag/implementations/concrete_new_component.py
   class ConcreteNewComponent(NewComponent):
       def process(self, data: Any) -> Any:
           # Implementation
           pass
   ```

3. **Add to Factory**:
   ```python
   # src/infrastructure/rag/factory.py
   def create_new_component(type: str) -> NewComponent:
       if type == "concrete":
           return ConcreteNewComponent()
       # Add other implementations
   ```

4. **Write Tests**:
   ```python
   # tests/unit/test_new_component.py
   def test_concrete_new_component():
       component = ConcreteNewComponent()
       result = component.process(test_data)
       assert result == expected_result
   ```

5. **Update Documentation**:
   - Update architecture documentation
   - Add usage examples
   - Update API documentation if applicable

### Adding New API Endpoint

1. **Define Route**:
   ```python
   # src/domains/your_domain/routes.py
   from flask import Blueprint, request, jsonify
   
   bp = Blueprint('your_domain', __name__)
   
   @bp.route('/your-endpoint', methods=['POST'])
   def your_endpoint():
       data = request.get_json()
       # Process data
       return jsonify(result)
   ```

2. **Implement Service Logic**:
   ```python
   # src/domains/your_domain/service.py
   class YourDomainService:
       def __init__(self, repository, other_deps):
           self.repository = repository
           self.other_deps = other_deps
       
       def process_endpoint_data(self, data):
           # Business logic
           return result
   ```

3. **Add Tests**:
   ```python
   # tests/unit/test_your_domain.py
   def test_your_endpoint():
       # Test endpoint logic
       pass
   ```

4. **Update API Documentation**:
   - Update OpenAPI specification
   - Add endpoint to API docs
   - Include request/response examples

### Adding New React Component

1. **Create Component**:
   ```typescript
   // src/components/your_component/YourComponent.tsx
   import React from 'react';
   
   interface YourComponentProps {
       title: string;
       onAction?: () => void;
   }
   
   export const YourComponent: React.FC<YourComponentProps> = ({ 
       title, 
       onAction 
   }) => {
       return (
           <div className="your-component">
               <h2>{title}</h2>
               {onAction && (
                   <button onClick={onAction}>
                       Action
                   </button>
               )}
           </div>
       );
   };
   ```

2. **Add Tests**:
   ```typescript
   // src/components/your_component/YourComponent.test.tsx
   import { render, screen } from '@testing-library/react';
   import { YourComponent } from './YourComponent';
   
   describe('YourComponent', () => {
       test('renders title correctly', () => {
           render(<YourComponent title="Test Title" />);
           expect(screen.getByText('Test Title')).toBeInTheDocument();
       });
   });
   ```

3. **Add Storybook Stories**:
   ```typescript
   // src/components/your_component/YourComponent.stories.tsx
   import type { Meta, StoryObj } from '@storybook/react';
   import { YourComponent } from './YourComponent';
   
   const meta: Meta<typeof YourComponent> = {
       title: 'Components/YourComponent',
       component: YourComponent,
   };
   
   export default meta;
   
   export const Default: StoryObj<typeof meta> = {
       args: {
           title: 'Default Title',
       },
   };
   ```

---

## Getting Help

### Resources

**Documentation**:
- Check `docs/` directory for comprehensive guides
- Review `CLAUDE.md` for architecture principles
- Read package-specific README files

**Code Examples**:
- Review similar implementations in the codebase
- Check test files for usage patterns
- Look at existing components for patterns

**Community**:
- **GitHub Issues**: Report bugs or ask questions
- **GitHub Discussions**: General questions and discussions
- **Code Reviews**: Learn from review comments on PRs

### Support Channels

**For Contributors**:
- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions and community discussion
- **Pull Request Reviews**: For code-specific questions

**For Users**:
- **Documentation**: Comprehensive guides in `docs/`
- **README.md**: Quick start and overview
- **Issues**: Bug reports and feature requests

### Development Tips

**Debugging**:
- Use IDE debugger for step-through debugging
- Add console.log statements for quick debugging
- Use browser dev tools for frontend debugging
- Check logs in Docker containers for backend issues

**Productivity**:
- Use Task commands instead of direct docker compose
- Configure your IDE with proper extensions
- Set up hot keys for common operations
- Use Git aliases for frequent commands

Thank you for contributing to InsightHub! Your contributions help make this dual RAG system better for everyone.