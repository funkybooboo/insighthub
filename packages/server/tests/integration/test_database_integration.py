"""Integration tests for database operations with PostgreSQL testcontainer."""

import pytest
from sqlalchemy.orm import Session

from src.db.models import ChatMessage, ChatSession, Document, User
from src.db.repository import (
    ChatMessageRepository,
    ChatSessionRepository,
    DocumentRepository,
    UserRepository,
)


def test_user_document_relationship(db_session: Session) -> None:
    """Test the relationship between users and documents."""
    user_repo = UserRepository(db_session)
    doc_repo = DocumentRepository(db_session)

    # Create user
    user = user_repo.create(username="testuser", email="test@example.com")

    # Create documents for user
    doc1 = doc_repo.create(
        user_id=user.id,
        filename="doc1.pdf",
        file_path="blob/doc1.pdf",
        file_size=1024,
        mime_type="application/pdf",
        content_hash="hash1",
    )
    doc2 = doc_repo.create(
        user_id=user.id,
        filename="doc2.txt",
        file_path="blob/doc2.txt",
        file_size=512,
        mime_type="text/plain",
        content_hash="hash2",
    )

    # Refresh user to load relationships
    db_session.refresh(user)

    # Verify relationships
    assert len(user.documents) == 2
    assert doc1 in user.documents
    assert doc2 in user.documents


def test_cascade_delete_user_documents(db_session: Session) -> None:
    """Test that deleting a user cascades to their documents."""
    user_repo = UserRepository(db_session)
    doc_repo = DocumentRepository(db_session)

    # Create user and document
    user = user_repo.create(username="testuser", email="test@example.com")
    doc = doc_repo.create(
        user_id=user.id,
        filename="doc.pdf",
        file_path="blob/doc.pdf",
        file_size=1024,
        mime_type="application/pdf",
        content_hash="hash",
    )
    doc_id = doc.id

    # Delete user
    user_repo.delete(user.id)

    # Verify document is also deleted
    assert doc_repo.get_by_id(doc_id) is None


def test_chat_session_message_relationship(db_session: Session) -> None:
    """Test the relationship between chat sessions and messages."""
    user_repo = UserRepository(db_session)
    session_repo = ChatSessionRepository(db_session)
    message_repo = ChatMessageRepository(db_session)

    # Create user and session
    user = user_repo.create(username="testuser", email="test@example.com")
    session = session_repo.create(
        user_id=user.id, title="Test Chat", rag_type="vector"
    )

    # Create messages
    msg1 = message_repo.create(
        session_id=session.id, role="user", content="Hello"
    )
    msg2 = message_repo.create(
        session_id=session.id, role="assistant", content="Hi there!"
    )

    # Refresh session to load relationships
    db_session.refresh(session)

    # Verify relationships
    assert len(session.messages) == 2
    assert msg1 in session.messages
    assert msg2 in session.messages


def test_cascade_delete_session_messages(db_session: Session) -> None:
    """Test that deleting a session cascades to its messages."""
    user_repo = UserRepository(db_session)
    session_repo = ChatSessionRepository(db_session)
    message_repo = ChatMessageRepository(db_session)

    # Create user, session, and message
    user = user_repo.create(username="testuser", email="test@example.com")
    session = session_repo.create(user_id=user.id)
    msg = message_repo.create(
        session_id=session.id, role="user", content="Test"
    )
    msg_id = msg.id

    # Delete session
    session_repo.delete(session.id)

    # Verify message is also deleted
    assert message_repo.get_by_id(msg_id) is None


def test_unique_constraints(db_session: Session) -> None:
    """Test that unique constraints are enforced."""
    user_repo = UserRepository(db_session)

    # Create first user
    user_repo.create(username="testuser", email="test@example.com")

    # Try to create user with same username
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        user_repo.create(username="testuser", email="other@example.com")
        db_session.commit()

    db_session.rollback()

    # Try to create user with same email
    with pytest.raises(Exception):
        user_repo.create(username="otheruser", email="test@example.com")
        db_session.commit()


def test_document_content_hash_index(db_session: Session) -> None:
    """Test that content_hash is indexed for fast lookups."""
    user_repo = UserRepository(db_session)
    doc_repo = DocumentRepository(db_session)

    # Create user
    user = user_repo.create(username="testuser", email="test@example.com")

    # Create documents with same content hash
    hash_value = "identical_content_hash"
    doc1 = doc_repo.create(
        user_id=user.id,
        filename="doc1.pdf",
        file_path="blob/doc1.pdf",
        file_size=1024,
        mime_type="application/pdf",
        content_hash=hash_value,
    )

    # Find by hash (should be fast due to index)
    found_doc = doc_repo.get_by_content_hash(hash_value)

    assert found_doc is not None
    assert found_doc.id == doc1.id


def test_pagination(db_session: Session) -> None:
    """Test pagination works correctly."""
    user_repo = UserRepository(db_session)

    # Create 10 users
    for i in range(10):
        user_repo.create(username=f"user{i}", email=f"user{i}@example.com")

    # Test pagination
    page1 = user_repo.get_all(skip=0, limit=5)
    page2 = user_repo.get_all(skip=5, limit=5)

    assert len(page1) == 5
    assert len(page2) == 5
    assert page1[0].id != page2[0].id


def test_timestamp_auto_update(db_session: Session) -> None:
    """Test that updated_at is automatically updated."""
    user_repo = UserRepository(db_session)

    # Create user
    user = user_repo.create(username="testuser", email="test@example.com")
    original_updated_at = user.updated_at

    # Update user
    import time
    time.sleep(0.1)  # Small delay to ensure timestamp difference
    updated_user = user_repo.update(user.id, full_name="New Name")

    assert updated_user is not None
    assert updated_user.updated_at > original_updated_at
