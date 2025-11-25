"""RAG Pipeline definitions and worker ordering system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Type

from shared.rag.base import WorkerFactory


class PipelineStage(Enum):
    """Stages in a RAG pipeline."""

    INGESTION = "ingestion"      # Document parsing, chunking
    PROCESSING = "processing"    # Embedding, entity extraction, etc.
    STORAGE = "storage"         # Vector/graph database storage
    RETRIEVAL = "retrieval"      # Query processing and retrieval
    GENERATION = "generation"    # Response generation


class WorkerRole(Enum):
    """Roles that workers can play in a RAG pipeline."""

    PARSER = "parser"                    # Document parsing
    CHUNKER = "chunker"                  # Text chunking
    EMBEDDER = "embedder"                # Vector embedding
    INDEXER = "indexer"                  # Vector storage
    ENTITY_EXTRACTOR = "entity_extractor"    # Named entity extraction
    RELATIONSHIP_EXTRACTOR = "relationship_extractor"  # Relationship extraction
    COMMUNITY_DETECTOR = "community_detector"      # Community detection
    GRAPH_BUILDER = "graph_builder"          # Graph construction
    RETRIEVER = "retriever"                # Information retrieval
    GENERATOR = "generator"                # Response generation
    ENRICHER = "enricher"                  # Content enrichment
    CLEANUP = "cleanup"                    # Maintenance/cleanup


@dataclass
class WorkerDefinition:
    """Definition of a worker in a RAG pipeline."""

    role: WorkerRole
    stage: PipelineStage
    name: str
    description: str
    dependencies: List[WorkerRole]  # Workers that must run before this one
    optional: bool = False         # Whether this worker is optional
    worker_class: Optional[Type] = None  # The actual worker class


@dataclass
class RAGPipeline:
    """Definition of a complete RAG pipeline."""

    name: str
    description: str
    system_type: str
    workers: List[WorkerDefinition]
    worker_factory: Type[WorkerFactory]

    def get_workers_by_stage(self, stage: PipelineStage) -> List[WorkerDefinition]:
        """Get all workers for a specific pipeline stage."""
        return [w for w in self.workers if w.stage == stage]

    def get_worker_dependencies(self, worker_role: WorkerRole) -> List[WorkerRole]:
        """Get dependencies for a specific worker."""
        worker = next((w for w in self.workers if w.role == worker_role), None)
        return worker.dependencies if worker else []

    def validate_pipeline(self) -> List[str]:
        """Validate the pipeline configuration."""
        errors = []

        # Check for circular dependencies (simplified check)
        for worker in self.workers:
            for dep in worker.dependencies:
                dep_worker = next((w for w in self.workers if w.role == dep), None)
                if not dep_worker:
                    errors.append(f"Worker {worker.role.value} depends on unknown worker {dep.value}")

        # Check that all required workers are present
        required_roles = {w.role for w in self.workers if not w.optional}
        for worker in self.workers:
            for dep in worker.dependencies:
                if dep not in required_roles and not any(w.role == dep and w.optional for w in self.workers):
                    errors.append(f"Required dependency {dep.value} for {worker.role.value} is missing")

        return errors


class PipelineRegistry:
    """Registry for RAG pipeline definitions."""

    _pipelines: Dict[str, RAGPipeline] = {}

    @classmethod
    def register_pipeline(cls, pipeline: RAGPipeline) -> None:
        """Register a RAG pipeline."""
        cls._pipelines[pipeline.system_type] = pipeline

    @classmethod
    def get_pipeline(cls, system_type: str) -> Optional[RAGPipeline]:
        """Get a pipeline by system type."""
        return cls._pipelines.get(system_type)

    @classmethod
    def list_pipelines(cls) -> Dict[str, RAGPipeline]:
        """List all registered pipelines."""
        return cls._pipelines.copy()


# Define the Vector RAG pipeline
VECTOR_RAG_PIPELINE = RAGPipeline(
    name="Vector RAG",
    description="Traditional vector-based retrieval augmented generation",
    system_type="vector",
    worker_factory=None,  # To be implemented
    workers=[
        WorkerDefinition(
            role=WorkerRole.PARSER,
            stage=PipelineStage.INGESTION,
            name="Document Parser",
            description="Parse documents into structured text",
            dependencies=[],
        ),
        WorkerDefinition(
            role=WorkerRole.CHUNKER,
            stage=PipelineStage.INGESTION,
            name="Text Chunker",
            description="Split documents into manageable chunks",
            dependencies=[WorkerRole.PARSER],
        ),
        WorkerDefinition(
            role=WorkerRole.EMBEDDER,
            stage=PipelineStage.PROCESSING,
            name="Vector Embedder",
            description="Generate vector embeddings from text chunks",
            dependencies=[WorkerRole.CHUNKER],
        ),
        WorkerDefinition(
            role=WorkerRole.INDEXER,
            stage=PipelineStage.STORAGE,
            name="Vector Indexer",
            description="Store embeddings in vector database",
            dependencies=[WorkerRole.EMBEDDER],
        ),
        WorkerDefinition(
            role=WorkerRole.ENRICHER,
            stage=PipelineStage.PROCESSING,
            name="Content Enricher",
            description="Enhance documents with metadata",
            dependencies=[WorkerRole.INDEXER],
            optional=True,
        ),
    ]
)

# Define the Graph RAG pipeline
GRAPH_RAG_PIPELINE = RAGPipeline(
    name="Graph RAG",
    description="Knowledge graph-based retrieval augmented generation",
    system_type="graph",
    worker_factory=None,  # To be implemented
    workers=[
        WorkerDefinition(
            role=WorkerRole.PARSER,
            stage=PipelineStage.INGESTION,
            name="Document Parser",
            description="Parse documents into structured text",
            dependencies=[],
        ),
        WorkerDefinition(
            role=WorkerRole.CHUNKER,
            stage=PipelineStage.INGESTION,
            name="Text Chunker",
            description="Split documents into manageable chunks",
            dependencies=[WorkerRole.PARSER],
        ),
        WorkerDefinition(
            role=WorkerRole.ENTITY_EXTRACTOR,
            stage=PipelineStage.PROCESSING,
            name="Entity Extractor",
            description="Extract named entities from text",
            dependencies=[WorkerRole.CHUNKER],
        ),
        WorkerDefinition(
            role=WorkerRole.RELATIONSHIP_EXTRACTOR,
            stage=PipelineStage.PROCESSING,
            name="Relationship Extractor",
            description="Extract relationships between entities",
            dependencies=[WorkerRole.ENTITY_EXTRACTOR],
        ),
        WorkerDefinition(
            role=WorkerRole.COMMUNITY_DETECTOR,
            stage=PipelineStage.PROCESSING,
            name="Community Detector",
            description="Apply clustering to group related entities",
            dependencies=[WorkerRole.RELATIONSHIP_EXTRACTOR],
        ),
        WorkerDefinition(
            role=WorkerRole.GRAPH_BUILDER,
            stage=PipelineStage.STORAGE,
            name="Graph Builder",
            description="Construct knowledge graph from entities/relationships",
            dependencies=[WorkerRole.COMMUNITY_DETECTOR],
        ),
        WorkerDefinition(
            role=WorkerRole.ENRICHER,
            stage=PipelineStage.PROCESSING,
            name="Content Enricher",
            description="Enhance documents with metadata",
            dependencies=[WorkerRole.GRAPH_BUILDER],
            optional=True,
        ),
    ]
)

# Register the pipelines
PipelineRegistry.register_pipeline(VECTOR_RAG_PIPELINE)
PipelineRegistry.register_pipeline(GRAPH_RAG_PIPELINE)


def get_pipeline_for_system(system_type: str) -> Optional[RAGPipeline]:
    """Get the pipeline definition for a RAG system type."""
    return PipelineRegistry.get_pipeline(system_type)


def validate_pipeline_order(system_type: str) -> List[str]:
    """Validate that a pipeline has correct worker ordering."""
    pipeline = PipelineRegistry.get_pipeline(system_type)
    if not pipeline:
        return [f"Pipeline for system type '{system_type}' not found"]

    return pipeline.validate_pipeline()


def get_execution_order(system_type: str) -> List[List[WorkerRole]]:
    """
    Get the execution order for workers in a pipeline.

    Returns a list of stages, where each stage contains workers that can run in parallel.
    """
    pipeline = PipelineRegistry.get_pipeline(system_type)
    if not pipeline:
        return []

    # Simple topological sort for execution order
    executed = set()
    result = []

    while len(executed) < len(pipeline.workers):
        # Find workers whose dependencies are all satisfied
        stage_workers = []
        for worker in pipeline.workers:
            if worker.role not in executed and all(dep in executed for dep in worker.dependencies):
                stage_workers.append(worker.role)

        if not stage_workers:
            # Circular dependency or other issue
            break

        result.append(stage_workers)
        executed.update(stage_workers)

    return result