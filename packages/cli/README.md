# InsightHub CLI

Command-line interface for InsightHub dual RAG system, providing terminal-based access to document management, chat interactions, and system administration.

## Features

### Core Functionality
- **Document Management**: Upload, list, and delete documents from workspaces
- **Chat Interface**: Interactive chat sessions with RAG-enhanced responses
- **Workspace Management**: Create, list, and manage workspaces
- **System Administration**: Health checks, configuration management, and diagnostics
- **Batch Operations**: Process multiple documents or commands efficiently

### User Experience
- **Interactive Mode**: Rich terminal interface with auto-completion
- **Progress Indicators**: Real-time progress for long-running operations
- **Colored Output**: Formatted output with syntax highlighting
- **Error Handling**: Comprehensive error messages and recovery suggestions
- **Configuration Management**: Persistent configuration across sessions

## Tech Stack

- **TypeScript** for type safety and modern JavaScript features
- **Bun** as the JavaScript runtime for optimal performance
- **Commander.js** for command-line argument parsing
- **Inquirer.js** for interactive prompts and menus
- **Chalk** for colored terminal output
- **Ora** for elegant loading spinners
- **Axios** for HTTP communication with the backend API

## Installation & Setup

### Prerequisites

- Node.js 18+ or Bun runtime
- InsightHub server running (see `packages/server/`)

### Installation

```bash
cd packages/cli

# Install dependencies
bun install

# Make CLI globally available (optional)
npm link
# or
bun link
```

### Configuration

The CLI can be configured via:

1. **Environment Variables**:
   ```bash
   export INSIGHTHUB_API_URL=http://localhost:5000
   export INSIGHTHUB_API_KEY=your-api-key
   ```

2. **Configuration File** (`~/.insighthub/config.json`):
   ```json
   {
     "apiUrl": "http://localhost:5000",
     "defaultWorkspace": "research-papers",
     "outputFormat": "table",
     "colorOutput": true
   }
   ```

3. **Command-line Flags**: Override configuration for individual commands

## Usage

### Basic Commands

```bash
# Get help
bun run index.ts --help
bun run index.ts <command> --help

# Interactive mode (default)
bun run index.ts

# Specify server URL
bun run index.ts --api-url http://localhost:8000

# Use specific workspace
bun run index.ts --workspace my-research
```

### Document Management

```bash
# Upload documents
bun run index.ts upload document.pdf
bun run index.ts upload *.pdf                    # Multiple files
bun run index.ts upload --workspace research paper.pdf

# List documents
bun run index.ts docs list
bun run index.ts docs list --workspace research
bun run index.ts docs list --status ready

# Get document details
bun run index.ts docs show <document-id>

# Delete documents
bun run index.ts docs delete <document-id>
bun run index.ts docs delete --workspace research <doc-id>

# Search documents
bun run index.ts docs search "machine learning"
bun run index.ts docs search --workspace research "neural networks"
```

### Chat Interface

```bash
# Start interactive chat
bun run index.ts chat
bun run index.ts chat --workspace research

# Send single message
bun run index.ts chat --message "What is RAG?"
bun run index.ts chat --workspace research --message "Explain vector databases"

# Chat sessions
bun run index.ts chat sessions list
bun run index.ts chat sessions create --workspace research
bun run index.ts chat sessions delete <session-id>

# Stream responses
bun run index.ts chat --stream --message "How does chunking work?"
```

### Workspace Management

```bash
# List workspaces
bun run index.ts workspaces list
bun run index.ts workspaces list --status ready

# Create workspace
bun run index.ts workspaces create "My Research"
bun run index.ts workspaces create "AI Papers" --rag-type vector

# Get workspace details
bun run index.ts workspaces show <workspace-id>
bun run index.ts workspaces show --name "My Research"

# Update workspace
bun run index.ts workspaces update <workspace-id> --name "New Name"
bun run index.ts workspaces update <workspace-id> --description "Updated description"

# Delete workspace
bun run index.ts workspaces delete <workspace-id>
bun run index.ts workspaces delete --name "My Research" --confirm
```

### System Administration

