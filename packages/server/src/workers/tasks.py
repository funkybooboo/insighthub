"""Background task execution utilities for workers."""

from threading import Thread
from typing import Callable, TypeVar

from src.infrastructure.logger import create_logger

logger = create_logger(__name__)

F = TypeVar("F", bound=Callable[..., object])


def run_async(func: F, *args: object, **kwargs: object) -> Thread:
    """Run a function asynchronously in a background thread.

    Args:
        func: The function to execute
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The thread object (daemon thread, does not block program exit)
    """
    thread = Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    logger.debug(f"Started background thread for {func.__name__}")
    return thread
