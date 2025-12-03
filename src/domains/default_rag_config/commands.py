"""Default RAG configuration CLI commands."""

import argparse
import sys

from src.context import AppContext
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.options import (
    get_chunking_options,
    get_default_chunking_algorithm,
    get_default_clustering_algorithm,
    get_default_embedding_algorithm,
    get_default_entity_extraction_algorithm,
    get_default_rag_type,
    get_default_relationship_extraction_algorithm,
    get_default_reranking_algorithm,
    get_embedding_options,
    get_graph_clustering_options,
    get_graph_entity_extraction_options,
    get_graph_relationship_extraction_options,
    get_rag_type_options,
    get_reranking_options,
    get_valid_rag_types,
)

logger = create_logger(__name__)


def cmd_show(ctx: AppContext, args: argparse.Namespace) -> None:
    """Show default RAG configuration (single-user system)."""
    try:
        config_obj = ctx.default_rag_config_service.get_config()

        # Auto-create default config if it doesn't exist
        if not config_obj:
            logger.info("No default RAG config found, creating default configuration")
            config_obj = ctx.default_rag_config_service.create_or_update_config(
                rag_type="vector",
                vector_config={},  # Uses defaults from model
                graph_config={},  # Uses defaults from model
            )

        # Display RAG type first
        print(f"RAG Type: {config_obj.rag_type}")

        # Display only the configuration for the selected RAG type in pipeline order
        if config_obj.rag_type == "vector":
            print(f"Chunking Algorithm: {config_obj.vector_config.chunking_algorithm}")
            print(f"Chunk Size: {config_obj.vector_config.chunk_size}")
            print(f"Chunk Overlap: {config_obj.vector_config.chunk_overlap}")
            print(f"Embedding Algorithm: {config_obj.vector_config.embedding_algorithm}")
            print(f"Top K: {config_obj.vector_config.top_k}")
            print(f"Rerank Algorithm: {config_obj.vector_config.rerank_algorithm}")
        elif config_obj.rag_type == "graph":
            print(f"Entity Extraction: {config_obj.graph_config.entity_extraction_algorithm}")
            print(
                f"Relationship Extraction: {config_obj.graph_config.relationship_extraction_algorithm}"
            )
            print(f"Clustering Algorithm: {config_obj.graph_config.clustering_algorithm}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to list default RAG config: {e}")
        sys.exit(1)


def cmd_new(ctx: AppContext, args: argparse.Namespace) -> None:
    """Create or update default RAG configuration (interactive, single-user system)."""
    try:
        # Show available RAG types
        rag_type_opts = get_rag_type_options()
        print("\nAvailable RAG types:")
        for opt in rag_type_opts:
            print(f"  - {opt['value']}: {opt['description']}")
        print()

        # Prompt for RAG type
        default_rag = get_default_rag_type()
        rag_type = input(f"RAG type [{default_rag}]: ").strip().lower() or default_rag
        valid_types = get_valid_rag_types()
        if rag_type not in valid_types:
            print(f"Error: RAG type must be one of: {', '.join(valid_types)}", file=sys.stderr)
            sys.exit(1)

        vector_config = {}
        graph_config = {}

        if rag_type == "vector":
            # Get available options from factories
            chunking_opts = get_chunking_options()
            embedding_opts = get_embedding_options()
            reranking_opts = get_reranking_options()

            # Show available options
            print("\nAvailable chunking algorithms:")
            for opt in chunking_opts:
                print(f"  - {opt['value']}: {opt['description']}")

            print("\nAvailable embedding algorithms:")
            for opt in embedding_opts:
                print(f"  - {opt['value']}: {opt['description']}")

            print("\nAvailable reranking algorithms:")
            for opt in reranking_opts:
                print(f"  - {opt['value']}: {opt['description']}")
            print()

            # Prompt for vector RAG configuration in pipeline order
            default_chunking = get_default_chunking_algorithm()
            chunking_algorithm = (
                input(f"Chunking algorithm [{default_chunking}]: ").strip() or default_chunking
            )

            chunk_size = input("Chunk size [1000]: ").strip() or "1000"
            chunk_overlap = input("Chunk overlap [200]: ").strip() or "200"

            default_embedding = get_default_embedding_algorithm()
            embedding_algorithm = (
                input(f"Embedding algorithm [{default_embedding}]: ").strip() or default_embedding
            )

            top_k = input("Top K [5]: ").strip() or "5"

            default_reranking = get_default_reranking_algorithm()
            rerank_algorithm = (
                input(f"Rerank algorithm [{default_reranking}]: ").strip() or default_reranking
            )

            vector_config = {
                "chunking_algorithm": chunking_algorithm,
                "chunk_size": int(chunk_size),
                "chunk_overlap": int(chunk_overlap),
                "embedding_algorithm": embedding_algorithm,
                "top_k": int(top_k),
                "rerank_algorithm": rerank_algorithm,
            }
        else:  # graph
            # Get available options from factories
            entity_opts = get_graph_entity_extraction_options()
            relationship_opts = get_graph_relationship_extraction_options()
            clustering_opts = get_graph_clustering_options()

            # Show available options
            print("\nAvailable entity extraction algorithms:")
            for opt in entity_opts:
                print(f"  - {opt['value']}: {opt['description']}")

            print("\nAvailable relationship extraction algorithms:")
            for opt in relationship_opts:
                print(f"  - {opt['value']}: {opt['description']}")

            print("\nAvailable clustering algorithms:")
            for opt in clustering_opts:
                print(f"  - {opt['value']}: {opt['description']}")
            print()

            # Prompt for graph RAG configuration
            default_entity = get_default_entity_extraction_algorithm()
            entity_extraction = (
                input(f"Entity extraction algorithm [{default_entity}]: ").strip() or default_entity
            )

            default_relationship = get_default_relationship_extraction_algorithm()
            relationship_extraction = (
                input(f"Relationship extraction algorithm [{default_relationship}]: ").strip()
                or default_relationship
            )

            default_clustering = get_default_clustering_algorithm()
            clustering = (
                input(f"Clustering algorithm [{default_clustering}]: ").strip() or default_clustering
            )

            graph_config = {
                "entity_extraction_algorithm": entity_extraction,
                "relationship_extraction_algorithm": relationship_extraction,
                "clustering_algorithm": clustering,
            }

        # Create/update config
        ctx.default_rag_config_service.create_or_update_config(
            rag_type=rag_type,
            vector_config=vector_config,
            graph_config=graph_config,
        )

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
