"""Pytest configuration and fixtures."""

import glob
from collections.abc import Generator

import pytest
from returns.result import Success
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from src.domains.workspace.repositories import WorkspaceRepository
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.sql_database import SqlDatabase


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "skip_ci: Skip in CI environment")


@pytest.fixture(scope="session")
def postgres_container():
    """Fixture to spin up a PostgreSQL container for testing."""
    with PostgresContainer("pgvector/pgvector:pg16") as container:
        yield container


@pytest.fixture(scope="session")
def redis_container():
    """Fixture to spin up a Redis container for testing."""
    with RedisContainer("redis:7-alpine") as container:
        yield container


@pytest.fixture(scope="function")
def db_instance(postgres_container: PostgresContainer):
    """Fixture to create a SqlDatabase instance connected to the test container."""
    db_url = postgres_container.get_connection_url().replace("+psycopg2", "")
    db = SqlDatabase(db_url)
    yield db
    db.close()


@pytest.fixture(scope="function")
def cache_instance(redis_container: RedisContainer) -> Generator[RedisCache, None, None]:
    """Fixture to create a RedisCache instance connected to the test container."""
    host = redis_container.get_container_host_ip()
    port = redis_container.get_exposed_port(6379)
    cache = RedisCache(host=host, port=int(port))
    cache.clear()
    yield cache


@pytest.fixture(scope="function")
def db_session(db_instance: SqlDatabase):
    """Fixture to set up and tear down the database schema for each test function."""
    # Run up migrations
    migration_files = sorted(glob.glob("migrations/up/*.sql"))
    for file in migration_files:
        with open(file, "r") as f:
            db_instance.execute(f.read())

    yield db_instance

    # Run down migrations in reverse order
    migration_files = sorted(glob.glob("migrations/down/*.sql"), reverse=True)
    for file in migration_files:
        with open(file, "r") as f:
            db_instance.execute(f.read())


@pytest.fixture(scope="function")
def workspace_repository(db_session: SqlDatabase) -> WorkspaceRepository:
    """Fixture to create a WorkspaceRepository."""
    return WorkspaceRepository(db_session)


@pytest.fixture(scope="function")
def setup_workspace(workspace_repository: WorkspaceRepository):
    """Fixture to set up a workspace for testing."""
    create_result = workspace_repository.create("test-ws", "test-desc", "vector")
    assert isinstance(create_result, Success)
    return create_result.unwrap()
