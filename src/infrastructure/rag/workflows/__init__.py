"""RAG workflows organized by workflow type.

Each workflow type has its own directory containing:
- Base workflow class (e.g., add_document_workflow.py)
- Vector RAG implementation (e.g., vector_rag_add_document_workflow.py)
- Graph RAG implementation (e.g., graph_rag_add_document_workflow.py)
- Factory for creating workflows (factory.py)
"""

# Add document workflows
from src.infrastructure.rag.workflows.add_document import (
    AddDocumentWorkflow,
    AddDocumentWorkflowError,
    AddDocumentWorkflowFactory,
    VectorRagAddDocumentWorkflow,
)

# Create resources workflows
from src.infrastructure.rag.workflows.create_resources import (
    CreateRagResourcesWorkflow,
    CreateRagResourcesWorkflowError,
    CreateResourcesWorkflowFactory,
    VectorRagCreateRagResourcesWorkflow,
)

# Query workflows
from src.infrastructure.rag.workflows.query import (
    GraphRagQueryWorkflow,
    QueryWorkflow,
    QueryWorkflowError,
    QueryWorkflowFactory,
    VectorRagQueryWorkflow,
)

# Remove document workflows
from src.infrastructure.rag.workflows.remove_document import (
    RemoveDocumentWorkflow,
    RemoveDocumentWorkflowError,
    RemoveDocumentWorkflowFactory,
    VectorRagRemoveDocumentWorkflow,
)

# Remove resources workflows
from src.infrastructure.rag.workflows.remove_resources import (
    RemoveRagResourcesWorkflow,
    RemoveRagResourcesWorkflowError,
    RemoveResourcesWorkflowFactory,
    VectorRagRemoveRagResourcesWorkflow,
)

__all__ = [
    # Add document
    "AddDocumentWorkflow",
    "AddDocumentWorkflowError",
    "AddDocumentWorkflowFactory",
    "VectorRagAddDocumentWorkflow",
    # Create resources
    "CreateRagResourcesWorkflow",
    "CreateRagResourcesWorkflowError",
    "CreateResourcesWorkflowFactory",
    "VectorRagCreateRagResourcesWorkflow",
    # Query
    "QueryWorkflow",
    "QueryWorkflowError",
    "QueryWorkflowFactory",
    "VectorRagQueryWorkflow",
    "GraphRagQueryWorkflow",
    # Remove document
    "RemoveDocumentWorkflow",
    "RemoveDocumentWorkflowError",
    "RemoveDocumentWorkflowFactory",
    "VectorRagRemoveDocumentWorkflow",
    # Remove resources
    "RemoveRagResourcesWorkflow",
    "RemoveRagResourcesWorkflowError",
    "RemoveResourcesWorkflowFactory",
    "VectorRagRemoveRagResourcesWorkflow",
]