```bash
# Health checks
bun run index.ts health
bun run index.ts health --detailed
bun run index.ts health --component database

# Configuration
bun run index.ts config show
bun run index.ts config set api.url http://localhost:8000
bun run index.ts config set default.workspace research

# Diagnostics
bun run index.ts diagnose
bun run index.ts diagnose --component api
bun run index.ts diagnose --component database

# Logs
bun run index.ts logs --tail 100
bun run index.ts logs --component server
bun run index.ts logs --level error
```

## Interactive Mode

The default interactive mode provides a rich terminal experience:

```bash
bun run index.ts
```

### Features

- **Auto-completion**: Tab completion for commands, file paths, and workspace names
- **Command History**: Navigate through previous commands with arrow keys
- **Contextual Help**: Get help relevant to current context
- **Progress Indicators**: Visual feedback for long-running operations
- **Error Recovery**: Suggestions for fixing common errors

### Interactive Prompts

```bash
# Workspace selection
? Select workspace: [Use arrows to move, type to filter]
> research-papers
  machine-learning
  nlp-research

# Document upload
? Select documents to upload: [Space to select, Enter to confirm]
> [x] document1.pdf
  [x] document2.txt
  [ ] notes.md

# Chat configuration
? Chat options:
> [x] Enable streaming
  [x] Show sources
  [ ] Save conversation
```

## Command Reference

### Global Options

```bash
--api-url <url>          # InsightHub API URL
--workspace <name>        # Default workspace
--format <type>          # Output format (table, json, yaml)
--no-color               # Disable colored output
--verbose                # Verbose output
--quiet                  # Minimal output
--config <path>          # Custom config file path
--help                   # Show help
--version                # Show version
```

### Document Commands

#### `upload`
```bash
bun run index.ts upload [options] <files...>

Options:
  -w, --workspace <name>    Target workspace
  -r, --recursive           Upload directories recursively
  -p, --progress            Show progress bar
  -m, --metadata <json>     Document metadata
  --no-process              Skip document processing
```

#### `docs list`
```bash
bun run index.ts docs list [options]

Options:
  -w, --workspace <name>    Filter by workspace
  -s, --status <status>     Filter by status
  -f, --format <type>       Output format
  -l, --limit <number>      Limit results
```

#### `docs delete`
```bash
bun run index.ts docs delete [options] <document-id>

Options:
  -w, --workspace <name>    Workspace name
  -y, --yes                Skip confirmation
  -f, --force              Force deletion
```

### Chat Commands

#### `chat`
```bash
bun run index.ts chat [options] [message]

Options:
  -w, --workspace <name>    Target workspace
  -s, --session <id>        Chat session ID
  -m, --message <text>      Single message mode
  --stream                  Enable streaming
  --sources                 Show source documents
  --save                   Save conversation
```

### Workspace Commands

#### `workspaces create`
```bash
bun run index.ts workspaces create [options] <name>

Options:
  -d, --description <text>  Workspace description
  -r, --rag-type <type>     RAG type (vector, graph)
  -c, --config <json>        RAG configuration
```

## Configuration

### Configuration File

Location: `~/.insighthub/config.json`

```json
{
  "api": {
    "url": "http://localhost:5000",
    "timeout": 30000,
    "retries": 3
  },
  "workspace": {
    "default": "research-papers",
    "autoCreate": false
  },
  "output": {
    "format": "table",
    "color": true,
    "pager": "less"
  },
  "chat": {
    "streaming": true,
    "showSources": true,
    "saveHistory": true
  },
  "upload": {
    "chunkSize": "10MB",
    "parallel": 3,
    "autoProcess": true
  }
}
```

### Environment Variables

```bash
# API Configuration
INSIGHTHUB_API_URL=http://localhost:5000
INSIGHTHUB_API_KEY=your-api-key
INSIGHTHUB_TIMEOUT=30000

# Default Settings
INSIGHTHUB_DEFAULT_WORKSPACE=research
INSIGHTHUB_OUTPUT_FORMAT=table
INSIGHTHUB_NO_COLOR=false

# Authentication
INSIGHTHUB_USERNAME=user
INSIGHTHUB_PASSWORD=password
INSIGHTHUB_TOKEN=jwt-token
```

