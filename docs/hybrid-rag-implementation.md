# Hybrid RAG Implementation

## Implementation Status

### CRITICAL: Read This First

**Current State:** Hybrid RAG is COMPLETELY UNIMPLEMENTED. Not even configuration exists.

**What EXISTS:**
- NOTHING related to hybrid RAG

**What DOES NOT EXIST:**
- NO `HybridRagConfig` model in `src/domains/workspace/models.py`
- NO `DefaultHybridRagConfig` model in `src/domains/default_rag_config/models.py`
- NO "hybrid" in `get_rag_type_options()` in `src/infrastructure/rag/options.py` (only "vector" and "graph" exist)
- NO `HybridRagConfigProvider` in `src/domains/workspace/rag_config_provider.py`
- NO fusion implementations (no RRF, no weighted, no max)
- NO fusion factories
- NO hybrid workflows (no add_document, no query)
- NO hybrid data access methods
- NO database tables for hybrid config
- NO tests for hybrid RAG

**CRITICAL DEPENDENCIES:**

Hybrid RAG is a COMPOSITE pattern that combines Vector RAG + Graph RAG. It CANNOT be implemented until:

1. **Vector RAG is complete** - Currently complete and operational
2. **Graph RAG is complete** - Currently NOT implemented (see graph-rag-implementation.md)

**Implementation Blockers:**

1. **Graph RAG Must Be Implemented First:**
   - Graph RAG workflows don't exist (raise NotImplementedError)
   - Graph RAG config is incomplete (missing 9 fields)
   - No entity extraction implementations
   - No relationship extraction implementations
   - No graph stores
   - No community detection

2. **Missing Hybrid Infrastructure:**
   - "hybrid" not in RAG type options
   - No config models
   - No config provider
   - No factory support

**Implementation Order (MUST follow this sequence):**

1. **FIRST: Complete Graph RAG implementation** (see graph-rag-implementation.md)
   - This is a prerequisite - hybrid cannot work without it

2. **THEN implement hybrid-specific code:**
   - Add "hybrid" to RAG type options
   - Create config models (HybridRagConfig, DefaultHybridRagConfig)
   - Create database migration
   - Create config provider
   - Create fusion implementations
   - Create hybrid workflows (composite pattern wrapping vector + graph)
   - Add data access methods
   - Tests

---

## Overview

Hybrid RAG combines vector similarity search and graph-based retrieval to leverage strengths of both approaches. Vector RAG excels at semantic similarity while Graph RAG captures entity relationships and community structure.

**Prerequisites (MUST be complete):**
- Vector RAG fully implemented (DONE)
- Graph RAG fully implemented (NOT DONE - see graph-rag-implementation.md)

## Architecture

### Retrieval Strategy

Execute vector and graph query workflows in parallel, merge results using rank fusion, deduplicate, and return top-k chunks.

### Configuration

Hybrid RAG requires both vector and graph configurations per workspace.

## RAG Type Options

**CRITICAL: Hybrid is MISSING from options**

**Current State:** `src/infrastructure/rag/options.py:13-31`

```python
def get_rag_type_options() -> list[dict[str, str]]:
    """Get available RAG type options."""
    return [
        {
            "value": "vector",
            "label": "Vector RAG",
            "description": "Traditional vector similarity search with embeddings",
        },
        {
            "value": "graph",
            "label": "Graph RAG",
            "description": "Knowledge graph-based retrieval with entity relationships",
        },
        # MISSING: "hybrid" option
    ]
```

**MUST ADD:**
```python
def get_rag_type_options() -> list[dict[str, str]]:
    """Get available RAG type options."""
    return [
        {
            "value": "vector",
            "label": "Vector RAG",
            "description": "Traditional vector similarity search with embeddings",
        },
        {
            "value": "graph",
            "label": "Graph RAG",
            "description": "Knowledge graph-based retrieval with entity relationships",
        },
        {
            "value": "hybrid",
            "label": "Hybrid RAG",
            "description": "Combine vector similarity and graph retrieval",
        },
    ]
```

## Data Models

### Configuration Models

**CRITICAL: These models DO NOT EXIST**

**Location:** `src/domains/default_rag_config/models.py`

**Current State:** Only has `DefaultVectorRagConfig` and `DefaultGraphRagConfig`, NO hybrid config

**MUST ADD:**
```python
@dataclass
class DefaultHybridRagConfig:
    """Default hybrid RAG configuration combining vector and graph."""

    # Fusion settings - use proper types, not Dict[str, Any]
    vector_weight: float = 0.5  # Weight for vector scores (0-1)
    graph_weight: float = 0.5   # Weight for graph scores (0-1)
    fusion_algorithm: str = "rrf"  # "rrf", "weighted", "max"
    enable_cross_encoder_rerank: bool = False
    final_rerank_top_k: int = 20  # Fetch this many before final reranking
```

