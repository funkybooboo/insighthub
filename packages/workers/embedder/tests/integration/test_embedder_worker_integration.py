
import pytest
import pika
import json
import threading
import time
import os
import psycopg2
from unittest.mock import patch, MagicMock

from src.main import EmbedderWorker

def apply_migrations(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        processing_status VARCHAR(50),
        processing_metadata JSONB,
        updated_at TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS document_chunks (
        id UUID PRIMARY KEY,
        document_id INTEGER,
        chunk_text TEXT,
        embedding JSONB
    );
    """)
    db_conn.commit()
    cursor.close()

@patch('src.main.create_embedding_encoder')
def test_embedder_worker_integration(mock_create_encoder, postgres_container, rabbitmq_container):
    # 1. Setup environment
    # RabbitMQ
    rabbit_conn = pika.BlockingConnection(pika.URLParameters(rabbitmq_container.get_connection_url()))
    rabbit_channel = rabbit_conn.channel()
    rabbit_channel.exchange_declare(exchange='insighthub', exchange_type='topic', durable=True)
    
    # PostgreSQL
    pg_conn = psycopg2.connect(postgres_container.get_connection_url())
    apply_migrations(pg_conn)
    cursor = pg_conn.cursor()
    cursor.execute("INSERT INTO documents (id) VALUES (1)")
    cursor.execute("INSERT INTO document_chunks (id, document_id, chunk_text) VALUES (%s, %s, %s)", ('a1b2c3d4-e5f6-7890-1234-567890abcdef', 1, "text1"))
    pg_conn.commit()
    cursor.close()

    # Mock encoder
    mock_encoder = MagicMock()
    mock_encoder.encode.return_value = MagicMock(unwrap=lambda: [[0.1, 0.2]])
    mock_encoder.get_dimension.return_value = 2
    mock_create_encoder.return_value = mock_encoder

    # Set environment variables
    os.environ['DATABASE_URL'] = postgres_container.get_connection_url()
    os.environ['RABBITMQ_URL'] = rabbitmq_container.get_connection_url()
    os.environ['OLLAMA_EMBEDDING_MODEL'] = 'test-model'
    os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
    os.environ['BATCH_SIZE'] = '1'

    # 2. Run worker
    worker = EmbedderWorker()
    worker_thread = threading.Thread(target=worker.start, daemon=True)
    worker_thread.start()
    time.sleep(2)

    # 3. Publish message
    message = {
        "document_id": "1",
        "workspace_id": "1",
        "chunk_ids": ["a1b2c3d4-e5f6-7890-1234-567890abcdef"],
    }
    rabbit_channel.basic_publish(
        exchange='insighthub',
        routing_key='document.chunked',
        body=json.dumps(message)
    )

    # 4. Consume result
    result = None
    for method_frame, properties, body in rabbit_channel.consume('embedder.document.chunked', inactivity_timeout=5):
        if body:
            result = json.loads(body)
            rabbit_channel.basic_ack(method_frame.delivery_tag)
            break
    
    # 5. Assertions
    assert result is not None
    assert result['document_id'] == '1'
    assert result['embedding_count'] == 1

    # Check database
    cursor = pg_conn.cursor()
    cursor.execute("SELECT embedding FROM document_chunks WHERE id = %s", ('a1b2c3d4-e5f6-7890-1234-567890abcdef',))
    embedding = cursor.fetchone()[0]
    assert embedding == '[0.1, 0.2]'
    cursor.close()

    # 6. Cleanup
    worker.stop()
    worker_thread.join()
    pg_conn.close()
    rabbit_conn.close()
