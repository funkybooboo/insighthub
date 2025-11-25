"""Main entry point for the infrastructure manager worker."""

import asyncio
import logging
import signal
import sys
from typing import Any

from shared.config import Config
from shared.messaging import create_message_consumer, create_message_publisher

from .infrastructure_manager_worker import create_infrastructure_manager_worker

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point for the infrastructure manager worker."""
    # Load configuration
    config = Config()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting Infrastructure Manager Worker")

    # Create messaging components
    consumer = create_message_consumer(
        broker_url=config.rabbitmq_url,
        queue_name="infrastructure_manager_queue",
        exchange_name=config.rabbitmq_exchange,
    )

    publisher = create_message_publisher(
        broker_url=config.rabbitmq_url,
        exchange_name=config.rabbitmq_exchange,
    )

    # Create worker
    worker = create_infrastructure_manager_worker(consumer, publisher, config)

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