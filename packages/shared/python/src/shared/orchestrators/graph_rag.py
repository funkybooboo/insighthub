"""Graph RAG orchestrator for indexing and querying documents."""

from typing import BinaryIO, List

from shared.database.graph.graph_store import GraphStore
from shared.documents.parsing.document_parser import DocumentParser
from shared.types.document import Document
from shared.types.retrieval import RetrievalResult


class GraphRAGIndexer:
    """
    Orchestrates the indexing part of the Graph RAG pipeline.
    """

    def __init__(
        self,
        parser: DocumentParser,
        graph_store: GraphStore,
    ):
        """
        Initialize the GraphRAGIndexer.

        Args:
            parser: The document parser.
            graph_store: The graph store.
        """
        self.parser = parser
        self.graph_store = graph_store

    def index(self, file: BinaryIO, metadata: dict | None = None) -> Document:
        """
        Index a document.

        Args:
            file: The file to index.
            metadata: Optional metadata to attach to the document.

        Returns:
            The indexed document.
        """
        raise NotImplementedError("Graph RAG Indexer is not yet implemented.")


class GraphRAG:
    """
    Orchestrates the query part of the Graph RAG pipeline.
    """

    def __init__(
        self,
        graph_store: GraphStore,
    ):
        """
        Initialize the GraphRAG.

        Args:
            graph_store: The graph store.
        """
        self.graph_store = graph_store

    def query(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        Query the RAG system.

        Args:
            query: The query string.
            top_k: The number of results to return.

        Returns:
            A list of retrieval results.
        """
        raise NotImplementedError("Graph RAG is not yet implemented.")
