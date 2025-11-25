#!/bin/bash

# Source environment variables from .env files
# Usage: ./source.sh [env_file]
# Examples:
#   ./source.sh .env.local    # Source local development env
#   ./source.sh .env.prod     # Source production env
#   ./source.sh               # Source .env.local if it exists, otherwise .env

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${1:-.env.local}"

# If no specific file provided and .env.local doesn't exist, try .env
if [ "$1" = "" ] && [ ! -f "$SCRIPT_DIR/.env.local" ] && [ -f "$SCRIPT_DIR/.env" ]; then
    ENV_FILE=".env"
fi

ENV_PATH="$SCRIPT_DIR/$ENV_FILE"

if [ ! -f "$ENV_PATH" ]; then
    echo "Error: Environment file '$ENV_PATH' not found"
    echo "Available files:"
    ls -la "$SCRIPT_DIR"/.env* 2>/dev/null || echo "  No .env files found"
    echo ""
    echo "Usage: $0 [env_file]"
    echo "Examples:"
    echo "  $0 .env.local     # Source local development env"
    echo "  $0 .env.prod      # Source production env"
    echo "  $0                # Source .env.local or .env (whichever exists)"
    exit 1
fi

echo "Sourcing environment variables from: $ENV_PATH"

# Source the .env file, but only export lines that look like KEY=VALUE
while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue

    # Only process lines that look like KEY=VALUE
    if [[ "$line" =~ ^[[:space:]]*([A-Z_][A-Z0-9_]*)=(.*)$ ]]; then
        key="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"

        # Remove surrounding quotes if present
        value="${value#\"}"
        value="${value%\"}"
        value="${value#\'}"
        value="${value%\'}"

        export "$key=$value"
        echo "  $key=***"
    fi
done < "$ENV_PATH"

echo "Environment variables loaded successfully"
echo ""
echo "Note: This script exports variables to your current shell session."
echo "For persistent environment variables, add 'source $SCRIPT_DIR/source.sh' to your shell profile."