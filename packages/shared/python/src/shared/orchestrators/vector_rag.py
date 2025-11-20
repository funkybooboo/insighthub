"""
Vector RAG orchestrators for ingestion and query pipelines.

Based on the architecture defined in vector_rag_notes.py.
"""

from collections.abc import Iterable
from typing import Any

from shared.components.chunking import Chunker, MetadataEnricher
from shared.components.embedding import EmbeddingEncoder
from shared.components.vector_store import VectorIndex
from shared.interfaces.vector.context import ContextBuilder
from shared.interfaces.vector.formatter import OutputFormatter
from shared.interfaces.vector.llm import LLM
from shared.interfaces.vector.parser import DocumentParser
from shared.interfaces.vector.ranker import Ranker
from shared.interfaces.vector.retriever import VectorRetriever
from shared.types import RagConfig


class VectorRAGIndexer:
    """
    Concrete ingestion pipeline for Vector RAG.

    Orchestrates the full document-to-vector pipeline:
    1. Parse documents (PDF, text, etc.)
    2. Chunk text into semantic segments
    3. Enrich chunk metadata
    4. Generate embeddings
    5. Upsert vectors into vector store

    Usage:
        indexer = VectorRAGIndexer(
            parser=PDFParser(),
            chunker=SentenceChunker(chunk_size=500),
            enricher=DefaultEnricher(),
            embedder=OllamaEmbeddings(model="nomic-embed-text"),
            vector_index=QdrantVectorStore(url="http://localhost:6333"),
        )
        
        # Ingest documents
        ids = indexer.ingest([
            (pdf_bytes, {"title": "Paper 1", "workspace_id": "ws_123"}),
            (text_bytes, {"title": "Paper 2", "workspace_id": "ws_123"}),
        ])
    """

    def __init__(
        self,
        parser: DocumentParser,
        chunker: Chunker,
        enricher: MetadataEnricher,
        embedder: EmbeddingEncoder,
        vector_index: VectorIndex,
        config: RagConfig | None = None,
    ):
        """
        Initialize the VectorRAGIndexer.

        Args:
            parser: Document parser (PDF, text, etc.)
            chunker: Text chunking strategy
            enricher: Metadata enrichment
            embedder: Embedding model
            vector_index: Vector storage (Qdrant, Pinecone, etc.)
            config: Optional RAG configuration
        """
        self.parser = parser
        self.chunker = chunker
        self.enricher = enricher
        self.embedder = embedder
        self.vector_index = vector_index
        self.config = config

    def ingest(
        self, raw_documents: Iterable[tuple[bytes, dict[str, Any] | None]]
    ) -> list[str]:
        """
        Ingest raw documents into the vector store.

        Pipeline:
        1. Parse raw bytes -> Document
        2. Chunk document -> List[Chunk]
        3. Enrich chunks with metadata
        4. Generate embeddings
        5. Upsert vectors to store

        Args:
            raw_documents: Iterable of (raw_bytes, optional_metadata) tuples

        Returns:
            List of upserted vector IDs

        Example:
            >>> ids = indexer.ingest([
            ...     (pdf_bytes, {"title": "Paper 1"}),
            ...     (text_bytes, {"title": "Paper 2"}),
            ... ])
            >>> print(f"Indexed {len(ids)} chunks")
        """
        upserted_ids: list[str] = []

        for raw, meta in raw_documents:
            # Step 1: Parse
            doc = self.parser.parse(raw, metadata=meta or {})

            # Step 2: Chunk
            chunks = self.chunker.chunk(doc)

            # Step 3: Extract text for embedding
            texts = [chunk.text for chunk in chunks]

            # Step 4: Generate embeddings
            vectors = self.embedder.encode(texts)

            # Step 5: Enrich and upsert
            for chunk, vector in zip(chunks, vectors):
                enriched = self.enricher.enrich(chunk)
                enriched.vector = vector

                # Build metadata for vector store
                vec_id = enriched.metadata.get("vector_id") or enriched.id
                vec_meta = dict(enriched.metadata)
                vec_meta.update(
                    {
                        "document_id": enriched.document_id,
                        "chunk_id": enriched.id,
                        "text": enriched.text,
                    }
                )

                # Upsert to vector store
                self.vector_index.upsert(vec_id, vector, vec_meta)
                upserted_ids.append(vec_id)

        return upserted_ids


