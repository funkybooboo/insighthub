"""Graph RAG add document workflow implementation.

This workflow orchestrates the full Graph RAG document ingestion process:
1. Parse document from binary
2. Chunk document into segments
3. Extract entities from chunks
4. Extract relationships between entities
5. Index entities and relationships in graph store
"""

from typing import BinaryIO, Optional

from returns.result import Failure, Result, Success

from src.infrastructure.graph_stores.graph_store import GraphStore
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.general.chunking.document_chunker import Chunker
from src.infrastructure.rag.steps.general.parsing.document_parser import DocumentParser
from src.infrastructure.rag.steps.graph_rag.entity_extraction.entity_extractor import (
    EntityExtractor,
)
from src.infrastructure.rag.steps.graph_rag.relationship_extraction.relationship_extractor import (
    RelationshipExtractor,
)
from src.infrastructure.rag.workflows.add_document.add_document_workflow import (
    AddDocumentWorkflow,
    AddDocumentWorkflowError,
)
from src.infrastructure.types.common import MetadataDict

logger = create_logger(__name__)


class GraphRagAddDocumentWorkflow(AddDocumentWorkflow):
    """
    Orchestrates document ingestion: parse -> chunk -> extract entities -> extract relationships -> index.

    This workflow encapsulates the complete Graph RAG ingestion pipeline.
    """

    def __init__(
        self,
        parser: DocumentParser,
        chunker: Chunker,
        entity_extractor: EntityExtractor,
        relationship_extractor: RelationshipExtractor,
        graph_store: GraphStore,
        clustering_algorithm: str = "leiden",
        clustering_resolution: float = 1.0,
        clustering_max_level: int = 3,
        community_min_size: int = 3,
    ) -> None:
        """
        Initialize the Graph RAG add document workflow.

        Args:
            parser: Document parser implementation
            chunker: Document chunker implementation
            entity_extractor: Entity extraction implementation
            relationship_extractor: Relationship extraction implementation
            graph_store: Graph store for indexing entities and relationships
            clustering_algorithm: Algorithm to use for community detection
            clustering_resolution: Resolution parameter for clustering
            clustering_max_level: Maximum hierarchy level for clustering
            community_min_size: Minimum size for valid communities
        """
        self.parser = parser
        self.chunker = chunker
        self.entity_extractor = entity_extractor
        self.relationship_extractor = relationship_extractor
        self.graph_store = graph_store
        self.clustering_algorithm = clustering_algorithm
        self.clustering_resolution = clustering_resolution
        self.clustering_max_level = clustering_max_level
        self.community_min_size = community_min_size

    def execute(
        self,
        raw_document: BinaryIO,
        document_id: str,
        workspace_id: str,
        metadata: Optional[MetadataDict] = None,
    ) -> Result[int, AddDocumentWorkflowError]:
        """
        Execute the full Graph RAG ingestion workflow.

        Args:
            raw_document: Binary document content
            document_id: Unique document identifier
            workspace_id: Workspace identifier
            metadata: Optional metadata to attach

        Returns:
            Result containing number of entities indexed, or error
        """
        # Step 1: Parse document
        logger.info(f"[GraphRagAddDocumentWorkflow] Parsing document {document_id}")
        parse_result = self.parser.parse(raw_document, metadata)

        if isinstance(parse_result, Failure):
            return Failure(
                AddDocumentWorkflowError(
                    message=f"Failed to parse document: {parse_result.failure()}",
                    step="parse",
                )
            )

        document = parse_result.unwrap()
        logger.debug(f"Parsed document with {len(document.content)} characters")

        # Step 2: Chunk document
        logger.info(f"[GraphRagAddDocumentWorkflow] Chunking document {document_id}")
        try:
            chunks = self.chunker.chunk(document)
            logger.debug(f"Created {len(chunks)} chunks")
        except Exception as e:
            return Failure(
                AddDocumentWorkflowError(
                    message=f"Failed to chunk document: {str(e)}",
                    step="chunk",
                )
            )

        # Step 3: Extract entities from all chunks
        logger.info(f"[GraphRagAddDocumentWorkflow] Extracting entities from {len(chunks)} chunks")

        try:
            # Extract entities from each chunk
            chunk_texts = [chunk.text for chunk in chunks]
            all_entities_batches = self.entity_extractor.extract_entities_batch(chunk_texts)

            # Flatten and add document/chunk metadata
            all_entities = []
            for chunk, entities in zip(chunks, all_entities_batches):
                for entity in entities:
                    # Add document and chunk metadata
                    entity.metadata["document_id"] = document_id
                    entity.metadata["chunk_id"] = chunk.id
                    all_entities.append(entity)

            logger.debug(f"Extracted {len(all_entities)} total entities")

        except Exception as e:
            return Failure(
                AddDocumentWorkflowError(
                    message=f"Failed to extract entities: {str(e)}",
                    step="entity_extraction",
                )
            )

        # Step 4: Deduplicate entities by ID
        unique_entities_map = {}
        for entity in all_entities:
            if entity.id not in unique_entities_map:
                unique_entities_map[entity.id] = entity

        unique_entities = list(unique_entities_map.values())
        logger.debug(f"Deduplicated to {len(unique_entities)} unique entities")

        # Step 5: Extract relationships
        logger.info("[GraphRagAddDocumentWorkflow] Extracting relationships")

        try:
            # Extract relationships from each chunk with its entities
            all_relationships = []
            for chunk, entities in zip(chunks, all_entities_batches):
                if entities:  # Only process chunks with entities
                    relationships = self.relationship_extractor.extract_relationships(
                        chunk.text, entities
                    )
                    # Add document metadata
                    for rel in relationships:
                        rel.metadata["document_id"] = document_id
                        rel.metadata["chunk_id"] = chunk.id
                    all_relationships.extend(relationships)

            logger.debug(f"Extracted {len(all_relationships)} relationships")

        except Exception as e:
            return Failure(
                AddDocumentWorkflowError(
                    message=f"Failed to extract relationships: {str(e)}",
                    step="relationship_extraction",
                )
            )

        # Step 6: Index in graph store
        logger.info(
            f"[GraphRagAddDocumentWorkflow] Indexing {len(unique_entities)} entities and {len(all_relationships)} relationships"
        )

        try:
            # Upsert entities
            if unique_entities:
                self.graph_store.upsert_entities(unique_entities, workspace_id)

            # Upsert relationships
            if all_relationships:
                self.graph_store.upsert_relationships(all_relationships, workspace_id)

            logger.info(
                f"Successfully indexed document {document_id} with {len(unique_entities)} entities"
            )

        except Exception as e:
            return Failure(
                AddDocumentWorkflowError(
                    message=f"Failed to index in graph store: {str(e)}",
                    step="graph_index",
                )
            )

        # Step 7: Detect communities (run after indexing)
        logger.info(
            f"[GraphRagAddDocumentWorkflow] Detecting communities for workspace {workspace_id}"
        )
        try:
            from src.infrastructure.rag.steps.graph_rag.clustering.factory import (
                CommunityDetectorFactory,
            )

            # Create community detector based on configured algorithm
            detector = CommunityDetectorFactory.create(
                self.clustering_algorithm,
                resolution=self.clustering_resolution,
                max_level=self.clustering_max_level,
            )

            # Detect communities across entire workspace graph
            communities = detector.detect_communities(self.graph_store, workspace_id)

            # Filter to communities meeting minimum size
            valid_communities = [
                c for c in communities if len(c.entity_ids) >= self.community_min_size
            ]

            # Upsert communities to graph store
            if valid_communities:
                self.graph_store.upsert_communities(valid_communities, workspace_id)
                logger.info(
                    f"Detected and stored {len(valid_communities)} communities "
                    f"(filtered from {len(communities)} total)"
                )
            else:
                logger.info("No communities meeting minimum size threshold")

        except Exception as e:
            # Don't fail the entire workflow if community detection fails
            logger.warning(
                f"Community detection failed: {str(e)}, continuing without communities",
                exc_info=True,
            )

        return Success(len(unique_entities))
