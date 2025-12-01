"""RAG workflow interfaces and implementations."""

# Base interfaces
from src.infrastructure.rag.workflows.add_document_workflow import (
    AddDocumentWorkflow,
    AddDocumentWorkflowError,
)
from src.infrastructure.rag.workflows.consume_workflow import ConsumeWorkflow, ConsumeWorkflowError
from src.infrastructure.rag.workflows.create_rag_resources_workflow import (
    CreateRagResourcesWorkflow,
    CreateRagResourcesWorkflowError,
)
from src.infrastructure.rag.workflows.factory import (
    WorkflowFactory,
    create_default_vector_rag_config,
)
from src.infrastructure.rag.workflows.query_workflow import QueryWorkflow, QueryWorkflowError
from src.infrastructure.rag.workflows.remove_document_workflow import (
    RemoveDocumentWorkflow,
    RemoveDocumentWorkflowError,
)
from src.infrastructure.rag.workflows.remove_rag_resources_workflow import (
    RemoveRagResourcesWorkflow,
    RemoveRagResourcesWorkflowError,
)

# Vector RAG implementations
from src.infrastructure.rag.workflows.vector_rag import (
    VectorRagAddDocumentWorkflow,
    VectorRagConsumeWorkflow,
    VectorRagCreateRagResourcesWorkflow,
    VectorRagQueryWorkflow,
    VectorRagRemoveDocumentWorkflow,
    VectorRagRemoveRagResourcesWorkflow,
)

__all__ = [
    # Base interfaces
    "AddDocumentWorkflow",
    "AddDocumentWorkflowError",
    "ConsumeWorkflow",
    "ConsumeWorkflowError",
    "CreateRagResourcesWorkflow",
    "CreateRagResourcesWorkflowError",
    "QueryWorkflow",
    "QueryWorkflowError",
    "RemoveDocumentWorkflow",
    "RemoveDocumentWorkflowError",
    "RemoveRagResourcesWorkflow",
    "RemoveRagResourcesWorkflowError",
    # Factory
    "WorkflowFactory",
    "create_default_vector_rag_config",
    # Vector RAG implementations
    "VectorRagAddDocumentWorkflow",
    "VectorRagConsumeWorkflow",
    "VectorRagCreateRagResourcesWorkflow",
    "VectorRagQueryWorkflow",
    "VectorRagRemoveDocumentWorkflow",
    "VectorRagRemoveRagResourcesWorkflow",
]