class VectorRAG:
    """
    Concrete query-side orchestrator for Vector RAG.

    Orchestrates the full query-to-answer pipeline:
    1. Encode query to vector
    2. Retrieve top-k similar vectors
    3. Re-rank results (optional)
    4. Build LLM context from chunks
    5. Generate answer with LLM
    6. Format output with citations

    Usage:
        rag = VectorRAG(
            embedder=OllamaEmbeddings(model="nomic-embed-text"),
            vector_retriever=QdrantRetriever(store),
            ranker=NoOpRanker(),
            context_builder=DefaultContextBuilder(),
            llm=OllamaLLM(model="llama3.2:1b"),
            formatter=CitationFormatter(),
        )
        
        # Query
        result = rag.query("What is RAG?", k=5)
        print(result["answer"])
        print(result["provenance"])
    """

    def __init__(
        self,
        embedder: EmbeddingEncoder,
        vector_retriever: VectorRetriever,
        ranker: Ranker,
        context_builder: ContextBuilder,
        llm: LLM,
        formatter: OutputFormatter,
        config: RagConfig | None = None,
    ):
        """
        Initialize the VectorRAG query pipeline.

        Args:
            embedder: Embedding model (same as indexing)
            vector_retriever: Vector retrieval interface
            ranker: Re-ranking algorithm
            context_builder: LLM context construction
            llm: Language model for generation
            formatter: Output formatting with citations
            config: Optional RAG configuration
        """
        self.embedder = embedder
        self.vector_retriever = vector_retriever
        self.ranker = ranker
        self.context_builder = context_builder
        self.llm = llm
        self.formatter = formatter
        self.config = config

    def query(self, query_text: str, k: int | None = None) -> dict[str, Any]:
        """
        Execute full Vector RAG query pipeline.

        Pipeline:
        1. Encode query -> vector
        2. Retrieve top-k chunks
        3. Re-rank for relevance
        4. Build LLM context
        5. Generate answer
        6. Format with citations

        Args:
            query_text: User input question or prompt
            k: Optional top-k results (overrides config)

        Returns:
            Formatted dictionary with:
                - 'answer': str (generated answer)
                - 'provenance': list (source chunks)
                - 'raw': str (raw LLM output)
                - 'metadata': dict (retrieval stats, scores, etc.)

        Example:
            >>> result = rag.query("Explain vector search")
            >>> print(result["answer"])
            >>> for source in result["provenance"]:
            ...     print(f"- {source['document_id']}: {source['score']}")
        """
        # Determine top-k
        top_k = k or (self.config.top_k if self.config else 8)

        # Step 1: Encode query
        query_vec = self.embedder.encode_one(query_text)

        # Step 2: Retrieve top-k chunks
        retrieved = self.vector_retriever.retrieve(query_vec, k=top_k)

        # Step 3: Re-rank results
        ranked = self.ranker.rerank(retrieved, query=query_text, top_k=top_k)

        # Step 4: Build LLM context
        prompt_text, context_metadata = self.context_builder.build(ranked, query=query_text)

        # Step 5: Generate answer
        raw_output = self.llm.generate(prompt_text)

        # Step 6: Format output
        formatted = self.formatter.format(raw_output, context_metadata)

        return formatted

    def query_stream(self, query_text: str, k: int | None = None):
        """
        Execute Vector RAG query pipeline with streaming generation.

        Same as query() but yields chunks as they're generated.

        Args:
            query_text: User input question
            k: Optional top-k results

        Yields:
            Partial text chunks from LLM generation

        Example:
            >>> for chunk in rag.query_stream("What is RAG?"):
            ...     print(chunk, end="", flush=True)
        """
        # Determine top-k
        top_k = k or (self.config.top_k if self.config else 8)

        # Retrieval pipeline (same as query)
        query_vec = self.embedder.encode_one(query_text)
        retrieved = self.vector_retriever.retrieve(query_vec, k=top_k)
        ranked = self.ranker.rerank(retrieved, query=query_text, top_k=top_k)
        prompt_text, context_metadata = self.context_builder.build(ranked, query=query_text)

        # Stream generation
        for chunk in self.llm.stream_generate(prompt_text):
            yield chunk
