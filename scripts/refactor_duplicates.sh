#!/bin/bash

# Script to remove duplicate code between server and shared library
# This script systematically updates imports and removes duplicate files

set -e  # Exit on error

PROJECT_ROOT="/home/nate/projects/insighthub"
SERVER_DIR="$PROJECT_ROOT/packages/server"
SHARED_DIR="$PROJECT_ROOT/packages/shared/python"

echo "============================================"
echo "Code Deduplication Refactoring Script"
echo "============================================"
echo ""

# Phase 1: Update imports in server code
echo "Phase 1: Updating imports to use shared library..."
echo ""

# 1.1: Update LLM imports
echo "  1.1: Updating LLM imports..."
find "$SERVER_DIR/src" -name "*.py" -type f -exec sed -i 's|from src\.infrastructure\.llm\.llm import|from shared.llm import|g' {} \;
find "$SERVER_DIR/src" -name "*.py" -type f -exec sed -i 's|from src\.infrastructure\.llm import LlmProvider|from shared.llm import LlmProvider|g' {} \;
find "$SERVER_DIR/tests" -name "*.py" -type f -exec sed -i 's|from src\.infrastructure\.llm\.llm import|from shared.llm import|g' {} \;

# 1.2: Update BlobStorage imports
echo "  1.2: Updating BlobStorage imports..."
find "$SERVER_DIR/src" -name "*.py" -type f -exec sed -i 's|from src\.infrastructure\.storage\.blob_storage import|from shared.storage import|g' {} \;
find "$SERVER_DIR/src" -name "*.py" -type f -exec sed -i 's|from src\.infrastructure\.storage import BlobStorage|from shared.storage import BlobStorage|g' {} \;
find "$SERVER_DIR/tests" -name "*.py" -type f -exec sed -i 's|from src\.infrastructure\.storage\.blob_storage import|from shared.storage import|g' {} \;

# 1.3: Update RabbitMQ imports
echo "  1.3: Updating RabbitMQ imports..."
find "$SERVER_DIR/src" -name "*.py" -type f -exec sed -i 's|from src\.infrastructure\.messaging\.publisher import|from shared.messaging import|g' {} \;
find "$SERVER_DIR/src" -name "*.py" -type f -exec sed -i 's|from src\.infrastructure\.messaging import RabbitMQPublisher|from shared.messaging import RabbitMQPublisher|g' {} \;

# 1.4: Update Database base imports
echo "  1.4: Updating Database base imports..."
find "$SERVER_DIR/src" -name "*.py" -type f -exec sed -i 's|from src\.infrastructure\.database\.base import|from shared.database.base import|g' {} \;

# 1.5: Update Chat model imports
echo "  1.5: Updating Chat model imports..."
find "$SERVER_DIR/src" -name "*.py" -type f -exec sed -i 's|from src\.domains\.chat\.models import|from shared.models.chat import|g' {} \;

# 1.6: Update Chat repository imports  
echo "  1.6: Updating Chat repository imports..."
find "$SERVER_DIR/src" -name "*.py" -type f -exec sed -i 's|from src\.domains\.chat\.repositories import|from shared.repositories.chat import|g' {} \;

echo ""
echo "Phase 2: Removing duplicate interface files..."
echo ""

# 2.1: Remove duplicate LLM interface
echo "  2.1: Removing duplicate LLM interface..."
rm -f "$SERVER_DIR/src/infrastructure/llm/llm.py"

# 2.2: Remove duplicate BlobStorage interface
echo "  2.2: Removing duplicate BlobStorage interface..."
rm -f "$SERVER_DIR/src/infrastructure/storage/blob_storage.py"

# 2.3: Remove duplicate RabbitMQ publisher
echo "  2.3: Removing duplicate RabbitMQ publisher..."
rm -f "$SERVER_DIR/src/infrastructure/messaging/publisher.py"

# 2.4: Remove duplicate database base
echo "  2.4: Removing duplicate database base..."
rm -f "$SERVER_DIR/src/infrastructure/database/base.py"

# 2.5: Remove duplicate chat models
echo "  2.5: Removing duplicate chat models..."
rm -f "$SERVER_DIR/src/domains/chat/models.py"

# 2.6: Remove duplicate chat repositories
echo "  2.6: Removing duplicate chat repositories..."
rm -f "$SERVER_DIR/src/domains/chat/repositories.py"

echo ""
echo "Phase 3: Updating factory files to import from shared..."
echo ""

# Update LLM factory
echo "  3.1: Updating LLM factory..."
sed -i 's|from \.llm import LlmProvider|from shared.llm import LlmProvider|g' "$SERVER_DIR/src/infrastructure/llm/factory.py"

# Update storage factory  
echo "  3.2: Updating storage factories..."
if [ -f "$SERVER_DIR/src/infrastructure/storage/blob_storage_factory.py" ]; then
    sed -i 's|from \.blob_storage import BlobStorage|from shared.storage import BlobStorage|g' "$SERVER_DIR/src/infrastructure/storage/blob_storage_factory.py"
fi

# Update messaging factory
echo "  3.3: Updating messaging factory..."
if [ -f "$SERVER_DIR/src/infrastructure/messaging/factory.py" ]; then
    sed -i 's|from \.publisher import RabbitMQPublisher|from shared.messaging import RabbitMQPublisher|g' "$SERVER_DIR/src/infrastructure/messaging/factory.py"
fi

# Update repository factory
echo "  3.4: Updating repository factory..."
if [ -f "$SERVER_DIR/src/infrastructure/factories/repository_factory.py" ]; then
    sed -i 's|from src\.domains\.chat\.repositories import|from shared.repositories.chat import|g' "$SERVER_DIR/src/infrastructure/factories/repository_factory.py"
