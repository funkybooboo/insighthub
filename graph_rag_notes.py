# Below is a comprehensive breakdown of **all the major parts of a Graph-RAG system** and the **algorithms / technologies** commonly used in each layer. This is a full stack view—from ingestion → storage → retrieval → reasoning.
#
# ---
#
# # **Parts of a Graph-RAG System**
#
# A Graph-RAG system is usually composed of **8 major subsystems**:
#
# ---
#
# ## **1. Ingestion & Chunking**
#
# Processes raw documents into structured pieces for indexing.
#
# ### **Techniques / Algorithms**
#
# * **Text splitting / chunking**
#
#   * Sentence-based chunking
#   * Recursive chunking
#   * Sliding window chunking
#   * Semantic chunking (via embedding similarity)
# * **Document parsing**
#
#   * PDF → text
#   * HTML parsing
#   * OCR (Tesseract, PaddleOCR)
#
# ### **Technologies**
#
# * LangChain text splitters
# * LlamaIndex node parser
# * PyPDF2 / pdfminer
# * spaCy / NLTK
#
# ---
#
# ## **2. Embeddings**
#
# Convert text to vectors and create semantic representations.
#
# ### **Algorithms**
#
# * Transformer embedding models (BERT-style, LLM encoder models)
# * Contrastive embedding models (e.g., SimCSE)
# * Dimensionality reduction:
#
#   * PCA
#   * LSH (Locality Sensitive Hashing)
#   * FAISS OPQ/IVF/HNSW quantization
#
# ### **Technologies**
#
# * OpenAI embeddings
# * SentenceTransformers
# * HuggingFace models
# * FAISS / HNSWlib (on client side)
#
# ---
#
# ## **3. Graph Construction**
#
# Converts documents into graph structures.
#
# ### **Graph Types**
#
# * **Knowledge Graph** (entities + relations)
# * **Semantic Graph** (chunks + similarity edges)
# * **Citation graph** (doc references)
# * **Topic graph** (clusters)
#
# ### **Algorithms**
#
# * Named Entity Recognition (NER)
# * Relation extraction (RE)
# * Dependency parsing
# * Clustering:
#
#   * K-Means, HDBSCAN
#   * Community detection (Louvain, Leiden)
# * Graph-building:
#
#   * Triplet extraction (LLM-based)
#   * Co-occurrence extraction
#   * Similarity graph construction using k-NN graph building
#
#     * k-NN (HNSW)
#     * Mutual k-NN
#
# ### **Technologies**
#
# * spaCy NER
# * HuggingFace RE models
# * Neo4j
# * Memgraph
# * ArangoDB
# * Weaviate Graph extension
# * TigerGraph
# * LlamaIndex KG builder
#
# ---
#
# ## **4. Graph Storage**
#
# Stores nodes, relationships, vectors.
#
# ### **Types of Storage**
#
# * Graph database
# * Vector store
# * Document store
#
# ### **Graph DB Technologies**
#
# * **Neo4j** (leading choice)
# * ArangoDB (multi-model)
# * Memgraph (fast, in-memory)
# * JanusGraph
# * Dgraph
# * Amazon Neptune
#
# ### **Vector Stores**
#
# * FAISS
# * Milvus
# * Weaviate
# * Pinecone
# * ChromaDB
# * Qdrant
#
# ---
#
# ## **5. Graph Retrieval**
#
# Retrieves relevant nodes and subgraphs for answering.
#
# ### **Retrieval Algorithms**
#
# * **Vector similarity search**
#
#   * HNSW
#   * IVF+PQ
#   * Annoy
# * **Graph traversal**
#
#   * BFS / DFS
#   * Personalized PageRank
#   * Random Walk with Restart
# * **Path-finding**
#
#   * Dijkstra
#   * A*
# * **Community-based retrieval**
#
#   * Louvain / Leiden cluster-based narrowing
# * **Subgraph extraction**
#
#   * k-hop neighborhood
#   * Ego-networks
#   * Reasoning chains (LLM-guided BFS)
#
# ### **Technologies**
#
# * Cypher queries (Neo4j)
# * Gremlin
# * GQL
# * GraphQL extensions
# * LlamaIndex GraphRetrievers
#
# ---
#
# ## **6. Ranking & Fusion**
#
# Blend vector similarity, graph relevance, and semantic significance.
#
# ### **Algorithms**
#
# * Reciprocal Rank Fusion (RRF)
# * Weighted scoring:
#
#   * α * vector_score + β * graph_score
# * Reranking:
#
#   * Cross-encoder rerankers (BERT, mini-LM)
# * Diversity algorithms:
#
#   * Maximal Marginal Relevance (MMR)
#   * Graph diversification (degree weighting)
#
# ### **Technologies**
#
# * OpenAI / Cohere rerankers
# * ReRank-BERT
# * ColBERT (late interaction search)
# * LlamaIndex fusion retrievers
#
# ---
#
# ## **7. Context Construction / Orchestration**
#
# Constructs the final context window for the LLM.
#
# ### **Algorithms**
#
# * Graph-based summarization:
#
#   * TextRank
#   * LexRank
#   * LLM-based summarization
# * Node ranking
#
#   * PageRank
#   * Closeness centrality
#   * GraphRank
# * Conversation memory selection
#
# ### **Technologies**
#
# * LangChain expression graph
# * LlamaIndex context builders
# * Custom score aggregators
#
# ---
#
# ## **8. LLM Reasoning Layer**
#
# Generates the final answer using retrieved graph context.
#
# ### **Techniques**
#
# * Chain-of-Thought (CoT)
# * Graph reasoning prompts
# * Subgraph → JSON → LLM reasoning
# * Multi-hop reasoning
# * Agentic refinement (RAG agents)
#
# ### **Technologies**
#
# * GPT-5 / GPT-4o
# * Llama 3.1
# * Claude
# * Mistral
#
# ---
#
# # **Complete List: Algorithms Used in Graph-RAG**
#
# ### **Text Processing**
#
# * Sentence splitting
# * Semantic chunking
# * TF-IDF
#
# ### **Embedding & Similarity**
#
# * Transformer embeddings
# * Cosine similarity
# * LSH
# * HNSW
# * IVF/OPQ
#
# ### **Graph Generation**
#
# * NER
# * RE
# * Triplet extraction
# * Clustering (Louvain, HDBSCAN, K-Means)
# * k-NN graph building
# * Community detection
# * Co-occurrence extraction
#
# ### **Graph Retrieval**
#
# * BFS, DFS
# * Personalized PageRank
# * Random walk
# * 1-hop, 2-hop, k-hop expansion
# * Ego network extraction
# * Weighted multi-hop traversal
# * Dijkstra/A*
#
# ### **Ranking / Fusion**
#
# * RRF (Reciprocal Rank Fusion)
# * BM25 (if using keywords)
# * MMR
# * Rerankers (cross-encoders)
# * Degree / centrality scoring
#
# ### **Graph Summarization**
#
# * TextRank
# * LexRank
# * LLM summary merging
# * Keyphrase extraction
#
# ### **LLM Reasoning**
#
# * CoT
# * Graph reasoning templates
# * Semantic compression
#
# ---
#
# # **Want a diagram of the whole system?**
#
# Below is a **clean, implementation-agnostic** architecture diagram of a **Graph-RAG workflow**, expressed entirely in terms of **interfaces**, **responsibilities**, and **data flow**—not vendors or technologies.
#
# ---
#
# # ** Graph-RAG System — High-Level Workflow Diagram (Interface-Level)**
#
# ```
#                     ┌────────────────────────────────────────┐
#                     │            1. Document Source           │
#                     │  (FileInput, WebInput, StreamInput)    │
#                     └────────────────────────────────────────┘
#                                       │
#                                       ▼
#                     ┌────────────────────────────────────────┐
#                     │         2. Ingestion Pipeline           │
#                     │ (DocumentParser, Chunker, MetadataEnricher)
#                     └────────────────────────────────────────┘
#                                       │
#                                       ▼
#             ┌──────────────────────────────────────────────────────────┐
#             │                    3. Embedding Layer                     │
#             │ (EmbeddingEncoder → Vector: float[], EmbedMetadataEncoder)│
#             └──────────────────────────────────────────────────────────┘
#                                       │
#               ┌───────────────────────┴────────────────────────┐
#               ▼                                                ▼
# ┌────────────────────────────────────────────┐   ┌───────────────────────────────┐
# │   4A. Knowledge Graph Construction Layer    │   │     4B. Vector Index Layer    │
# │ (EntityExtractor, RelationExtractor,        │   │  (VectorIndex, VectorWriter)  │
# │  GraphBuilder, GraphSchemaAdapter)          │   │                               │
# └────────────────────────────────────────────┘   └───────────────────────────────┘
#               │                                                │
#               ▼                                                ▼
# ┌─────────────────────────────────────────────┐   ┌────────────────────────────────────────┐
# │         5A. Graph Store Interface           │   │           5B. Vector Store Interface   │
# │ (GraphStore: add_nodes/edges, query_paths,  │   │ (VectorStore: upsert, similarity_search) │
# │  query_neighbors, query_subgraph)           │   └────────────────────────────────────────┘
# └─────────────────────────────────────────────┘
#               │                                                │
#               └───────────────┬────────────────────────────────┘
#                               ▼
#                 ┌────────────────────────────────────────┐
#                 │          6. Retrieval Orchestrator      │
#                 │  (retrieves via GraphRetriever +        │
#                 │   VectorRetriever + HybridRetriever)    │
#                 └────────────────────────────────────────┘
#                               │
#                               ▼
#                 ┌────────────────────────────────────────┐
#                 │          7. Ranking & Fusion Layer      │
#                 │   (Ranker, Reranker, Fusion Scorer,     │
#                 │    DiversitySelector)                   │
#                 └────────────────────────────────────────┘
#                               │
#                               ▼
#                 ┌────────────────────────────────────────┐
#                 │        8. Context Builder               │
#                 │  (ContextSummarizer, NodeExpander,      │
#                 │   ContextCompressor, ProvenanceBinder)  │
#                 └────────────────────────────────────────┘
#                               │
#                               ▼
#                 ┌────────────────────────────────────────┐
#                 │           9. LLM Reasoning Layer        │
#                 │ (LLMInterface: generate, reason, refine)│
#                 └────────────────────────────────────────┘
#                               │
#                               ▼
#                 ┌────────────────────────────────────────┐
#                 │            10. Final Answer             │
#                 │   (includes summaries + citations)      │
#                 └────────────────────────────────────────┘
# ```
#
# ---
#
# # ** Component Responsibilities (Interface-First View)**
#
# Below is the same workflow described purely using interface semantics.
#
# ---
#
# ## **1. Document Source**
#
# Interfaces:
#
# * `FileInput`
# * `WebInput`
# * `StreamInput`
#
# Responsibilities:
#
# * Provide raw bytes or text streams to ingestion.
#
# ---
#
# ## **2. Ingestion Pipeline**
#
# Interfaces:
#
# * `DocumentParser`
# * `Chunker`
# * `MetadataEnricher`
#
# Responsibilities:
#
# * Convert input → text → structured chunks.
# * Assign IDs, metadata, timestamps.
#
# ---
#
# ## **3. Embedding Layer**
#
# Interfaces:
#
# * `EmbeddingEncoder`
# * `EmbedMetadataEncoder`
#
# Responsibilities:
#
# * Convert text or metadata into dense vectors.
# * Provide unified embedding contract:
#
#   ```
#   encode(text) -> float[]
#   ```
#
# ---
#
# ## **4A. Knowledge Graph Construction Layer**
#
# Interfaces:
#
# * `EntityExtractor`
# * `RelationExtractor`
# * `GraphBuilder`
# * `GraphSchemaAdapter`
#
# Responsibilities:
#
# * Produce nodes + edges from text chunks.
# * Normalize them to the graph schema interface.
#
# ---
#
# ## **4B. Vector Index Layer**
#
# Interfaces:
#
# * `VectorIndex`
# * `VectorWriter`
#
# Responsibilities:
#
# * Index embeddings for similarity search.
#
# ---
#
# ## **5A. Graph Store Interface**
#
# A normalized database abstractor:
#
# ```
# GraphStore:
#     add_nodes(nodes)
#     add_edges(edges)
#     query_nodes(filter)
#     query_neighbors(node_id)
#     query_paths(start, end, constraints)
#     query_subgraph(seed, hops)
# ```
#
# ---
#
# ## **5B. Vector Store Interface**
#
# Abstract vector search:
#
# ```
# VectorStore:
#     upsert(id, vector, metadata)
#     similarity_search(vector, k) -> results[]
#     delete(id)
# ```
#
# ---
#
# ## **6. Retrieval Orchestrator**
#
# Interfaces:
#
# * `GraphRetriever`
# * `VectorRetriever`
# * `HybridRetriever`
#
# Responsibilities:
#
# * Decide which retriever(s) to use.
# * Merge graph neighborhoods + vector results.
# * Apply constraints (k-hop, depth, relevance thresholds).
#
# ---
#
# ## **7. Ranking & Fusion Layer**
#
# Interfaces:
#
# * `Ranker`
# * `Reranker`
# * `FusionScorer`
# * `DiversitySelector`
#
# Responsibilities:
#
# * Sort by relevance.
# * Combine graph + vector scores.
# * Rerank using semantic relevance.
# * Ensure output is diverse, non-redundant.
#
# ---
#
# ## **8. Context Builder**
#
# Interfaces:
#
# * `ContextSummarizer`
# * `NodeExpander`
# * `ContextCompressor`
# * `ProvenanceBinder`
#
# Responsibilities:
#
# * Convert retrieved nodes/chunks into an LLM-friendly prompt window.
# * Maintain citations + provenance.
# * Compress if window exceeds model limits.
#
# ---
#
# ## **9. LLM Reasoning Layer**
#
# Interface:
#
# * `LLMInterface`
#
#   ```
#   generate(prompt)
#   reason(graph_context)
#   refine(previous_output)
#   ```
#
# Responsibilities:
#
# * Perform synthesis, reasoning, refinement.
# * Use context built from graph + vector search.
#
# ---
#
# ## **10. Final Answer**
#
# * Structured output returned to the end-user.
# * Includes:
#
#   * answer text
#   * references
#   * extracted knowledge
#   * optional JSON reasoning

