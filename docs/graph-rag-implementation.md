# Graph RAG Implementation

## Implementation Status

### CRITICAL: Read This First

**Current State:** Graph RAG is NOT implemented. Only configuration infrastructure exists.

**What EXISTS:**
- Configuration models: `GraphRagConfig` in `src/domains/workspace/models.py` (3 fields only)
- Default config: `DefaultGraphRagConfig` in `src/domains/default_rag_config/models.py` (3 fields only)
- Config provider: `GraphRagConfigProvider` in `src/domains/workspace/rag_config_provider.py` (incomplete)
- Workflow stubs: `GraphRagQueryWorkflow` (raises NotImplementedError)
- Factory placeholders in `src/infrastructure/rag/workflows/*/factory.py` (all raise NotImplementedError)
- Empty directory: `src/infrastructure/rag/steps/graph_rag/` (no implementations)

**What DOES NOT EXIST:**
- Graph types: NO `src/infrastructure/types/graph.py` (Entity, Relationship, Community, GraphSubgraph)
- Graph stores: NO implementations, NO base interface, NO Neo4j connector
- Entity extraction: NO implementations (no SpaCy, no LLM, no factories)
- Relationship extraction: NO implementations (no dependency parser, no LLM, no factories)
- Community detection: NO implementations (no Leiden, no Louvain, no factories)
- Workflows: NO actual implementations, only stubs raising NotImplementedError
- Database migrations: NO tables for graph RAG config extensions
- Tests: NO graph RAG tests

**CRITICAL ISSUES to Fix BEFORE Implementing New Components:**

1. **Missing Config Fields** - `GraphRagConfig` and `DefaultGraphRagConfig` ONLY have 3 fields:
   - MISSING: `entity_types: List[str]`
   - MISSING: `relationship_types: List[str]`
   - MISSING: `max_traversal_depth: int`
   - MISSING: `top_k_entities: int`
   - MISSING: `top_k_communities: int`
   - MISSING: `include_entity_neighborhoods: bool`
   - MISSING: `community_min_size: int`
   - MISSING: `clustering_resolution: float`
   - MISSING: `clustering_max_level: int`

2. **Incomplete Config Provider** - `GraphRagConfigProvider.build_query_settings()` returns ONLY:
   - `rag_type`, `entity_extraction_algorithm`, `relationship_extraction_algorithm`, `clustering_algorithm`
   - MISSING ALL graph store config, traversal settings, top_k settings

3. **Placeholder Options** - `src/infrastructure/rag/options.py` has TODO placeholders instead of factory calls:
   - Lines 61-79: `get_graph_entity_extraction_options()` - hardcoded list, needs factory
   - Lines 82-100: `get_graph_relationship_extraction_options()` - hardcoded list, needs factory
   - Lines 103-121: `get_graph_clustering_options()` - hardcoded list, needs factory

4. **NotImplementedError Everywhere:**
   - `src/infrastructure/rag/workflows/add_document/factory.py:94` - raises NotImplementedError
   - `src/infrastructure/rag/workflows/query/factory.py:85` - raises NotImplementedError
   - `src/infrastructure/rag/workflows/query/graph_rag_query_workflow.py:64` - raises QueryWorkflowError

**Implementation Order (MUST follow this sequence):**

1. **FIX EXISTING CODE FIRST:**
   - Add 9 missing fields to `GraphRagConfig` and `DefaultGraphRagConfig`
   - Update `GraphRagConfigProvider.build_query_settings()` to return ALL required fields
   - Add database migration for new config fields
   - Create `src/infrastructure/types/graph.py` with proper TypedDicts and enums

2. **THEN implement new components:**
   - Graph store interface and Neo4j implementation
   - Entity extraction (factories first, then implementations)
   - Relationship extraction (factories first, then implementations)
   - Community detection (factories first, then implementations)
   - Update `options.py` to use factories instead of hardcoded TODOs
   - Workflows (replace NotImplementedError with real code)
   - Tests

