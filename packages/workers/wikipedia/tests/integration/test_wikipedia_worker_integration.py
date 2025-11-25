
import pytest
import pika
import json
import threading
import time
import os
import psycopg2
from minio import Minio

from src.main import WikipediaWorker

# Assume conftest.py with postgres, rabbitmq, minio containers exists

def apply_migrations(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY);
    CREATE TABLE IF NOT EXISTS workspaces (id SERIAL PRIMARY KEY, user_id INTEGER);
    CREATE TABLE IF NOT EXISTS documents (id SERIAL PRIMARY KEY, user_id INTEGER, workspace_id INTEGER, filename VARCHAR(255), file_path VARCHAR(255), file_size INTEGER, mime_type VARCHAR(255), content_hash VARCHAR(255), processing_status VARCHAR(50));
    """)
    db_conn.commit()
    cursor.close()

def test_wikipedia_worker_integration(postgres_container, rabbitmq_container, minio_container):
    # 1. Setup
    rabbit_conn = pika.BlockingConnection(pika.URLParameters(rabbitmq_container.get_connection_url()))
    rabbit_channel = rabbit_conn.channel()
    rabbit_channel.exchange_declare(exchange='insighthub', exchange_type='topic', durable=True)
    
    pg_conn = psycopg2.connect(postgres_container.get_connection_url())
    apply_migrations(pg_conn)
    cursor = pg_conn.cursor()
    cursor.execute("INSERT INTO users (id) VALUES (1) ON CONFLICT DO NOTHING")
    cursor.execute("INSERT INTO workspaces (id, user_id) VALUES (1, 1) ON CONFLICT DO NOTHING")
    pg_conn.commit()
    cursor.close()

    minio_client = Minio(endpoint=minio_container.get_config()["endpoint"], access_key="minioadmin", secret_key="minioadmin", secure=False)
    if not minio_client.bucket_exists("wiki-bucket"):
        minio_client.make_bucket("wiki-bucket")

    os.environ.update({
        'DATABASE_URL': postgres_container.get_connection_url(),
        'RABBITMQ_URL': rabbitmq_container.get_connection_url(),
        'S3_ENDPOINT_URL': minio_container.get_config()["endpoint"], 'S3_ACCESS_KEY': "minioadmin", 'S3_SECRET_KEY': "minioadmin", 'S3_BUCKET_NAME': "wiki-bucket",
    })

    # 2. Run worker
    worker = WikipediaWorker()
    worker_thread = threading.Thread(target=worker.start, daemon=True)
    worker_thread.start()
    time.sleep(2)

    # 3. Publish message
    message = {"workspace_id": "1", "user_id": "1", "query": "Python (programming language)"}
    rabbit_channel.basic_publish(exchange='insighthub', routing_key='wikipedia.fetch_requested', body=json.dumps(message))

    # 4. Consume results
    doc_uploaded_msg = None
    for method_frame, properties, body in rabbit_channel.consume('document.uploaded', inactivity_timeout=10):
        if body:
            doc_uploaded_msg = json.loads(body)
            rabbit_channel.basic_ack(method_frame.delivery_tag)
            break
            
    # 5. Assertions
    assert doc_uploaded_msg is not None
    assert doc_uploaded_msg['workspace_id'] == '1'
    assert 'Python' in doc_uploaded_msg['metadata']['title']

    cursor = pg_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM documents WHERE workspace_id = 1")
    assert cursor.fetchone()[0] == 1
    cursor.close()

    # 6. Cleanup
    worker.stop()
    worker_thread.join()
    pg_conn.close()
    rabbit_conn.close()
