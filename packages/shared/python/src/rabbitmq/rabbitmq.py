import os
import json
import pika
from dotenv import load_dotenv
from typing import Callable

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


def get_connection():
    """Create a durable RabbitMQ connection and channel."""
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    return connection, channel


def publish_message(queue: str, message: dict):
    """
    Publish a persistent JSON message to a durable queue.
    """
    connection, channel = get_connection()
    # Declare durable queue
    channel.queue_declare(queue=queue, durable=True)
    # Publish persistent message
    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2),  # persistent
    )
    print(f"[x] Sent message to {queue}: {message}")
    connection.close()


def consume_messages(queue: str, callback: Callable[[dict], None]):
    """
    Consume messages from a durable queue with manual acknowledgment.

    Parameters:
    - queue: name of the RabbitMQ queue
    - callback: function to handle message body (dict)
    """
    connection, channel = get_connection()
    channel.queue_declare(queue=queue, durable=True)

    def internal_callback(ch, method, properties, body):
        message = json.loads(body)
        try:
            callback(message)
            ch.basic_ack(delivery_tag=method.delivery_tag)  # only ack after success
        except Exception as e:
            print(f"[!] Error processing message: {e}")
            # Optional: message will be requeued if exception occurs

    channel.basic_consume(queue=queue, on_message_callback=internal_callback, auto_ack=False)
    print(f"[*] Waiting for messages in queue '{queue}'. To exit press CTRL+C")
    channel.start_consuming()
