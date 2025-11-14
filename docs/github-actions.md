# GitHub Actions

CI/CD workflows and local testing with `act`.

## Workflows

### Client CI
**File**: `.github/workflows/client-ci.yml`

Runs on push/PR affecting `packages/client/` or root `Taskfile.yml`:
- Install Task runner
- Format check (Prettier)
- Lint (ESLint)
- TypeScript compilation and build
- Unit tests

All checks use Task commands.

### Server CI
**File**: `.github/workflows/server-ci.yml`

Runs on push/PR affecting `packages/server/` or root `Taskfile.yml`:
- Install Task runner
- Format check (Black)
- Lint (Ruff)
- Type check (mypy strict)
- Unit and integration tests
- Code coverage (Codecov)

All checks use Task commands.

### TODO to Issue
**File**: `.github/workflows/todo-to-issue.yml`

Automatically creates GitHub issues from TODO comments:
```typescript
// TODO: Add authentication
// TODO(username): Refactor component
// TODO: [P1] Fix critical bug
```

Issues auto-assigned to commit authors, closed when TODOs removed.

## Local Testing with act

[act](https://github.com/nektos/act) runs GitHub Actions locally in Docker.

### Installation

```bash
# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# macOS
brew install act

# Windows
choco install act-cli
```

### Setup

1. Create `.secrets` file (gitignored):
   ```bash
   cp .secrets.example .secrets
   ```

2. Add GitHub token:
   ```
   GITHUB_TOKEN=ghp_your_token_here
   ```

   Create token at: GitHub Settings > Developer settings > Personal access tokens
   Required scope: `repo`

### Usage

```bash
# Run all workflows
act

# Specific workflow
act -W .github/workflows/client-ci.yml

# Specific job
act -j client-ci

# List workflows
act -l

# Dry run
act -n
```

### Troubleshooting

**"Bad credentials" error**: Create `.secrets` file with valid `GITHUB_TOKEN` (needs `repo` scope)

**Slow execution**: First run downloads Docker images. Server CI installs PyTorch with CUDA (5-10 min)

**Disk space**: Clean up with `docker system prune -a`

## Best Practices

- All checks must pass before merging
- Main branch is protected, requires status checks
- Run locally before pushing:
  ```bash
  task format  # Format code
  task lint    # Run linter
  task test    # Run tests
  task check   # All checks
  ```
