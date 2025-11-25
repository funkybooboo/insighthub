import io
import json
import os
import threading
import time

import pika
from minio import Minio

from src.main import ParserWorker


def test_parser_worker_integration(
    postgres_container, rabbitmq_container, minio_container
):
    # 1. Setup environment
    # RabbitMQ
    time.sleep(10)
    rabbit_conn = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", port=5672)
    )
    rabbit_channel = rabbit_conn.channel()
    rabbit_channel.exchange_declare(
        exchange="insighthub", exchange_type="topic", durable=True
    )

    # MinIO
    minio_client = Minio(
        endpoint=minio_container.get_config()["endpoint"],
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False,
    )
    bucket_name = "test-bucket"
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    # Upload a test file to MinIO
    file_content = b"This is a test file."
    file_path = "test-doc.txt"
    minio_client.put_object(
        bucket_name, file_path, io.BytesIO(file_content), len(file_content)
    )

    # Set environment variables for the worker
    os.environ["DATABASE_URL"] = postgres_container.get_connection_url()
    os.environ["RABBITMQ_URL"] = "amqp://guest:guest@localhost:5672/%2F"
    os.environ["S3_ENDPOINT_URL"] = minio_container.get_config()["endpoint"]
    os.environ["S3_ACCESS_KEY"] = "minioadmin"
    os.environ["S3_SECRET_KEY"] = "minioadmin"
    os.environ["S3_BUCKET_NAME"] = bucket_name

    # 2. Run the worker in a separate thread
    worker = ParserWorker()
    worker_thread = threading.Thread(target=worker.start, daemon=True)
    worker_thread.start()
    time.sleep(2)  # Give worker time to start

    # 3. Publish a message
    message = {
        "document_id": "1",
        "workspace_id": "1",
        "user_id": "1",
        "file_path": file_path,
        "content_type": "text/plain",
        "metadata": {},
    }
    rabbit_channel.basic_publish(
        exchange="insighthub", routing_key="document.uploaded", body=json.dumps(message)
    )

    # 4. Consume the result
    result = None
    for method_frame, properties, body in rabbit_channel.consume(
        "parser.document.parsed", inactivity_timeout=5
    ):
        if body:
            result = json.loads(body)
            rabbit_channel.basic_ack(method_frame.delivery_tag)
            break

    # 5. Assertions
    assert result is not None
    assert result["document_id"] == "1"
    assert result["text_length"] == len(file_content)

    # 6. Cleanup
    worker.stop()
    worker_thread.join()
    rabbit_conn.close()
