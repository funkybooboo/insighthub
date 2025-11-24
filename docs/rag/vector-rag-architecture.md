# ## **Vector-RAG System Workflow**
#
# ### **Step 1: Document Ingestion**
#
# * **Purpose:** Get raw documents (PDF, HTML, text) into a structured form.
# * **Tasks:**
#
#   * Load or receive document bytes.
#   * Parse into clean text.
#   * Optional: add metadata (title, author, timestamp, etc.).
#
# ---
#
# ### **Step 2: Chunking**
#
# * **Purpose:** Split long text into smaller, semantically meaningful pieces.
# * **Tasks:**
#
#   * Sentence-level, paragraph-level, or custom chunking.
#   * Each chunk gets a unique ID and associated document ID.
#
# ---
#
# ### **Step 3: Embedding / Vectorization**
#
# * **Purpose:** Convert each chunk into a vector representation for similarity search.
# * **Tasks:**
#
#   * Use embeddings from a model (e.g., OpenAI, SentenceTransformers, custom).
#   * Store embedding vectors in memory or persistent vector store.
#
# ---
#
# ### **Step 4: Vector Storage**
#
# * **Purpose:** Store embeddings and metadata for retrieval.
# * **Tasks:**
#
#   * Persist vectors + chunk metadata in a vector database (e.g., FAISS, Pinecone, Weaviate, Milvus).
#   * Support retrieval queries (nearest neighbor search).
#
# ---
#
# ### **Step 5: Query Encoding**
#
# * **Purpose:** Convert user query into the same embedding space.
# * **Tasks:**
#
#   * Encode query text using the same embedding model used for documents.
#
# ---
#
# ### **Step 6: Vector Retrieval**
#
# * **Purpose:** Find the top-k chunks most similar to the query vector.
# * **Tasks:**
#
#   * Run similarity search in vector database.
#   * Retrieve chunk text + metadata + scores.
#
# ---
#
# ### **Step 7: Ranking (Optional)**
#
# * **Purpose:** Re-rank retrieved chunks using heuristics or cross-encoders.
# * **Tasks:**
#
#   * Apply score adjustments based on recency, provenance, or semantic relevance.
#   * Return top-k candidates for context building.
#
# ---
#
# ### **Step 8: Context Construction**
#
# * **Purpose:** Assemble retrieved chunks into a context prompt for LLM.
# * **Tasks:**
#
#   * Concatenate chunk texts.
#   * Include metadata, provenance, or summaries.
#   * Respect LLM token limits.
#
# ---
#
# ### **Step 9: LLM Answer Generation**
#
# * **Purpose:** Generate a response using the constructed context.
# * **Tasks:**
#
#   * Feed prompt to the LLM.
#   * Generate answer (streaming or synchronous).
#   * Optionally include citations or provenance.
#
# ---
#
# ### **Step 10: Output Formatting**
#
# * **Purpose:** Present the answer to the user in structured form.
# * **Tasks:**
#
#   * Return final answer text.
#   * Include metadata (source chunks, document IDs, confidence scores).
#
# ---
#
# ## **Vector-RAG Workflow Diagram (Text Representation)**
#
# ```
# Raw Documents
#       |
#       v
# [Document Parser]
#       |
#       v
# [Chunker] --> Chunk 1, Chunk 2, ...
#       |
#       v
# [Embedding Encoder] --> Embedding Vectors
#       |
#       v
# [Vector Store] <---------------+
#       |                       |
#       v                       |
# User Query                    |
#       |                       |
# [Query Encoder] --------------+
#       |
#       v
# [Vector Retriever] --> Top-k Chunks
#       |
#       v
# [Ranker] (optional)
#       |
#       v
# [Context Builder] --> Prompt for LLM
#       |
#       v
# [LLM] --> Raw Answer
#       |
#       v
# [Output Formatter] --> Final Answer + Provenance
# ```
#
# ---
#
# This shows a **pure vector-based RAG system**: no graph database is involved, all retrieval is nearest-neighbor vector search.

