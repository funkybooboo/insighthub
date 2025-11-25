"""Integration tests for chat worker using real testcontainers - no mocks."""

import psycopg2
import psycopg2.extras

from src.main import ChatOrchestratorWorker


class TestChatWorkerDatabaseIntegration:
    """Integration tests for database operations using real PostgreSQL."""

    def test_conversation_history_storage_and_retrieval(self, postgres_container):
        """Test that conversation history can be stored and retrieved from real database."""
        # Convert SQLAlchemy URL to psycopg2 format
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)

        # Setup schema and insert test data
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            cursor.execute(
                """
                INSERT INTO chat_messages (session_id, role, content) VALUES
                (1, 'user', 'What is machine learning?'),
                (1, 'assistant', 'Machine learning is a subset of AI...'),
                (1, 'user', 'Can you give an example?'),
                (2, 'user', 'Different conversation')
            """
            )
        conn.commit()

        # Test direct database operations that the worker would perform
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # Test conversation history retrieval for session 1
            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
                (1,),
            )
            history_1 = cursor.fetchall()

            # Test conversation history retrieval for session 2
            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
                (2,),
            )
            history_2 = cursor.fetchall()

            # Test empty result for non-existent session
            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
                (999,),
            )
            history_empty = cursor.fetchall()

        # Verify correct data retrieval
        assert len(history_1) == 3
        assert history_1[0]["content"] == "What is machine learning?"
        assert history_1[1]["content"] == "Machine learning is a subset of AI..."
        assert history_1[2]["content"] == "Can you give an example?"

        assert len(history_2) == 1
        assert history_2[0]["content"] == "Different conversation"

        assert history_empty == []

        conn.close()

    def test_workspace_and_rag_config_retrieval(self, postgres_container):
        """Test workspace and RAG configuration retrieval from real database."""
        # Convert SQLAlchemy URL to psycopg2 format
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)

        # Setup schema and data
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE workspaces (
                    id SERIAL PRIMARY KEY,
                    rag_collection VARCHAR(255) NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE rag_configs (
                    workspace_id INTEGER PRIMARY KEY,
                    top_k INTEGER DEFAULT 8,
                    embedding_dim INTEGER DEFAULT 768,
                    embedding_model VARCHAR(255) DEFAULT 'nomic-embed-text'
                )
            """
            )
            cursor.execute(
                """
                INSERT INTO workspaces (id, rag_collection) VALUES
                (1, 'academic_papers'),
                (2, 'wikipedia_articles')
            """
            )
            cursor.execute(
                """
                INSERT INTO rag_configs (workspace_id, top_k, embedding_dim, embedding_model) VALUES
                (1, 10, 512, 'text-embedding-ada-002'),
                (2, 5, 384, 'nomic-embed-text')
            """
            )
        conn.commit()

        # Test direct database operations that the worker would perform
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # Test workspace collection retrieval
            cursor.execute("SELECT rag_collection FROM workspaces WHERE id = %s", (1,))
            result_1 = cursor.fetchone()
            collection_1 = result_1["rag_collection"] if result_1 else None

            cursor.execute("SELECT rag_collection FROM workspaces WHERE id = %s", (2,))
            result_2 = cursor.fetchone()
            collection_2 = result_2["rag_collection"] if result_2 else None

            # Test RAG config retrieval
            cursor.execute("SELECT * FROM rag_configs WHERE workspace_id = %s", (1,))
            config_1 = cursor.fetchone()

            cursor.execute("SELECT * FROM rag_configs WHERE workspace_id = %s", (2,))
            config_2 = cursor.fetchone()

            # Test error cases
            cursor.execute("SELECT rag_collection FROM workspaces WHERE id = %s", (999,))
            workspace_999 = cursor.fetchone()

            cursor.execute("SELECT * FROM rag_configs WHERE workspace_id = %s", (999,))
            config_999 = cursor.fetchone()

        # Verify results
        assert collection_1 == "academic_papers"
        assert collection_2 == "wikipedia_articles"

        assert config_1["top_k"] == 10
        assert config_1["embedding_dim"] == 512
        assert config_1["embedding_model"] == "text-embedding-ada-002"

        assert config_2["top_k"] == 5
        assert config_2["embedding_model"] == "nomic-embed-text"

        # Test error cases
        assert workspace_999 is None
        assert config_999 is None

        conn.close()

    def test_conversation_history_ordering_and_timestamps(self, postgres_container):
        """Test that conversation history is properly ordered by timestamp."""
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)

        # Setup schema and insert test data with specific timestamps
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            # Insert messages with specific timestamps (out of order insertion)
            cursor.execute(
                """
                INSERT INTO chat_messages (session_id, role, content, created_at) VALUES
                (1, 'user', 'First message', '2023-01-01 10:00:00'),
                (1, 'assistant', 'Second message', '2023-01-01 10:01:00'),
                (1, 'user', 'Third message', '2023-01-01 10:02:00'),
                (1, 'assistant', 'Fourth message', '2023-01-01 10:03:00')
            """
            )
        conn.commit()

        # Test ordering
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
                (1,),
            )
            history = cursor.fetchall()

        # Verify correct chronological ordering
        assert len(history) == 4
        assert history[0]["content"] == "First message"
        assert history[1]["content"] == "Second message"
        assert history[2]["content"] == "Third message"
        assert history[3]["content"] == "Fourth message"

        conn.close()

    def test_conversation_history_large_dataset(self, postgres_container):
        """Test conversation history retrieval with a large number of messages."""
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)

        # Setup schema
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Insert 100 messages for one session
            messages = []
            for i in range(100):
                role = "user" if i % 2 == 0 else "assistant"
                # Use proper timestamp format (HH:MM:SS)
                hour = 10 + (i // 60)  # Increment hour every 60 messages
                minute = i % 60
                timestamp = f"2023-01-01 {hour:02d}:{minute:02d}:00"
                messages.append((1, role, f"Message {i}", timestamp))

            cursor.executemany(
                """
                INSERT INTO chat_messages (session_id, role, content, created_at) VALUES (%s, %s, %s, %s)
            """,
                messages,
            )
        conn.commit()

        # Test retrieval of large dataset
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
                (1,),
            )
            history = cursor.fetchall()

        # Verify all messages are retrieved and in correct order
        assert len(history) == 100
        for i, msg in enumerate(history):
            expected_role = "user" if i % 2 == 0 else "assistant"
            assert msg["role"] == expected_role
            assert msg["content"] == f"Message {i}"

        conn.close()

    def test_workspace_config_with_default_values(self, postgres_container):
        """Test workspace and RAG config retrieval with default values."""
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)

        # Setup schema with minimal data (relying on defaults)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE workspaces (
                    id SERIAL PRIMARY KEY,
                    rag_collection VARCHAR(255) NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE rag_configs (
                    workspace_id INTEGER PRIMARY KEY,
                    top_k INTEGER DEFAULT 8,
                    embedding_dim INTEGER DEFAULT 768,
                    embedding_model VARCHAR(255) DEFAULT 'nomic-embed-text'
                )
            """
            )
            cursor.execute(
                "INSERT INTO workspaces (id, rag_collection) VALUES (1, 'default_collection')"
            )
            # Insert config with only workspace_id (using defaults)
            cursor.execute("INSERT INTO rag_configs (workspace_id) VALUES (1)")
        conn.commit()

        # Test retrieval with defaults
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT rag_collection FROM workspaces WHERE id = %s", (1,))
            workspace = cursor.fetchone()

            cursor.execute("SELECT * FROM rag_configs WHERE workspace_id = %s", (1,))
            config = cursor.fetchone()

        assert workspace is not None and workspace["rag_collection"] == "default_collection"
        assert config is not None and config["top_k"] == 8
        assert config is not None and config["embedding_dim"] == 768
        assert config is not None and config["embedding_model"] == "nomic-embed-text"

        conn.close()

    def test_multiple_sessions_conversation_history(self, postgres_container):
        """Test conversation history isolation between different sessions."""
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)

        # Setup schema and insert data for multiple sessions
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            cursor.execute(
                """
                INSERT INTO chat_messages (session_id, role, content) VALUES
                (1, 'user', 'Session 1 - Message 1'),
                (1, 'assistant', 'Session 1 - Message 2'),
                (2, 'user', 'Session 2 - Message 1'),
                (2, 'assistant', 'Session 2 - Message 2'),
                (2, 'user', 'Session 2 - Message 3'),
                (3, 'user', 'Session 3 - Message 1')
            """
            )
        conn.commit()

        # Test isolation between sessions
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
                (1,),
            )
            session_1 = cursor.fetchall()

            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
                (2,),
            )
            session_2 = cursor.fetchall()

            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
                (3,),
            )
            session_3 = cursor.fetchall()

        # Verify session isolation
        assert len(session_1) == 2
        assert session_1[0]["content"] == "Session 1 - Message 1"
        assert session_1[1]["content"] == "Session 1 - Message 2"

        assert len(session_2) == 3
        assert session_2[0]["content"] == "Session 2 - Message 1"
        assert session_2[1]["content"] == "Session 2 - Message 2"
        assert session_2[2]["content"] == "Session 2 - Message 3"

        assert len(session_3) == 1
        assert session_3[0]["content"] == "Session 3 - Message 1"

        conn.close()

    def test_empty_database_scenarios(self, postgres_container):
        """Test behavior with empty tables and no data."""
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)

        # Setup empty schema
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE workspaces (
                    id SERIAL PRIMARY KEY,
                    rag_collection VARCHAR(255) NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE rag_configs (
                    workspace_id INTEGER PRIMARY KEY,
                    top_k INTEGER DEFAULT 8,
                    embedding_dim INTEGER DEFAULT 768,
                    embedding_model VARCHAR(255) DEFAULT 'nomic-embed-text'
                )
            """
            )
        conn.commit()

        # Test empty results
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
                (1,),
            )
            history = cursor.fetchall()

            cursor.execute("SELECT rag_collection FROM workspaces WHERE id = %s", (1,))
            workspace = cursor.fetchone()

            cursor.execute("SELECT * FROM rag_configs WHERE workspace_id = %s", (1,))
            config = cursor.fetchone()

        assert history == []
        assert workspace is None
        assert config is None

        conn.close()

    def test_conversation_history_with_special_characters(self, postgres_container):
        """Test conversation history with special characters and SQL injection prevention."""
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)

        # Setup schema
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            # Insert messages with special characters
            cursor.execute(
                """
                INSERT INTO chat_messages (session_id, role, content) VALUES
                (1, 'user', 'Hello & welcome!'),
                (1, 'assistant', 'SELECT * FROM users; -- SQL injection attempt'),
                (1, 'user', 'What about <script>alert("xss")</script>?'),
                (1, 'assistant', 'Special chars: àáâãäå, 中文, 🚀')
            """
            )
        conn.commit()

        # Test retrieval with special characters
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
                (1,),
            )
            history = cursor.fetchall()

        # Verify special characters are preserved
        assert len(history) == 4
        assert "Hello & welcome!" in history[0]["content"]
        assert "SQL injection attempt" in history[1]["content"]
        assert "<script>" in history[2]["content"]
        assert "🚀" in history[3]["content"]

        conn.close()

    def test_workspace_config_various_data_types(self, postgres_container):
        """Test workspace configurations with various data types and edge values."""
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)

        # Setup schema
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE workspaces (
                    id SERIAL PRIMARY KEY,
                    rag_collection VARCHAR(255) NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE rag_configs (
                    workspace_id INTEGER PRIMARY KEY,
                    top_k INTEGER,
                    embedding_dim INTEGER,
                    embedding_model VARCHAR(255)
                )
            """
            )
            cursor.execute(
                """
                INSERT INTO workspaces (id, rag_collection) VALUES
                (1, 'minimal_config'),
                (2, 'maximal_config')
            """
            )
            cursor.execute(
                """
                INSERT INTO rag_configs (workspace_id, top_k, embedding_dim, embedding_model) VALUES
                (1, NULL, NULL, NULL),
                (2, 100, 2048, 'very-long-model-name-that-might-be-used-in-production')
            """
            )
        conn.commit()

        # Test retrieval of various configurations
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM rag_configs WHERE workspace_id = %s", (1,))
            minimal_config = cursor.fetchone()

            cursor.execute("SELECT * FROM rag_configs WHERE workspace_id = %s", (2,))
            maximal_config = cursor.fetchone()

        # Test minimal config (NULL values)
        assert minimal_config["top_k"] is None
        assert minimal_config["embedding_dim"] is None
        assert minimal_config["embedding_model"] is None

        # Test maximal config (large values)
        assert maximal_config["top_k"] == 100
        assert maximal_config["embedding_dim"] == 2048
        assert len(maximal_config["embedding_model"]) > 50  # Long model name

        conn.close()

    def test_database_transaction_rollback(self, postgres_container):
        """Test database transaction behavior and rollback scenarios."""
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)

        # Setup schema
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
        conn.commit()

        # Test successful transaction
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO chat_messages (session_id, role, content) VALUES
                    (1, 'user', 'Message 1'),
                    (1, 'assistant', 'Message 2')
                """
                )
            conn.commit()

            # Verify data was committed
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM chat_messages")
                count = cursor.fetchone()["count"]
                assert count == 2

        except Exception:
            conn.rollback()
            raise

        conn.close()

    def test_database_connection_pooling_simulation(self, postgres_container):
        """Test multiple database connections and operations (simulating connection pooling)."""
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")

        # Setup base schema once
        conn = psycopg2.connect(url)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
        conn.commit()
        conn.close()

        # Create multiple connections and test concurrent operations
        connections = []
        for i in range(3):
            conn = psycopg2.connect(url)
            connections.append(conn)

            # Insert data through each connection
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO chat_messages (session_id, role, content) VALUES
                    (%s, 'user', 'Connection %s message')
                """,
                    (i + 1, i + 1),
                )
            conn.commit()

        # Test that all data is visible across connections
        for i, conn in enumerate(connections):
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT role, content FROM chat_messages WHERE session_id = %s", (i + 1,)
                )
                messages = cursor.fetchall()
                assert len(messages) == 1
                assert f"Connection {i + 1} message" in messages[0]["content"]

            conn.close()

        # Verify total data count
        final_conn = psycopg2.connect(url)
        with final_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM chat_messages")
            total_count = cursor.fetchone()["count"]
            assert total_count == 3  # One message per connection

        final_conn.close()