---

## Overview

Graph RAG implementation requires building knowledge graphs from documents and using graph-based retrieval. The codebase has minimal configuration infrastructure in place but ALL graph processing components need implementation.

## Data Models

### Core Graph Types

**CRITICAL: These types DO NOT EXIST. Must create file.**

**Location:** `src/infrastructure/types/graph.py` (CREATE THIS FILE)

**Type Safety Requirements:**
- Use `EntityType` enum instead of `str` for entity types
- Use `RelationType` enum instead of `str` for relationship types
- Use proper TypedDict for metadata instead of `Dict[str, Any]`

```python
from enum import Enum
from typing import TypedDict
from dataclasses import dataclass

class EntityType(str, Enum):
    """Valid entity types for graph extraction."""
    PERSON = "PERSON"
    ORGANIZATION = "ORG"
    LOCATION = "GPE"
    PRODUCT = "PRODUCT"
    EVENT = "EVENT"
    CONCEPT = "CONCEPT"

class RelationType(str, Enum):
    """Valid relationship types for graph extraction."""
    WORKS_AT = "WORKS_AT"
    LOCATED_IN = "LOCATED_IN"
    RELATED_TO = "RELATED_TO"
    PART_OF = "PART_OF"
    CREATED_BY = "CREATED_BY"

class EntityMetadata(TypedDict, total=False):
    """Type-safe entity metadata."""
    document_id: str
    chunk_id: str
    source_text: str
    extraction_method: str
    confidence_source: str

class RelationshipMetadata(TypedDict, total=False):
    """Type-safe relationship metadata."""
    document_id: str
    chunk_id: str
    sentence: str
    extraction_method: str

class CommunityMetadata(TypedDict, total=False):
    """Type-safe community metadata."""
    detection_algorithm: str
    resolution: float
    modularity: float

@dataclass
class Entity:
    id: str
    text: str
    type: EntityType  # Use enum, not str
    confidence: float
    metadata: EntityMetadata

@dataclass
class Relationship:
    id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: RelationType  # Use enum, not str
    confidence: float
    context: str
    metadata: RelationshipMetadata

@dataclass
class Community:
    id: str
    workspace_id: str
    entity_ids: list[str]
    level: int
    summary: str
    score: float
    metadata: CommunityMetadata

@dataclass
class GraphSubgraph:
    entities: list[Entity]
    relationships: list[Relationship]
    central_entities: list[str]
```

**Update:** `src/infrastructure/types/__init__.py` to export these types

### Configuration Models

**CRITICAL: Current configs are INCOMPLETE. These fields are MISSING.**

**Current State:** `src/domains/default_rag_config/models.py:22-28`

```python
@dataclass
class DefaultGraphRagConfig:
    """Default graph RAG configuration (single-user system)."""

    # ONLY 3 fields exist currently:
    entity_extraction_algorithm: str = "spacy"
    relationship_extraction_algorithm: str = "dependency-parsing"
    clustering_algorithm: str = "leiden"

    # MISSING 9 REQUIRED FIELDS - MUST ADD:
    entity_types: list[EntityType] = field(default_factory=lambda: [
        EntityType.PERSON, EntityType.ORGANIZATION, EntityType.LOCATION,
        EntityType.PRODUCT, EntityType.EVENT, EntityType.CONCEPT
    ])
    relationship_types: list[RelationType] = field(default_factory=lambda: [
        RelationType.WORKS_AT, RelationType.LOCATED_IN, RelationType.RELATED_TO
    ])
    max_traversal_depth: int = 2
    top_k_entities: int = 10
    top_k_communities: int = 3
    include_entity_neighborhoods: bool = True
    community_min_size: int = 3
    clustering_resolution: float = 1.0
    clustering_max_level: int = 3
```

**Current State:** `src/domains/workspace/models.py:108-116`