"""
vector_rag_interfaces_and_orchestrators.py

Complete, fully-documented Python API for a Vector-RAG system.

Contents:
- Helper datatypes: Document, Chunk, RetrievalResult, RagConfig
- Interfaces for ingestion, embedding, storage, retrieval, ranking, context, LLM, and output formatting
- Concrete orchestrators:
    * VectorRAGIndexer  -- document ingestion and indexing pipeline
    * VectorRAG         -- query pipeline from user query to LLM answer
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


# -----------------------------
# Helper Data Types
# -----------------------------

@dataclass
class Document:
    """
    Represents a document in the Vector-RAG system.

    Attributes:
        id: Unique identifier for the document.
        workspace_id: Workspace or tenant identifier.
        title: Optional human-readable title of the document.
        content: Raw textual content of the document.
        metadata: Arbitrary metadata dictionary (author, source, timestamps, etc.).
    """
    id: str
    workspace_id: str
    title: Optional[str]
    content: str
    metadata: Dict[str, Any]


@dataclass
class Chunk:
    """
    Represents a chunked segment of a Document.

    Attributes:
        id: Unique identifier for the chunk.
        document_id: Identifier of the source document.
        text: Textual content of the chunk.
        metadata: Chunk-level metadata (offset, tokenizer info, provenance, etc.).
        vector: Optional embedding vector assigned during indexing.
    """
    id: str
    document_id: str
    text: str
    metadata: Dict[str, Any]
    vector: Optional[List[float]] = None


@dataclass
class RetrievalResult:
    """
    Represents a single retrieval result from the vector store.

    Attributes:
        id: Identifier of the chunk or object retrieved.
        score: Relevance score (higher = more relevant).
        source: Source type ('vector', etc.).
        payload: Arbitrary payload containing chunk text, metadata, and provenance.
    """
    id: str
    score: float
    source: str
    payload: Dict[str, Any]


@dataclass
class RagConfig:
    """
    Configuration parameters for a Vector-RAG workspace or instance.

    Attributes:
        workspace_id: Workspace or tenant identifier.
        chunking_strategy: Chunking method (e.g., 'sentence', 'paragraph', 'custom').
        embedding_model: Name of the embedding model to use.
        embedding_dim: Dimensionality of the embedding vectors.
        top_k: Default number of results to retrieve for queries.
    """
    workspace_id: str
    chunking_strategy: str
    embedding_model: str
    embedding_dim: int
    top_k: int = 8


# -----------------------------
# Ingestion Interfaces
# -----------------------------

class DocumentParser(ABC):
    """
    Converts raw document bytes into structured Document objects.
    """
    @abstractmethod
    def parse(self, raw: bytes, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """
        Parse raw document bytes into a Document.

        Args:
            raw: Binary content of the document.
            metadata: Optional metadata to attach to the document.

        Returns:
            Document object containing text and metadata.
        """
        raise NotImplementedError


class Chunker(ABC):
    """
    Splits Document content into smaller, semantically meaningful chunks.
    """
    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]:
        """
        Chunk the document into a list of Chunk objects.

        Args:
            document: Document to split into chunks.

        Returns:
            List of Chunk objects.
        """
        raise NotImplementedError


class MetadataEnricher(ABC):
    """
    Enriches chunks with additional metadata (e.g., token count, language, provenance).
    """
    @abstractmethod
    def enrich(self, chunk: Chunk) -> Chunk:
        """
        Add or modify metadata for a chunk.

        Args:
            chunk: Chunk to enrich.

        Returns:
            Enriched Chunk object.
        """
        raise NotImplementedError


# -----------------------------
# Embedding Interfaces
# -----------------------------

class EmbeddingEncoder(ABC):
    """
    Encodes text into vector representations for similarity search.
    """
    @abstractmethod
    def encode(self, texts: Iterable[str]) -> List[List[float]]:
        """
        Batch-encode multiple strings into vectors.

        Args:
            texts: Iterable of strings to encode.

        Returns:
            List of embedding vectors (one per text).
        """
        raise NotImplementedError

    @abstractmethod
    def encode_one(self, text: str) -> List[float]:
        """
        Encode a single string into a vector.

        Args:
            text: Input string.

        Returns:
            Vector representation of the text.
        """
        raise NotImplementedError


# -----------------------------
# Vector Storage & Retrieval
# -----------------------------

class VectorIndex(ABC):
    """
    Abstract vector storage interface.
    """
    @abstractmethod
    def upsert(self, id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        """
        Insert or update a vector in the store.

        Args:
            id: Unique identifier for the vector.
            vector: Vector embedding.
            metadata: Metadata associated with the vector.
        """
        raise NotImplementedError

    @abstractmethod
    def upsert_many(self, items: Iterable[Tuple[str, List[float], Dict[str, Any]]]) -> None:
        """
        Batch upsert multiple vectors.

        Args:
            items: Iterable of (id, vector, metadata) tuples.
        """
        raise NotImplementedError

    @abstractmethod
    def similarity_search(self, vector: List[float], top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[RetrievalResult]:
        """
        Retrieve the top-k most similar vectors.

        Args:
            vector: Query vector.
            top_k: Number of results to retrieve.
            filters: Optional metadata filters.

        Returns:
            List of RetrievalResult objects.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: str) -> None:
        """
        Delete a vector by its ID.

        Args:
            id: Vector identifier to delete.
        """
        raise NotImplementedError


