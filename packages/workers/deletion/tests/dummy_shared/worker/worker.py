"""Dummy worker module for testing."""


class Worker:
    def __init__(
        self,
        worker_name: str,
        rabbitmq_url: str,
        exchange: str,
        exchange_type: str,
        consume_routing_key: str,
        consume_queue: str,
        prefetch_count: int,
    ):
        self.worker_name = worker_name
        self.rabbitmq_url = rabbitmq_url
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.consume_routing_key = consume_routing_key
        self.consume_queue = consume_queue
        self.prefetch_count = prefetch_count
        self.connection = None
        self.channel = None

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def publish_event(self, routing_key: str, event: dict) -> None:
        pass
