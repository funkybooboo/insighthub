"""Default RAG configuration CLI commands."""

import argparse
import sys

from src.context import AppContext
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def cmd_list(ctx: AppContext, args: argparse.Namespace) -> None:
    """List default RAG configuration (single-user system)."""
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
            print(f"Relationship Extraction: {config_obj.graph_config.relationship_extraction_algorithm}")
            print(f"Clustering Algorithm: {config_obj.graph_config.clustering_algorithm}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Failed to list default RAG config: {e}")
        sys.exit(1)


def cmd_new(ctx: AppContext, args: argparse.Namespace) -> None:
    """Create or update default RAG configuration (interactive, single-user system)."""
    try:
        # Prompt for RAG type
        rag_type = input("RAG type (vector/graph) [vector]: ").strip().lower() or "vector"
        if rag_type not in ["vector", "graph"]:
            print("Error: RAG type must be 'vector' or 'graph'", file=sys.stderr)
            sys.exit(1)

        vector_config = {}
        graph_config = {}

        if rag_type == "vector":
            # Prompt for vector RAG configuration in pipeline order
            chunking_algorithm = input("Chunking algorithm [sentence]: ").strip() or "sentence"
            chunk_size = input("Chunk size [1000]: ").strip() or "1000"
            chunk_overlap = input("Chunk overlap [200]: ").strip() or "200"
            embedding_algorithm = input("Embedding algorithm [ollama]: ").strip() or "ollama"
            top_k = input("Top K [5]: ").strip() or "5"
            rerank_algorithm = input("Rerank algorithm [none]: ").strip() or "none"

            vector_config = {
                "chunking_algorithm": chunking_algorithm,
                "chunk_size": int(chunk_size),
                "chunk_overlap": int(chunk_overlap),
                "embedding_algorithm": embedding_algorithm,
                "top_k": int(top_k),
                "rerank_algorithm": rerank_algorithm,
            }
        else:  # graph
            # Prompt for graph RAG configuration
            entity_extraction = input("Entity extraction algorithm [spacy]: ").strip() or "spacy"
            relationship_extraction = input("Relationship extraction algorithm [dependency-parsing]: ").strip() or "dependency-parsing"
            clustering = input("Clustering algorithm [leiden]: ").strip() or "leiden"

            graph_config = {
                "entity_extraction_algorithm": entity_extraction,
                "relationship_extraction_algorithm": relationship_extraction,
                "clustering_algorithm": clustering,
            }

        # Create/update config
        config_obj = ctx.default_rag_config_service.create_or_update_config(
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