**MUST UPDATE:** `DefaultRagConfig` in same file:
```python
@dataclass
class DefaultRagConfig:
    """Default RAG configuration (single-user system, used when creating new workspace)."""

    id: int
    rag_type: str = "vector"  # "vector", "graph", or "hybrid"
    # Default configurations for different RAG types
    vector_config: DefaultVectorRagConfig = field(default_factory=DefaultVectorRagConfig)
    graph_config: DefaultGraphRagConfig = field(default_factory=DefaultGraphRagConfig)
    hybrid_config: DefaultHybridRagConfig = field(default_factory=DefaultHybridRagConfig)  # ADD THIS
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
```

**Location:** `src/domains/workspace/models.py`

**Current State:** Only has `VectorRagConfig` and `GraphRagConfig`, NO hybrid config

**MUST ADD:**
```python
@dataclass
class HybridRagConfig:
    """Hybrid RAG configuration for workspace."""

    workspace_id: int
    vector_weight: float = 0.5
    graph_weight: float = 0.5
    fusion_algorithm: str = "rrf"
    enable_cross_encoder_rerank: bool = False
    final_rerank_top_k: int = 20
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
```

**Note:** Workspace also needs separate `VectorRagConfig` and `GraphRagConfig` instances when using hybrid mode

### Database Migration

**CRITICAL: NO hybrid config table exists**

**Create migration:** `migrations/add_hybrid_rag_config_table.sql`

```sql
CREATE TABLE hybrid_rag_config (
    workspace_id INTEGER PRIMARY KEY REFERENCES workspaces(id) ON DELETE CASCADE,
    vector_weight REAL NOT NULL DEFAULT 0.5,
    graph_weight REAL NOT NULL DEFAULT 0.5,
    fusion_algorithm VARCHAR(50) NOT NULL DEFAULT 'rrf',
    enable_cross_encoder_rerank BOOLEAN NOT NULL DEFAULT FALSE,
    final_rerank_top_k INTEGER NOT NULL DEFAULT 20,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hybrid_rag_config_workspace ON hybrid_rag_config(workspace_id);
```

**Also update** `default_rag_config` table to include hybrid settings

## Result Fusion

**CRITICAL: NO fusion implementations exist**

### Base Interface

**Location:** `src/infrastructure/rag/steps/hybrid_rag/fusion/base.py` (CREATE DIRECTORIES)

**Type Safety:** Use proper types, not `Dict[str, Any]`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypedDict
from src.infrastructure.types.rag import ChunkData

class FusionMetadata(TypedDict, total=False):
    """Type-safe fusion metadata."""
    fusion_method: str
    in_vector: bool
    in_graph: bool
    original_vector_score: float
    original_graph_score: float
    vector_rank: int
    graph_rank: int

@dataclass
class RankedResult:
    """Unified result type for fusion."""
    chunk_data: ChunkData
    rank: int
    source: str  # "vector" or "graph"
    original_score: float

class ResultFusion(ABC):
    @abstractmethod
    def fuse(
        self,
        vector_results: list[ChunkData],
        graph_results: list[ChunkData],
        vector_weight: float,
        graph_weight: float
    ) -> list[ChunkData]:
        """Fuse vector and graph results.

        Args:
            vector_results: Results from vector search
            graph_results: Results from graph search
            vector_weight: Weight for vector scores (0-1)
            graph_weight: Weight for graph scores (0-1)

        Returns:
            Fused and ranked results with FusionMetadata
        """
        pass
