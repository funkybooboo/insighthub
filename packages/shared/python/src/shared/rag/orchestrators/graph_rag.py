"""
Graph RAG orchestrators for ingestion and query pipelines.

Based on the architecture defined in graph_rag_notes.py.
"""

from collections.abc import Iterable
from typing import Any

from shared.interfaces.graph import (
    EntityExtractor,
    GraphBuilder,
    GraphRetriever,
    GraphStore,
    RelationExtractor,
)
from shared.interfaces.vector import (
    Chunker,
    ContextBuilder,
    DocumentParser,
    LLM,
    OutputFormatter,
)
from shared.types import Document, RagConfig


class GraphRAGIndexer:
    """
    Concrete ingestion pipeline for Graph RAG.

    Orchestrates the full document-to-graph pipeline:
    1. Parse documents
    2. Chunk text
    3. Extract entities from chunks
    4. Extract relations between entities
    5. Build knowledge graph
    6. Apply clustering (Leiden algorithm)
    7. Store in graph database

    Usage:
        indexer = GraphRAGIndexer(
            parser=PDFParser(),
            chunker=SentenceChunker(chunk_size=500),
            entity_extractor=LLMEntityExtractor(llm),
            relation_extractor=LLMRelationExtractor(llm),
            graph_builder=LeidenGraphBuilder(),
            graph_store=Neo4jGraphStore(url="bolt://localhost:7687"),
        )
        
        ids = indexer.ingest([
            (pdf_bytes, {"title": "Paper 1", "workspace_id": "ws_123"}),
        ])
    """

    def __init__(
        self,
        parser: DocumentParser,
        chunker: Chunker,
        entity_extractor: EntityExtractor,
        relation_extractor: RelationExtractor,
        graph_builder: GraphBuilder,
        graph_store: GraphStore,
        config: RagConfig | None = None,
    ):
        """
        Initialize the GraphRAGIndexer.

        Args:
            parser: Document parser
            chunker: Text chunking strategy
            entity_extractor: Entity extraction (NER or LLM-based)
            relation_extractor: Relation extraction
            graph_builder: Graph construction and clustering
            graph_store: Graph database storage
            config: Optional RAG configuration
        """
        self.parser = parser
        self.chunker = chunker
        self.entity_extractor = entity_extractor
        self.relation_extractor = relation_extractor
        self.graph_builder = graph_builder
        self.graph_store = graph_store
        self.config = config

    def ingest(
        self, raw_documents: Iterable[tuple[bytes, dict[str, Any] | None]]
    ) -> dict[str, Any]:
        """
        Ingest raw documents into the graph store.

        Pipeline:
        1. Parse raw bytes -> Documents
        2. Chunk documents
        3. Extract entities from chunks
        4. Extract relations between entities
        5. Build knowledge graph
        6. Apply clustering
        7. Store in graph database

        Args:
            raw_documents: Iterable of (raw_bytes, optional_metadata) tuples

        Returns:
            Dictionary with ingestion statistics:
                - document_count: int
                - node_count: int
                - edge_count: int
                - community_count: int
        """
        documents: list[Document] = []

        # Step 1-2: Parse and prepare documents
        for raw, meta in raw_documents:
            doc = self.parser.parse(raw, metadata=meta or {})
            documents.append(doc)

        # Step 3-5: Build graph from documents
        nodes, edges = self.graph_builder.build_graph(documents)

        # Step 6: Apply clustering
        clustering_result = self.graph_builder.apply_clustering(nodes, edges)

        # Step 7: Store in graph database
        self.graph_store.add_nodes(nodes)
        self.graph_store.add_edges(edges)

        return {
            "document_count": len(documents),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "community_count": clustering_result.get("community_count", 0),
            "clustering_metadata": clustering_result,
        }


class GraphRAG:
    """
    Concrete query-side orchestrator for Graph RAG.

    Orchestrates the full query-to-answer pipeline using graph retrieval:
    1. Retrieve relevant graph nodes/subgraphs
    2. Build LLM context from graph structure
    3. Generate answer with LLM
    4. Format output with graph provenance

    Usage:
        rag = GraphRAG(
            graph_retriever=CommunityGraphRetriever(store),
            context_builder=GraphContextBuilder(),
            llm=OllamaLLM(model="llama3.2:1b"),
            formatter=GraphCitationFormatter(),
        )
        
        result = rag.query("What entities are related to RAG?")
        print(result["answer"])
        print(result["graph_context"])
    """

    def __init__(
        self,
        graph_retriever: GraphRetriever,
        context_builder: ContextBuilder,
        llm: LLM,
        formatter: OutputFormatter,
        config: RagConfig | None = None,
    ):
        """
        Initialize the GraphRAG query pipeline.

        Args:
            graph_retriever: Graph-based retrieval
            context_builder: LLM context construction from graph
            llm: Language model for generation
            formatter: Output formatting with graph provenance
            config: Optional RAG configuration
        """
        self.graph_retriever = graph_retriever
        self.context_builder = context_builder
        self.llm = llm
        self.formatter = formatter
        self.config = config

    def query(self, query_text: str, k: int | None = None) -> dict[str, Any]:
        """
        Execute full Graph RAG query pipeline.

        Pipeline:
        1. Retrieve relevant graph nodes/communities
        2. Build LLM context from graph structure
        3. Generate answer
        4. Format with graph provenance

        Args:
            query_text: User input question
            k: Optional top-k results (communities or nodes)

        Returns:
            Formatted dictionary with:
                - 'answer': str
                - 'provenance': list (graph nodes, edges)
                - 'graph_context': dict (subgraph information)
                - 'raw': str
        """
        # Determine top-k
        top_k = k or (self.config.top_k if self.config else 3)

        # Step 1: Retrieve from graph
        retrieved = self.graph_retriever.retrieve(query_text, k=top_k)

        # Step 2: Build LLM context from graph
        prompt_text, context_metadata = self.context_builder.build(
            retrieved, query=query_text
        )

        # Step 3: Generate answer
        raw_output = self.llm.generate(prompt_text)

        # Step 4: Format output
        formatted = self.formatter.format(raw_output, context_metadata)

        return formatted

    def query_stream(self, query_text: str, k: int | None = None):
        """
        Execute Graph RAG query pipeline with streaming generation.

        Args:
            query_text: User input question
            k: Optional top-k results

        Yields:
            Partial text chunks from LLM generation
        """
        top_k = k or (self.config.top_k if self.config else 3)

        # Retrieval pipeline
        retrieved = self.graph_retriever.retrieve(query_text, k=top_k)
        prompt_text, context_metadata = self.context_builder.build(
            retrieved, query=query_text
        )

        # Stream generation
        for chunk in self.llm.stream_generate(prompt_text):
            yield chunk
