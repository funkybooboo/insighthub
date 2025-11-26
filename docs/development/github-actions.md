# GitHub Actions

Comprehensive CI/CD workflows and local testing setup for InsightHub dual RAG system using GitHub Actions and act for local development.

## Table of Contents

- [Overview](#overview)
- [Workflows](#workflows)
  - [Client CI](#client-ci)
  - [Server CI](#server-ci)
  - [TODO to Issue](#todo-to-issue)
- [Local Testing with act](#local-testing-with-act)
  - [Installation](#installation)
  - [Setup](#setup)
  - [Usage](#usage)
- [Workflow Configuration](#workflow-configuration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

InsightHub uses GitHub Actions for automated CI/CD with separate workflows for client and server packages. The CI ensures code quality, testing, and proper formatting across the monorepo.

### CI/CD Strategy

**Branch Protection**:
- Main branch requires passing CI checks
- PRs must pass all required status checks
- Required checks: format, lint, test, build

**Workflow Structure**:
- **Client CI**: Frontend testing, linting, and building
- **Server CI**: Backend testing, type checking, and security scanning
- **TODO to Issue**: Auto-creates GitHub issues from code TODO comments

**Matrix Builds**:
- Multiple Node.js versions for client
- Multiple Python versions for server
- Different operating systems for critical workflows

---

## Workflows

### Client CI

**Trigger**: Push/PR affecting `packages/client/` or client-related files

**Jobs**:
1. **Setup**:
   - Checkout code
   - Setup Node.js 18+
   - Install Bun
   - Cache dependencies

2. **Quality**:
   - Run ESLint
   - Check Prettier formatting
   - TypeScript type checking

3. **Testing**:
   - Run Vitest unit tests
   - Generate coverage reports
   - Run component tests

4. **Build**:
   - Build production bundle
   - Check bundle size
   - Upload build artifacts

**Configuration**:
```yaml
# .github/workflows/client-ci.yml
name: Client CI
on:
  push:
    paths:
      - 'packages/client/**'
      - '.github/workflows/client-ci.yml'
  pull_request:
    paths:
      - 'packages/client/**'
```

**Jobs Overview**:

#### Setup Job

```yaml
jobs:
  setup:
    name: Setup
    runs-on: ubuntu-latest
    outputs:
      node-version: ${{ steps.setup-node.outputs.node-version }}
      cache-key: ${{ steps.setup-node.outputs.cache-key }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        id: setup-node
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: |
            packages/client/package-lock.json
            packages/client/node_modules
```

#### Quality Checks

```yaml
  format:
    name: Format Check
    runs-on: ubuntu-latest
    needs: setup
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ needs.setup.outputs.node-version }}
          cache: 'npm'
          
      - name: Install dependencies
        run: |
          cd packages/client
          bun install --frozen-lockfile
          
      - name: Check formatting
        run: |
          cd packages/client
          bun run format-check

  lint:
    name: Lint Check
    runs-on: ubuntu-latest
    needs: setup
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ needs.setup.outputs.node-version }}
          cache: 'npm'
          
      - name: Install dependencies
        run: |
          cd packages/client
          bun install --frozen-lockfile
          
      - name: Run ESLint
        run: |
          cd packages/client
          bun run lint
```

#### Testing

```yaml
  test:
    name: Test
    runs-on: ubuntu-latest
    needs: setup
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ needs.setup.outputs.node-version }}
          cache: 'npm'
          
      - name: Install dependencies
        run: |
          cd packages/client
          bun install --frozen-lockfile
          
      - name: Run tests
        run: |
          cd packages/client
          bun run test:coverage
          
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./packages/client/coverage/lcov.info
          flags: client
          name: client-coverage
```

#### Build

```yaml
  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [setup, format, lint]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ needs.setup.outputs.node-version }}
          cache: 'npm'
          
      - name: Install dependencies
        run: |
          cd packages/client
          bun install --frozen-lockfile
          
      - name: Build application
        run: |
          cd packages/client
          bun run build
          
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: client-build
          path: packages/client/dist/
          retention-days: 7
```

### Server CI

**Trigger**: Push/PR affecting `packages/server/` or server-related files

**Jobs**:
1. **Setup**:
   - Checkout code
   - Setup Python 3.11+
   - Install Poetry
   - Cache dependencies

2. **Quality**:
   - Run Ruff linting
   - Check Black formatting
   - Run MyPy type checking

3. **Testing**:
   - Run Pytest unit tests (with dummy implementations)
   - Run integration tests (with testcontainers)
   - Generate coverage reports

4. **Security**:
   - Run security scanning
   - Check dependencies for vulnerabilities

5. **Build**:
   - Build Docker image
   - Run basic container tests

**Configuration**:
```yaml
# .github/workflows/server-ci.yml
name: Server CI
on:
  push:
    paths:
      - 'packages/server/**'
      - 'packages/shared/python/**'
      - '.github/workflows/server-ci.yml'
  pull_request:
    paths:
      - 'packages/server/**'
      - 'packages/shared/python/**'
```

**Jobs Overview**:

#### Setup Job

```yaml
jobs:
  setup:
    name: Setup
    runs-on: ubuntu-latest
    outputs:
      python-version: ${{ steps.setup-python.outputs.python-version }}
      cache-key: ${{ steps.setup-python.outputs.cache-key }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Python
        id: setup-python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
          cache-dependency-path: |
            packages/server/poetry.lock
            packages/server/.venv
```

#### Quality Checks

```yaml
  format:
    name: Format Check
    runs-on: ubuntu-latest
    needs: setup
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ needs.setup.outputs.python-version }}
          cache: 'pip'
          
      - name: Install Poetry
        run: |
          pip install poetry
          
      - name: Install dependencies
        run: |
          cd packages/server
          poetry install --no-dev
          
      - name: Check formatting
        run: |
          cd packages/server
          poetry run black --check src tests
          poetry run isort --check-only src tests

  lint:
    name: Lint Check
    runs-on: ubuntu-latest
    needs: setup
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ needs.setup.outputs.python-version }}
          cache: 'pip'
          
      - name: Install Poetry
        run: |
          pip install poetry
          
      - name: Install dependencies
        run: |
          cd packages/server
          poetry install --no-dev
          
      - name: Run Ruff
        run: |
          cd packages/server
          poetry run ruff check src tests

  typecheck:
    name: Type Check
    runs-on: ubuntu-latest
    needs: setup
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ needs.setup.outputs.python-version }}
          cache: 'pip'
          
      - name: Install Poetry
        run: |
          pip install poetry
          
      - name: Install dependencies
        run: |
          cd packages/server
          poetry install --no-dev
          
      - name: Run MyPy
        run: |
          cd packages/server
          poetry run mypy src tests
```

#### Testing

```yaml
  test:
    name: Test
    runs-on: ubuntu-latest
    needs: setup
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
          
      - name: Install Poetry
        run: |
          pip install poetry
          
      - name: Install dependencies
        run: |
          cd packages/server
          poetry install --no-dev
          
      - name: Run tests
        run: |
          cd packages/server
          poetry run pytest tests/ -v --cov=src --cov-report=xml --cov-report=html
          
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./packages/server/coverage.xml
          flags: server-py${{ matrix.python-version }}
          name: server-py${{ matrix.python-version }}-coverage
```

#### Security Scanning

```yaml
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: setup
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ needs.setup.outputs.python-version }}
          cache: 'pip'
          
      - name: Install Poetry
        run: |
          pip install poetry
          
      - name: Install dependencies
        run: |
          cd packages/server
          poetry install --no-dev
          
      - name: Run Bandit security scan
        run: |
          cd packages/server
          poetry run bandit -r src -f json -o bandit-report.json
          
      - name: Run pip-audit
        run: |
          cd packages/server
          poetry run pip-audit --format=json --output=pip-audit-report.json
          
      - name: Upload security reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            packages/server/bandit-report.json
            packages/server/pip-audit-report.json
```

### TODO to Issue

**File**: `.github/workflows/todo-to-issue.yml`

**Purpose**: Automatically create GitHub issues from TODO comments in code.

**Configuration**:
```yaml
name: TODO to Issue

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  todo-to-issue:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Find TODOs and create issues
        uses: alstr/todo-to-issue-action@v4
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          issue-label: "todo"
          auto-close: true
```

**Supported TODO Formats**:
```typescript
// TODO: Add authentication to this endpoint
// TODO(username): Refactor this component
// TODO: [P1] Fix critical bug in query handling
// TODO: [P2] Improve error messages
// TODO: [bug] Investigate memory leak
// TODO: [enhancement] Add dark mode support
```

---

## Local Testing with act

[act](https://github.com/nektos/act) runs GitHub Actions workflows locally in Docker, enabling fast feedback without pushing to GitHub.

### Installation

#### Linux/macOS

```bash
# Install latest version
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Or using Homebrew
brew install act

# Or using Go
go install github.com/nektos/act@latest

# Verify installation
act --version
```

#### Windows

```bash
# Using Scoop
scoop install act

# Or using Chocolatey
choco install act-cli

# Or using Go
go install github.com/nektos/act@latest
```

### Setup

#### 1. Create Secrets File

Create `.secrets` file in project root:

```bash
# Create secrets file
cat > .secrets << EOF
GITHUB_TOKEN=ghp_your_personal_access_token_here
EOF

# Make file readable only to owner
chmod 600 .secrets

# Add to .gitignore
echo ".secrets" >> .gitignore
```

#### 2. Configure Environment

```bash
# Create act environment file
cat > .actrc << EOF
-P ubuntu-latest=catthehacker/ubuntu:act-latest
-P ubuntu-22.04=catthehacker/ubuntu:ubuntu-22.04
-b
-v
EOF
```

### Usage

#### Basic Commands

```bash
# Run all workflows
act

# Run specific workflow
act -W .github/workflows/client-ci.yml

# Run specific job
act -j client-ci -j format

# Run with specific platform
act -P ubuntu-latest

# List available workflows
act -l

# Dry run (show what would be executed)
act -n

# Verbose output
act -v

# Run with artifact collection
act --artifact-server-path /tmp/artifacts
```

#### Advanced Usage

```bash
# Run specific event
act -e push

# Run with custom environment variables
act -e MY_VAR=value

# Run with matrix selection
act -j test -m python-version=3.11

# Run with container reuse
act --reuse

# Run with specific directory
act -W .github/workflows/client-ci.yml -C packages/client
```

### Workflow-Specific Examples

#### Client Workflow

```bash
# Run client format check
act -W .github/workflows/client-ci.yml -j format

# Run client tests
act -W .github/workflows/client-ci.yml -j test

# Run client build
act -W .github/workflows/client-ci.yml -j build

# Run with artifacts
act -W .github/workflows/client-ci.yml --artifact-server-path /tmp/client-artifacts
```

#### Server Workflow

```bash
# Run server format check
act -W .github/workflows/server-ci.yml -j format

# Run server linting
act -W .github/workflows/server-ci.yml -j lint

# Run server type checking
act -W .github/workflows/server-ci.yml -j typecheck

# Run server tests
act -W .github/workflows/server-ci.yml -j test

# Run security scan
act -W .github/workflows/server-ci.yml -j security
```

---

## Workflow Configuration

### Workflow Syntax

#### Basic Structure

```yaml
name: Workflow Name

on:
  push:
    branches: [main, develop]
    paths: ['packages/**']
  pull_request:
    branches: [main]

env:
  GLOBAL_VAR: value

jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - name: Step name
        uses: actions/checkout@v4
```

#### Triggers

**Push Events**:
```yaml
on:
  push:
    branches: [main, develop]
    tags: ['v*']
    paths:
      - 'packages/client/**'
      - 'packages/server/**'
      - 'Taskfile.yml'
```

**Pull Request Events**:
```yaml
on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
```

**Scheduled Events**:
```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
    - cron: '0 6 * * 1'  # Weekly on Monday at 6 AM UTC
```

#### Job Configuration

**Runner Selection**:
```yaml
jobs:
  job-name:
    runs-on: ubuntu-latest
    # Alternative runners
    # runs-on: ubuntu-22.04
    # runs-on: windows-latest
    # runs-on: macos-latest
```

**Matrix Strategy**:
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16, 18, 20]
        python-version: [3.11, 3.12]
        os: [ubuntu-latest, windows-latest]
      fail-fast: false
```

**Conditional Execution**:
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

### Caching

#### Node.js Dependencies

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'npm'
    cache-dependency-path: |
      package-lock.json
      node_modules
```

#### Python Dependencies

```yaml
- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'
    cache-dependency-path: |
      poetry.lock
      .venv
```

#### Custom Caching

```yaml
- name: Cache custom data
  uses: actions/cache@v3
  with:
    path: |
      ~/.cache/pip
      ~/.cache/pypoetry
    key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### Artifacts

#### Upload Artifacts

```yaml
- name: Upload build artifacts
  uses: actions/upload-artifact@v3
  with:
    name: build-artifacts
    path: |
      dist/
      coverage/
    retention-days: 30
    if-no-files-found: warn
```

#### Download Artifacts

```yaml
- name: Download artifacts
  uses: actions/download-artifact@v3
  with:
    name: build-artifacts
    path: dist/
```

### Secrets Management

#### Using Secrets

```yaml
- name: Use secret
  env:
    API_TOKEN: ${{ secrets.API_TOKEN }}
  run: |
    echo "Using token for API access"
```

#### Required Secrets

```yaml
- name: Check required secrets
  run: |
    if [ -z "${{ secrets.REQUIRED_SECRET }}" ]; then
      echo "Required secret not set"
      exit 1
    fi
```

---

## Best Practices

### Workflow Design

1. **Fast Feedback**: Prioritize quick checks first (format, lint)
2. **Parallel Execution**: Run independent jobs in parallel
3. **Fail Fast**: Use `fail-fast: true` for test matrices
4. **Resource Efficiency**: Use appropriate runner sizes
5. **Caching**: Implement comprehensive caching strategy

### Security

1. **Pin Actions**: Use specific versions of GitHub Actions
2. **Review Actions**: Use actions from reputable organizations
3. **Limit Permissions**: Use minimum required permissions
4. **Secret Management**: Never log or expose secrets
5. **Dependency Scanning**: Regular security audits

### Performance

1. **Conditional Jobs**: Skip unnecessary jobs based on file changes
2. **Matrix Optimization**: Use matrix only when necessary
3. **Cache Strategy**: Cache dependencies and build artifacts
4. **Runner Selection**: Use appropriate runners for workloads
5. **Timeout Management**: Set reasonable timeouts for jobs

### Maintainability

1. **Reusable Workflows**: Use composite actions for common patterns
2. **Documentation**: Document workflow purposes and configurations
3. **Version Control**: Version workflow files and configurations
4. **Testing**: Test workflows locally with act
5. **Monitoring**: Monitor workflow performance and success rates

---

## Troubleshooting

### Common Issues

#### "Permission denied" Errors

```bash
# Check file permissions
ls -la .github/workflows/

# Fix permissions
chmod 644 .github/workflows/*.yml
```

#### "Cache not found" Warnings

```bash
# Clear act cache
act --rm-cache

# Rebuild with fresh cache
act --pull
```

#### "Action not found" Errors

```bash
# Check action versions
grep -r "uses:" .github/workflows/

# Update to specific versions
# Use actions/checkout@v4 instead of actions/checkout
```

#### "Out of memory" Errors

```bash
# Increase Docker memory
export DOCKER_OPTS="--memory=8g"

# Use smaller matrix
# Reduce parallel jobs
```

#### "Secret not found" Errors

```bash
# Check secrets file
cat .secrets

# Verify token permissions
gh auth status

# Regenerate token if needed
gh auth refresh
```

### Debug Mode

#### Verbose Output

```bash
# Enable verbose logging
act -v

# Show environment variables
act --list

# Dry run to check steps
act -n
```

#### Local Debugging

```bash
# Run specific step interactively
act -j job-name -s step-name

# Keep containers for debugging
act --bind

# Execute shell in container
act exec bash
```

### Performance Issues

#### Optimize act Performance

```bash
# Use local Docker images
act -P ubuntu-latest=local:ubuntu-latest

# Reuse containers
act --reuse

# Limit parallelism
act -p 2

# Use artifact server
act --artifact-server-path /tmp/artifacts
```

#### Network Issues

```bash
# Check Docker daemon
docker info

# Restart Docker service
sudo systemctl restart docker

# Check firewall settings
sudo ufw status
```

This comprehensive GitHub Actions setup ensures reliable CI/CD pipelines for the InsightHub dual RAG system, with both automated cloud execution and local development capabilities.