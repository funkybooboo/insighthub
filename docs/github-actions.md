# GitHub Actions

This document explains the GitHub Actions workflows in this project and how to run them locally using `act`.

## Workflows

### Client CI (.github/workflows/client-ci.yml)

Runs on every push/PR affecting `packages/client/`:
- Formatting check with Prettier
- Linting with ESLint
- TypeScript compilation and production build
- Unit tests with Bun

### Server CI (.github/workflows/server-ci.yml)

Runs on every push/PR affecting `packages/server/`:
- Code formatting check with Black
- Linting with Ruff
- Type checking with mypy (strict mode)
- Unit and integration tests with pytest
- Code coverage reporting with Codecov

### TODO to Issue (.github/workflows/todo-to-issue.yml)

Automatically creates GitHub issues from TODO comments in code:
```typescript
// TODO: Add authentication to this endpoint
// TODO(username): Refactor this component
// TODO: [P1] Fix critical bug in query handling
```

Issues are auto-assigned to commit authors and closed when TODOs are removed.

## Running Workflows Locally with act

[act](https://github.com/nektos/act) allows you to run GitHub Actions workflows locally in Docker containers.

### Installation

```bash
# On Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# On macOS
brew install act

# On Windows
choco install act-cli
```

### Setup

1. Create a `.secrets` file in the project root (this file is gitignored):
   ```bash
   cp .secrets.example .secrets
   ```

2. Edit `.secrets` and add your GitHub personal access token:
   ```
   GITHUB_TOKEN=ghp_your_token_here
   ```

   To create a GitHub personal access token:
   - Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control of private repositories)
   - Copy the token and paste it into `.secrets`

### Usage

Run all workflows:
```bash
act
```

Run a specific workflow:
```bash
act -W .github/workflows/client-ci.yml
```

Run a specific job:
```bash
act -j client-ci
```

List available workflows:
```bash
act -l
```

Dry run (don't execute, just show what would run):
```bash
act -n
```

### Troubleshooting

#### TODO to Issue workflow fails with "Bad credentials"

Make sure you have created the `.secrets` file with a valid `GITHUB_TOKEN`. The token needs `repo` scope to access the GitHub API.

#### Workflows run slowly

The first time you run `act`, it downloads Docker images which can take several minutes. Subsequent runs are much faster. The Server CI workflow installs many Python packages (especially PyTorch with CUDA) which can take 5-10 minutes.

#### Out of disk space

`act` creates Docker containers and images which can consume significant disk space. Clean up with:
```bash
docker system prune -a
```

## CI/CD Best Practices

- All checks must pass before merging PRs
- The `main` branch is protected and requires status checks to pass
- Format code before committing: `bun run format` (client) or `poetry run black .` (server)
- Run linters locally: `bun run lint` (client) or `poetry run ruff check .` (server)
- Run tests locally before pushing: `bun test` (client) or `poetry run pytest` (server)
