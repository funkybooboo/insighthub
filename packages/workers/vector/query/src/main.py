"""Main entry point for the vector query worker."""

import asyncio
import logging
import signal
import sys
from typing import Any

from shared.config import config
from shared.messaging import create_message_consumer, create_message_publisher

from .vector_query_worker import create_vector_query_worker

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point for the vector query worker."""
    # Configuration is already loaded

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting Vector Query Worker")

    # Create messaging components
    consumer = create_message_consumer(
        consumer_type="rabbitmq",
        rabbitmq_url=config.rabbitmq_url,
        exchange=config.rabbitmq_exchange,
        exchange_type="topic",
        prefetch_count=config.worker_concurrency,
    )

    # Connect and declare queue
    consumer.connect()
    consumer.declare_queue("vector_query_queue", "chat.vector_query")

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
    worker = create_vector_query_worker(consumer, publisher, config)
    worker.set_queue_name("vector_query_queue")

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