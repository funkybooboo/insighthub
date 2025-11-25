
import pytest
import pika
import json
import threading
import time
import os
import psycopg2
from qdrant_client import QdrantClient, models
from unittest.mock import patch, MagicMock

from src.main import ChatOrchestratorWorker

# Assume conftest.py with postgres, rabbitmq, qdrant containers exists

def apply_migrations(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workspaces (id SERIAL PRIMARY KEY, rag_collection VARCHAR(255));
    CREATE TABLE IF NOT EXISTS rag_configs (workspace_id INTEGER, top_k INTEGER, embedding_model VARCHAR(255), embedding_dim INTEGER);
    CREATE TABLE IF NOT EXISTS chat_messages (id SERIAL PRIMARY KEY, session_id INTEGER, role VARCHAR(50), content TEXT, created_at TIMESTAMP DEFAULT NOW());
    """)
    db_conn.commit()
    cursor.close()

@patch('src.main.create_llm_provider')
def test_chat_worker_integration(mock_create_llm, postgres_container, rabbitmq_container, qdrant_container):
    # 1. Setup environment
    # RabbitMQ, Postgres, Qdrant setup
    rabbit_conn = pika.BlockingConnection(pika.URLParameters(rabbitmq_container.get_connection_url()))
    rabbit_channel = rabbit_conn.channel()
    rabbit_channel.exchange_declare(exchange='insighthub', exchange_type='topic', durable=True)
    
    pg_conn = psycopg2.connect(postgres_container.get_connection_url())
    apply_migrations(pg_conn)
    cursor = pg_conn.cursor()
    cursor.execute("INSERT INTO workspaces (id, rag_collection) VALUES (1, 'chat_test_collection')")
    cursor.execute("INSERT INTO rag_configs (workspace_id, top_k, embedding_model, embedding_dim) VALUES (1, 1, 'test-embed', 3)")
    pg_conn.commit()
    cursor.close()

    qdrant_client = QdrantClient(url=qdrant_container.get_url())
    qdrant_client.recreate_collection(
        collection_name="chat_test_collection",
        vectors_config=models.VectorParams(size=3, distance="Cosine")
    )
    qdrant_client.upsert(
        collection_name="chat_test_collection",
        points=[models.PointStruct(id="a-guid", vector=[0.9, 0.8, 0.7], payload={"chunk_text": "RAG is great."})]
    )

    # Mock LLM
    mock_llm = MagicMock()
    mock_llm.chat_stream.return_value = iter(["This is a test", " response."])
    mock_create_llm.return_value = mock_llm
    
    # Set environment variables
    os.environ.update({
        'DATABASE_URL': postgres_container.get_connection_url(),
        'RABBITMQ_URL': rabbitmq_container.get_connection_url(),
        'QDRANT_HOST': qdrant_container.host,
        'QDRANT_PORT': str(qdrant_container.port),
        'OLLAMA_BASE_URL': 'http://mock-ollama',
        'OLLAMA_LLM_MODEL': 'mock-llm',
        'OLLAMA_EMBEDDING_MODEL': 'test-embed',
    })

    # 2. Run worker
    worker = ChatOrchestratorWorker()
    worker_thread = threading.Thread(target=worker.start, daemon=True)
    worker_thread.start()
    time.sleep(2)

    # 3. Publish message
    message = {"message_id": "1", "session_id": "1", "workspace_id": "1", "content": "What about RAG?"}
    rabbit_channel.basic_publish(exchange='insighthub', routing_key='chat.message_received', body=json.dumps(message))

    # 4. Consume results
    chunks = []
    completion = None
    for i in range(3): # Expect 2 chunks and 1 completion
        method_frame, properties, body = rabbit_channel.basic_get(queue='chat.message_received', auto_ack=True)
        if body:
            data = json.loads(body)
            if 'chunk' in data:
                chunks.append(data['chunk'])
            elif 'full_response' in data:
                completion = data['full_response']
    
    # 5. Assertions
    assert len(chunks) == 2
    assert "".join(chunks) == "This is a test response."
    assert completion == "This is a test response."

    # 6. Cleanup
    worker.stop()
    worker_thread.join()
    pg_conn.close()
    rabbit_conn.close()
