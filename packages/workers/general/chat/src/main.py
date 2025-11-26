"""
Chat Orchestrator Worker - Processes chat messages with RAG and LLM.

Consumes: chat.message_received, chat.vector_query_completed, chat.graph_query_completed
Produces: chat.vector_query, chat.graph_query, chat.response_chunk, chat.response_complete, chat.error, chat.no_context_found
"""

import asyncio
import logging
import signal
import sys
from typing import Any, Dict

from shared.config import config
from shared.messaging import create_message_consumer, create_message_publisher

from .chat_worker import create_chat_worker

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point for the chat worker."""
    # Configuration is already loaded

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting Chat Worker")

    # Create messaging components
    consumer = create_message_consumer(
        consumer_type="rabbitmq",
        rabbitmq_url=config.rabbitmq_url,
        exchange=config.rabbitmq_exchange,
        exchange_type="topic",
        prefetch_count=config.worker_concurrency,
    )

    # Parse RabbitMQ URL to extract components
    from urllib.parse import urlparse

    parsed = urlparse(config.rabbitmq_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 5672
    username = parsed.username or "guest"
    password = parsed.password or "guest"

    publisher = create_message_publisher(
        publisher_type="rabbitmq",
        host=host,
        port=port,
        username=username,
        password=password,
        exchange=config.rabbitmq_exchange,
        exchange_type="topic",
    )

    # Create worker
    worker = create_chat_worker(consumer, publisher, config)

    # Connect and declare a single queue for all chat events
    consumer.connect()
    consumer.declare_queue("chat_worker_queue", "chat.*")
    worker.set_queue_name("chat_worker_queue")

    # Setup signal handlers
    def signal_handler(signum: int, frame: Any) -> None:
        logger.info(f"Received signal {signum}, shutting down...")
        worker.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start the worker
        await worker.start()
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())