```

### Reciprocal Rank Fusion

**Location:** `src/infrastructure/rag/steps/hybrid_rag/fusion/rrf_fusion.py` (CREATE)

**Algorithm:**
```
RRF_score(d) = Σ(1 / (k + rank(d))) for all rankings
where k = 60 (constant)
```

**Implementation:**
```python
class ReciprocalRankFusion(ResultFusion):
    def __init__(self, k: int = 60):
        self.k = k

    def fuse(
        self,
        vector_results: list[ChunkData],
        graph_results: list[ChunkData],
        vector_weight: float,
        graph_weight: float
    ) -> list[ChunkData]:
        # Create maps: chunk_id -> (ChunkData, rank)
        vector_map: dict[str, tuple[ChunkData, int]] = {
            r.chunk_id: (r, i) for i, r in enumerate(vector_results)
        }
        graph_map: dict[str, tuple[ChunkData, int]] = {
            r.chunk_id: (r, i) for i, r in enumerate(graph_results)
        }

        # Get all unique chunk IDs
        all_chunk_ids = set(vector_map.keys()) | set(graph_map.keys())

        # Calculate RRF scores
        scored_results: list[ChunkData] = []
        for chunk_id in all_chunk_ids:
            rrf_score = 0.0
            chunk_data = None
            fusion_meta: FusionMetadata = {
                "fusion_method": "rrf",
                "in_vector": chunk_id in vector_map,
                "in_graph": chunk_id in graph_map,
            }

            if chunk_id in vector_map:
                chunk_data, rank = vector_map[chunk_id]
                rrf_score += vector_weight * (1.0 / (self.k + rank))
                fusion_meta["vector_rank"] = rank
                fusion_meta["original_vector_score"] = chunk_data.score

            if chunk_id in graph_map:
                if chunk_data is None:
                    chunk_data, rank = graph_map[chunk_id]
                else:
                    _, rank = graph_map[chunk_id]
                rrf_score += graph_weight * (1.0 / (self.k + rank))
                fusion_meta["graph_rank"] = rank
                fusion_meta["original_graph_score"] = graph_map[chunk_id][0].score

            # Create fused chunk with typed metadata
            fused_chunk = ChunkData(
                chunk_id=chunk_data.chunk_id,
                document_id=chunk_data.document_id,
                text=chunk_data.text,
                score=rrf_score,
                metadata={**chunk_data.metadata, **fusion_meta}
            )
            scored_results.append(fused_chunk)

        # Sort by RRF score descending
        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results
```

### Weighted Score Fusion

**Location:** `src/infrastructure/rag/steps/hybrid_rag/fusion/weighted_fusion.py` (CREATE)

**Algorithm:**
```
Weighted_score(d) = vector_weight * normalize(vector_score) + graph_weight * normalize(graph_score)
```

**Implementation:**
```python
class WeightedScoreFusion(ResultFusion):
    def fuse(
        self,
        vector_results: list[ChunkData],
        graph_results: list[ChunkData],
        vector_weight: float,
        graph_weight: float
    ) -> list[ChunkData]:
        # Normalize scores to [0, 1]
        vector_scores = [r.score for r in vector_results]
        graph_scores = [r.score for r in graph_results]

        vector_max = max(vector_scores) if vector_scores else 1.0
        vector_min = min(vector_scores) if vector_scores else 0.0
        graph_max = max(graph_scores) if graph_scores else 1.0
        graph_min = min(graph_scores) if graph_scores else 0.0

        def normalize(score: float, min_s: float, max_s: float) -> float:
            if max_s == min_s:
                return 1.0
            return (score - min_s) / (max_s - min_s)

        # Create maps with normalized scores
        vector_map: dict[str, tuple[ChunkData, float]] = {
            r.chunk_id: (r, normalize(r.score, vector_min, vector_max))
            for r in vector_results
        }
        graph_map: dict[str, tuple[ChunkData, float]] = {
            r.chunk_id: (r, normalize(r.score, graph_min, graph_max))
            for r in graph_results
        }

        all_chunk_ids = set(vector_map.keys()) | set(graph_map.keys())

        scored_results: list[ChunkData] = []
        for chunk_id in all_chunk_ids:
            weighted_score = 0.0
            chunk_data = None
            fusion_meta: FusionMetadata = {
                "fusion_method": "weighted",
                "in_vector": chunk_id in vector_map,
                "in_graph": chunk_id in graph_map,
            }

            if chunk_id in vector_map:
                chunk_data, norm_score = vector_map[chunk_id]
                weighted_score += vector_weight * norm_score
                fusion_meta["original_vector_score"] = chunk_data.score

            if chunk_id in graph_map:
                if chunk_data is None:
                    chunk_data, norm_score = graph_map[chunk_id]
                else:
                    _, norm_score = graph_map[chunk_id]
                weighted_score += graph_weight * norm_score
                fusion_meta["original_graph_score"] = graph_map[chunk_id][0].score

            fused_chunk = ChunkData(
                chunk_id=chunk_data.chunk_id,
                document_id=chunk_data.document_id,
                text=chunk_data.text,
                score=weighted_score,
                metadata={**chunk_data.metadata, **fusion_meta}
            )
            scored_results.append(fused_chunk)

        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results