```python
@dataclass
class GraphRagConfig:
    """Graph RAG configuration for a workspace."""

    workspace_id: int

    # ONLY 3 fields exist currently:
    entity_extraction_algorithm: str = "spacy"
    relationship_extraction_algorithm: str = "dependency-parsing"
    clustering_algorithm: str = "leiden"

    # MISSING 9 REQUIRED FIELDS - Apply same additions as DefaultGraphRagConfig
```

**Database Migration Required:** Create migration to add 9 new columns to `graph_rag_config` table

### Config Provider Updates

**CRITICAL: Current implementation is INCOMPLETE**

**Location:** `src/domains/workspace/rag_config_provider.py:206-222`

**Current State:** `build_query_settings()` returns ONLY 4 fields:
```python
def build_query_settings(self, workspace_id: int) -> dict[str, Any]:
    """Build graph query settings."""
    graph_config = self.get_config_model(workspace_id)

    base_settings = {
        "rag_type": "graph",
    }

    if graph_config:
        base_settings.update({
            "entity_extraction_algorithm": graph_config.entity_extraction_algorithm,
            "relationship_extraction_algorithm": graph_config.relationship_extraction_algorithm,
            "clustering_algorithm": graph_config.clustering_algorithm,
        })

    return base_settings
```

**MUST ADD these missing fields:**
```python
def build_query_settings(self, workspace_id: int) -> dict[str, Any]:
    """Build graph query settings."""
    graph_config = self.get_config_model(workspace_id)

    base_settings = {
        "rag_type": "graph",
        # ADD THESE MISSING FIELDS:
        "graph_store_type": "neo4j",
        "graph_store_config": {
            "uri": config.graph_store.neo4j_url,
            "username": config.graph_store.neo4j_user,
            "password": config.graph_store.neo4j_password,
        },
        "max_traversal_depth": 2,
        "top_k_entities": 10,
        "top_k_communities": 3,
        "include_entity_neighborhoods": True,
    }

    if graph_config:
        base_settings.update({
            "entity_extraction_algorithm": graph_config.entity_extraction_algorithm,
            "relationship_extraction_algorithm": graph_config.relationship_extraction_algorithm,
            "clustering_algorithm": graph_config.clustering_algorithm,
            "entity_types": [et.value for et in graph_config.entity_types],
            "relationship_types": [rt.value for rt in graph_config.relationship_types],
            "max_traversal_depth": graph_config.max_traversal_depth,
            "top_k_entities": graph_config.top_k_entities,
            "top_k_communities": graph_config.top_k_communities,
            "include_entity_neighborhoods": graph_config.include_entity_neighborhoods,
        })

    return base_settings
```

## Entity Extraction

**CRITICAL: NO implementations exist. Only TODO placeholders in options.py**

### Base Interface

**Location:** `src/infrastructure/rag/steps/graph_rag/entity_extraction/base.py` (CREATE)

```python
from abc import ABC, abstractmethod
from src.infrastructure.types.graph import Entity

class EntityExtractor(ABC):
    @abstractmethod
    def extract_entities(self, text: str) -> list[Entity]:
        """Extract entities from text.

        Args:
            text: Input text

        Returns:
            List of extracted entities with proper EntityType enums
        """
        pass

    @abstractmethod
    def extract_entities_batch(self, texts: list[str]) -> list[list[Entity]]:
        """Extract entities from multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of entity lists, one per input text
        """
        pass
```

### SpaCy Implementation

**Location:** `src/infrastructure/rag/steps/graph_rag/entity_extraction/spacy_entity_extractor.py` (CREATE)

**Dependencies:** `spacy>=3.5.0`, `en_core_web_trf` model

**Implementation:**
- Use `spacy.load("en_core_web_trf")` transformer model
- Extract NER entities: Map spaCy labels to `EntityType` enum values
- Generate deterministic IDs: `hashlib.sha256(normalized_text.encode()).hexdigest()[:16]`
- Normalize entity text: lowercase, strip whitespace, handle Unicode
- Return confidence from `ent._.score` or default 0.8
- Create `EntityMetadata` TypedDict, not `Dict[str, Any]`

