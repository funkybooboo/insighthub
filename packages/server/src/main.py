"""
Main entry point for RAG system
Demonstrates the factory pattern for easy algorithm configuration
"""

import os
import sys
import time

from dotenv import load_dotenv

from src.rag.algorithms.vector_rag import ollama_llm_generator
from src.rag.factory import create_rag
from src.rag.types import Document

# Load environment variables from .env file
load_dotenv()


def wait_for_service(url: str, service_name: str, max_retries: int = 30):
    """Wait for a service to be ready."""
    import requests

    print(f"  - Waiting for {service_name} to be ready...")
    for i in range(max_retries):
        try:
            requests.get(url, timeout=2)
            print(f"  [OK] {service_name} is ready")
            return True
        except Exception:
            if i < max_retries - 1:
                time.sleep(1)
    print(f"  [FAIL] {service_name} failed to start")
    return False


def main():
    """
    Main function demonstrating the RAG factory pattern.
    Easy configuration of algorithms, chunking, embeddings, and storage!
    """
    print("=" * 60)
    print("RAG System - Algorithm Playground")
    print("=" * 60)
    print()

    # Get configuration from environment
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_llm_model = os.getenv("OLLAMA_LLM_MODEL", "llama3.2")
    ollama_embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    qdrant_collection = os.getenv("QDRANT_COLLECTION_NAME", "rag_collection")

    chunk_strategy = os.getenv("CHUNK_STRATEGY", "sentence")
    chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))

    top_k = int(os.getenv("RAG_TOP_K", "5"))

    print(f"Configuration:")
    print(f"  RAG Type: Vector")
    print(f"  Chunking: {chunk_strategy} (size={chunk_size}, overlap={chunk_overlap})")
    print(f"  Embeddings: Ollama ({ollama_embedding_model})")
    print(f"  Vector Store: Qdrant ({qdrant_host}:{qdrant_port})")
    print(f"  LLM: Ollama ({ollama_llm_model})")
    print()

    # Wait for services to be ready
    print("Waiting for services...")
    wait_for_service(ollama_url, "Ollama")
    wait_for_service(f"http://{qdrant_host}:{qdrant_port}", "Qdrant")
    print()

    # Create RAG system using factory - SO EASY!
    print("Creating RAG system...")
    print("-" * 60)

    rag = create_rag(
        # Algorithm selection
        rag_type="vector",
        # Chunking configuration
        chunking_strategy=chunk_strategy,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # Embedding configuration
        embedding_type="ollama",
        embedding_model_name=ollama_embedding_model,
        embedding_base_url=ollama_url,
        # Vector store configuration
        vector_store_type="qdrant",
        vector_store_host=qdrant_host,
        vector_store_port=qdrant_port,
        vector_store_collection=qdrant_collection,
    )

    print(f"[OK] {rag.rag_type.value.upper()} RAG system created!")
    print()

    # Sample documents
    print("Adding documents to knowledge base...")
    print("-" * 60)

    documents: list[Document] = [
        {
            "text": """
                Retrieval-Augmented Generation (RAG) is a technique that combines information retrieval
                with text generation to produce more accurate and grounded responses. The RAG process works
                in two main steps: first, relevant documents are retrieved from a knowledge base using
                similarity search on embeddings. Second, these retrieved documents are provided as context
                to a language model, which generates a response based on both the query and the retrieved
                information. This approach significantly reduces hallucinations and improves factual accuracy.
            """,
            "metadata": {"source": "rag_overview", "topic": "RAG", "category": "AI"},
        },
        {
            "text": """
                Vector databases are specialized databases designed to store and query high-dimensional
                vectors efficiently. They use techniques like Approximate Nearest Neighbor (ANN) search
                to quickly find similar vectors. Popular vector databases include Pinecone, Weaviate,
                Milvus, and Qdrant. These databases are essential for modern AI applications that rely
                on semantic search and similarity matching.
            """,
            "metadata": {
                "source": "vector_db_intro",
                "topic": "Vector Databases",
                "category": "AI",
            },
        },
        {
            "text": """
                Ollama is a tool that makes it easy to run large language models locally on your own hardware.
                It supports popular models like Llama 3, Mistral, Phi-3, and many others. Ollama provides
                a simple API for generating text and embeddings, making it ideal for privacy-focused
                applications or situations where you want to avoid API costs. The models run entirely
                on your machine, ensuring data privacy.
            """,
            "metadata": {"source": "ollama_guide", "topic": "Ollama", "category": "Tools"},
        },
        {
            "text": """
                Python is a versatile programming language widely used in data science, machine learning,
                and web development. Its simple syntax and extensive ecosystem of libraries make it ideal
                for rapid prototyping and production applications. Key libraries include NumPy for numerical
                computing, pandas for data manipulation, and scikit-learn for machine learning.
            """,
            "metadata": {"source": "python_basics", "topic": "Python", "category": "Programming"},
        },
        {
            "text": """
                Docker is a containerization platform that packages applications and their dependencies
                into containers. Containers are lightweight, portable, and ensure consistent behavior
                across different environments. Docker Compose allows you to define and run multi-container
                applications using a YAML file, making it easy to orchestrate complex setups with multiple
                services working together.
            """,
            "metadata": {"source": "docker_intro", "topic": "Docker", "category": "DevOps"},
        },
    ]

    num_chunks = rag.add_documents(documents)
    print(f"[OK] Added {len(documents)} documents ({num_chunks} chunks)")
    print()

    # Query the system
    print("Querying the RAG system")
    print("-" * 60)
    print()

    queries = [
        "What is RAG and how does it work?",
        "Tell me about Ollama",
        "What is Docker used for?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"Query {i}: {query}")
        print()

        # Retrieve relevant chunks
        print(f"  Retrieving relevant context (top_k={top_k})...")
        results = rag.retrieve(query, top_k=top_k)

        print(f"  Found {len(results)} relevant chunks:")
        for j, result in enumerate(results, 1):
            score = result["score"]
            metadata = result["metadata"]
            if isinstance(metadata, dict):
                source = metadata.get("source", "unknown")
                topic = metadata.get("topic", "unknown")
            else:
                source = "unknown"
                topic = "unknown"
            print(f"    [{j}] Score: {score:.4f} | Source: {source} | Topic: {topic}")

        # Generate answer using Ollama
        print()
        print(f"  Generating answer with Ollama ({ollama_llm_model})...")
        print()

        def generator(q, ctx):
            return ollama_llm_generator(q, ctx, model=ollama_llm_model, base_url=ollama_url)

        query_result = rag.query(query=query, top_k=top_k, llm_generator=generator)

        print("  Answer:")
        print("  " + "-" * 56)
        answer = query_result.get("answer", "")
        if isinstance(answer, str):
            answer_lines = answer.split("\n")
            for line in answer_lines:
                print(f"  {line}")
        print("  " + "-" * 56)
        print()
        print()

    # System statistics
    print("System Statistics")
    print("-" * 60)
    stats = rag.get_stats()
    print(f"Total vectors in database: {stats.get('total_vector_count', 0)}")
    print()

    print("=" * 60)
    print("Demo completed successfully!")
    print()
    print("Try different configurations in .env:")
    print("  CHUNK_STRATEGY: character, sentence, word")
    print("  Different chunk sizes and overlaps")
    print("  Different embedding models")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
