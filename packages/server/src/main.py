"""Flask API application."""

from src.app import create_app as create_app_instance, create_flask_app
from src.config import config
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def main() -> None:
    """Create and configure Flask application."""
    app = create_app_instance()
    flask_app = create_flask_app(app)
    flask_app.run(host=config.host, port=config.port, debug=config.debug)


if __name__ == "__main__":
    main()
