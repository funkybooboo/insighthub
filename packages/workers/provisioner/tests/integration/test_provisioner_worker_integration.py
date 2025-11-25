
import pytest
import pika
import json
import threading
import time
import os
import psycopg2
from qdrant_client import QdrantClient

from src.main import ProvisionerWorker

# Assume conftest.py with postgres, rabbitmq, qdrant containers exists

def apply_migrations(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workspaces (id SERIAL PRIMARY KEY, status VARCHAR(50), status_message TEXT, rag_collection VARCHAR(255), updated_at TIMESTAMP);
    """)
    db_conn.commit()
    cursor.close()

def test_provisioner_worker_integration(postgres_container, rabbitmq_container, qdrant_container):
    # 1. Setup
    rabbit_conn = pika.BlockingConnection(pika.URLParameters(rabbitmq_container.get_connection_url()))
    rabbit_channel = rabbit_conn.channel()
    rabbit_channel.exchange_declare(exchange='insighthub', exchange_type='topic', durable=True)
    
    pg_conn = psycopg2.connect(postgres_container.get_connection_url())
    apply_migrations(pg_conn)
    cursor = pg_conn.cursor()
    cursor.execute("INSERT INTO workspaces (id, status) VALUES (1, 'provisioning')")
    pg_conn.commit()
    cursor.close()

    qdrant_client = QdrantClient(url=qdrant_container.get_url())

    os.environ.update({
        'DATABASE_URL': postgres_container.get_connection_url(),
        'RABBITMQ_URL': rabbitmq_container.get_connection_url(),
        'QDRANT_HOST': qdrant_container.host, 'QDRANT_PORT': str(qdrant_container.port),
    })

    # 2. Run worker
    worker = ProvisionerWorker()
    worker_thread = threading.Thread(target=worker.start, daemon=True)
    worker_thread.start()
    time.sleep(2)

    # 3. Publish message
    message = {"workspace_id": "1", "user_id": "1", "rag_config": {"embedding_dim": 3}}
    rabbit_channel.basic_publish(exchange='insighthub', routing_key='workspace.provision_requested', body=json.dumps(message))

    # 4. Consume results
    status_updates = []
    for _ in range(2): # Expecting two status updates
        method_frame, properties, body = rabbit_channel.basic_get(queue='provisioner.workspace.provision_requested', auto_ack=True)
        if body:
            status_updates.append(json.loads(body))
    
    # 5. Assertions
    assert len(status_updates) > 0 # At least one for ready
    ready_status = [s for s in status_updates if s['status'] == 'ready']
    assert len(ready_status) == 1

    # Check Qdrant
    collection_info = qdrant_client.get_collection(collection_name="workspace_1")
    assert collection_info.vectors_config.params.size == 3
    
    # Check DB
    cursor = pg_conn.cursor()
    cursor.execute("SELECT status, rag_collection FROM workspaces WHERE id = 1")
    db_status, db_collection = cursor.fetchone()
    assert db_status == 'ready'
    assert db_collection == 'workspace_1'
    cursor.close()

    # 6. Cleanup
    worker.stop()
    worker_thread.join()
    pg_conn.close()
    rabbit_conn.close()
