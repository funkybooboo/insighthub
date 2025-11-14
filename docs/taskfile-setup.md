# Task Setup Guide

[Task](https://taskfile.dev) is a modern task runner used instead of Make.

## Installation

```bash
# Linux/macOS
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin

# macOS (Homebrew)
brew install go-task

# Verify
task --version
```

## Usage

```bash
task --list          # Show all available tasks
task <task-name>     # Run a task
task --help          # Get help
```

## Command Reference

### Root Commands (from project root)

```bash
# Services
task up              # Start production
task up-dev          # Start development (hot-reload)
task up-infra        # Infrastructure only
task down            # Stop all
task restart         # Restart production
task restart-dev     # Restart development
task ps              # Service status

# Building
task build           # Build production images
task build-dev       # Build development images

# Logs
task logs            # All services
task logs-server-dev # Development server
task logs-client-dev # Development client

# Quality
task check           # Run all checks

# Development
task dev-server      # Run server locally
task dev-client      # Run client locally

# Cleanup
task clean           # Remove all containers/volumes
```

### Server Commands (from packages/server/)

```bash
task install         # Install dependencies
task server          # Run Flask API
task cli             # RAG CLI
task test            # All tests
task test-unit       # Unit tests only
task format          # Auto-format code
task lint            # Run linter
task check           # All checks
task clean           # Clean generated files
```

### Client Commands (from packages/client/)

```bash
task install         # Install dependencies
task dev             # Vite dev server
task build           # Build for production
task format          # Prettier
task lint            # ESLint
task check           # All checks
task clean           # Clean generated files
```

### Task Delegation

Run package tasks from project root:

```bash
task server:test     # Run server tests
task server:check    # Server quality checks
task client:build    # Build client
task client:check    # Client quality checks
```

## Project Structure

```
insighthub/
├── Taskfile.yml              # Root tasks
└── packages/
    ├── server/Taskfile.yml   # Server tasks
    └── client/Taskfile.yml   # Client tasks
```

## Why Task over Make?

- YAML syntax (more readable)
- Cross-platform (Linux, Mac, Windows)
- Built-in parallelism
- Better variable system
- No tab/space issues

## Documentation

- [Official Docs](https://taskfile.dev)
- [GitHub](https://github.com/go-task/task)
