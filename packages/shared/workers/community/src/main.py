"""Community detection worker main entry point."""

import logging
import sys
from pathlib import Path

# Add shared package to path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "python" / "src"
sys.path.insert(0, str(shared_path))

from shared.config import load_config
from shared.messaging.consumer import create_message_consumer
from shared.messaging.publisher import create_message_publisher
from shared.worker import Worker

from .community_detection_worker import create_community_detection_worker


def main() -> None:
    """Main entry point for community detection worker."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting community detection worker")

    try:
        # Load configuration
        config = load_config()

        # Create messaging components
        consumer = create_message_consumer(config)
        publisher = create_message_publisher(config)

        # Create and run worker
        worker = create_community_detection_worker(consumer, publisher, config)
        worker.run()

    except KeyboardInterrupt:
        logger.info("Community detection worker stopped by user")
    except Exception as e:
        logger.error(f"Community detection worker failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()