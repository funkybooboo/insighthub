import os
from collections.abc import Generator

import pytest

try:
    from testcontainers.postgresql import PostgreSQLContainer

    POSTGRES_AVAILABLE = True
except Exception:
    POSTGRES_AVAILABLE = False


@pytest.fixture(scope="session")
def postgres_url() -> Generator[str, None, None]:
    if not POSTGRES_AVAILABLE:
        pytest.skip("testcontainers PostgreSQL not available; skipping integration tests")
    with PostgreSQLContainer("postgres:15-alpine") as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(5432)
        url = f"postgresql+psycopg2://postgres:postgres@{host}:{port}/postgres"
        os.environ["DATABASE_URL"] = url
        yield url
        del os.environ["DATABASE_URL"]
