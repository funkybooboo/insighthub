# Task Setup Guide

Comprehensive guide to Task, the modern task runner used throughout InsightHub for build automation, development workflows, and deployment orchestration.

## Table of Contents

- [Installation](#installation)
- [Why Task over Make?](#why-task-over-make)
- [Project Structure](#project-structure)
- [Command Reference](#command-reference)
  - [Root Commands](#root-commands)
  - [Package Commands](#package-commands)
  - [Task Delegation](#task-delegation)
- [Taskfile Configuration](#taskfile-configuration)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Installation

### System Requirements

- **Operating Systems**: Linux, macOS, Windows
- **Go Runtime**: Go 1.17+ (automatically installed by Task)
- **Shell**: Bash, Zsh, PowerShell (Windows)

### Installation Methods

#### Method 1: Official Script (Recommended)

```bash
# Linux/macOS
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin

# Verify installation
task --version
```

#### Method 2: Package Managers

```bash
# macOS (Homebrew)
brew install go-task

# Windows (Scoop)
scoop install task

# Arch Linux
pacman -S go-task

# Nix/NixOS
nix-env -iA nixpkgs.go-task
```

#### Method 3: Go Install

```bash
# Install directly with Go
go install github.com/go-task/task/v3/cmd/task@latest

# Add to PATH (if needed)
export PATH=$PATH:$(go env GOPATH)/bin
```

### Verification

```bash
# Check Task version
task --version

# Show available tasks
task --list

# Get help
task --help
```

---

## Why Task over Make?

### Advantages of Task

| Feature | Task | Make |
|---------|-------|-------|
| **Syntax** | YAML (human-readable) | Makefile (complex syntax) |
| **Cross-Platform** | Native support | Requires workarounds |
| **Parallelism** | Built-in | Manual implementation |
| **Variables** | Rich variable system | Limited |
| **Conditionals** | Native support | Complex shell logic |
| **Error Handling** | Graceful error handling | Limited |
| **Dependencies** | Task dependencies | Phony targets |

### Key Benefits

1. **YAML Configuration**: Human-readable, no tab/space issues
2. **Cross-Platform**: Works consistently across all operating systems
3. **Built-in Features**: Parallel execution, variables, conditionals
4. **Task Dependencies**: Define task execution order
5. **Extensible**: Plugins and custom functions
6. **Modern Development**: Active development and community support

---

## Project Structure

### Taskfile Organization

```
insighthub/
- Taskfile.yml              # Root tasks (orchestration)
- .task/                   # Task configuration and includes
|   - includes/            # Shared task definitions
|   |   - docker.yml      # Docker-related tasks
|   |   - quality.yml     # Code quality tasks
|   |   - testing.yml     # Testing tasks
|   - Taskvars.yml        # Global variables
- packages/
    - server/
    |   - Taskfile.yml      # Server-specific tasks
    - client/
    |   - Taskfile.yml      # Client-specific tasks
    - cli/
    |   - Taskfile.yml      # CLI-specific tasks
    - workers/
        - Taskfile.yml      # Worker-specific tasks
```

### Include System

**Root Taskfile.yml**:
```yaml
# Include shared task definitions
includes:
  - docker
  - quality
  - testing
  - deployment

# Override variables
version: '3.0.0'
```

**Shared Task Files** (`.task/includes/`):

**docker.yml**:
```yaml
version: '3'

tasks:
  docker:build:
    desc: Build all Docker images
    cmds:
      - docker compose build
  
  docker:up:
    desc: Start all services
    cmds:
      - docker compose up -d
  
  docker:down:
    desc: Stop all services
    cmds:
      - docker compose down
```

**quality.yml**:
```yaml
version: '3'

tasks:
  check:
    desc: Run all quality checks
    deps:
      - lint
      - test
      - typecheck
  
  lint:
    desc: Run linting
    cmds:
      - task:server:lint
      - task:client:lint
  
  format:
    desc: Format all code
    cmds:
      - task:server:format
      - task:client:format
```

---

## Command Reference

### Root Commands

From project root directory (`insighthub/`):

#### Service Management

```bash
# Start production environment
task up
# Equivalent to: docker compose up -d

# Start development environment
task up-dev
# Equivalent to: docker compose -f docker-compose.dev.yml -f docker-compose.yml up -d

# Start infrastructure only
task up-infra
# Equivalent to: docker compose -f docker-compose.yml up -d postgres qdrant minio ollama rabbitmq

# Stop all services
task down
# Equivalent to: docker compose down

# Restart services
task restart
# Equivalent to: task down && task up

# View service status
task ps
# Equivalent to: docker compose ps
```

#### Building and Deployment

```bash
# Build production images
task build
# Builds all Docker images with production optimizations

# Build development images
task build-dev
# Builds all Docker images with development tools

# Deploy to production
task deploy
# Runs production build and deployment sequence
```

#### Development

```bash
# Start local development
task dev
# Starts server locally + infrastructure in containers

# Start server locally
task dev-server
# Equivalent to: cd packages/server && poetry run python -m src.api

# Start client locally
task dev-client
# Equivalent to: cd packages/client && bun run dev
```

#### Quality Assurance

```bash
# Run all quality checks
task check
# Runs: linting, type checking, testing, build verification

# Format all code
task format
# Runs: server formatting + client formatting

# Lint all code
task lint
# Runs: server linting + client linting

# Type check all code
task typecheck
# Runs: server type checking + client type checking

# Test all code
task test
# Runs: server tests + client tests
```

#### Monitoring and Logs

```bash
# View all service logs
task logs

# View specific service logs
task logs-server
task logs-client
task logs-postgres
task logs-qdrant

# Follow logs in real-time
task logs:follow
```

#### Cleanup

```bash
# Clean generated files
task clean
# Removes: build artifacts, temporary files, cache

# Deep clean
task clean:all
# Removes: containers, volumes, images, build artifacts

# Clean Docker resources
task clean:docker
# Removes: stopped containers, unused images, dangling volumes
```

### Package Commands

#### Server Tasks (`packages/server/Taskfile.yml`)

```bash
cd packages/server

# Install dependencies
task install
# Equivalent to: poetry install

# Start development server
task server
# Equivalent to: poetry run python -m src.api

# Start production server
task server:prod
# Equivalent to: poetry run gunicorn src.api:app

# Run tests
task test
# Equivalent to: poetry run pytest tests/ -v --cov=src

# Run unit tests only
task test:unit
# Equivalent to: poetry run pytest tests/unit/ -v

# Run integration tests only
task test:integration
# Equivalent to: poetry run pytest tests/integration/ -v

# Format code
task format
# Equivalent to: poetry run black src tests && poetry run isort src tests

# Lint code
task lint
# Equivalent to: poetry run ruff check src tests

# Type check
task typecheck
# Equivalent to: poetry run mypy src tests

# Run all quality checks
task check
# Runs: format, lint, typecheck, test

# Database operations
task db:migrate
# Equivalent to: poetry run python migrations/migrate.py

task db:reset
# Equivalent to: poetry run python migrations/migrate.py --reset

# API testing
task test:api
# Equivalent to: bru run --env local bruno/
```

#### Client Tasks (`packages/client/Taskfile.yml`)

```bash
cd packages/client

# Install dependencies
task install
# Equivalent to: bun install

# Start development server
task dev
# Equivalent to: bun run dev

# Build for production
task build
# Equivalent to: bun run build

# Preview production build
task preview
# Equivalent to: bun run preview

# Run tests
task test
# Equivalent to: bun run test

# Run tests in watch mode
task test:watch
# Equivalent to: bun run test

# Run tests with coverage
task test:coverage
# Equivalent to: bun run test:coverage

# Run tests with UI
task test:ui
# Equivalent to: bun run test:ui

# Format code
task format
# Equivalent to: bun run format

# Lint code
task lint
# Equivalent to: bun run lint

# Type check
task typecheck
# Equivalent to: bun run tsc --noEmit

# Run Storybook
task storybook
# Equivalent to: bun run storybook

# Build Storybook
task storybook:build
# Equivalent to: bun run storybook:build

# Run all quality checks
task check
# Runs: format, lint, typecheck, test, build

# Security audit
task audit
# Equivalent to: bun audit

# Security scan
task scan
# Equivalent to: bun run trivy fs .
```

#### CLI Tasks (`packages/cli/Taskfile.yml`)

```bash
cd packages/cli

# Install dependencies
task install
# Equivalent to: bun install

# Run CLI
task cli
# Equivalent to: bun run index.ts

# Build CLI
task build
# Equivalent to: bun run build

# Test CLI
task test
# Equivalent to: bun run test

# Check CLI
task check
# Runs: format, lint, typecheck, test
```

#### Worker Tasks (`packages/workers/*/Taskfile.yml`)

```bash
cd packages/workers/{worker}

# Install dependencies
task install
# Equivalent to: poetry install

# Start worker
task start
# Equivalent to: poetry run python -m src.main

# Build worker image
task build
# Equivalent to: docker build -t insighthub-{worker} .

# Test worker
task test
# Equivalent to: poetry run pytest tests/ -v
```

### Task Delegation

Run package-specific tasks from project root:

```bash
# Run server tests from root
task server:test

# Run client build from root
task client:build

# Run server formatting from root
task server:format

# Run client linting from root
task client:lint

# Multiple package tasks
task server:check && client:check

# Parallel execution
task -p server:test client:test
```

---

## Taskfile Configuration

### Root Taskfile.yml

```yaml
# Task version
version: '3'

# Global variables
vars:
  PROJECT_NAME: InsightHub
  VERSION: '1.0.0'
  DOCKER_REGISTRY: insighthub
  
# Environment-specific variables
env:
  DEVELOPMENT:
    COMPOSE_FILE: docker-compose.dev.yml
  PRODUCTION:
    COMPOSE_FILE: docker-compose.yml

# Task output formatting
output:
  group:
    begin: "::group::{{.TASK}}"
    end: "::endgroup::{{.TASK}}"

# Include shared task files
includes:
  - docker
  - quality
  - testing
  - deployment

# Default task
default:
  - help

# Task definitions
tasks:
  help:
    desc: Show available tasks
    cmds:
      - task --list

  up:
    desc: Start production environment
    summary: |
      Starts InsightHub production environment with:
      - Production Docker images
      - Optimized configuration
      - ELK monitoring
    cmds:
      - task build
      - docker compose -f {{.COMPOSE_FILE}} up -d

  up-dev:
    desc: Start development environment
    summary: |
      Starts InsightHub development environment with:
      - Development Docker images
      - Hot reload enabled
      - Debug logging
    cmds:
      - task build-dev
      - docker compose -f docker-compose.dev.yml -f docker-compose.yml up -d

  check:
    desc: Run all quality checks
    deps:
      - format
      - lint
      - typecheck
      - test
      - build
    summary: |
      Runs complete quality assurance pipeline:
      - Code formatting
      - Linting and type checking
      - Unit and integration testing
      - Build verification
```

### Package Taskfile.yml

**Server Example** (`packages/server/Taskfile.yml`):

```yaml
version: '3'

# Package-specific variables
vars:
  PACKAGE: server
  PYTHON_VERSION: '3.11'
  POETRY_VERSION: '1.7.1'

# Environment setup
set:
  - .env.local
  - .env.test

# Tasks
tasks:
  install:
    desc: Install Python dependencies
    summary: |
      Installs dependencies using Poetry:
      - Python {{.PYTHON_VERSION}}
      - Production and development dependencies
    cmds:
      - poetry install
      - poetry install --with dev

  server:
    desc: Start Flask development server
    env:
      FLASK_ENV: development
      FLASK_DEBUG: '1'
    cmds:
      - poetry run python -m src.api

  test:
    desc: Run Python tests
    summary: |
      Runs comprehensive test suite:
      - Unit tests with dummy implementations
      - Integration tests with testcontainers
      - Coverage reporting
    cmds:
      - poetry run pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

  check:
    desc: Run all quality checks
    deps:
      - format
      - lint
      - typecheck
      - test
    cmds:
      - echo "[x] All checks completed successfully"
```

**Client Example** (`packages/client/Taskfile.yml`):

```yaml
version: '3'

# Package-specific variables
vars:
  PACKAGE: client
  NODE_VERSION: '18'
  BUN_VERSION: '1.0.0'

# Tasks
tasks:
  install:
    desc: Install Node.js dependencies
    summary: |
      Installs dependencies using Bun:
      - Node.js {{.NODE_VERSION}} compatible
      - Production and development dependencies
    cmds:
      - bun install

  dev:
    desc: Start Vite development server
    env:
      NODE_ENV: development
    cmds:
      - bun run dev

  build:
    desc: Build for production
    summary: |
      Builds optimized production bundle:
      - TypeScript compilation
      - Asset optimization
      - Source map generation
    cmds:
      - bun run build

  test:
    desc: Run TypeScript tests
    summary: |
      Runs comprehensive test suite:
      - Unit tests with Vitest
      - Component tests with React Testing Library
      - Coverage reporting
    cmds:
      - bun run test

  check:
    desc: Run all quality checks
    deps:
      - format
      - lint
      - typecheck
      - test
      - build
    cmds:
      - echo "[x] All checks completed successfully"
```

---

## Advanced Features

### Task Variables

#### Global Variables

```yaml
# Taskfile.yml
vars:
  PROJECT_NAME: InsightHub
  VERSION: '1.0.0'
  DOCKER_REGISTRY: insighthub
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'

tasks:
  build:
    desc: Build {{.PROJECT_NAME}} v{{.VERSION}}
    cmds:
      - echo "Building {{.PROJECT_NAME}} version {{.VERSION}}"
      - docker build -t {{.DOCKER_REGISTRY}}/{{.PROJECT_NAME}}:{{.VERSION}} .
```

#### Environment Variables

```yaml
# Taskfile.yml
env:
  DEVELOPMENT:
    LOG_LEVEL: debug
    BUILD_TYPE: debug
  PRODUCTION:
    LOG_LEVEL: info
    BUILD_TYPE: release

tasks:
  deploy:
    desc: Deploy to {{.BUILD_TYPE}} environment
    cmds:
      - echo "Deploying with log level: {{.LOG_LEVEL}}"
```

#### Dynamic Variables

```yaml
# Taskfile.yml
vars:
  TIMESTAMP: "{{.NOW | date \"20060102\"}}"
  GIT_COMMIT: "{{.GIT_COMMIT}}"

tasks:
  build:
    desc: Build with timestamp and commit
    cmds:
      - echo "Building at {{.TIMESTAMP}} from commit {{.GIT_COMMIT}}"
```

### Task Dependencies

#### Sequential Dependencies

```yaml
tasks:
  deploy:
    desc: Deploy application
    deps:
      - build
      - test
      - security-scan
    cmds:
      - echo "Deployment completed"
```

#### Parallel Dependencies

```yaml
tasks:
  test-all:
    desc: Run all tests in parallel
    deps:
      - test:unit
      - test:integration
      - test:e2e
    cmds:
      - echo "All tests completed"
```

### Conditional Tasks

```yaml
tasks:
  test:
    desc: Run tests based on environment
    cmds:
      - task: test:unit
      - cmd: task: test:integration
        when: { eq: .ENV "development" }
```

### Custom Functions

```yaml
# Taskfile.yml
functions:
  notify:
    desc: Send notification
    params:
      message:
        type: string
    cmds:
      - echo "[notify] {{.message}}"
      - curl -X POST "https://hooks.slack.com/..." -d "text={{.message}}"

tasks:
  deploy:
    desc: Deploy with notification
    cmds:
      - task: deploy:actual
      - task: notify: { message: "Deployment completed!" }
```

---

## Best Practices

### Task Organization

1. **Logical Grouping**: Group related tasks together
2. **Clear Descriptions**: Use `desc` field for task documentation
3. **Consistent Naming**: Use consistent naming conventions
4. **Dependency Management**: Use `deps` for task ordering
5. **Variable Usage**: Use variables for reusable values

### Task Naming

```yaml
# Good naming conventions
tasks:
  build:              # Simple, clear
  build:prod:         # Environment-specific
  build:dev:          # Environment-specific
  test:unit:          # Test type-specific
  test:integration:    # Test type-specific
  docker:up:          # Domain-specific
  docker:build:        # Domain-specific
```

### Documentation

```yaml
# Comprehensive task documentation
tasks:
  deploy:
    desc: Deploy application to production
    summary: |
      Deploys InsightHub with the following steps:
      1. Builds production Docker images
      2. Runs security scans
      3. Pushes to registry
      4. Updates Kubernetes deployment
    vars:
      ENVIRONMENT: production
      REGISTRY: docker.io/insighthub
    cmds:
      - echo "Deploying to {{.ENVIRONMENT}} environment"
      - task: build
      - task: security:scan
      - task: docker:push
      - task: k8s:deploy
```

### Error Handling

```yaml
tasks:
  deploy:
    desc: Deploy with error handling
    cmds:
      - task: pre-deploy-check
      - task: deploy:actual || { task: rollback; exit 1; }
      - task: post-deploy-verify
    preconditions:
      - sh: test -f ".env.production"
        msg: "Production environment file not found"
```

---

## Troubleshooting

### Common Issues

#### Task Not Found

```bash
# Verify Task installation
which task
task --version

# Reinstall if needed
curl -sL https://taskfile.dev/install.sh | sh
```

#### Taskfile Syntax Errors

```bash
# Validate Taskfile syntax
task --dry-run

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('Taskfile.yml'))"
```

#### Variable Not Expanding

```bash
# Debug variable expansion
task --list
task --help <task-name>

# Check variable scope
task vars
```

#### Permission Issues

```bash
# Make Task executable (Linux/macOS)
chmod +x /usr/local/bin/task

# Check PATH
echo $PATH | grep -o "/usr/local/bin"
```

#### Performance Issues

```bash
# Run tasks in parallel where possible
task -p task1 task2 task3

# Use task-specific caching
task --dry-run  # Check what will be executed
```

### Debug Mode

```bash
# Enable verbose output
task --verbose <task-name>

# Run in dry-run mode
task --dry-run <task-name>

# Show task expansion
task --list --json
```

### Getting Help

```bash
# General help
task --help

# Task-specific help
task --help <task-name>

# List all tasks
task --list

# List tasks with details
task --list --json
```

### Configuration Issues

```bash
# Check Task configuration
task --version
task --help

# Reset Task configuration
rm -rf ~/.task/
```

This comprehensive Task setup provides a robust foundation for build automation, development workflows, and deployment orchestration throughout the InsightHub project.