**Constructor parameters:**
- `model_name: str = "en_core_web_trf"`
- `entity_types: list[EntityType]` - filter to these types
- `min_confidence: float = 0.5`

### LLM Implementation

**Location:** `src/infrastructure/rag/steps/graph_rag/entity_extraction/llm_entity_extractor.py` (CREATE)

**Integration:** Use `src/domains/workspace/chat/llm_client.py` for LLM calls

**Prompt template:**
```
Extract entities from the following text. Return JSON array of entities with format:
[{"text": "entity name", "type": "PERSON|ORG|GPE|PRODUCT|EVENT|CONCEPT"}]

Text: {text}
```

**Implementation:**
- Parse JSON response and map string types to `EntityType` enum
- Generate deterministic IDs same as SpaCy
- Create `EntityMetadata` TypedDict
- Retry on malformed JSON (max 3 retries)

**Constructor parameters:**
- `llm_client: LLMClient`
- `entity_types: list[EntityType]`
- `temperature: float = 0.1`

### Factory

**CRITICAL: This factory DOES NOT EXIST**

**Location:** `src/infrastructure/rag/steps/graph_rag/entity_extraction/factory.py` (CREATE)

```python
class EntityExtractorFactory:
    @staticmethod
    def create(extractor_type: str, **config) -> EntityExtractor:
        if extractor_type == "spacy":
            return SpacyEntityExtractor(
                model_name=config.get("model", "en_core_web_trf"),
                entity_types=config.get("entity_types", list(EntityType))
            )
        elif extractor_type == "llm":
            llm_client = config["llm_client"]
            return LLMEntityExtractor(
                llm_client=llm_client,
                entity_types=config.get("entity_types", list(EntityType))
            )
        raise ValueError(f"Unknown extractor: {extractor_type}")

    @staticmethod
    def get_available_extractors() -> list[dict[str, str]]:
        return [
            {"value": "spacy", "label": "spaCy NER", "description": "..."},
            {"value": "llm", "label": "LLM-based", "description": "..."}
        ]
```

**MUST FIX:** `src/infrastructure/rag/options.py:61-79` currently has TODO placeholder:
```python
# CURRENT CODE (WRONG):
def get_graph_entity_extraction_options() -> list[dict[str, str]]:
    # TODO: Implement when graph RAG entity extraction factory is created
    return [
        {"value": "spacy", "label": "spaCy", ...},
        {"value": "llm", "label": "LLM-based", ...},
    ]

# MUST CHANGE TO:
def get_graph_entity_extraction_options() -> list[dict[str, str]]:
    from src.infrastructure.rag.steps.graph_rag.entity_extraction.factory import EntityExtractorFactory
    return EntityExtractorFactory.get_available_extractors()
```

## Relationship Extraction

**CRITICAL: NO implementations exist. Only TODO placeholders in options.py**

### Base Interface

**Location:** `src/infrastructure/rag/steps/graph_rag/relationship_extraction/base.py` (CREATE)

```python
from abc import ABC, abstractmethod
from src.infrastructure.types.graph import Entity, Relationship

class RelationshipExtractor(ABC):
    @abstractmethod
    def extract_relationships(self, text: str, entities: list[Entity]) -> list[Relationship]:
        """Extract relationships between entities.

        Args:
            text: Input text
            entities: Entities found in text

        Returns:
            List of relationships with proper RelationType enums
        """
        pass

    @abstractmethod
    def extract_relationships_batch(
        self, texts: list[str], entities_batch: list[list[Entity]]
    ) -> list[list[Relationship]]:
        """Extract relationships from multiple texts."""
        pass
```

### Dependency Parser Implementation

