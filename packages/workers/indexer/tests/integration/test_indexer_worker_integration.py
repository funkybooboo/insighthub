
import pytest
import pika
import json
import threading
import time
import os
import psycopg2
from qdrant_client import QdrantClient

from src.main import IndexerWorker

# Add QdrantContainer to conftest.py if not present
# from testcontainers.qdrant import QdrantContainer
# @pytest.fixture(scope="session")
# def qdrant_container():
#     with QdrantContainer("qdrant/qdrant:latest") as qdrant:
#         yield qdrant

def apply_migrations(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workspaces (id SERIAL PRIMARY KEY, rag_collection VARCHAR(255));
    CREATE TABLE IF NOT EXISTS documents (id SERIAL PRIMARY KEY, workspace_id INTEGER, processing_status VARCHAR(50), processing_metadata JSONB, updated_at TIMESTAMP);
    CREATE TABLE IF NOT EXISTS document_chunks (id UUID PRIMARY KEY, document_id INTEGER, embedding JSONB, chunk_text TEXT, chunk_index INTEGER);
    """)
    db_conn.commit()
    cursor.close()

def test_indexer_worker_integration(postgres_container, rabbitmq_container, qdrant_container):
    # 1. Setup environment
    # RabbitMQ
    rabbit_conn = pika.BlockingConnection(pika.URLParameters(rabbitmq_container.get_connection_url()))
    rabbit_channel = rabbit_conn.channel()
    rabbit_channel.exchange_declare(exchange='insighthub', exchange_type='topic', durable=True)
    
    # PostgreSQL
    pg_conn = psycopg2.connect(postgres_container.get_connection_url())
    apply_migrations(pg_conn)
    cursor = pg_conn.cursor()
    cursor.execute("INSERT INTO workspaces (id, rag_collection) VALUES (1, 'test_collection')")
    cursor.execute("INSERT INTO documents (id, workspace_id) VALUES (1, 1)")
    cursor.execute("INSERT INTO document_chunks (id, document_id, embedding) VALUES (%s, %s, %s)", ('a1b2c3d4-e5f6-7890-1234-567890abcdef', 1, json.dumps([0.1, 0.2, 0.3])))
    pg_conn.commit()
    cursor.close()

    # Qdrant
    qdrant_client = QdrantClient(url=qdrant_container.get_url())
    qdrant_client.recreate_collection(
        collection_name="test_collection",
        vectors_config={"size": 3, "distance": "Cosine"}
    )

    # Set environment variables
    os.environ['DATABASE_URL'] = postgres_container.get_connection_url()
    os.environ['RABBITMQ_URL'] = rabbitmq_container.get_connection_url()
    os.environ['QDRANT_HOST'] = qdrant_container.host
    os.environ['QDRANT_PORT'] = str(qdrant_container.port)

    # 2. Run worker
    worker = IndexerWorker()
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
        routing_key='document.embedded',
        body=json.dumps(message)
    )

    # 4. Consume result
    result = None
    for method_frame, properties, body in rabbit_channel.consume('indexer.document.embedded', inactivity_timeout=5):
        if body:
            result = json.loads(body)
            rabbit_channel.basic_ack(method_frame.delivery_tag)
            break
    
    # 5. Assertions
    assert result is not None
    assert result['document_id'] == '1'
    assert result['vector_count'] == 1
    assert result['collection_name'] == 'test_collection'

    # Check Qdrant
    retrieved_points = qdrant_client.retrieve(collection_name="test_collection", ids=['a1b2c3d4-e5f6-7890-1234-567890abcdef'])
    assert len(retrieved_points) == 1

    # 6. Cleanup
    worker.stop()
    worker_thread.join()
    pg_conn.close()
    rabbit_conn.close()
