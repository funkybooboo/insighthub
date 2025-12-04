"""RAG Options CLI commands."""

import argparse
import sys

from returns.result import Failure

from src.context import AppContext
from src.infrastructure.cli_io import IO
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def cmd_list(ctx: AppContext, args: argparse.Namespace) -> None:
    """List all available RAG options."""
    try:
        # Call orchestrator
        result = ctx.rag_options_orchestrator.get_all_options()

        if isinstance(result, Failure):
            error = result.failure()
            message = error.message if hasattr(error, "message") else str(error)
            IO.print_error(f"Error: {message}")
            sys.exit(1)

        response = result.unwrap()

        # Present options
        IO.print("Available RAG Options:")
        IO.print("")

        IO.print("RAG Types:")
        for opt in response.rag_types:
            IO.print(f"  - {opt.value}: {opt.description}")
        IO.print("")

        IO.print("Chunking Algorithms:")
        for opt in response.chunking_algorithms:
            IO.print(f"  - {opt.value}: {opt.description}")
        IO.print("")

        IO.print("Embedding Algorithms:")
        for opt in response.embedding_algorithms:
            IO.print(f"  - {opt.value}: {opt.description}")
        IO.print("")

        IO.print("Rerank Algorithms:")
        for opt in response.rerank_algorithms:
            IO.print(f"  - {opt.value}: {opt.description}")
        IO.print("")

        IO.print("Entity Extraction Algorithms:")
        for opt in response.entity_extraction_algorithms:
            IO.print(f"  - {opt.value}: {opt.description}")
        IO.print("")

        IO.print("Relationship Extraction Algorithms:")
        for opt in response.relationship_extraction_algorithms:
            IO.print(f"  - {opt.value}: {opt.description}")
        IO.print("")

        IO.print("Clustering Algorithms:")
        for opt in response.clustering_algorithms:
            IO.print(f"  - {opt.value}: {opt.description}")

    except Exception as e:
        IO.print_error(f"Error: {e}")
        logger.error(f"Failed to list RAG options: {e}")
        sys.exit(1)