**Location:** `src/infrastructure/rag/steps/graph_rag/relationship_extraction/dependency_parser_extractor.py` (CREATE)

**Dependencies:** `spacy>=3.5.0`

**Implementation:**
- Use spaCy dependency parser
- Extract subject-verb-object triples
- Map verb lemmas to `RelationType` enum values (not strings)
- Create `RelationshipMetadata` TypedDict
- Generate IDs: `f"{source_id}_{relation_type.value}_{target_id}"`

### LLM Implementation

**Location:** `src/infrastructure/rag/steps/graph_rag/relationship_extraction/llm_relationship_extractor.py` (CREATE)

**Implementation:**
- Parse JSON and map to `RelationType` enum
- Create `RelationshipMetadata` TypedDict

### Factory

**CRITICAL: This factory DOES NOT EXIST**

**Location:** `src/infrastructure/rag/steps/graph_rag/relationship_extraction/factory.py` (CREATE)

Similar structure to EntityExtractorFactory

**MUST FIX:** `src/infrastructure/rag/options.py:82-100` to use factory instead of TODO

## Graph Store

**CRITICAL: NO graph store exists. Not even base interface.**

### Base Interface

**Location:** `src/infrastructure/graph_stores/base.py` (CREATE DIRECTORY AND FILE)

```python
from abc import ABC, abstractmethod
from typing import Optional
from src.infrastructure.types.graph import Entity, Relationship, Community, GraphSubgraph

class GraphStore(ABC):
    @abstractmethod
    def upsert_entities(self, entities: list[Entity], workspace_id: str) -> None:
        """Upsert entities with proper EntityType enum values."""
        pass

    @abstractmethod
    def upsert_relationships(self, relationships: list[Relationship], workspace_id: str) -> None:
        """Upsert relationships with proper RelationType enum values."""
        pass

    @abstractmethod
    def get_entity_by_id(self, entity_id: str, workspace_id: str) -> Optional[Entity]:
        pass

    @abstractmethod
    def find_entities(self, query: str, workspace_id: str, limit: int) -> list[Entity]:
        pass

    @abstractmethod
    def traverse_graph(self, entity_ids: list[str], workspace_id: str, max_depth: int) -> GraphSubgraph:
        pass

    @abstractmethod
    def get_communities(self, entity_ids: list[str], workspace_id: str) -> list[Community]:
        pass

    @abstractmethod
    def delete_document_graph(self, document_id: str, workspace_id: str) -> None:
        pass

    @abstractmethod
    def create_constraint(self, label: str, property: str) -> None:
        pass

    @abstractmethod
    def create_index(self, label: str, properties: list[str]) -> None:
        pass

    @abstractmethod
    def export_subgraph(self, workspace_id: str) -> tuple[list[Entity], list[Relationship]]:
        pass
```

### Neo4j Implementation

**Location:** `src/infrastructure/graph_stores/neo4j_graph_store.py` (CREATE)

**Dependencies:** `neo4j>=5.0.0`

**Configuration:** `src/config.py:101-107` already has GraphStoreConfig

**Connection management:**
```python
from neo4j import GraphDatabase

class Neo4jGraphStore(GraphStore):
    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()
```

**Node schema:**
```cypher
CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;
CREATE INDEX entity_workspace IF NOT EXISTS FOR (e:Entity) ON (e.workspace_id);
CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.workspace_id, e.type);
CREATE INDEX community_workspace IF NOT EXISTS FOR (c:Community) ON (c.workspace_id, c.level);
```

**Entity node properties:**
- `id` (unique)
- `text`
- `type` (store as string from EntityType.value)
- `confidence`
- `workspace_id`
- `document_ids: list[str]` (array)

**Relationship properties:**
- `type` (dynamic, from RelationType.value)
- `confidence`
- `context`
- `document_id`

**Note:** Requires APOC plugin for dynamic relationship types

### Factory

**Location:** `src/infrastructure/graph_stores/factory.py` (CREATE)