"""
graph_rag_interfaces_and_orchestrators.py

Single-file, implementation-agnostic, fully-documented Python API for a Graph-RAG system.

Contents:
- Helper datatypes (Document, Chunk, GraphNode, GraphEdge, RetrievalResult, RagConfig)
- All interfaces (ABC classes) required for ingestion, embedding, graph construction,
  storage, retrieval, ranking, context building, LLM, and output formatting.
- Two concrete orchestrators:
    * GraphRAGIndexer  -- concrete ingestion/indexing pipeline (Document -> vectors + graph)
    * GraphRAG         -- concrete query pipeline (Query -> Retrieval -> LLM -> Answer)

Notes:
- This file contains *only* interfaces and the orchestrators. No concrete implementations
  for vector stores, graph DBs, embedders, etc. are included.
- Implementations should adhere to these interfaces and be injected into the orchestrators.
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
    Represents a logical document uploaded to the system.

    Fields:
      id: stable identifier for the document (string)
      workspace_id: identifier for workspace/tenant
      title: optional human-readable title
      content: raw (already-decoded) textual content of the document
      metadata: arbitrary metadata (source, author, timestamps, original filename, etc.)
    """
    id: str
    workspace_id: str
    title: Optional[str]
    content: str
    metadata: Dict[str, Any]