```

### Max Score Fusion

**Location:** `src/infrastructure/rag/steps/hybrid_rag/fusion/max_fusion.py` (CREATE)

**Algorithm:**
```
Max_score(d) = max(normalize(vector_score), normalize(graph_score))
```

**Implementation:** Similar to weighted fusion but takes max instead of weighted sum

### Factory

**Location:** `src/infrastructure/rag/steps/hybrid_rag/fusion/factory.py` (CREATE)

```python
class FusionFactory:
    @staticmethod
    def create(fusion_type: str, **config) -> ResultFusion:
        if fusion_type == "rrf":
            return ReciprocalRankFusion(k=config.get("k", 60))
        elif fusion_type == "weighted":
            return WeightedScoreFusion()
        elif fusion_type == "max":
            return MaxScoreFusion()
        raise ValueError(f"Unknown fusion type: {fusion_type}")

    @staticmethod
    def get_available_fusion_methods() -> list[dict[str, str]]:
        return [
            {
                "value": "rrf",
                "label": "Reciprocal Rank Fusion",
                "description": "Combine rankings using reciprocal rank scores"
            },
            {
                "value": "weighted",
                "label": "Weighted Score Fusion",
                "description": "Combine normalized scores with weights"
            },
            {
                "value": "max",
                "label": "Maximum Score Fusion",
                "description": "Take maximum of normalized scores"
            }
        ]
```

**MUST ADD to** `src/infrastructure/rag/options.py`:
```python
def get_fusion_algorithm_options() -> list[dict[str, str]]:
    """Get available fusion algorithm options."""
    from src.infrastructure.rag.steps.hybrid_rag.fusion.factory import FusionFactory
    return FusionFactory.get_available_fusion_methods()

def get_default_fusion_algorithm() -> str:
    """Get default fusion algorithm."""
    return "rrf"

def is_valid_fusion_algorithm(algorithm: str) -> bool:
    """Check if fusion algorithm is valid."""
    valid_values = [opt["value"] for opt in get_fusion_algorithm_options()]
    return algorithm in valid_values
```

## Add Document Workflow

**CRITICAL: NO hybrid workflow exists**

**Location:** `src/infrastructure/rag/workflows/add_document/hybrid_rag_add_document_workflow.py` (CREATE)

**Implementation:**
```python
from concurrent.futures import ThreadPoolExecutor
from src.infrastructure.rag.workflows.add_document.add_document_workflow import AddDocumentWorkflow
from src.infrastructure.rag.workflows.add_document.vector_rag_add_document_workflow import VectorRagAddDocumentWorkflow
from src.infrastructure.rag.workflows.add_document.graph_rag_add_document_workflow import GraphRagAddDocumentWorkflow

class HybridRagAddDocumentWorkflow(AddDocumentWorkflow):
    """Composite workflow executing both vector and graph workflows."""

    def __init__(
        self,
        vector_workflow: VectorRagAddDocumentWorkflow,
        graph_workflow: GraphRagAddDocumentWorkflow
    ):
        self.vector_workflow = vector_workflow
        self.graph_workflow = graph_workflow

    def execute(self, raw_document, document_id, workspace_id, metadata):
        """Execute both workflows in parallel.

        Returns:
            Success with dict containing counts from both workflows
        """
        # Execute both workflows in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            vector_future = executor.submit(
                self.vector_workflow.execute,
                raw_document,
                document_id,
                workspace_id,
                metadata
            )

            # Need to reset file pointer for second workflow
            raw_document.seek(0)

            graph_future = executor.submit(
                self.graph_workflow.execute,
                raw_document,
                document_id,
                workspace_id,
                metadata
            )

            vector_result = vector_future.result()
            graph_result = graph_future.result()

        # Check both succeeded
        if isinstance(vector_result, Failure):
            return vector_result
        if isinstance(graph_result, Failure):
            return graph_result

        # Return combined count
        vector_count = vector_result.unwrap()
        graph_count = graph_result.unwrap()

        return Success({"vector_chunks": vector_count, "graph_entities": graph_count})
```

**MUST UPDATE:** `src/infrastructure/rag/workflows/add_document/factory.py`

**Current State:** No hybrid support, only vector and graph

**MUST ADD:**
```python
@staticmethod
def _create_hybrid(config: dict) -> HybridRagAddDocumentWorkflow:
    """Create Hybrid RAG add document workflow."""
    logger.info("Creating Hybrid RAG add document workflow")

    # Create vector workflow
    vector_config = {
        "rag_type": "vector",
        **config.get("vector_config", {})
    }
    vector_workflow = AddDocumentWorkflowFactory._create_vector(vector_config)

    # Create graph workflow
    graph_config = {
        "rag_type": "graph",
        **config.get("graph_config", {})
    }
    graph_workflow = AddDocumentWorkflowFactory._create_graph(graph_config)

    return HybridRagAddDocumentWorkflow(
        vector_workflow=vector_workflow,
        graph_workflow=graph_workflow
    )

