"""Integration tests for database operations with PostgreSQL testcontainer."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.domains.chat.repositories import ChatMessageRepository, ChatSessionRepository
from src.domains.documents.repositories import DocumentRepository
from src.domains.users.repositories import UserRepository


def test_user_document_relationship(
    user_repository: UserRepository, document_repository: DocumentRepository, db_session: Session
) -> None:
    """Test the relationship between users and documents."""
    # Create user
    user = user_repository.create(
        username="testuser", email="test@example.com", password="password123"
    )

    # Create documents for user
    doc1 = document_repository.create(
        user_id=user.id,
        filename="doc1.pdf",
        file_path="blob/doc1.pdf",
        file_size=1024,
        mime_type="application/pdf",
        content_hash="hash1",
    )
    doc2 = document_repository.create(
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


def test_cascade_delete_user_documents(
    user_repository: UserRepository, document_repository: DocumentRepository
) -> None:
    """Test that deleting a user cascades to their documents."""
    # Create user and document
    user = user_repository.create(
        username="testuser", email="test@example.com", password="password123"
    )
    doc = document_repository.create(
        user_id=user.id,
        filename="doc.pdf",
        file_path="blob/doc.pdf",
        file_size=1024,
        mime_type="application/pdf",
        content_hash="hash",
    )
    doc_id = doc.id

    # Delete user
    user_repository.delete(user.id)

    # Verify document is also deleted
    assert document_repository.get_by_id(doc_id) is None


def test_chat_session_message_relationship(
    user_repository: UserRepository,
    chat_session_repository: ChatSessionRepository,
    chat_message_repository: ChatMessageRepository,
    db_session: Session,
) -> None:
    """Test the relationship between chat sessions and messages."""
    # Create user and session
    user = user_repository.create(
        username="testuser", email="test@example.com", password="password123"
    )
    session = chat_session_repository.create(user_id=user.id, title="Test Chat", rag_type="vector")

    # Create messages
    msg1 = chat_message_repository.create(session_id=session.id, role="user", content="Hello")
    msg2 = chat_message_repository.create(
        session_id=session.id, role="assistant", content="Hi there!"
    )

    # Refresh session to load relationships
    db_session.refresh(session)

    # Verify relationships
    assert len(session.messages) == 2
    assert msg1 in session.messages
    assert msg2 in session.messages


def test_cascade_delete_session_messages(
    user_repository: UserRepository,
    chat_session_repository: ChatSessionRepository,
    chat_message_repository: ChatMessageRepository,
) -> None:
    """Test that deleting a session cascades to its messages."""
    # Create user, session, and message
    user = user_repository.create(
        username="testuser", email="test@example.com", password="password123"
    )
    session = chat_session_repository.create(user_id=user.id)
    msg = chat_message_repository.create(session_id=session.id, role="user", content="Test")
    msg_id = msg.id

    # Delete session
    chat_session_repository.delete(session.id)

    # Verify message is also deleted
    assert chat_message_repository.get_by_id(msg_id) is None


def test_unique_constraints(user_repository: UserRepository, db_session: Session) -> None:
    """Test that unique constraints are enforced."""
    # Create first user
    user_repository.create(username="testuser", email="test@example.com", password="password123")

    # Try to create user with same username
    with pytest.raises(IntegrityError):
        user_repository.create(
            username="testuser", email="other@example.com", password="password123"
        )
        db_session.commit()

    db_session.rollback()

    # Try to create user with same email
    with pytest.raises(IntegrityError):
        user_repository.create(
            username="otheruser", email="test@example.com", password="password123"
        )
        db_session.commit()


def test_document_content_hash_index(
    user_repository: UserRepository, document_repository: DocumentRepository
) -> None:
    """Test that content_hash is indexed for fast lookups."""
    # Create user
    user = user_repository.create(
        username="testuser", email="test@example.com", password="password123"
    )

    # Create documents with same content hash
    hash_value = "identical_content_hash"
    doc1 = document_repository.create(
        user_id=user.id,
        filename="doc1.pdf",
        file_path="blob/doc1.pdf",
        file_size=1024,
        mime_type="application/pdf",
        content_hash=hash_value,
    )

    # Find by hash (should be fast due to index)
    found_doc = document_repository.get_by_content_hash(hash_value)

    assert found_doc is not None
    assert found_doc.id == doc1.id


def test_pagination(user_repository: UserRepository) -> None:
    """Test pagination works correctly."""
    # Create 10 users
    for i in range(10):
        user_repository.create(
            username=f"user{i}", email=f"user{i}@example.com", password="password123"
        )

    # Test pagination
    page1 = user_repository.get_all(skip=0, limit=5)
    page2 = user_repository.get_all(skip=5, limit=5)

    assert len(page1) == 5
    assert len(page2) == 5
    assert page1[0].id != page2[0].id


def test_timestamp_auto_update(user_repository: UserRepository) -> None:
    """Test that updated_at is automatically updated."""
    # Create user
    user = user_repository.create(
        username="testuser", email="test@example.com", password="password123"
    )
    original_updated_at = user.updated_at

    # Update user
    import time

    time.sleep(0.1)  # Small delay to ensure timestamp difference
    updated_user = user_repository.update(user.id, full_name="New Name")

    assert updated_user is not None
    assert updated_user.updated_at > original_updated_at