```python
class GraphStoreFactory:
    @staticmethod
    def create(store_type: str, **config) -> GraphStore:
        if store_type == "neo4j":
            return Neo4jGraphStore(
                uri=config["uri"],
                username=config.get("username", "neo4j"),
                password=config.get("password", "password")
            )
        raise ValueError(f"Unknown graph store: {store_type}")
```

## Community Detection

**CRITICAL: NO implementations exist. Only TODO placeholders in options.py**

### Base Interface

**Location:** `src/infrastructure/rag/steps/graph_rag/clustering/base.py` (CREATE)

```python
from abc import ABC, abstractmethod
from src.infrastructure.graph_stores.base import GraphStore
from src.infrastructure.types.graph import Community

class CommunityDetector(ABC):
    @abstractmethod
    def detect_communities(self, graph_store: GraphStore, workspace_id: str) -> list[Community]:
        pass

    @abstractmethod
    def generate_summary(self, community: Community, graph_store: GraphStore) -> str:
        pass
```

### Leiden Implementation

**Location:** `src/infrastructure/rag/steps/graph_rag/clustering/leiden_detector.py` (CREATE)

**Dependencies:** `python-igraph>=0.10.0`, `leidenalg>=0.9.0`

### Louvain Implementation

**Location:** `src/infrastructure/rag/steps/graph_rag/clustering/louvain_detector.py` (CREATE)

**Dependencies:** `networkx>=3.0`

### Factory

**CRITICAL: This factory DOES NOT EXIST**

**Location:** `src/infrastructure/rag/steps/graph_rag/clustering/factory.py` (CREATE)

```python
class CommunityDetectorFactory:
    @staticmethod
    def create(detector_type: str, **config) -> CommunityDetector:
        if detector_type == "leiden":
            return LeidenDetector(
                resolution=config.get("resolution", 1.0),
                max_level=config.get("max_level", 3),
                llm_client=config.get("llm_client")
            )
        elif detector_type == "louvain":
            return LouvainDetector(
                resolution=config.get("resolution", 1.0),
                max_level=config.get("max_level", 3)
            )
        raise ValueError(f"Unknown detector: {detector_type}")

    @staticmethod
    def get_available_detectors() -> list[dict[str, str]]:
        return [
            {"value": "leiden", "label": "Leiden", "description": "..."},
            {"value": "louvain", "label": "Louvain", "description": "..."}
        ]
```

**MUST FIX:** `src/infrastructure/rag/options.py:103-121` to use factory instead of TODO

## Add Document Workflow

**CRITICAL: Current code raises NotImplementedError**

**Location:** `src/infrastructure/rag/workflows/add_document/graph_rag_add_document_workflow.py` (CREATE)

**Current State:** `src/infrastructure/rag/workflows/add_document/factory.py:90-94` raises NotImplementedError:
```python
@staticmethod
def _create_graph(config: dict) -> AddDocumentWorkflow:
    """Create Graph RAG add document workflow."""
    logger.warning("Graph RAG add document workflow not yet implemented")
    raise NotImplementedError("Graph RAG add document workflow not yet implemented")
```

**MUST REPLACE WITH:**

Create the workflow file first:

```python
# src/infrastructure/rag/workflows/add_document/graph_rag_add_document_workflow.py
from src.infrastructure.rag.steps.general.parsing.base import DocumentParser
from src.infrastructure.rag.steps.general.chunking.base import Chunker
from src.infrastructure.rag.steps.graph_rag.entity_extraction.base import EntityExtractor
from src.infrastructure.rag.steps.graph_rag.relationship_extraction.base import RelationshipExtractor
from src.infrastructure.graph_stores.base import GraphStore
from src.infrastructure.types.graph import Entity

class GraphRagAddDocumentWorkflow(AddDocumentWorkflow):
    def __init__(
        self,
        parser: DocumentParser,
        chunker: Chunker,
        entity_extractor: EntityExtractor,
        relationship_extractor: RelationshipExtractor,
        graph_store: GraphStore
    ):
        self.parser = parser
        self.chunker = chunker
        self.entity_extractor = entity_extractor
        self.relationship_extractor = relationship_extractor
        self.graph_store = graph_store

    def execute(self, raw_document, document_id, workspace_id, metadata):
        # 1. Parse document
        # 2. Chunk
        # 3. Extract entities (returns list[Entity] with EntityType enums)
        # 4. Deduplicate entities
        # 5. Extract relationships (returns list[Relationship] with RelationType enums)
        # 6. Upsert to graph store
        pass
```