@staticmethod
def create(rag_config: dict) -> AddDocumentWorkflow:
    """Create an add document workflow based on configuration."""
    rag_type = rag_config.get("rag_type", "vector")

    if rag_type == "vector":
        return AddDocumentWorkflowFactory._create_vector(rag_config)
    elif rag_type == "graph":
        return AddDocumentWorkflowFactory._create_graph(rag_config)
    elif rag_type == "hybrid":  # ADD THIS
        return AddDocumentWorkflowFactory._create_hybrid(rag_config)
    else:
        raise ValueError(f"Unsupported RAG type: {rag_type}")
```

## Query Workflow

**CRITICAL: NO hybrid workflow exists**

**Location:** `src/infrastructure/rag/workflows/query/hybrid_rag_query_workflow.py` (CREATE)

**Implementation:**
```python
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from src.infrastructure.rag.workflows.query.query_workflow import QueryWorkflow
from src.infrastructure.rag.workflows.query.vector_rag_query_workflow import VectorRagQueryWorkflow
from src.infrastructure.rag.workflows.query.graph_rag_query_workflow import GraphRagQueryWorkflow
from src.infrastructure.rag.steps.hybrid_rag.fusion.base import ResultFusion
from src.infrastructure.rag.steps.vector_rag.reranking.base import Reranker
from src.infrastructure.types.rag import ChunkData
from src.infrastructure.types.common import FilterDict

class HybridRagQueryWorkflow(QueryWorkflow):
    """Composite workflow combining vector and graph retrieval."""

    def __init__(
        self,
        vector_workflow: VectorRagQueryWorkflow,
        graph_workflow: GraphRagQueryWorkflow,
        fusion: ResultFusion,
        vector_weight: float = 0.5,
        graph_weight: float = 0.5,
        enable_cross_encoder_rerank: bool = False,
        cross_encoder_reranker: Optional[Reranker] = None,
        final_rerank_top_k: int = 20
    ):
        self.vector_workflow = vector_workflow
        self.graph_workflow = graph_workflow
        self.fusion = fusion
        self.vector_weight = vector_weight
        self.graph_weight = graph_weight
        self.enable_cross_encoder_rerank = enable_cross_encoder_rerank
        self.cross_encoder_reranker = cross_encoder_reranker
        self.final_rerank_top_k = final_rerank_top_k

    def execute(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[FilterDict] = None
    ) -> list[ChunkData]:
        """Execute both workflows in parallel, fuse results."""
        # Fetch more results if final reranking is enabled
        search_k = self.final_rerank_top_k if self.enable_cross_encoder_rerank else top_k

        # Execute both workflows in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            vector_future = executor.submit(
                self.vector_workflow.execute,
                query_text,
                search_k * 2,  # Fetch 2x for fusion
                filters
            )
            graph_future = executor.submit(
                self.graph_workflow.execute,
                query_text,
                search_k * 2,
                filters
            )

            vector_results = vector_future.result()
            graph_results = graph_future.result()

        # Fuse results
        fused_results = self.fusion.fuse(
            vector_results,
            graph_results,
            self.vector_weight,
            self.graph_weight
        )

        # Take top search_k
        fused_results = fused_results[:search_k]

        # Apply cross-encoder reranking if enabled
        if self.enable_cross_encoder_rerank and self.cross_encoder_reranker:
            fused_results = self._apply_cross_encoder_rerank(
                query_text,
                fused_results
            )

        # Return final top_k
        return fused_results[:top_k]

    def _apply_cross_encoder_rerank(
        self,
        query_text: str,
        results: list[ChunkData]
    ) -> list[ChunkData]:
        """Apply cross-encoder reranking to fused results."""
        logger.info(f"Applying cross-encoder reranking to {len(results)} results")

        # Convert ChunkData to format expected by reranker
        texts = [r.text for r in results]
        scores = [r.score for r in results]

        rerank_result = self.cross_encoder_reranker.rerank(
            query=query_text,
            texts=texts,
            scores=scores
        )

        if isinstance(rerank_result, Failure):
            logger.warning("Cross-encoder reranking failed, using fusion scores")
            return results

        reranked_pairs = rerank_result.unwrap()

        # Map back to ChunkData
        text_to_chunk = {r.text: r for r in results}
        reranked_results: list[ChunkData] = []
        for text, score in reranked_pairs:
            if text in text_to_chunk:
                chunk = text_to_chunk[text]
                reranked_chunk = ChunkData(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    text=chunk.text,
                    score=score,
                    metadata={
                        **chunk.metadata,
                        "reranked": True,
                        "original_score": chunk.score
                    }
                )
                reranked_results.append(reranked_chunk)

        return reranked_results
