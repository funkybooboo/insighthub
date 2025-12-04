# Developer Guide: Workspaces

This document provides a developer-focused overview of the Workspace feature.

## Core Components

The Workspace feature is primarily implemented in the `src/domains/workspace` directory.

- **Service Layer:** `src/domains/workspace/service.py`
- **Data Transfer Objects (DTOs):** `src/domains/workspace/dtos.py`
- **Database Model:** `src/infrastructure/models/workspace.py`
- **Repository:** `src/infrastructure/repositories/workspace_repository.py`

## Service Logic (`WorkspaceService`)

The `WorkspaceService` (in `service.py`) orchestrates all operations related to workspaces. It is the main entry point for any business logic involving workspaces.

### Key Methods:

- `create_workspace(dto: CreateWorkspaceDTO) -> WorkspaceDTO`:
    1.  Validates the input DTO.
    2.  Creates a `Workspace` database entity.
    3.  **Crucially, it calls the `_provision_rag_resources` method.** This method, located in the same service, acts as a router to provision the necessary infrastructure for the chosen RAG type (e.g., creating a Qdrant collection for a `vector` workspace).
    4.  The specific provisioning logic is delegated to a RAG workflow (e.g., `CreateVectorResourcesWorkflow`).
    5.  Saves the workspace to the database via the `WorkspaceRepository`.
    6.  Returns a `WorkspaceDTO`.

- `delete_workspace(workspace_id: UUID)`:
    1.  Retrieves the workspace.
    2.  Calls a workflow to de-allocate the associated RAG resources (e.g., `RemoveVectorResourcesWorkflow`).
    3.  Deletes the workspace from the database.

## Data Structures (DTOs)

The `dtos.py` file defines the data contracts for the workspace feature.

- `WorkspaceDTO`: The standard representation of a workspace that is exposed to the application's boundaries. It contains the full state of the workspace.
- `CreateWorkspaceDTO`: The data required to create a new workspace. This includes the `name` and the RAG configuration (`rag_config`). This DTO is validated to ensure that the provided configuration is correct for the specified `rag_type`.
- `VectorRagConfigDTO` / `GraphRagConfigDTO`: These are nested DTOs within `CreateWorkspaceDTO` that hold the specific configuration for each RAG type.

## Extending the Feature

To add a new RAG type, you would need to:
1.  Create a new RAG config DTO (e.g., `MyNewRagConfigDTO`) in `dtos.py`.
2.  Update the `CreateWorkspaceDTO` to include your new config type.
3.  Implement the provisioning and de-allocation logic in new workflows under `src/infrastructure/rag/workflows/`.
4.  Update the `_provision_rag_resources` and `_remove_rag_resources` methods in `WorkspaceService` to call your new workflows based on the `rag_type`.