class VectorRetriever(ABC):
    """
    High-level interface for retrieving top-k vectors from a VectorIndex.
    """
    @abstractmethod
    def retrieve(self, query_vector: List[float], k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[RetrievalResult]:
        """
        Retrieve top-k relevant chunks from the vector store.

        Args:
            query_vector: Query embedding vector.
            k: Number of results to retrieve.
            filters: Optional metadata filters.

        Returns:
            List of RetrievalResult objects.
        """
        raise NotImplementedError


# -----------------------------
# Ranking & Context Interfaces
# -----------------------------

class Ranker(ABC):
    """
    Re-ranks retrieved chunks to improve relevance for LLM context.
    """
    @abstractmethod
    def rerank(self, candidates: List[RetrievalResult], query: Optional[str] = None, top_k: Optional[int] = None) -> List[RetrievalResult]:
        """
        Re-rank retrieval candidates.

        Args:
            candidates: List of retrieved results.
            query: Optional query string for cross-encoder ranking.
            top_k: Optional limit for top-k results.

        Returns:
            Re-ranked list of RetrievalResult.
        """
        raise NotImplementedError


class ContextBuilder(ABC):
    """
    Constructs LLM prompt from ranked chunks.
    """
    @abstractmethod
    def build(self, ranked_results: List[RetrievalResult], query: Optional[str] = None, max_tokens: Optional[int] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Build LLM context from retrieved chunks.

        Args:
            ranked_results: List of ranked RetrievalResult objects.
            query: Original user query.
            max_tokens: Optional maximum token limit.

        Returns:
            Tuple of (prompt_text, metadata dictionary).
        """
        raise NotImplementedError


# -----------------------------
# LLM & Output Interfaces
# -----------------------------

class LLM(ABC):
    """
    Interface for large language models.
    """
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512, stop: Optional[List[str]] = None) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: Input text prompt.
            max_tokens: Maximum number of tokens to generate.
            stop: Optional list of stop sequences.

        Returns:
            Generated text string.
        """
        raise NotImplementedError

    @abstractmethod
    def stream_generate(self, prompt: str, max_tokens: int = 512, stop: Optional[List[str]] = None) -> Iterable[str]:
        """
        Stream generation output.

        Args:
            prompt: Input prompt.
            max_tokens: Maximum tokens to generate.
            stop: Optional stop sequences.

        Yields:
            Partial text chunks as they are generated.
        """
        raise NotImplementedError


class OutputFormatter(ABC):
    """
    Formats raw LLM output for user consumption.
    """
    @abstractmethod
    def format(self, raw_output: str, context_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format the LLM output into structured form.

        Args:
            raw_output: Raw text from LLM.
            context_metadata: Optional metadata from context building.

        Returns:
            Dictionary containing:
                'answer': str
                'provenance': list
                'raw': str
        """
        raise NotImplementedError


# -----------------------------
# Concrete Orchestrators
# -----------------------------

class VectorRAGIndexer:
    """
    Concrete ingestion pipeline for Vector-RAG.

    Responsibilities:
        - Parse documents
        - Chunk text
        - Enrich chunk metadata
        - Encode vectors
        - Upsert vectors into VectorIndex
    """
    def __init__(
        self,
        parser: DocumentParser,
        chunker: Chunker,
        enricher: MetadataEnricher,
        embedder: EmbeddingEncoder,
        vector_index: VectorIndex,
        config: Optional[RagConfig] = None,
    ):
        self.parser = parser
        self.chunker = chunker
        self.enricher = enricher
        self.embedder = embedder
        self.vector_index = vector_index
        self.config = config

    def ingest(self, raw_documents: Iterable[Tuple[bytes, Optional[Dict[str, Any]]]]) -> List[str]:
        """
        Ingest raw documents into the vector store.

        Args:
            raw_documents: Iterable of tuples (raw_bytes, optional_metadata).

        Returns:
            List of upserted vector IDs.
        """
        upserted_ids: List[str] = []

        for raw, meta in raw_documents:
            doc = self.parser.parse(raw, metadata=meta or {})
            chunks = self.chunker.chunk(doc)
            texts = [chunk.text for chunk in chunks]
            vectors = self.embedder.encode(texts)

            for chunk, vector in zip(chunks, vectors):
                enriched = self.enricher.enrich(chunk)
                enriched.vector = vector
                vec_id = enriched.metadata.get("vector_id") or enriched.id
                vec_meta = dict(enriched.metadata)
                vec_meta.update({"document_id": enriched.document_id, "chunk_id": enriched.id})
                self.vector_index.upsert(vec_id, vector, vec_meta)
                upserted_ids.append(vec_id)

        return upserted_ids


class VectorRAG:
    """
    Concrete query-side orchestrator for Vector-RAG.

    Responsibilities:
        - Encode query
        - Retrieve top-k vectors
        - Re-rank candidates
        - Build LLM context
        - Generate answer
        - Format output
    """
    def __init__(
        self,
        embedder: EmbeddingEncoder,
        vector_retriever: VectorRetriever,
        ranker: Ranker,
        context_builder: ContextBuilder,
        llm: LLM,
        formatter: OutputFormatter,
        config: Optional[RagConfig] = None,
    ):
        self.embedder = embedder
        self.vector_retriever = vector_retriever
        self.ranker = ranker
        self.context_builder = context_builder
        self.llm = llm
        self.formatter = formatter
        self.config = config

    def query(self, query_text: str, k: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute full Vector-RAG query pipeline.

        Args:
            query_text: User input question or prompt.
            k: Optional top-k results to retrieve.

        Returns:
            Formatted dictionary with 'answer', 'provenance', and 'raw'.
        """
        top_k = k or (self.config.top_k if self.config else 8)

        query_vec = self.embedder.encode_one(query_text)
        retrieved = self.vector_retriever.retrieve(query_vec, k=top_k)
        ranked = self.ranker.rerank(retrieved, query=query_text, top_k=top_k)
        prompt_text, context_metadata = self.context_builder.build(ranked, query=query_text)
        raw_output = self.llm.generate(prompt_text)
        formatted = self.formatter.format(raw_output, context_metadata)
        return formatted