Then update factory:

```python
# src/infrastructure/rag/workflows/add_document/factory.py:90-94
@staticmethod
def _create_graph(config: dict) -> GraphRagAddDocumentWorkflow:
    logger.info("Creating Graph RAG add document workflow")

    parser = ParserFactory.create_parser(config.get("parser_type", "text"))
    chunker = ChunkerFactory.create_chunker(
        config.get("chunker_type", "sentence"),
        **config.get("chunker_config", {})
    )

    # Import factory (will exist after implementation)
    from src.infrastructure.rag.steps.graph_rag.entity_extraction.factory import EntityExtractorFactory
    entity_extractor = EntityExtractorFactory.create(
        config["entity_extraction_type"],
        **config.get("entity_extraction_config", {})
    )

    from src.infrastructure.rag.steps.graph_rag.relationship_extraction.factory import RelationshipExtractorFactory
    relationship_extractor = RelationshipExtractorFactory.create(
        config["relationship_extraction_type"],
        **config.get("relationship_extraction_config", {})
    )

    from src.infrastructure.graph_stores.factory import GraphStoreFactory
    graph_store = GraphStoreFactory.create(
        config["graph_store_type"],
        **config["graph_store_config"]
    )

    return GraphRagAddDocumentWorkflow(
        parser=parser,
        chunker=chunker,
        entity_extractor=entity_extractor,
        relationship_extractor=relationship_extractor,
        graph_store=graph_store
    )
```

## Query Workflow

**CRITICAL: Current code raises QueryWorkflowError**

**Location:** `src/infrastructure/rag/workflows/query/graph_rag_query_workflow.py:1-68`

**Current State:** Stub implementation that raises `QueryWorkflowError` with message "Graph RAG query workflow not yet implemented"

**MUST REPLACE WITH:**

Full implementation that:
1. Extracts entities from query (using EntityExtractor)
2. Finds matching entities in graph
3. Traverses graph to build subgraphs
4. Gets relevant communities
5. Returns ChunkData with graph context

**Current Factory:** `src/infrastructure/rag/workflows/query/factory.py:81-85` raises NotImplementedError:
```python
@staticmethod
def _create_graph(config: dict) -> QueryWorkflow:
    """Create Graph RAG query workflow."""
    logger.warning("Graph RAG query workflow not yet implemented")
    raise NotImplementedError("Graph RAG query workflow not yet implemented")
```

**MUST REPLACE WITH:** Factory that creates EntityExtractor and GraphStore

## Resource Provisioning

**Location:** `src/infrastructure/rag/workflows/create_resources/graph_rag_create_resources_workflow.py` (CREATE)

Create workflow to provision Neo4j constraints and indexes.

## Resource Removal

**Location:** `src/infrastructure/rag/workflows/remove_resources/graph_rag_remove_resources_workflow.py` (CREATE)

Create workflow to delete graph data for workspace.

## Testing

**CRITICAL: NO tests exist for graph RAG**

### Unit Tests

**Location:** `tests/unit/infrastructure/rag/steps/graph_rag/` (CREATE)

**Required test files:**
- `test_spacy_entity_extractor.py`
- `test_llm_entity_extractor.py`
- `test_dependency_parser_extractor.py`
- `test_llm_relationship_extractor.py`
- `test_leiden_detector.py`
- `test_louvain_detector.py`

