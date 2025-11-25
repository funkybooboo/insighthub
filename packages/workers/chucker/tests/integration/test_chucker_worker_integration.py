import json
import os
import threading
import time

import pika
import psycopg2

from src.main import ChuckerWorker


def apply_migrations(db_conn):
    cursor = db_conn.cursor()
    # Simplified schema for testing
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        parsed_text TEXT,
        processing_status VARCHAR(50),
        processing_metadata JSONB,
        updated_at TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS document_chunks (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        document_id INTEGER,
        chunk_index INTEGER,
        chunk_text TEXT
    );
    """
    )
    db_conn.commit()
    cursor.close()


def test_chucker_worker_integration(postgres_container, rabbitmq_container):
    # 1. Setup environment
    # RabbitMQ
    rabbit_conn = pika.BlockingConnection(
        pika.URLParameters(rabbitmq_container.get_connection_url())
    )
    rabbit_channel = rabbit_conn.channel()
    rabbit_channel.exchange_declare(
        exchange="insighthub", exchange_type="topic", durable=True
    )

    # PostgreSQL
    pg_conn = psycopg2.connect(postgres_container.get_connection_url())
    apply_migrations(pg_conn)
    cursor = pg_conn.cursor()
    cursor.execute(
        "INSERT INTO documents (id, parsed_text) VALUES (%s, %s)",
        (1, "This is a long text to be chunked into several pieces."),
    )
    pg_conn.commit()
    cursor.close()

    # Set environment variables for the worker
    os.environ["DATABASE_URL"] = postgres_container.get_connection_url()
    os.environ["RABBITMQ_URL"] = rabbitmq_container.get_connection_url()
    os.environ["CHUNK_SIZE"] = "10"
    os.environ["CHUNK_OVERLAP"] = "2"

    # 2. Run the worker
    worker = ChuckerWorker()
    worker_thread = threading.Thread(target=worker.start, daemon=True)
    worker_thread.start()
    time.sleep(2)

    # 3. Publish message
    message = {
        "document_id": "1",
        "workspace_id": "1",
    }
    rabbit_channel.basic_publish(
        exchange="insighthub", routing_key="document.parsed", body=json.dumps(message)
    )

    # 4. Consume result
    result = None
    for method_frame, properties, body in rabbit_channel.consume(
        "chucker.document.parsed", inactivity_timeout=5
    ):
        if body:
            result = json.loads(body)
            rabbit_channel.basic_ack(method_frame.delivery_tag)
            break

    # 5. Assertions
    assert result is not None
    assert result["document_id"] == "1"
    assert result["chunk_count"] > 1

    # Check database
    cursor = pg_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM document_chunks WHERE document_id = %s", (1,))
    chunk_count = cursor.fetchone()[0]
    assert chunk_count == result["chunk_count"]
    cursor.close()

    # 6. Cleanup
    worker.stop()
    worker_thread.join()
    pg_conn.close()
    rabbit_conn.close()
