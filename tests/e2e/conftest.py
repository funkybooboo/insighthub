"""Pytest configuration for E2E tests.

This module ensures backing services (PostgreSQL, Ollama, Qdrant, Neo4j, MinIO, Redis)
are running before E2E tests execute. If services are not running, it attempts to start
them once using docker compose. If they still don't start, tests fail with a clear message.

It also provides automatic cleanup fixtures that run after each test to ensure test isolation
by cleaning up all resources created during tests (database records, Qdrant collections,
MinIO files, Redis cache, Neo4j nodes).
"""

import subprocess
import time
from typing import Literal

import pytest


def check_service_health(service: str) -> Literal["healthy", "unhealthy", "not_running"]:
    """Check if a Docker Compose service is healthy.

    Args:
        service: Name of the service to check

    Returns:
        "healthy" if service is running and healthy
        "unhealthy" if service is running but not healthy
        "not_running" if service is not running
    """
    try:
        # Check if service is running
        state_result = subprocess.run(
            ["docker", "compose", "ps", service, "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )

        if not state_result.stdout.strip():
            return "not_running"

        # Parse state and health from JSON output
        import json

        service_info = json.loads(state_result.stdout)

        state = service_info.get("State", "unknown")
        health = service_info.get("Health", "unknown")

        if state != "running":
            return "not_running"

        # If service doesn't have a healthcheck, assume healthy if running
        if health in ("healthy", "unknown"):
            return "healthy"

        return "unhealthy"

    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        return "not_running"


def check_all_services_healthy() -> tuple[bool, list[str]]:
    """Check if all backing services are healthy.

    Returns:
        Tuple of (all_healthy, list of unhealthy service names)
    """
    services = ["postgres", "ollama", "qdrant", "neo4j", "minio", "redis"]
    unhealthy_services = []

    for service in services:
        status = check_service_health(service)
        if status != "healthy":
            unhealthy_services.append(f"{service} ({status})")

    return len(unhealthy_services) == 0, unhealthy_services


def start_services() -> bool:
    """Start backing services using docker compose.

    Returns:
        True if services started successfully, False otherwise
    """
    try:
        print("\n[WARNING] Backing services not running. Attempting to start them...")
        subprocess.run(
            ["docker", "compose", "up", "-d"],
            check=True,
            capture_output=True,
        )

        # Wait for services to become healthy (max 60 seconds)
        print("[INFO] Waiting for services to become healthy...")
        max_wait = 60
        wait_interval = 2
        elapsed = 0

        while elapsed < max_wait:
            time.sleep(wait_interval)
            elapsed += wait_interval

            all_healthy, unhealthy = check_all_services_healthy()
            if all_healthy:
                print(f"[OK] All services are healthy after {elapsed}s")
                return True

            print(f"   Waiting... ({elapsed}s) - Unhealthy: {', '.join(unhealthy)}")

        print(f"[FAIL] Services did not become healthy after {max_wait}s")
        return False

    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Failed to start services: {e}")
        return False


@pytest.fixture(scope="session", autouse=True)
def ensure_backing_services():
    """Ensure backing services are running before E2E tests.

    This fixture runs once per test session and:
    1. Checks if all backing services are healthy
    2. If not, attempts to start them once
    3. Checks again after starting
    4. Fails the test session if services still aren't healthy
    """
    all_healthy, unhealthy = check_all_services_healthy()

    if all_healthy:
        print("\n[OK] All backing services are healthy")
        return

    # Services not healthy - try to start them once
    print(f"\n[WARNING] Some services are not healthy: {', '.join(unhealthy)}")
    started = start_services()

    if not started:
        pytest.exit(
            "[FAIL] Failed to start backing services. Please run 'task up' manually "
            "and ensure all services are healthy before running E2E tests.",
            returncode=1,
        )

    # Verify services are now healthy
    all_healthy, still_unhealthy = check_all_services_healthy()

    if not all_healthy:
        pytest.exit(
            f"[FAIL] Backing services started but some are still unhealthy: {', '.join(still_unhealthy)}. "
            "Please check service logs with 'task logs' and ensure all services are healthy.",
            returncode=1,
        )

    print("[OK] All backing services are now healthy and ready for E2E tests")


@pytest.fixture(scope="function", autouse=True)
def cleanup_resources():
    """Clean up ALL resources created during tests.

    This fixture ensures complete test isolation by cleaning up:
    - Database: workspaces, documents, chat sessions, CLI state
    - Qdrant: vector collections created for workspaces
    - MinIO: uploaded document files in S3 storage
    - Redis: cached data
    - Neo4j: graph nodes and relationships

    The cleanup happens automatically without requiring tests to track resources manually.
    """
    import psycopg2

    from src.config import config

    # Get database connection and record existing resources
    # Use a single query to fetch all resource IDs at once to reduce round trips
    conn = psycopg2.connect(config.database_url)
    cursor = conn.cursor()

    # Record existing resource IDs before test (single query for efficiency)
    cursor.execute(
        """
        SELECT 'workspace' as type, id FROM workspaces
        UNION ALL
        SELECT 'document' as type, id FROM documents
        UNION ALL
        SELECT 'session' as type, id FROM chat_sessions
    """
    )
    results = cursor.fetchall()
    existing_workspaces = {row[1] for row in results if row[0] == "workspace"}
    existing_documents = {row[1] for row in results if row[0] == "document"}
    existing_sessions = {row[1] for row in results if row[0] == "session"}

    # Store config info needed for lazy cleanup (don't connect to services yet)
    # This reduces memory usage by only connecting when actually needed
    qdrant_config = {"host": config.qdrant_host, "port": config.qdrant_port}
    s3_config = {
        "endpoint_url": config.s3_endpoint_url,
        "aws_access_key_id": config.s3_access_key,
        "aws_secret_access_key": config.s3_secret_key,
        "bucket_name": config.s3_bucket_name,
    }
    neo4j_config = {
        "url": config.neo4j_url,
        "user": config.neo4j_user,
        "password": config.neo4j_password,
    }

    cursor.close()
    conn.close()

    # Yield to run the test
    yield

    # === CLEANUP PHASE ===
    # Clean up resources in the correct order to respect dependencies

    # 1. Find new resources in database (single query for efficiency)
    conn = psycopg2.connect(config.database_url)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 'workspace' as type, id FROM workspaces
        UNION ALL
        SELECT 'document' as type, id FROM documents
        UNION ALL
        SELECT 'session' as type, id FROM chat_sessions
    """
    )
    current_results = cursor.fetchall()
    current_workspaces = {row[1] for row in current_results if row[0] == "workspace"}
    current_documents = {row[1] for row in current_results if row[0] == "document"}
    current_sessions = {row[1] for row in current_results if row[0] == "session"}

    new_sessions = current_sessions - existing_sessions
    new_documents = current_documents - existing_documents
    new_workspaces = current_workspaces - existing_workspaces

    cursor.close()
    conn.close()

    # Early exit if no new resources were created (saves memory and time)
    if not (new_sessions or new_documents or new_workspaces):
        return

    # 2. Delete database resources using CLI (also triggers cascade cleanup)
    # Order: sessions -> documents -> workspaces

    import sys

    for session_id in new_sessions:
        try:
            subprocess.run(
                [sys.executable, "-m", "src.cli", "chat", "delete", str(session_id)],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception:
            pass

    for document_id in new_documents:
        try:
            subprocess.run(
                [sys.executable, "-m", "src.cli", "document", "remove", str(document_id)],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception:
            pass

    for workspace_id in new_workspaces:
        try:
            subprocess.run(
                [sys.executable, "-m", "src.cli", "workspace", "delete", str(workspace_id)],
                input="yes\n",  # Confirm deletion
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception:
            pass  # Best effort cleanup

    # 3. Clean up Qdrant collections (only connect if needed)
    if new_workspaces:
        try:
            from qdrant_client import QdrantClient

            qdrant_client = QdrantClient(host=qdrant_config["host"], port=qdrant_config["port"])
            try:
                # Get collections and delete workspace-specific ones
                collections = qdrant_client.get_collections().collections
                for collection in collections:
                    # Check if collection name contains workspace ID
                    for workspace_id in new_workspaces:
                        if str(workspace_id) in collection.name:
                            try:
                                qdrant_client.delete_collection(collection.name)
                            except Exception:
                                pass
            finally:
                # Ensure client is closed to free memory
                del qdrant_client
        except Exception:
            pass

    # 4. Clean up MinIO objects (only connect if needed)
    if new_documents or new_workspaces:
        try:
            import boto3

            s3_client = boto3.client(
                "s3",
                endpoint_url=s3_config["endpoint_url"],
                aws_access_key_id=s3_config["aws_access_key_id"],
                aws_secret_access_key=s3_config["aws_secret_access_key"],
            )
            try:
                response = s3_client.list_objects_v2(Bucket=s3_config["bucket_name"])
                if "Contents" in response:
                    for obj in response["Contents"]:
                        # Delete objects related to new workspaces
                        for workspace_id in new_workspaces:
                            if str(workspace_id) in obj["Key"]:
                                try:
                                    s3_client.delete_object(
                                        Bucket=s3_config["bucket_name"], Key=obj["Key"]
                                    )
                                except Exception:
                                    pass
            finally:
                # Close S3 client to free resources
                s3_client.close()
        except Exception:
            pass

    # 5. Clean up Neo4j nodes (only connect if needed)
    if new_workspaces and neo4j_config["url"]:
        try:
            from neo4j import GraphDatabase

            neo4j_driver = GraphDatabase.driver(
                neo4j_config["url"],
                auth=(neo4j_config["user"], neo4j_config["password"]),
            )
            try:
                # Delete all nodes related to new workspaces
                with neo4j_driver.session() as session:
                    for workspace_id in new_workspaces:
                        try:
                            session.run(
                                "MATCH (n) WHERE n.workspace_id = $workspace_id DETACH DELETE n",
                                workspace_id=workspace_id,
                            )
                        except Exception:
                            pass
            finally:
                # Explicitly close driver to free memory
                neo4j_driver.close()
        except Exception:
            pass

    # 6. Clear Redis cache
    try:
        import redis

        redis_client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db,
            decode_responses=True,
        )
        # Delete CLI state cache if workspaces were deleted
        if new_workspaces:
            try:
                redis_client.delete("cli_state:1")
            except Exception:
                pass

        # Delete cache keys related to workspaces/documents
        for workspace_id in new_workspaces:
            try:
                pattern = f"*workspace*{workspace_id}*"
                for key in redis_client.scan_iter(match=pattern):
                    redis_client.delete(key)
            except Exception:
                pass
        for document_id in new_documents:
            try:
                pattern = f"*document*{document_id}*"
                for key in redis_client.scan_iter(match=pattern):
                    redis_client.delete(key)
            except Exception:
                pass
    except Exception:
        pass

    # 7. Clear CLI state (only if workspaces were created/deleted during test)
    # Reset CLI state to NULL if it's pointing to a deleted workspace
    if new_workspaces:
        try:
            conn = psycopg2.connect(config.database_url)
            cursor = conn.cursor()
            # Reset workspace selection if pointing to a deleted workspace
            cursor.execute(
                "UPDATE cli_state SET current_workspace_id = NULL WHERE current_workspace_id = ANY(%s)",
                (list(new_workspaces),),
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception:
            pass


def get_workspace_create_input(
    name: str,
    description: str = "",
    rag_type: str = "vector",
    # Vector RAG defaults (empty string means use default)
    chunking_algorithm: str = "",
    chunk_size: str = "",
    chunk_overlap: str = "",
    embedding_algorithm: str = "",
    top_k: str = "",
    rerank_algorithm: str = "",
    # Graph RAG defaults (empty string means use default)
    entity_extraction_algorithm: str = "",
    relationship_extraction_algorithm: str = "",
    clustering_algorithm: str = "",
) -> str:
    """Generate input string for workspace create command with all RAG config prompts.

    Args:
        name: Workspace name
        description: Workspace description (optional)
        rag_type: RAG type (vector or graph)
        chunking_algorithm: Chunking algorithm (empty = default)
        chunk_size: Chunk size (empty = default)
        chunk_overlap: Chunk overlap (empty = default)
        embedding_algorithm: Embedding algorithm (empty = default)
        top_k: Top K (empty = default)
        rerank_algorithm: Rerank algorithm (empty = default)
        entity_extraction_algorithm: Entity extraction algorithm (empty = default)
        relationship_extraction_algorithm: Relationship extraction algorithm (empty = default)
        clustering_algorithm: Clustering algorithm (empty = default)

    Returns:
        Input string with newlines for all prompts
    """
    # Start with common prompts
    input_lines = [name, description, rag_type]

    # Add RAG type-specific prompts
    if rag_type == "vector":
        input_lines.extend(
            [
                chunking_algorithm,
                chunk_size,
                chunk_overlap,
                embedding_algorithm,
                top_k,
                rerank_algorithm,
            ]
        )
    elif rag_type == "graph":
        input_lines.extend(
            [
                entity_extraction_algorithm,
                relationship_extraction_algorithm,
                clustering_algorithm,
            ]
        )

    return "\n".join(input_lines) + "\n"