fi

echo ""
echo "Phase 4: Removing duplicate LLM provider implementations..."
echo ""

echo "  4.1: Checking for duplicate Ollama provider..."
if [ -f "$SERVER_DIR/src/infrastructure/llm/ollama.py" ] && [ -f "$SHARED_DIR/src/shared/llm/ollama.py" ]; then
    echo "    Found duplicate - updating imports in factory..."
    sed -i 's|from \.ollama import OllamaLlmProvider|from shared.llm.ollama import OllamaLlmProvider|g' "$SERVER_DIR/src/infrastructure/llm/factory.py"
    echo "    Removing server copy..."
    rm -f "$SERVER_DIR/src/infrastructure/llm/ollama.py"
fi

echo "  4.2: Checking for duplicate OpenAI provider..."
if [ -f "$SERVER_DIR/src/infrastructure/llm/openai_provider.py" ] && [ -f "$SHARED_DIR/src/shared/llm/openai_provider.py" ]; then
    sed -i 's|from \.openai_provider import OpenAiLlmProvider|from shared.llm.openai_provider import OpenAiLlmProvider|g' "$SERVER_DIR/src/infrastructure/llm/factory.py"
    rm -f "$SERVER_DIR/src/infrastructure/llm/openai_provider.py"
fi

echo "  4.3: Checking for duplicate Claude provider..."
if [ -f "$SERVER_DIR/src/infrastructure/llm/claude_provider.py" ] && [ -f "$SHARED_DIR/src/shared/llm/claude_provider.py" ]; then
    sed -i 's|from \.claude_provider import ClaudeLlmProvider|from shared.llm.claude_provider import ClaudeLlmProvider|g' "$SERVER_DIR/src/infrastructure/llm/factory.py"
    rm -f "$SERVER_DIR/src/infrastructure/llm/claude_provider.py"
fi

echo "  4.4: Checking for duplicate HuggingFace provider..."
if [ -f "$SERVER_DIR/src/infrastructure/llm/huggingface_provider.py" ] && [ -f "$SHARED_DIR/src/shared/llm/huggingface_provider.py" ]; then
    sed -i 's|from \.huggingface_provider import HuggingFaceLlmProvider|from shared.llm.huggingface_provider import HuggingFaceLlmProvider|g' "$SERVER_DIR/src/infrastructure/llm/factory.py"
    rm -f "$SERVER_DIR/src/infrastructure/llm/huggingface_provider.py"
fi

echo ""
echo "Phase 5: Removing duplicate storage implementations..."
echo ""

echo "  5.1: Checking for duplicate MinIO storage..."
if [ -f "$SERVER_DIR/src/infrastructure/storage/minio_blob_storage.py" ] && [ -f "$SHARED_DIR/src/shared/storage/minio_storage.py" ]; then
    rm -f "$SERVER_DIR/src/infrastructure/storage/minio_blob_storage.py"
fi

echo "  5.2: Checking for duplicate FileSystem storage..."
if [ -f "$SERVER_DIR/src/infrastructure/storage/file_system_blob_storage.py" ] && [ -f "$SHARED_DIR/src/shared/storage/file_system_blob_storage.py" ]; then
    rm -f "$SERVER_DIR/src/infrastructure/storage/file_system_blob_storage.py"
fi

echo "  5.3: Checking for duplicate InMemory storage..."
if [ -f "$SERVER_DIR/src/infrastructure/storage/in_memory_blob_storage.py" ] && [ -f "$SHARED_DIR/src/shared/storage/in_memory_blob_storage.py" ]; then
    rm -f "$SERVER_DIR/src/infrastructure/storage/in_memory_blob_storage.py"
fi

# Update storage factory to import from shared
if [ -f "$SERVER_DIR/src/infrastructure/storage/blob_storage_factory.py" ]; then
    echo "  5.4: Updating storage factory imports..."
    sed -i 's|from \.minio_blob_storage import MinIOBlobStorage|from shared.storage.minio_storage import MinIOBlobStorage|g' "$SERVER_DIR/src/infrastructure/storage/blob_storage_factory.py"
    sed -i 's|from \.file_system_blob_storage import FileSystemBlobStorage|from shared.storage.file_system_blob_storage import FileSystemBlobStorage|g' "$SERVER_DIR/src/infrastructure/storage/blob_storage_factory.py"
    sed -i 's|from \.in_memory_blob_storage import InMemoryBlobStorage|from shared.storage.in_memory_blob_storage import InMemoryBlobStorage|g' "$SERVER_DIR/src/infrastructure/storage/blob_storage_factory.py"
fi

echo ""
echo "============================================"
echo "Refactoring Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Run tests: cd packages/server && task test"
echo "2. Run type check: cd packages/server && task check"
echo "3. Start dev environment: task up-dev"
echo "4. Verify functionality"
echo ""
echo "Files removed:"
echo "  - server/src/infrastructure/llm/llm.py"
echo "  - server/src/infrastructure/storage/blob_storage.py"
echo "  - server/src/infrastructure/messaging/publisher.py"
echo "  - server/src/infrastructure/database/base.py"
echo "  - server/src/domains/chat/models.py"
echo "  - server/src/domains/chat/repositories.py"
echo "  - server/src/infrastructure/llm/*_provider.py (if duplicates)"
echo "  - server/src/infrastructure/storage/*_blob_storage.py (if duplicates)"
echo ""
echo "All imports updated to use shared library!"