```

**MUST UPDATE:** `src/infrastructure/rag/workflows/query/factory.py`

**Current State:** No hybrid support

**MUST ADD:**
```python
@staticmethod
def _create_hybrid(config: dict) -> HybridRagQueryWorkflow:
    """Create Hybrid RAG query workflow."""
    logger.info("Creating Hybrid RAG query workflow")

    # Create vector workflow
    vector_config = {
        "rag_type": "vector",
        **config.get("vector_config", {})
    }
    vector_workflow = QueryWorkflowFactory._create_vector(vector_config)

    # Create graph workflow
    graph_config = {
        "rag_type": "graph",
        **config.get("graph_config", {})
    }
    graph_workflow = QueryWorkflowFactory._create_graph(graph_config)

    # Create fusion
    from src.infrastructure.rag.steps.hybrid_rag.fusion.factory import FusionFactory
    fusion_type = config.get("fusion_algorithm", "rrf")
    fusion = FusionFactory.create(fusion_type)

    # Optional cross-encoder reranker
    cross_encoder_reranker = None
    if config.get("enable_cross_encoder_rerank", False):
        cross_encoder_reranker = RerankerFactory.create_reranker(
            "cross-encoder",
            **config.get("cross_encoder_config", {})
        )

    return HybridRagQueryWorkflow(
        vector_workflow=vector_workflow,
        graph_workflow=graph_workflow,
        fusion=fusion,
        vector_weight=config.get("vector_weight", 0.5),
        graph_weight=config.get("graph_weight", 0.5),
        enable_cross_encoder_rerank=config.get("enable_cross_encoder_rerank", False),
        cross_encoder_reranker=cross_encoder_reranker,
        final_rerank_top_k=config.get("final_rerank_top_k", 20)
    )

@staticmethod
def create(rag_config: dict) -> QueryWorkflow:
    """Create a query workflow based on configuration."""
    rag_type = rag_config.get("rag_type", "vector")

    if rag_type == "vector":
        return QueryWorkflowFactory._create_vector(rag_config)
    elif rag_type == "graph":
        return QueryWorkflowFactory._create_graph(rag_config)
    elif rag_type == "hybrid":  # ADD THIS
        return QueryWorkflowFactory._create_hybrid(rag_config)
    else:
        raise ValueError(f"Unsupported RAG type: {rag_type}")
```

## Config Provider

**CRITICAL: NO HybridRagConfigProvider exists**

**Location:** `src/domains/workspace/rag_config_provider.py`

**Current State:** Only has `VectorRagConfigProvider` and `GraphRagConfigProvider`

**MUST ADD:**

```python
class HybridRagConfigProvider(RagConfigProvider):
    """Provider for Hybrid RAG configuration."""

    def __init__(
        self,
        workspace_data_access: WorkspaceDataAccess,
        vector_provider: VectorRagConfigProvider,
        graph_provider: GraphRagConfigProvider
    ):
        """Initialize hybrid RAG config provider.

        Args:
            workspace_data_access: Workspace data access layer
            vector_provider: Vector RAG config provider
            graph_provider: Graph RAG config provider
        """
        self.workspace_data_access = workspace_data_access
        self.vector_provider = vector_provider
        self.graph_provider = graph_provider

    def get_config_model(self, workspace_id: int) -> Optional[HybridRagConfig]:
        """Get hybrid RAG config model."""
        return self.workspace_data_access.get_hybrid_rag_config(workspace_id)

    def build_query_settings(self, workspace_id: int) -> dict[str, Any]:
        """Build hybrid query settings."""
        hybrid_config = self.get_config_model(workspace_id)

        base_settings = {
            "rag_type": "hybrid",
            "vector_config": self.vector_provider.build_query_settings(workspace_id),
            "graph_config": self.graph_provider.build_query_settings(workspace_id),
            "fusion_algorithm": "rrf",
            "vector_weight": 0.5,
            "graph_weight": 0.5,
            "enable_cross_encoder_rerank": False,
            "final_rerank_top_k": 20
        }

        if hybrid_config:
            base_settings.update({
                "fusion_algorithm": hybrid_config.fusion_algorithm,
                "vector_weight": hybrid_config.vector_weight,
                "graph_weight": hybrid_config.graph_weight,
                "enable_cross_encoder_rerank": hybrid_config.enable_cross_encoder_rerank,
                "final_rerank_top_k": hybrid_config.final_rerank_top_k
            })

        return base_settings

    def build_indexing_settings(self, workspace_id: int) -> dict[str, Any]:
        """Build hybrid indexing settings."""
        return {
            "rag_type": "hybrid",
            "vector_config": self.vector_provider.build_indexing_settings(workspace_id),
            "graph_config": self.graph_provider.build_indexing_settings(workspace_id)
        }

    def build_provisioning_settings(self, workspace_id: int) -> dict[str, Any]:
        """Build hybrid provisioning settings."""
        return {
            "rag_type": "hybrid",
            "vector_config": self.vector_provider.build_provisioning_settings(workspace_id),
            "graph_config": self.graph_provider.build_provisioning_settings(workspace_id)
        }