@dataclass
class Chunk:
    """
    Represents a chunked piece of a document.

    Fields:
      id: unique id (often document_id::offset or uuid)
      document_id: original document.id
      text: chunk text content
      metadata: chunk-level metadata (offset, tokenizer info, etc.)
      vector: optional embedding vector (set by embedder during ingestion)
    """
    id: str
    document_id: str
    text: str
    metadata: Dict[str, Any]
    vector: Optional[List[float]] = None


@dataclass
class GraphNode:
    """
    Graph node representation (normalized schema-level type).
    Implementations may map this to DB-specific node objects.
    """
    id: str
    labels: List[str]
    properties: Dict[str, Any]


@dataclass
class GraphEdge:
    """
    Graph edge representation connecting two nodes.
    """
    id: str
    source: str
    target: str
    label: str
    properties: Dict[str, Any]


@dataclass
class RetrievalResult:
    """
    Standardized retrieval result used across vector and graph retrieval.

    Fields:
      id: id of the returned object (chunk id, node id, vector id, etc.)
      score: normalized relevance score (higher = more relevant)
      source: string describing source modality ('vector', 'graph', 'doc', etc.)
      payload: arbitrary payload dictionary (text snippet, node properties, provenance, etc.)
    """
    id: str
    score: float
    source: str
    payload: Dict[str, Any]


