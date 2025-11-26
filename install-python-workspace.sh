#!/bin/bash
# Install Python workspace packages
# This script installs all Python packages in the correct order with workspace dependencies

set -e

echo "Installing Python workspace packages..."
echo ""

# Install shared package first (it has no local dependencies)
echo "[1/3] Installing shared-python package..."
cd packages/shared/python
poetry lock
poetry install --no-root
poetry build
cd ../../..
echo "  ✓ shared-python package installed"
echo ""

# Install server (depends on shared)
echo "[2/3] Installing server..."
cd packages/server
poetry lock
poetry install --no-root
cd ../..
echo "  ✓ Server installed"
echo ""

# Install all workers (depend on shared)
echo "[3/3] Installing workers..."

WORKERS=(
  "packages/workers/general/chat"
  "packages/workers/general/chunker"
  "packages/workers/general/enricher"
  "packages/workers/general/infrastructure-manager"
  "packages/workers/general/parser"
  "packages/workers/general/router"
  "packages/workers/general/wikipedia"
  "packages/workers/vector/processor"
  "packages/workers/vector/query"
  "packages/workers/graph/connector"
  "packages/workers/graph/construction"
  "packages/workers/graph/preprocessor"
  "packages/workers/graph/query"
)

for worker in "${WORKERS[@]}"; do
  if [ -d "$worker" ]; then
    echo "  Installing $worker..."
    cd "$worker"
    poetry lock
    poetry install --no-root
    cd - > /dev/null
  fi
done

echo "  ✓ All workers installed"
echo ""
echo "Python workspace setup complete!"
echo ""
echo "All packages now use shared-python from packages/shared/python"
echo "Any changes to the shared package will be immediately available to all consumers."
