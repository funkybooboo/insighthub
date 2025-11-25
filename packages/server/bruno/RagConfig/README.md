# RAG Config API Tests

Bruno tests for the Workspace RAG Configuration API endpoints.

## Setup

1. Start the InsightHub server on `http://localhost:8000`
2. Create a user account and get an authentication token
3. Create a workspace and get its ID
4. Update the environment variables in `bru.env.json`:
   - `base_url`: Server URL (default: `http://localhost:8000`)
   - `auth_token`: Your JWT authentication token
   - `workspace_id`: ID of the workspace to test with

## Test Sequence

Run the tests in this order:

1. **Create Rag Config** - Creates a new RAG configuration for the workspace
2. **Get Rag Config** - Retrieves the RAG configuration
3. **Update Rag Config** - Updates the RAG configuration
4. **Validation Errors** - Tests validation error handling

## API Endpoints Tested

- `GET /api/workspaces/{workspace_id}/rag-config` - Get RAG config
- `POST /api/workspaces/{workspace_id}/rag-config` - Create RAG config
- `PATCH /api/workspaces/{workspace_id}/rag-config` - Update RAG config

## Test Coverage

- [x] Successful CRUD operations
- [x] Data validation (chunk_size, chunk_overlap, top_k ranges)
- [x] Retriever type validation (vector, graph, hybrid)
- [x] Access control (workspace ownership)
- [x] Error handling and status codes
- [x] Response format validation
- [x] Partial updates (unchanged fields preserved)

## Running Tests

```bash
# Using Bruno GUI
bruno run packages/server/bruno/RagConfig

# Or using Bruno CLI
bru run packages/server/bruno/RagConfig
```