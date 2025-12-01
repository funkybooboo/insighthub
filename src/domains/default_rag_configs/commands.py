"""Default RAG configuration CLI commands."""

import argparse
import sys

from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def cmd_list(ctx: object, args: argparse.Namespace) -> None:
    """List default RAG configuration."""
    try:
        config_obj = ctx.default_rag_config_service.get_config()
        if not config_obj:
            print("No default RAG config found")
            return

        print("\nDefault RAG Configuration:")
        print("=" * 80)
        print(f"Vector RAG Config: {config_obj.vector_config}")
        print(f"Graph RAG Config: {config_obj.graph_config}")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Failed to list default RAG config: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def cmd_new(ctx: object, args: argparse.Namespace) -> None:
    """Create or update default RAG configuration (interactive)."""
    try:
        print("Create/Update Default RAG Configuration")
        print("=" * 80)

        # For simplicity, just use defaults
        # In a full implementation, this would prompt for all config options
        print("Using default configuration values...")

        config_obj = ctx.default_rag_config_service.create_or_update_config(
            vector_config={},
            graph_config={},
        )

        print("\nDefault RAG config saved")

    except KeyboardInterrupt:
        print("\nCancelled")
    except Exception as e:
        logger.error(f"Failed to create default RAG config: {e}")
        print(f"Error: {e}")
        sys.exit(1)