**Location:** `tests/unit/infrastructure/graph_stores/` (CREATE)

**Required test files:**
- `test_neo4j_graph_store.py`

### Integration Tests

**Location:** `tests/integration/`

**Required test files:**
- `test_graph_rag_workflow.py`

**Setup:** Use testcontainers for Neo4j

## Dependencies

**Add to requirements.txt:**
```
neo4j>=5.0.0
spacy>=3.5.0
python-igraph>=0.10.0
leidenalg>=0.9.0
networkx>=3.0
```

**Download spaCy model:**
```bash
python -m spacy download en_core_web_trf
```

## Neo4j Setup

**Docker Compose:** Add to existing compose file

```yaml
neo4j:
  image: neo4j:5.12
  ports:
    - "7474:7474"
    - "7687:7687"
  environment:
    - NEO4J_AUTH=neo4j/password
    - NEO4J_PLUGINS=["apoc"]
  volumes:
    - neo4j_data:/data
    - neo4j_logs:/logs

volumes:
  neo4j_data:
  neo4j_logs:
```

## Implementation Order

**CRITICAL: Follow this exact sequence**

### Phase 1: Fix Existing Code (MUST DO FIRST)
1. Add 9 missing fields to `GraphRagConfig` model in `src/domains/workspace/models.py`
2. Add 9 missing fields to `DefaultGraphRagConfig` model in `src/domains/default_rag_config/models.py`
3. Create database migration for new config columns
4. Update `GraphRagConfigProvider.build_query_settings()` to return ALL required fields
5. Update `GraphRagConfigProvider.build_indexing_settings()` with entity/relationship extraction configs

### Phase 2: Type Definitions
6. Create `src/infrastructure/types/graph.py` with EntityType enum, RelationType enum, TypedDicts for metadata
7. Update `src/infrastructure/types/__init__.py` to export graph types

### Phase 3: Core Infrastructure
8. Create graph store base interface: `src/infrastructure/graph_stores/base.py`
9. Create Neo4j implementation: `src/infrastructure/graph_stores/neo4j_graph_store.py`
10. Create graph store factory: `src/infrastructure/graph_stores/factory.py`

### Phase 4: Entity Extraction
11. Create entity extractor base: `src/infrastructure/rag/steps/graph_rag/entity_extraction/base.py`
12. Create SpaCy extractor: `src/infrastructure/rag/steps/graph_rag/entity_extraction/spacy_entity_extractor.py`
13. Create LLM extractor: `src/infrastructure/rag/steps/graph_rag/entity_extraction/llm_entity_extractor.py`
14. Create factory: `src/infrastructure/rag/steps/graph_rag/entity_extraction/factory.py`
15. Update `src/infrastructure/rag/options.py:61-79` to use factory

### Phase 5: Relationship Extraction
16. Create relationship extractor base
17. Create dependency parser extractor
18. Create LLM extractor
19. Create factory
20. Update `src/infrastructure/rag/options.py:82-100` to use factory

### Phase 6: Community Detection
21. Create community detector base
22. Create Leiden detector
23. Create Louvain detector
24. Create factory
25. Update `src/infrastructure/rag/options.py:103-121` to use factory

### Phase 7: Workflows
26. Create `GraphRagAddDocumentWorkflow` implementation
27. Update `src/infrastructure/rag/workflows/add_document/factory.py:90-94` to use real implementation
28. Replace `GraphRagQueryWorkflow` stub with real implementation
29. Update `src/infrastructure/rag/workflows/query/factory.py:81-85` to use real implementation

### Phase 8: Resource Management
30. Create resource provisioning workflow
31. Create resource removal workflow

### Phase 9: Testing
32. Unit tests for all components
33. Integration tests with testcontainers

### Phase 10: Community Detection Job
34. Background job for periodic community detection
