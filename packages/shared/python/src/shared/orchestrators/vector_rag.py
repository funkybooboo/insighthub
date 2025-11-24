"""Vector RAG orchestrator for indexing and querying documents."""

from typing import List, BinaryIO

from shared.database.vector.vector_store import VectorStore
from shared.documents.chunking.document_chunker import Chunker
from shared.documents.embedding.vector_embedding_encoder import VectorEmbeddingEncoder
from shared.documents.parsing.document_parser import DocumentParser
from shared.types.document import Chunk, Document
from shared.types.retrieval import RetrievalResult


class VectorRAGIndexer:
    """
    Orchestrates the indexing part of the Vector RAG pipeline.
    """

    def __init__(
        self,
        parser: DocumentParser,
        chunker: Chunker,
        embedder: VectorEmbeddingEncoder,
        vector_store: VectorStore,
    ):
        """
        Initialize the VectorRAGIndexer.

        Args:
            parser: The document parser.
            chunker: The document chunker.
            embedder: The vector embedding encoder.
            vector_store: The vector store.
        """
        self.parser = parser
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store

    def index(self, file: BinaryIO, metadata: dict | None = None) -> Document:
        """
        Index a document.

        Args:
            file: The file to index.
            metadata: Optional metadata to attach to the document.

        Returns:
            The indexed document.
        """
        document_result = self.parser.parse(file, metadata)
        if document_result.is_err():
            raise document_result.err()

        document = document_result.ok()
        chunks = self.chunker.chunk(document)
        
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings_result = self.embedder.encode(chunk_texts)
        if embeddings_result.is_err():
            raise embeddings_result.err()

        embeddings = embeddings_result.ok()
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i]

        self.vector_store.add(chunks)
        document.chunk_count = len(chunks)
        return document


class VectorRAG:
    """
    Orchestrates the query part of the Vector RAG pipeline.
    """

    def __init__(
        self,
        embedder: VectorEmbeddingEncoder,
        vector_store: VectorStore,
    ):
        """
        Initialize the VectorRAG.

        Args:
            embedder: The vector embedding encoder.
            vector_store: The vector store.
        """
        self.embedder = embedder
        self.vector_store = vector_store

    def query(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        Query the RAG system.

        Args:
            query: The query string.
            top_k: The number of results to return.

        Returns:
            A list of retrieval results.
        """
        query_embedding_result = self.embedder.encode_one(query)
        if query_embedding_result.is_err():
            raise query_embedding_result.err()
        
        query_embedding = query_embedding_result.ok()

        search_results = self.vector_store.search(query_embedding, top_k)

        return [
            RetrievalResult(chunk=chunk, score=score)
            for chunk, score in search_results
        ]
