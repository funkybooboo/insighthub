"""Event handler registry and dispatcher."""

from typing import Any, Callable, Dict, List

from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


class EventHandlerRegistry:
    """Registry for event handlers with automatic dispatching."""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    def register(self, event_type: str, handler: Callable) -> None:
        """Register an event handler for a specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug(f"Registered handler for event type: {event_type}")

    def unregister(self, event_type: str, handler: Callable) -> None:
        """Unregister an event handler."""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                logger.debug(f"Unregistered handler for event type: {event_type}")
            except ValueError:
                logger.warning(f"Handler not found for event type: {event_type}")

    def dispatch(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Dispatch an event to all registered handlers."""
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    logger.error(f"Event handler failed for {event_type}: {e}")
        else:
            logger.debug(f"No handlers registered for event type: {event_type}")

    def get_registered_events(self) -> List[str]:
        """Get list of all registered event types."""
        return list(self._handlers.keys())

    def get_handler_count(self, event_type: str) -> int:
        """Get number of handlers registered for an event type."""
        return len(self._handlers.get(event_type, []))


# Global event handler registry
event_registry = EventHandlerRegistry()


def register_event_handler(event_type: str, handler: Callable) -> None:
    """Register an event handler for a specific event type."""
    event_registry.register(event_type, handler)


def unregister_event_handler(event_type: str, handler: Callable) -> None:
    """Unregister an event handler."""
    event_registry.unregister(event_type, handler)


def dispatch_event(event_type: str, event_data: Dict[str, Any]) -> None:
    """Dispatch an event to all registered handlers."""
    event_registry.dispatch(event_type, event_data)