```

**MUST UPDATE:** `RagConfigProviderFactory` in same file:

**Current State:**
```python
class RagConfigProviderFactory:
    def __init__(
        self,
        vector_provider: VectorRagConfigProvider,
        graph_provider: GraphRagConfigProvider,
    ):
        self._providers = {
            "vector": vector_provider,
            "graph": graph_provider,
        }

    def get_provider(self, rag_type: str) -> Optional[RagConfigProvider]:
        return self._providers.get(rag_type)
```

**MUST CHANGE TO:**
```python
class RagConfigProviderFactory:
    def __init__(
        self,
        vector_provider: VectorRagConfigProvider,
        graph_provider: GraphRagConfigProvider,
        hybrid_provider: HybridRagConfigProvider  # ADD THIS
    ):
        self._providers = {
            "vector": vector_provider,
            "graph": graph_provider,
            "hybrid": hybrid_provider  # ADD THIS
        }

    def get_provider(self, rag_type: str) -> Optional[RagConfigProvider]:
        return self._providers.get(rag_type)
```

## Workspace Data Access

**CRITICAL: NO hybrid data access methods exist**

**Location:** `src/domains/workspace/data_access.py`

**Current State:** Has methods for vector and graph configs, NO hybrid methods

**MUST ADD:**
```python
def get_hybrid_rag_config(self, workspace_id: int) -> Optional[HybridRagConfig]:
    """Get hybrid RAG config for workspace.

    Args:
        workspace_id: Workspace ID

    Returns:
        HybridRagConfig or None if not found
    """
    # Query hybrid_rag_config table
    pass

def create_hybrid_rag_config(self, config: HybridRagConfig) -> HybridRagConfig:
    """Create hybrid RAG config for workspace.

    Args:
        config: HybridRagConfig to create

    Returns:
        Created HybridRagConfig
    """
    # Insert into hybrid_rag_config table
    pass

def update_hybrid_rag_config(self, workspace_id: int, updates: dict) -> HybridRagConfig:
    """Update hybrid RAG config for workspace.

    Args:
        workspace_id: Workspace ID
        updates: Dict of fields to update

    Returns:
        Updated HybridRagConfig
    """
    # Update hybrid_rag_config table
    pass
```

## Resource Provisioning

**CRITICAL: NO hybrid provisioning workflow exists**

**Location:** `src/infrastructure/rag/workflows/create_resources/hybrid_rag_create_resources_workflow.py` (CREATE)

```python
class HybridRagCreateResourcesWorkflow(CreateRagResourcesWorkflow):
    """Composite workflow for provisioning both vector and graph resources."""

    def __init__(
        self,
        vector_workflow: VectorRagCreateResourcesWorkflow,
        graph_workflow: GraphRagCreateResourcesWorkflow
    ):
        self.vector_workflow = vector_workflow
        self.graph_workflow = graph_workflow

    def execute(self, workspace_id: str, config: dict[str, Any]) -> Result[None]:
        """Execute both provisioning workflows."""
        # Execute both provisioning workflows
        vector_config = config.get("vector_config", {})
        vector_result = self.vector_workflow.execute(workspace_id, vector_config)

        if isinstance(vector_result, Failure):
            return vector_result

        graph_config = config.get("graph_config", {})
        graph_result = self.graph_workflow.execute(workspace_id, graph_config)

        if isinstance(graph_result, Failure):
            return graph_result

        return Success(None)
```

**Update factory** in create_resources workflow file to support hybrid type

## Resource Removal

**CRITICAL: NO hybrid removal workflow exists**

**Location:** `src/infrastructure/rag/workflows/remove_resources/hybrid_rag_remove_resources_workflow.py` (CREATE)

```python
class HybridRagRemoveResourcesWorkflow(RemoveRagResourcesWorkflow):
    """Composite workflow for removing both vector and graph resources."""

    def __init__(
        self,
        vector_workflow: VectorRagRemoveResourcesWorkflow,
        graph_workflow: GraphRagRemoveResourcesWorkflow
    ):
        self.vector_workflow = vector_workflow
        self.graph_workflow = graph_workflow

    def execute(self, workspace_id: str) -> Result[None]:
        """Remove both vector and graph resources."""
        # Remove both vector and graph resources
        vector_result = self.vector_workflow.execute(workspace_id)
        graph_result = self.graph_workflow.execute(workspace_id)

        # Return success if both succeeded
        if isinstance(vector_result, Failure):
            return vector_result
        if isinstance(graph_result, Failure):
            return graph_result

        return Success(None)
