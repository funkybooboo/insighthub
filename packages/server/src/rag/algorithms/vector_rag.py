"""
Vector-based Retrieval-Augmented Generation (RAG) System
Implements the core RAG pipeline using vector similarity search
"""

import hashlib
import time

from src.rag.base import BaseRAG, RAGType
from src.rag.chunking.base import BaseChunker
from src.rag.embeddings.base import EmbeddingModel
from src.rag.stores.vector.base import VectorStore
from src.rag.types import Document, JsonValue, LLMGenerator, Metadata, SearchResult, Stats


class VectorRAG(BaseRAG):
    """
    Vector-based RAG system that orchestrates retrieval and generation.
    Uses vector similarity search for document retrieval.
    """

    def __init__(
        self, vector_store: VectorStore, embedding_model: EmbeddingModel, chunker: BaseChunker
    ):
        """
        Initialize the vector RAG system.

        Args:
            vector_store: Vector database for storing and retrieving chunks
            embedding_model: Model for generating embeddings
            chunker: Document chunker
        """
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.chunker = chunker

    def add_documents(
        self,
        documents: list[Document],
        text_key: str = "text",
        metadata_key: str = "metadata",
        batch_size: int = 100,
        **kwargs: JsonValue,
    ) -> int:
        """
        Add documents to the RAG system.
        Documents are chunked, embedded, and stored in the vector database.

        Args:
            documents: List of documents to add
            text_key: Key containing document text
            metadata_key: Key containing document metadata
            batch_size: Batch size for embedding and storing
            **kwargs: Additional arguments (unused)

        Returns:
            Number of chunks added
        """
        print(f"Chunking {len(documents)} documents...")
        chunks = self.chunker.chunk_documents(
            documents, text_key=text_key, metadata_key=metadata_key
        )

        print(f"Created {len(chunks)} chunks")

        # Process in batches
        total_added = 0
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            # Extract texts
            texts = [str(chunk["text"]) for chunk in batch]

            # Generate embeddings
            print(
                f"Embedding batch {i // batch_size + 1}/{(len(chunks) + batch_size - 1) // batch_size}..."
            )
            embeddings = self.embedding_model.embed(texts)

            # Generate IDs (using hash of text + timestamp for uniqueness)
            ids = [
                self._generate_id(str(chunk["text"]), i + idx) for idx, chunk in enumerate(batch)
            ]

            # Prepare metadata
            metadata_list: list[Metadata] = []
            for chunk in batch:
                meta_value = chunk.get("metadata", {})
                if isinstance(meta_value, dict):
                    metadata_list.append(meta_value)
                else:
                    metadata_list.append({})

            # Store in vector database
            self.vector_store.add(vectors=embeddings, ids=ids, metadata=metadata_list)

            total_added += len(batch)

        print(f"Successfully added {total_added} chunks to the vector store")
        return total_added

    def retrieve(
        self, query: str, top_k: int = 5, filter: Metadata | None = None, **kwargs: JsonValue
    ) -> list[SearchResult]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: The query text
            top_k: Number of results to return
            filter: Optional metadata filter
            **kwargs: Additional arguments (unused)

        Returns:
            List of retrieved chunks with scores and metadata
        """
        # Embed the query
        query_embedding = self.embedding_model.embed(query)[0]

        # Search the vector store
        results = self.vector_store.search(query_vector=query_embedding, top_k=top_k, filter=filter)

        return results

    def query(
        self,
        query: str,
        top_k: int = 5,
        filter: Metadata | None = None,
        llm_generator: LLMGenerator | None = None,
        return_context: bool = False,
        **kwargs: JsonValue,
    ) -> dict[str, str | list[SearchResult]]:
        """
        Full RAG query: retrieve relevant chunks and optionally generate a response.

        Args:
            query: The query text
            top_k: Number of chunks to retrieve
            filter: Optional metadata filter
            llm_generator: Optional function that takes (query, context) and generates a response
            return_context: Whether to return the retrieved context
            **kwargs: Additional arguments (unused)

        Returns:
            Dictionary containing:
                - 'query': The original query
                - 'retrieved_chunks': Retrieved chunks with scores
                - 'answer': Generated answer (if llm_generator provided)
                - 'context': Retrieved context text (if return_context=True)
        """
        # Retrieve relevant chunks
        retrieved_chunks = self.retrieve(query, top_k=top_k, filter=filter)

        result: dict[str, str | list[SearchResult]] = {
            "query": query,
            "retrieved_chunks": retrieved_chunks,
        }

        # Prepare context from retrieved chunks
        if return_context or llm_generator:
            context_texts: list[str] = []
            for chunk in retrieved_chunks:
                metadata = chunk.get("metadata", {})
                if isinstance(metadata, dict):
                    text = metadata.get("text", "")
                    if isinstance(text, str):
                        context_texts.append(text)

            context = "\n\n".join([f"[{i+1}] {text}" for i, text in enumerate(context_texts)])

            if return_context:
                result["context"] = context

            # Generate answer if generator provided
            if llm_generator:
                answer = llm_generator(query, context)
                result["answer"] = answer

        return result

    def _generate_id(self, text: str, index: int) -> str:
        """
        Generate a unique ID for a chunk.

        Args:
            text: Chunk text
            index: Chunk index

        Returns:
            Unique ID string
        """
        # Create hash from text and timestamp
        content = f"{text}_{index}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()

    def clear(self):
        """Clear all vectors from the database."""
        self.vector_store.delete_all()
        print("Cleared all vectors from the database")

    def get_stats(self) -> Stats:
        """Get statistics about the RAG system."""
        return self.vector_store.get_stats()

    @property
    def rag_type(self) -> RAGType:
        """Get the type of RAG implementation."""
        return RAGType.VECTOR


def simple_llm_generator(
    query: str, context: str, api_key: str | None = None, model: str = "gpt-3.5-turbo"
) -> str:
    """
    Simple LLM generator using OpenAI.

    Args:
        query: User query
        context: Retrieved context
        api_key: OpenAI API key
        model: Model to use

    Returns:
        Generated response
    """
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    prompt = f"""You are a helpful assistant. Answer the user's question based on the provided context.

Context:
{context}

Question: {query}

Answer the question based on the context above. If the context doesn't contain relevant information, say so."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions based on provided context.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    content = response.choices[0].message.content
    return content if content is not None else ""


def ollama_llm_generator(
    query: str, context: str, model: str = "llama3.2", base_url: str = "http://localhost:11434"
) -> str:
    """
    LLM generator using Ollama for local models.

    Args:
        query: User query
        context: Retrieved context
        model: Ollama model name (e.g., 'llama3.2', 'mistral', 'phi3')
        base_url: Base URL for Ollama API

    Returns:
        Generated response
    """
    import requests

    base_url = base_url.rstrip("/")

    prompt = f"""You are a helpful assistant. Answer the user's question based on the provided context.

Context:
{context}

Question: {query}

Answer the question based on the context above. If the context doesn't contain relevant information, say so."""

    response = requests.post(
        f"{base_url}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.7}},
    )

    response.raise_for_status()
    return response.json()["response"]  # type: ignore[no-any-return]
