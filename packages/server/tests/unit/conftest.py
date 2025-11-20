"""Unit test fixtures using dummy implementations."""

from collections.abc import Generator
from io import BytesIO

import pytest
from shared.database import Base
from shared.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    DocumentRepository,
    UserRepository,
)
from shared.storage import BlobStorage
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from tests.context import UnitTestContext, create_unit_test_context


@pytest.fixture(scope="function")
def unit_db_engine() -> Generator[Engine, None, None]:
    """Create an in-memory SQLite database engine for unit tests."""
    # Use SQLite in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(unit_db_engine: Engine) -> Generator[Session, None, None]:
    """Create a database session for unit tests."""

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=unit_db_engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def test_context(db_session: Session) -> UnitTestContext:
    """Create a test context for unit tests with in-memory implementations."""
    return create_unit_test_context(db=db_session)


@pytest.fixture(scope="function")
def blob_storage(test_context: UnitTestContext) -> BlobStorage:
    """Get blob storage from test context."""
    return test_context.blob_storage


@pytest.fixture(scope="function")
def user_repository(test_context: UnitTestContext) -> UserRepository:
    """Get user repository from test context."""
    return test_context.user_repository


@pytest.fixture(scope="function")
def document_repository(test_context: UnitTestContext) -> DocumentRepository:
    """Get document repository from test context."""
    return test_context.document_repository


@pytest.fixture(scope="function")
def chat_session_repository(test_context: UnitTestContext) -> ChatSessionRepository:
    """Get chat session repository from test context."""
    return test_context.chat_session_repository


@pytest.fixture(scope="function")
def chat_message_repository(test_context: UnitTestContext) -> ChatMessageRepository:
    """Get chat message repository from test context."""
    return test_context.chat_message_repository


@pytest.fixture
def sample_text_file() -> BytesIO:
    """Create a sample text file for testing."""
    content = b"This is a test document.\nIt has multiple lines.\nFor testing purposes."
    return BytesIO(content)


@pytest.fixture
def sample_pdf_file() -> BytesIO:
    """Create a sample PDF file for testing."""
    # Minimal valid PDF
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
409
%%EOF"""
    return BytesIO(pdf_content)