@dataclass
class RagConfig:
    """
    Configuration for a RAG workspace or instance.

    Fields:
      workspace_id: workspace/tenant id
      rag_type: 'vector' | 'graph' | 'hybrid'
      chunking_strategy: e.g. 'sentence' | 'recursive' | 'custom'
      embedding_model: name of embedding model or implementation key
      embedding_dim: dimensionality of embedding vectors
      top_k: default number of results to retrieve
    """
    workspace_id: str
    rag_type: str
    chunking_strategy: str
    embedding_model: str
    embedding_dim: int
    top_k: int = 8


# -----------------------------
# Ingestion Interfaces
# -----------------------------


class DocumentParser(ABC):
    """
    Converts raw bytes (or file-like payload) into UTF-8 text ready for chunking.

    Implementations should handle PDFs, HTML, DOCX, plain text, etc.
    """

    @abstractmethod
    def parse(self, raw: bytes, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """
        Parse raw bytes -> Document dataclass.

        Args:
            raw: binary payload of the document
            metadata: optional metadata passed from upstream (uploader)
        Returns:
            Document
        """
        raise NotImplementedError


class Chunker(ABC):
    """
    Splits Document.content into chunks.
    """

    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]:
        """
        Chunk the document into a list of Chunk objects.

        Implementations should set chunk.id and chunk.document_id.

        Args:
            document: Document to split

        Returns:
            list of Chunk
        """
        raise NotImplementedError


