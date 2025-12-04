# Developer Guide: RAG Pipelines & Workflows

This document details the architecture of the Retrieval-Augmented Generation (RAG) pipelines and the workflow pattern used to implement them.

## The Workflow Pattern

The core logic of the RAG pipelines is encapsulated in a set of **Workflows**. A workflow is a class dedicated to a single, high-level action within the RAG lifecycle. This pattern allows the domain services to remain agnostic of the specific RAG implementation details.

The workflows are organized by action in `src/infrastructure/rag/workflows/`:
- `create_resources`: For provisioning new resources for a workspace.
- `add_document`: For indexing a new document.
- `query`: For retrieving context and generating an answer.
- `remove_document`: For removing a document from the index.
- `remove_resources`: For de-allocating all resources for a workspace.

## The Factory Design

Within each action directory, a `factory.py` file implements the Factory Method design pattern.

- **Domain services** (e.g., `WorkspaceService`, `DocumentService`) do not instantiate workflow classes directly.
- Instead, they call a factory function, passing the `rag_type` (e.g., 'vector', 'graph').
- The factory returns the appropriate concrete workflow implementation for that `rag_type`.

This design makes the system highly extensible.

## Example: The `add_document` Workflow

Let's look at the `add_document` action as an example:

- **`add_document_workflow.py`:** Defines the abstract base class `AddDocumentWorkflow`. All concrete implementations must inherit from this and implement the `add_document` method.

- **`vector_rag_add_document_workflow.py`:** Contains `VectorRagAddDocumentWorkflow`, the concrete implementation for the `vector` RAG type. Its `add_document` method will:
    1. Load the document.
    2. Use the configured chunking strategy to split the document.
    3. Use the configured embedding model to create embeddings for each chunk.
    4. Call the vector store to index the chunks and their embeddings.

- **`factory.py`:** The factory might look something like this:
  ```python
  def get_add_document_workflow(rag_type: str) -> AddDocumentWorkflow:
      if rag_type == 'vector':
          return VectorRagAddDocumentWorkflow()
      elif rag_type == 'graph':
          # Return graph implementation
          pass
      raise ValueError(f"Unknown RAG type: {rag_type}")
  ```

## Implementing a New RAG Type

To add a new RAG type called `my_new_rag`, you would follow this process:

1.  **Create DTOs:** Define your RAG configuration DTO (e.g., `MyNewRagConfigDTO`) in `src/domains/workspace/dtos.py`.
2.  **Implement Workflows:** For each of the five action types (`create_resources`, `add_document`, etc.), create a new workflow implementation file (e.g., `my_new_rag_add_document_workflow.py`).
3.  **Update Factories:** In each of the five `factory.py` files, add a condition to return an instance of your new workflow class when the `rag_type` is `my_new_rag`.
4.  **Update Domain Services:** The domain services should now be able to use your new RAG type without any modification to their own code, as they only interact with the factories and the abstract workflow classes.
