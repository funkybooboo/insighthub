# Developer Guide: Document Management

This document covers the technical implementation of the Document Management feature.

## Core Components

The Document Management feature is located in the `src/domains/workspace/document` directory.

- **Service Layer:** `src/domains/workspace/document/service.py`
- **Data Transfer Objects (DTOs):** `src/domains/workspace/document/dtos.py`
- **Database Model:** `src/infrastructure/models/document.py`
- **Repository:** `src/infrastructure/repositories/document_repository.py`

## Service Logic (`DocumentService`)

The `DocumentService` in `service.py` manages the lifecycle of documents within a workspace.

### Key Methods:

- `upload_and_process_document(dto: DocumentUploadRequest) -> DocumentResponse`:
    This is the main entry point for adding a new document.
    1.  It first saves the uploaded file to the configured storage backend (e.g., File System or S3), getting a `source_uri`.
    2.  It creates a `Document` entity in the database with a `processing_status` of `PENDING`.
    3.  **It then triggers an asynchronous background task to process the document.** This is a critical design choice to avoid blocking the user while a potentially long processing job runs.
    4.  The method immediately returns a `DocumentResponse` with the `PENDING` status.

- `_process_document(document_id: UUID, workspace_id: UUID)`:
    This private method runs in the background.
    1.  It fetches the document and the workspace configuration.
    2.  It calls `_build_rag_config` to construct the appropriate RAG pipeline configuration based on the workspace settings.
    3.  It invokes the `add_document` workflow for the specific RAG type (e.g., `AddDocumentVectorWorkflow`). This workflow is responsible for the actual chunking, embedding, and indexing.
    4.  Upon completion, it updates the document's `processing_status` to `SUCCESS` or `FAILURE` and populates the `chunk_count`.

- `remove_document(document_id: UUID)`:
    1.  It fetches the document and workspace.
    2.  It invokes the `remove_document` RAG workflow to delete the document's chunks from the index.
    3.  It deletes the source file from the storage backend.
    4.  It deletes the `Document` entity from the database.

## Data Structures (DTOs)

- `DocumentUploadRequest`: The DTO for uploading a new document. It contains the `workspace_id` and the file data.
- `DocumentResponse`: The standard representation of a document. It includes all properties, including the `processing_status`, which a client can use to poll for the result of the indexing job.

## Asynchronous Processing

The decision to process documents asynchronously is key to the system's responsiveness. It decouples the initial upload request from the computationally intensive indexing process. The actual implementation of the background task runner is not within the domain itself but is a concern of the application's top-level composition (e.g., using a task queue like Celery or Dramatiq).
