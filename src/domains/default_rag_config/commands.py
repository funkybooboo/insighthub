"""Default RAG configuration CLI commands."""

import argparse
import sys

from src.context import AppContext
from src.domains.default_rag_config.dtos import CreateUpdateDefaultRagConfigRequest
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.options import (
    get_default_chunking_algorithm,
    get_default_clustering_algorithm,
    get_default_embedding_algorithm,
    get_default_entity_extraction_algorithm,
    get_default_rag_type,
    get_default_relationship_extraction_algorithm,
    get_default_reranking_algorithm,
)
from src.infrastructure.types import ResultHandler

logger = create_logger(__name__)


def cmd_show(ctx: AppContext, args: argparse.Namespace) -> None:
    """Show default RAG configuration (single-user system)."""
    try:
        # === Call Orchestrator ===
        result = ctx.default_rag_config_orchestrator.get_config()

        # === Handle Result (CLI-specific output) ===
        response = ResultHandler.unwrap_or_exit(result, "get default RAG config")

        # Display RAG type first
        print(f"RAG Type: {response.rag_type}")

        # Display only the configuration for the selected RAG type
        if response.rag_type == "vector":
            print(f"Chunking Algorithm: {response.vector_config.chunking_algorithm}")
            print(f"Chunk Size: {response.vector_config.chunk_size}")
            print(f"Chunk Overlap: {response.vector_config.chunk_overlap}")
            print(f"Embedding Algorithm: {response.vector_config.embedding_algorithm}")
            print(f"Top K: {response.vector_config.top_k}")
            print(f"Rerank Algorithm: {response.vector_config.rerank_algorithm}")
        elif response.rag_type == "graph":
            print(f"Entity Extraction: {response.graph_config.entity_extraction_algorithm}")
            print(
                f"Relationship Extraction: {response.graph_config.relationship_extraction_algorithm}"
            )
            print(f"Clustering Algorithm: {response.graph_config.clustering_algorithm}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to list default RAG config: {e}")
        sys.exit(1)


def cmd_new(ctx: AppContext, args: argparse.Namespace) -> None:
    """Create or update default RAG configuration (interactive, single-user system)."""
    try:
        # === CLI Interface: Gather user input ===

        # Get all available options from service
        options_result = ctx.rag_options_orchestrator.get_all_options()
        options = ResultHandler.unwrap_or_exit(options_result, "get RAG options")

        # Show available RAG types
        print("\nAvailable RAG types:")
        for opt in options.rag_types:
            print(f"  - {opt.value}: {opt.description}")
        print()

        # Prompt for RAG type
        default_rag = get_default_rag_type()
        rag_type = input(f"RAG type [{default_rag}]: ").strip().lower() or None

        # Initialize fields
        chunking_algorithm = None
        chunk_size = None
        chunk_overlap = None
        embedding_algorithm = None
        top_k = None
        rerank_algorithm = None
        entity_extraction = None
        relationship_extraction = None
        clustering = None

        # Collect vector config if needed
        if (rag_type or default_rag) == "vector":
            # Show available options
            print("\nAvailable chunking algorithms:")
            for opt in options.chunking_algorithms:
                print(f"  - {opt.value}: {opt.description}")

            print("\nAvailable embedding algorithms:")
            for opt in options.embedding_algorithms:
                print(f"  - {opt.value}: {opt.description}")

            print("\nAvailable reranking algorithms:")
            for opt in options.rerank_algorithms:
                print(f"  - {opt.value}: {opt.description}")
            print()

            # Prompt for vector RAG configuration
            default_chunking = get_default_chunking_algorithm()
            chunking_algorithm = input(f"Chunking algorithm [{default_chunking}]: ").strip() or None

            chunk_size_str = input("Chunk size [1000]: ").strip()
            chunk_size = int(chunk_size_str) if chunk_size_str else None

            chunk_overlap_str = input("Chunk overlap [200]: ").strip()
            chunk_overlap = int(chunk_overlap_str) if chunk_overlap_str else None

            default_embedding = get_default_embedding_algorithm()
            embedding_algorithm = (
                input(f"Embedding algorithm [{default_embedding}]: ").strip() or None
            )

            top_k_str = input("Top K [5]: ").strip()
            top_k = int(top_k_str) if top_k_str else None

            default_reranking = get_default_reranking_algorithm()
            rerank_algorithm = input(f"Rerank algorithm [{default_reranking}]: ").strip() or None

        else:  # graph
            # Show available options
            print("\nAvailable entity extraction algorithms:")
            for opt in options.entity_extraction_algorithms:
                print(f"  - {opt.value}: {opt.description}")

            print("\nAvailable relationship extraction algorithms:")
            for opt in options.relationship_extraction_algorithms:
                print(f"  - {opt.value}: {opt.description}")

            print("\nAvailable clustering algorithms:")
            for opt in options.clustering_algorithms:
                print(f"  - {opt.value}: {opt.description}")
            print()

            # Prompt for graph RAG configuration
            default_entity = get_default_entity_extraction_algorithm()
            entity_extraction = (
                input(f"Entity extraction algorithm [{default_entity}]: ").strip() or None
            )

            default_relationship = get_default_relationship_extraction_algorithm()
            relationship_extraction = (
                input(f"Relationship extraction algorithm [{default_relationship}]: ").strip()
                or None
            )

            default_clustering = get_default_clustering_algorithm()
            clustering = input(f"Clustering algorithm [{default_clustering}]: ").strip() or None

        # === Create Request DTO ===
        request = CreateUpdateDefaultRagConfigRequest(
            rag_type=rag_type,
            chunking_algorithm=chunking_algorithm,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            embedding_algorithm=embedding_algorithm,
            top_k=top_k,
            rerank_algorithm=rerank_algorithm,
            entity_extraction_algorithm=entity_extraction,
            relationship_extraction_algorithm=relationship_extraction,
            clustering_algorithm=clustering,
        )

        # === Call Orchestrator ===
        result = ctx.default_rag_config_orchestrator.create_or_update_config(request, default_rag)

        # === Handle Result (CLI-specific output) ===
        ResultHandler.unwrap_or_exit(result, "save default RAG config")
        print("Default RAG config saved")

    except KeyboardInterrupt:
        print("\nCancelled")
    except ValueError as e:
        print(f"Error: Invalid input - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to create default RAG config: {e}")
        sys.exit(1)