class MetadataEnricher(ABC):
    """
    Adds or normalizes metadata at the chunk level.
    """

    @abstractmethod
    def enrich(self, chunk: Chunk) -> Chunk:
        """
        Add/modify chunk.metadata in-place or return a new Chunk.
        Examples of metadata: language, token_count, content_type, filename, hash.

        Args:
            chunk: chunk to enrich

        Returns:
            enriched Chunk
        """
        raise NotImplementedError


# -----------------------------
# Embedding Interfaces
# -----------------------------


class EmbeddingEncoder(ABC):
    """
    Encodes text into numerical vectors.

    Implementations may call remote APIs or local models.
    """

    @abstractmethod
    def encode(self, texts: Iterable[str]) -> List[List[float]]:
        """
        Batch-encode multiple strings into list of vectors.

        Args:
            texts: iterable of str

        Returns:
            list of embedding vectors (one per text)
        """
        raise NotImplementedError

    @abstractmethod
    def encode_one(self, text: str) -> List[float]:
        """
        Encode a single string.

        Args:
            text: input text

        Returns:
            vector
        """
        raise NotImplementedError


# -----------------------------
# Graph Construction Interfaces
# -----------------------------


class EntityExtractor(ABC):
    """
    Extract entity candidates (concepts, named entities, keyphrases) from text.
    """

    @abstractmethod
    def extract_entities(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Return a list of entity dictionaries with keys such as:
            - id (optional)
            - label or type
            - mention/text
            - span offsets
            - confidence

        Implementations should produce normalized entity representations suitable for GraphBuilder.
        """
        raise NotImplementedError


class RelationExtractor(ABC):
    """
    Extract relations between entities described in a piece of text.
    """

    @abstractmethod
    def extract_relations(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Return list of relations, each relation being a dict with keys:
            - source_entity_id
            - target_entity_id
            - predicate/label
            - confidence
            - properties (optional)
        """
        raise NotImplementedError


class GraphBuilder(ABC):
    """
    Convert normalized entity/relation dicts -> GraphNode / GraphEdge dataclasses.
    """

    @abstractmethod
    def build_nodes(self, entities: List[Dict[str, Any]]) -> List[GraphNode]:
        """
        Convert entity dicts into GraphNode objects ready to be persisted.
        """
        raise NotImplementedError

    @abstractmethod
    def build_edges(self, relations: List[Dict[str, Any]]) -> List[GraphEdge]:
        """
        Convert relation dicts into GraphEdge objects ready to be persisted.
        """
        raise NotImplementedError


# -----------------------------
# Storage Interfaces
# -----------------------------


class GraphStore(ABC):
    """
    Abstract knowledge graph store interface.

    Must support node & edge upsert, neighborhood queries, path queries, and deletion.
    """

    @abstractmethod
    def add_nodes(self, nodes: Iterable[GraphNode]) -> None:
        """
        Upsert nodes into the graph store.

        Implementations should be idempotent (safe to call multiple times).
        """
        raise NotImplementedError

    @abstractmethod
    def add_edges(self, edges: Iterable[GraphEdge]) -> None:
        """
        Upsert edges into the graph store.
        """
        raise NotImplementedError

    @abstractmethod
    def query_neighbors(self, node_id: str, hops: int = 1, limit: int = 100) -> List[GraphNode]:
        """
        Return neighbor nodes within `hops` hops of the given node_id.
        """
        raise NotImplementedError

    @abstractmethod
    def query_subgraph(self, seed_ids: Iterable[str], hops: int = 1, limit: int = 100) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """
        Return nodes and edges in the k-hop subgraph around `seed_ids`.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_nodes(self, ids: Iterable[str]) -> None:
        """
        Delete nodes by id; also consider cleaning up incident edges as needed.
        """
        raise NotImplementedError


class VectorIndex(ABC):
    """
    Abstract vector index interface (vector store).

    Responsibilities:
      - upsert vector + metadata
      - similarity search
      - delete vectors by id
    """

    @abstractmethod
    def upsert(self, id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        """
        Insert or update a vector with metadata. Implementations should be idempotent.
        """
        raise NotImplementedError

    @abstractmethod
    def upsert_many(self, items: Iterable[Tuple[str, List[float], Dict[str, Any]]]) -> None:
        """
        Batch upsert many vectors.
        """
        raise NotImplementedError

    @abstractmethod
    def similarity_search(self, vector: List[float], top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[RetrievalResult]:
        """
        Return top_k RetrievalResult entries for the query vector. `filters` is optional metadata filter.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: str) -> None:
        """
        Delete vector by id.
        """
        raise NotImplementedError


