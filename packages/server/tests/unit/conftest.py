# Temporarily disabled due to shared package import issues
# """Unit test fixtures using dummy implementations."""

# from collections.abc import Generator
# from io import BytesIO
# from pathlib import Path

# import psycopg2
# import pytest
# from shared.database.sql import PostgresSQLDatabase
# from shared.repositories import (
#     ChatMessageRepository,
#     ChatSessionRepository,
#     DocumentRepository,
#     UserRepository,
# )
# from shared.storage import BlobStorage
# from testcontainers.postgres import PostgresContainer

# from tests.context import UnitTestContext, create_unit_test_context


# def _run_migrations(db_url: str) -> None:
#     """Run migration SQL files against the database."""
#     migrations_dir = Path(__file__).parent.parent.parent / "migrations"
#     migration_files = sorted(migrations_dir.glob("*.sql"))

#     conn = psycopg2.connect(db_url)
#     try:
#         with conn.cursor() as cur:
#             for migration_file in migration_files:
#                 sql = migration_file.read_text()
#                 cur.execute(sql)
#         conn.commit()
#     finally:
#         conn.close()


# def _drop_all_tables(db_url: str) -> None:
#     """Drop all tables from the database."""
#     conn = psycopg2.connect(db_url)
#     try:
#         with conn.cursor() as cur:
#             cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
#         conn.commit()
#     finally:
#         conn.close()


# @pytest.fixture(scope="session", autouse=False)
# def unit_postgres_container() -> Generator[PostgresContainer, None, None]:
#     """Start a PostgreSQL container for unit tests."""
#     with PostgresContainer("postgres:16-alpine") as postgres:
#         yield postgres


# @pytest.fixture(scope="function")
# def db_url(unit_postgres_container: PostgresContainer) -> Generator[str, None, None]:
#     """Get database URL and run migrations for unit tests."""
#     url = unit_postgres_container.get_connection_url()
#     _run_migrations(url)
#     yield url
#     _drop_all_tables(url)


# @pytest.fixture(scope="function")
# def db(db_url: str) -> Generator[PostgresSQLDatabase, None, None]:
#     """Create a test database connection for unit tests."""
#     database = PostgresSQLDatabase(db_url)
#     try:
#         yield database
#     finally:
#         database.close()


# @pytest.fixture(scope="function")
# def test_context(db: PostgresSQLDatabase) -> UnitTestContext:
#     """Create a test context for unit tests with in-memory implementations."""
#     return create_unit_test_context(db=db)


# @pytest.fixture(scope="function")
# def blob_storage(test_context: UnitTestContext) -> BlobStorage:
#     """Get blob storage from test context."""
#     return test_context.blob_storage


# @pytest.fixture(scope="function")
# def user_repository(test_context: UnitTestContext) -> UserRepository:
#     """Get users repository from test context."""
#     return test_context.user_repository


# @pytest.fixture(scope="function")
# def document_repository(test_context: UnitTestContext) -> DocumentRepository:
#     """Get document repository from test context."""
#     return test_context.document_repository


# @pytest.fixture(scope="function")
# def chat_session_repository(test_context: UnitTestContext) -> ChatSessionRepository:
#     """Get chats session repository from test context."""
#     return test_context.chat_session_repository


# @pytest.fixture(scope="function")
# def chat_message_repository(test_context: UnitTestContext) -> ChatMessageRepository:
#     """Get chats message repository from test context."""
#     return test_context.chat_message_repository


# @pytest.fixture
# def sample_text_file() -> BytesIO:
#     """Create a sample text file for testing."""
#     content = b"This is a test document.\nIt has multiple lines.\nFor testing purposes."
#     return BytesIO(content)


# @pytest.fixture
# def sample_pdf_file() -> BytesIO:
#     """Create a sample PDF file for testing."""
#     # Minimal valid PDF
#     pdf_content = b"""%PDF-1.4
# 1 0 obj
# <<
# /Type /Catalog
# /Pages 2 0 R
# >>
# endobj
# 2 0 obj
# <<
# /Type /Pages
# /Kids [3 0 R]
# /Count 1
# >>
# endobj
# 3 0 obj
# <<
# /Type /Page
# /Parent 2 0 R
# /Resources <<
# /Font <<
# /F1 <<
# /Type /Font
# /Subtype /Type1
# /BaseFont /Helvetica
# >>
# >>
# >>
# /MediaBox [0 0 612 792]
# /Contents 4 0 R
# >>
# endobj
# 4 0 obj
# <<
# /Length 44
# >>
# stream
# BT
# /F1 12 Tf
# 100 700 Td
# (Hello World) Tj
# ET
# endstream
# endobj
# xref
# 0 5
# 0000000000 65535 f
# 0000000009 00000 n
# 0000000058 00000 n
# 0000000115 00000 n
# 0000000317 00000 n
# trailer
# <<
# /Size 5
# /Root 1 0 R
# >>
# startxref
# 409
# %%EOF"""
#     return BytesIO(pdf_content)
