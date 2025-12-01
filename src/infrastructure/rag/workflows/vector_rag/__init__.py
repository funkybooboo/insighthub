"""Vector RAG workflow implementations."""

from src.infrastructure.rag.workflows.vector_rag.consume_workflow import (
    VectorRagAddDocumentWorkflow,
)
from src.infrastructure.rag.workflows.vector_rag.provision_workflow import (
    VectorRagCreateRagResourcesWorkflow,
)
from src.infrastructure.rag.workflows.vector_rag.query_workflow import VectorRagQueryWorkflow
from src.infrastructure.rag.workflows.vector_rag.remove_document_workflow import (
    VectorRagRemoveDocumentWorkflow,
)
from src.infrastructure.rag.workflows.vector_rag.remove_rag_resources_workflow import (
    VectorRagRemoveRagResourcesWorkflow,
)

# Backward compatibility alias
VectorRagConsumeWorkflow = VectorRagAddDocumentWorkflow

__all__ = [
    "VectorRagAddDocumentWorkflow",
    "VectorRagConsumeWorkflow",
    "VectorRagCreateRagResourcesWorkflow",
    "VectorRagQueryWorkflow",
    "VectorRagRemoveDocumentWorkflow",
    "VectorRagRemoveRagResourcesWorkflow",
]