# -----------------------------
# Retrieval Interfaces
# -----------------------------


class VectorRetriever(ABC):
    """
    High-level vector retrieval abstraction that uses a VectorIndex under the hood.
    """

    @abstractmethod
    def retrieve(self, query_vector: List[float], k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[RetrievalResult]:
        """
        Return top-k RetrievalResult from the vector index for the given query_vector.
        """
        raise NotImplementedError


class GraphRetriever(ABC):
    """
    High-level graph retrieval abstraction that queries the GraphStore.
    """

    @abstractmethod
    def retrieve_by_seed(self, seed_ids: Iterable[str], hops: int = 1, limit: int = 100) -> List[RetrievalResult]:
        """
        Return RetrievalResult items (node metadata, scores) from graph neighborhood expansion.
        """
        raise NotImplementedError

    @abstractmethod
    def retrieve_by_query(self, query: str, limit: int = 100) -> List[RetrievalResult]:
        """
        Return RetrievalResult items using structured graph queries / semantic matching.
        """
        raise NotImplementedError


class HybridRetriever(ABC):
    """
    Combines vector + graph retrieval strategies into a single interface.

    Typical strategies:
      - vector-first: get top vectors -> expand via graph
      - graph-first: find entities -> use their embeddings as seeds
      - interleaved: interleave both
    """

    @abstractmethod
    def retrieve(self, query: str, k: int = 10, hops: int = 1) -> List[RetrievalResult]:
        """
        Return fused retrieval results (unsorted or lightly scored).
        """
        raise NotImplementedError


# -----------------------------
# Ranking & Fusion Interfaces
# -----------------------------


class FusionScorer(ABC):
    """
    Combine and re-score vector + graph results into a unified list.
    """

    @abstractmethod
    def fuse(self, vector_results: List[RetrievalResult], graph_results: List[RetrievalResult]) -> List[RetrievalResult]:
        """
        Return a merged list of RetrievalResult with updated scores (higher => better).
        Should not perform expensive cross-encoder reranking (that is Ranker job).
        """
        raise NotImplementedError


class Ranker(ABC):
    """
    Expensive/reranking stage (optionally uses cross-encoders).
    """

    @abstractmethod
    def rerank(self, candidates: List[RetrievalResult], query: Optional[str] = None, top_k: Optional[int] = None) -> List[RetrievalResult]:
        """
        Return a reranked/subset of candidates (top_k if provided).
        """
        raise NotImplementedError


# -----------------------------
# Context Building Interface
# -----------------------------


class ContextBuilder(ABC):
    """
    Build the LLM prompt/context window from ranked retrieval results.

    Responsibilities:
      - Assemble textual context segments (snippets, summaries)
      - Attach provenance for each snippet
      - Compress or summarize when token limits are exceeded
    """

    @abstractmethod
    def build(self, ranked_results: List[RetrievalResult], query: Optional[str] = None, max_tokens: Optional[int] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Build the prompt text and return a tuple (prompt_text, metadata) where metadata
        contains provenance information (list of ids, original scores, sources).
        """
        raise NotImplementedError


# -----------------------------
# LLM & Output Interfaces
# -----------------------------


class LLM(ABC):
    """
    Abstraction for an LLM provider.

    Responsibilities:
      - generate text from prompts
      - optionally support streaming, stopping tokens, system/instruction prompts
    """

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512, stop: Optional[List[str]] = None) -> str:
        """
        Synchronous generation.

        Returns the raw text output of the model.
        """
        raise NotImplementedError

    @abstractmethod
    def stream_generate(self, prompt: str, max_tokens: int = 512, stop: Optional[List[str]] = None) -> Iterable[str]:
        """
        Optional streaming generator that yields partial text chunks.
        If streaming is not supported, implementations may raise NotImplementedError.
        """
        raise NotImplementedError


class OutputFormatter(ABC):
    """
    Format the raw LLM outputs into user-facing answer objects.

    Responsibilities:
      - clean final text
      - attach citations and provenance
      - optionally return a structured JSON with answer, provenance, source list
    """

    @abstractmethod
    def format(self, raw_output: str, context_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format and return a dictionary containing at least:
          - 'answer': str
          - 'provenance': list
          - 'raw': raw_output
        """
        raise NotImplementedError


# -----------------------------
# Document Store Interface (DB + Cache)
# -----------------------------


class DocumentStore(ABC):
    """
    Persistent storage for original documents, with a read-through cache (e.g., Redis).

    Contract:
      - save_document writes to persistent DB and optionally updates cache
      - load_document tries cache first then DB
      - list_documents returns document metadata for a workspace
    """

    @abstractmethod
    def save_document(self, document: Document) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_document(self, document_id: str) -> Document:
        raise NotImplementedError

    @abstractmethod
    def list_documents(self, workspace_id: str) -> List[Document]:
        raise NotImplementedError


# -----------------------------
# Concrete Orchestrators (Template-Method Style, Concrete)
# -----------------------------


class GraphRAGIndexer:
    """
    Concrete ingestion/indexing orchestrator.

    Responsibilities:
      - Parse raw documents
      - Chunk documents
      - Enrich chunk metadata
      - Encode embeddings
      - Upsert vectors to VectorIndex
      - Extract entities/relations and build GraphNode/GraphEdge
      - Persist nodes/edges to GraphStore

    All processing steps are pluggable via interface injection.
    """

    def __init__(
        self,
        parser: DocumentParser,
        chunker: Chunker,
        enricher: MetadataEnricher,
        embedder: EmbeddingEncoder,
        vector_index: VectorIndex,
        entity_extractor: EntityExtractor,
        relation_extractor: RelationExtractor,
        graph_builder: GraphBuilder,
        graph_store: GraphStore,
        document_store: Optional[DocumentStore] = None,
        config: Optional[RagConfig] = None,
    ):
        self.parser = parser
        self.chunker = chunker
        self.enricher = enricher
        self.embedder = embedder
        self.vector_index = vector_index
        self.entity_extractor = entity_extractor
        self.relation_extractor = relation_extractor
        self.graph_builder = graph_builder
        self.graph_store = graph_store
        self.document_store = document_store
        self.config = config

    def ingest(self, raw_documents: Iterable[Tuple[bytes, Optional[Dict[str, Any]]]]) -> List[str]:
        """
        Index a set of raw documents.

        Args:
            raw_documents: iterable of tuples (raw_bytes, optional_metadata)

        Returns:
            list of upserted vector ids
        """
        upserted_ids: List[str] = []

        for raw, meta in raw_documents:
            # 1. parse
            doc = self.parser.parse(raw, metadata=meta or {})

            # 1.a optional persist original doc
            if self.document_store:
                try:
                    self.document_store.save_document(doc)
                except Exception:
                    # let implementations handle failure modes
                    pass

            # 2. chunk
            chunks = self.chunker.chunk(doc)

            # 3. per-chunk processing
            # batch encode capability: collect texts, call embedder.encode once per batch
            texts_batch = [chunk.text for chunk in chunks]
            if texts_batch:
                vectors = self.embedder.encode(texts_batch)
            else:
                vectors = []

            for chunk, vector in zip(chunks, vectors):
                # 3.a enrich metadata
                enriched = self.enricher.enrich(chunk)

                # 3.b attach vector
                enriched.vector = vector

                # 3.c upsert vector
                vec_id = enriched.metadata.get("vector_id") or enriched.id
                # ensure metadata includes source info (document id, chunk id)
                vec_meta = dict(enriched.metadata)
                vec_meta.update({"document_id": enriched.document_id, "chunk_id": enriched.id})
                self.vector_index.upsert(vec_id, vector, vec_meta)
                upserted_ids.append(vec_id)

                # 3.d extract entities and relations
                entities = self.entity_extractor.extract_entities(enriched.text, enriched.metadata)
                relations = self.relation_extractor.extract_relations(enriched.text, entities)

                # 3.e build GraphNodes and GraphEdges
                nodes = self.graph_builder.build_nodes(entities)
                edges = self.graph_builder.build_edges(relations)

                # 3.f persist to graph store
                if nodes:
                    self.graph_store.add_nodes(nodes)
                if edges:
                    self.graph_store.add_edges(edges)

        return upserted_ids


class GraphRAG:
    """
    Concrete query-side orchestrator for Graph-RAG.

    Responsibilities:
      - encode query via embedder
      - retrieve via vector_retriever and graph_retriever or hybrid retriever
      - fuse and rerank
      - build LLM context
      - call LLM and format answer
    """

    def __init__(
        self,
        embedder: EmbeddingEncoder,
        vector_retriever: VectorRetriever,
        graph_retriever: GraphRetriever,
        fusion_scorer: FusionScorer,
        ranker: Ranker,
        context_builder: ContextBuilder,
        llm: LLM,
        formatter: OutputFormatter,
        hybrid_retriever: Optional[HybridRetriever] = None,
        config: Optional[RagConfig] = None,
    ):
        self.embedder = embedder
        self.vector_retriever = vector_retriever
        self.graph_retriever = graph_retriever
        self.fusion_scorer = fusion_scorer
        self.ranker = ranker
        self.context_builder = context_builder
        self.llm = llm
        self.formatter = formatter
        self.hybrid_retriever = hybrid_retriever
        self.config = config

    def query(self, query_text: str, k: Optional[int] = None, hops: int = 1) -> Dict[str, Any]:
        """
        Execute full query pipeline.

        Args:
            query_text: user question
            k: top-k requested (falls back to config.top_k if available)
            hops: graph expansion hops (used by graph retriever)

        Returns:
            formatted answer dict from OutputFormatter (contains 'answer', 'provenance', etc.)
        """
        top_k = k or (self.config.top_k if self.config else 8)

        # 1. encode query
        query_vec = self.embedder.encode_one(query_text)

        # 2. retrieve
        if self.hybrid_retriever:
            # allow hybrid retriever to control strategy
            raw_results = self.hybrid_retriever.retrieve(query_text, k=top_k, hops=hops)
            vector_results: List[RetrievalResult] = [r for r in raw_results if r.source == "vector"]
            graph_results: List[RetrievalResult] = [r for r in raw_results if r.source == "graph"]
        else:
            # vector-first + graph expansion
            vector_results = self.vector_retriever.retrieve(query_vec, k=top_k)
            # Use top vector ids as seeds to expand graph
            seed_ids = [r.id for r in vector_results[:top_k]]
            graph_results = self.graph_retriever.retrieve_by_seed(seed_ids, hops=hops, limit=top_k)

        # 3. fuse
        fused = self.fusion_scorer.fuse(vector_results, graph_results)

        # 4. rerank
        ranked = self.ranker.rerank(fused, query=query_text, top_k=top_k)

        # 5. build context
        prompt_text, context_metadata = self.context_builder.build(ranked, query=query_text, max_tokens=None)

        # 6. LLM
        raw_output = self.llm.generate(prompt_text)

        # 7. format result
        formatted = self.formatter.format(raw_output, context_metadata)

        return formatted