## Development

### Project Structure

```
packages/cli/
--- src/
|   --- commands/              # Command implementations
|   |   --- auth.ts          # Authentication commands
|   |   --- chat.ts          # Chat commands
|   |   --- docs.ts          # Document commands
|   |   --- workspaces.ts    # Workspace commands
|   |   --- system.ts        # System commands
|   --- lib/                 # Utilities and helpers
|   |   --- api.ts           # API client
|   |   --- config.ts        # Configuration management
|   |   --- utils.ts         # General utilities
|   |   --- ui.ts            # Terminal UI helpers
|   --- types/               # TypeScript type definitions
|   --- cli.ts               # Main CLI entry point
--- tests/                   # Test files
--- package.json             # Dependencies and scripts
--- tsconfig.json           # TypeScript configuration
--- README.md               # This file
```

### Available Scripts

```bash
# Development
bun run dev              # Start development mode
bun run build            # Build for production
bun run start            # Run built CLI

# Testing
bun run test             # Run tests
bun run test:watch       # Watch mode
bun run test:coverage    # Coverage report

# Code Quality
bun run lint             # Run ESLint
bun run format           # Format with Prettier
bun run typecheck        # TypeScript checking
bun run check            # Run all checks

# CLI
bun run cli              # Run CLI in development
bun run cli --help       # Show CLI help
```

### Adding New Commands

1. Create command file in `src/commands/`
2. Implement command interface:
   ```typescript
   import { Command } from 'commander';

   export const newCommand = new Command('new')
     .description('New command description')
     .option('-o, --option <value>', 'Option description')
     .action(async (options) => {
       // Command implementation
     });
   ```

3. Register command in `src/cli.ts`
4. Add tests in appropriate test file
5. Update documentation

## Error Handling

### Error Types

- **API Errors**: Communication issues with the server
- **Validation Errors**: Invalid input or parameters
- **Authentication Errors**: Login or permission issues
- **Network Errors**: Connection or timeout problems
- **File System Errors**: File access or permission issues

### Error Recovery

The CLI provides automatic suggestions for common errors:

```bash
# API connection failed
Error: Cannot connect to InsightHub server at http://localhost:5000
Suggestions:
  - Check if the server is running: task up
  - Verify the API URL: bun run index.ts config set api.url http://localhost:8000
  - Check network connectivity

# Authentication failed
Error: Invalid credentials
Suggestions:
  - Login again: bun run index.ts auth login
  - Check configuration: bun run index.ts config show
  - Reset credentials: bun run index.ts auth logout
```

## Integration with IDE

### VS Code Integration

Add to `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "InsightHub: Upload Document",
      "type": "shell",
      "command": "bun",
      "args": ["run", "index.ts", "upload", "${file}"],
      "group": "build"
    }
  ]
}
```

### Shell Integration

Add to shell profile for aliases:
```bash
# ~/.bashrc or ~/.zshrc
alias ih='bun run /path/to/insighthub/packages/cli/index.ts'
alias ih-upload='ih upload'
alias ih-chat='ih chat'
alias ih-docs='ih docs list'
```

## Troubleshooting

### Common Issues

```bash
# Command not found
bun install  # Install dependencies
npm link     # Make CLI globally available

# API connection issues
bun run index.ts health diagnose
bun run index.ts config set api.url http://localhost:8000

# Permission denied
chmod +x packages/cli/index.ts

# Module resolution errors
bun install --force
rm -rf node_modules bun.lockb && bun install
```

### Debug Mode

```bash
# Enable debug logging
DEBUG=insighthub:* bun run index.ts <command>

# Verbose output
bun run index.ts <command> --verbose

# API request debugging
INSIGHTHUB_DEBUG=true bun run index.ts <command>
```

## Contributing

1. Follow TypeScript best practices
2. Add comprehensive error handling
3. Include help text for all commands
4. Write tests for new functionality
5. Update documentation and examples
6. Test across different terminals and platforms