```

## Testing

**CRITICAL: NO hybrid tests exist**

### Unit Tests

**Location:** `tests/unit/infrastructure/rag/steps/hybrid_rag/fusion/` (CREATE)

**Required test files:**
- `test_rrf_fusion.py`
- `test_weighted_fusion.py`
- `test_max_fusion.py`

**Test cases:**
- Fusion correctness with overlapping results
- Fusion with disjoint results
- Score normalization
- Weight effects
- Empty result handling

### Integration Tests

**Location:** `tests/integration/`

**Required test files:**
- `test_hybrid_rag_workflow.py`

**Test cases:**
- End-to-end hybrid query with both vector and graph results
- Hybrid indexing of documents
- Cross-encoder reranking
- Different fusion algorithms
- Weight tuning effects

## Performance Optimization

### Parallel Execution

Vector and graph workflows execute in parallel using `ThreadPoolExecutor`. Ensure both workflows are thread-safe.

### Caching

Cache entity extraction results during query to avoid re-extracting if same query runs multiple times.

### Result Limiting

Fetch 2x search_k from each workflow to ensure good fusion candidates. Tune based on overlap percentage.

## Weight Tuning

### Empirical Tuning

Provide API endpoint to test different weights:
```python
POST /workspaces/{id}/hybrid-rag/tune
{
    "test_queries": ["query1", "query2"],
    "weight_range": {"min": 0.0, "max": 1.0, "step": 0.1}
}
```

Returns optimal weights based on result diversity and relevance.

### Adaptive Weights

Implement adaptive weighting based on query characteristics:
- Entity-rich queries: increase graph_weight
- Semantic similarity queries: increase vector_weight
- Use query classification model to determine weights dynamically

**Location:** `src/infrastructure/rag/steps/hybrid_rag/adaptive_weighting.py` (FUTURE)

## Dependencies

No additional dependencies beyond vector and graph RAG requirements.

## Configuration Example

**workspace_config.json:**
```json
{
    "rag_type": "hybrid",
    "hybrid_config": {
        "vector_weight": 0.6,
        "graph_weight": 0.4,
        "fusion_algorithm": "rrf",
        "enable_cross_encoder_rerank": true,
        "final_rerank_top_k": 20
    },
    "vector_config": {
        "embedding_algorithm": "ollama",
        "chunking_algorithm": "sentence",
        "top_k": 10
    },
    "graph_config": {
        "entity_extraction_algorithm": "spacy",
        "relationship_extraction_algorithm": "dependency-parsing",
        "clustering_algorithm": "leiden",
        "top_k_entities": 8,
        "top_k_communities": 3
    }
}
```

## Implementation Order

**CRITICAL: Follow this exact sequence**

### Phase 0: Prerequisites (MUST BE COMPLETE FIRST)
1. Vector RAG implementation - **DONE**
2. Graph RAG implementation - **NOT DONE** (see graph-rag-implementation.md)

### Phase 1: Configuration Infrastructure
3. Add "hybrid" to `get_rag_type_options()` in `src/infrastructure/rag/options.py`
4. Create `DefaultHybridRagConfig` model in `src/domains/default_rag_config/models.py`
5. Add `hybrid_config` field to `DefaultRagConfig`
6. Create `HybridRagConfig` model in `src/domains/workspace/models.py`
7. Create database migration for `hybrid_rag_config` table
8. Add hybrid data access methods to `WorkspaceDataAccess`

### Phase 2: Fusion Implementations
9. Create fusion base interface with `FusionMetadata` TypedDict
10. Create RRF fusion implementation
11. Create weighted fusion implementation
12. Create max fusion implementation
13. Create fusion factory
14. Add fusion options to `src/infrastructure/rag/options.py`

### Phase 3: Workflows
15. Create `HybridRagAddDocumentWorkflow` (composite pattern)
16. Update `AddDocumentWorkflowFactory` to support "hybrid"
17. Create `HybridRagQueryWorkflow` (composite pattern)
18. Update `QueryWorkflowFactory` to support "hybrid"

### Phase 4: Config Provider
19. Create `HybridRagConfigProvider`
20. Update `RagConfigProviderFactory` to include hybrid provider

### Phase 5: Resource Management
21. Create `HybridRagCreateResourcesWorkflow`
22. Create `HybridRagRemoveResourcesWorkflow`
23. Update factories to support hybrid

### Phase 6: Testing
24. Unit tests for all fusion implementations
25. Integration tests for hybrid workflows

### Phase 7: Optimization (Future)
26. Weight tuning utilities
27. Adaptive weighting based on query characteristics
