
import pytest
import pika
import json
import threading
import time
import os
import psycopg2
from qdrant_client import QdrantClient, models
from minio import Minio

from src.main import DeletionWorker

# Assume conftest.py with postgres, rabbitmq, qdrant, minio containers exists

def apply_migrations(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workspaces (id SERIAL PRIMARY KEY, rag_collection VARCHAR(255));
    CREATE TABLE IF NOT EXISTS documents (id SERIAL PRIMARY KEY, workspace_id INTEGER, file_path VARCHAR(255));
    CREATE TABLE IF NOT EXISTS document_chunks (id UUID PRIMARY KEY, document_id INTEGER);
    """)
    db_conn.commit()
    cursor.close()

def setup_environment(pg_conn, qdrant_client, minio_client):
    cursor = pg_conn.cursor()
    cursor.execute("INSERT INTO workspaces (id, rag_collection) VALUES (1, 'delete_test_collection') ON CONFLICT DO NOTHING")
    cursor.execute("INSERT INTO documents (id, workspace_id, file_path) VALUES (1, 1, 'delete_test.txt') ON CONFLICT DO NOTHING")
    pg_conn.commit()
    cursor.close()

    qdrant_client.recreate_collection(
        collection_name="delete_test_collection",
        vectors_config=models.VectorParams(size=3, distance="Cosine")
    )
    if not minio_client.bucket_exists("delete-bucket"):
        minio_client.make_bucket("delete-bucket")
    minio_client.put_object("delete-bucket", "delete_test.txt", io.BytesIO(b"data"), 4)

def test_deletion_worker_integration(postgres_container, rabbitmq_container, qdrant_container, minio_container):
    # Setup
    rabbit_conn = pika.BlockingConnection(pika.URLParameters(rabbitmq_container.get_connection_url()))
    rabbit_channel = rabbit_conn.channel()
    rabbit_channel.exchange_declare(exchange='insighthub', exchange_type='topic', durable=True)
    pg_conn = psycopg2.connect(postgres_container.get_connection_url())
    apply_migrations(pg_conn)
    qdrant_client = QdrantClient(url=qdrant_container.get_url())
    minio_client = Minio(endpoint=minio_container.get_config()["endpoint"], access_key="minioadmin", secret_key="minioadmin", secure=False)
    
    os.environ.update({
        'DATABASE_URL': postgres_container.get_connection_url(),
        'RABBITMQ_URL': rabbitmq_container.get_connection_url(),
        'QDRANT_HOST': qdrant_container.host, 'QDRANT_PORT': str(qdrant_container.port),
        'S3_ENDPOINT_URL': minio_container.get_config()["endpoint"], 'S3_ACCESS_KEY': "minioadmin", 'S3_SECRET_KEY': "minioadmin", 'S3_BUCKET_NAME': "delete-bucket",
    })

    worker = DeletionWorker()
    worker_thread = threading.Thread(target=worker.start, daemon=True)
    worker_thread.start()
    time.sleep(2)

    # Test Workspace Deletion
    setup_environment(pg_conn, qdrant_client, minio_client)
    rabbit_channel.basic_publish(exchange='insighthub', routing_key='workspace.deletion_requested', body=json.dumps({"workspace_id": "1"}))
    time.sleep(2) # Allow time for deletion
    
    with pytest.raises(Exception):
        qdrant_client.get_collection("delete_test_collection")
    with pytest.raises(Exception):
        minio_client.stat_object("delete-bucket", "delete_test.txt")
    
    # Test Document Deletion
    setup_environment(pg_conn, qdrant_client, minio_client)
    qdrant_client.upsert(collection_name="delete_test_collection", points=[models.PointStruct(id='a-guid', vector=[0.1,0.2,0.3])])
    
    rabbit_channel.basic_publish(exchange='insighthub', routing_key='document.deleted', body=json.dumps({"document_id": "1", "workspace_id": "1", "file_path": "delete_test.txt"}))
    time.sleep(2)

    with pytest.raises(Exception):
        minio_client.stat_object("delete-bucket", "delete_test.txt")

    # Cleanup
    worker.stop()
    worker_thread.join()
    pg_conn.close()
    rabbit_conn.close()
