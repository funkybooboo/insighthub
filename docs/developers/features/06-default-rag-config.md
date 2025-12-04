# Developer Guide: Default & Workspace RAG Configuration

This document explains the implementation of the `default_rag_config` feature and how it serves as the template for creating persistent, workspace-specific RAG configurations.

## Feature Goal

The system requires two levels of configuration:
1. A global `default-rag-config` that provides a sensible, updatable template.
2. A `workspace-rag-config` for each individual workspace, which is created as a **snapshot** of the defaults at the time of the workspace's creation.

This ensures that each workspace has its own persistent configuration that is not affected by later changes to the global defaults, and that all operations within a workspace (document processing, chat) use its own specific config.

## Core Components

- **Default Config Domain:** `src/domains/default_rag_config/`
- **Workspace-Specific Models:** `VectorRagConfig` and `GraphRagConfig` in `src/infrastructure/models/workspace.py`.
- **Repository:** `WorkspaceRepository`, which now has a concrete implementation for `create_vector_rag_config`.

## Implementation Workflow

The implementation follows these key steps:

### 1. Extending the Configuration Models

To make the configurations comprehensive, the data models for *both* the default and workspace-specific configs were extended to include all necessary parameters. For example, `DefaultVectorRagConfig` and `VectorRagConfig` now both include:

```python
# In both default_rag_config.py and workspace.py models
class ...VectorRagConfig:
    # ... other fields
    embedding_model_vector_size: int = 768
    distance_metric: str = "cosine"
```

### 2. Implementing the Repository Method

The `create_vector_rag_config` method in `WorkspaceRepository` was implemented to execute a SQL `INSERT` statement into the `vector_rag_configs` table, allowing new workspace-specific configs to be saved.

### 3. Workspace Creation Logic (The Core Workflow)

The `WorkspaceService.create_workspace` method orchestrates the entire process:

1.  **Fetch Default:** It calls `self.default_rag_config_service.get_config()` to get the global default template.
2.  **Create Workspace:** It creates the base `Workspace` entity in the `workspaces` table.
3.  **Snapshot Configuration:** It creates a new `VectorRagConfig` object.
4.  It populates this object with the values from the fetched `default_config`.
5.  It sets the `workspace_id` on the new `VectorRagConfig` object to link it to the workspace created in step 2.
6.  **Save Snapshot:** It calls `self.repository.create_vector_rag_config()` to save this new, workspace-specific configuration to the `vector_rag_configs` table.
7.  **Provision Resources:** It calls the `_provision_rag_resources` method, passing the `default_config` object to it so it has the necessary data (like vector size) for provisioning.

### 4. Consistent Configuration Usage

This new implementation ensures that all parts of the application now work as intended:
- **On Write (`create_workspace`):** A new workspace gets a dedicated RAG configuration that is a copy of the current defaults.
- **On Read (`DocumentService`, `ChatMessageService`):** These services query for the workspace-specific configuration using `workspace_repository.get_vector_rag_config(workspace_id)` and use it for their operations, ensuring they are always using the configuration that was established when their parent workspace was created.