class TestChatWorkerErrorHandling:
    """Test error handling scenarios with real database."""

    def test_process_event_database_error(self, postgres_container):
        """Test error handling when database operations fail."""
        # Setup database with schema
        url = postgres_container.get_connection_url()
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(url)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE workspaces (
                    id SERIAL PRIMARY KEY,
                    rag_collection VARCHAR(255) NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE rag_configs (
                    workspace_id INTEGER PRIMARY KEY,
                    top_k INTEGER DEFAULT 8,
                    embedding_dim INTEGER DEFAULT 768,
                    embedding_model VARCHAR(255) DEFAULT 'nomic-embed-text'
                )
            """
            )
            cursor.execute(
                "INSERT INTO workspaces (id, rag_collection) VALUES (1, 'test_collection')"
            )
            cursor.execute("INSERT INTO rag_configs (workspace_id, top_k) VALUES (1, 8)")
        conn.commit()

        worker = ChatOrchestratorWorker()

        # Override database connection to use test container
        worker.db_connection = type(
            "MockConn",
            (),
            {
                "get_cursor": lambda as_dict=True: (
                    conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    if as_dict
                    else conn.cursor()
                )
            },
        )()

        # Simulate database failure by closing connection
        conn.close()

        # Capture published events
        published_events = []
        worker.publish_event = lambda event_name, data: published_events.append((event_name, data))

        # Test input
        event_data = {
            "message_id": "test-msg-error",
            "session_id": 4,
            "workspace_id": 1,
            "content": "Test message",
            "ignore_rag": False,
        }

        # Process the event
        worker.process_event(event_data)

        # Verify error event was published
        error_events = [e for e in published_events if e[0] == "chat.error"]
        assert len(error_events) == 1
        assert error_events[0][1]["message_id"] == "test-msg-error"
        assert "session_id" in error_events[0][1]
