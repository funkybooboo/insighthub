"""Unit tests for service factories."""

from unittest.mock import patch

import pytest

from src.blob_storages import BlobStorage, InMemoryBlobStorage
from src.services.chat_service import (
    ChatServiceType,
    DefaultChatService,
    create_chat_service,
)
from src.services.document_service import (
    DefaultDocumentService,
    DocumentServiceType,
    create_document_service,
)
from src.services.user_service import (
    DefaultUserService,
    UserServiceType,
    create_user_service,
)

# Import unit test fixtures (SQLite in-memory database)
from tests.unit.conftest import *


class TestUserServiceFactory:
    """Test cases for user service factory."""

    def test_create_default_service_explicitly(self, db_session) -> None:
        """Test creating default user service with explicit type."""
        # Use real SQLite session, not mocks
        service = create_user_service(db_session, UserServiceType.DEFAULT)

        assert isinstance(service, DefaultUserService)
        assert service.repository is not None

    def test_create_service_from_config(self, db_session) -> None:
        """Test creating user service from config."""
        with patch("src.config.USER_SERVICE_TYPE", "default"):
            service = create_user_service(db_session)

            assert isinstance(service, DefaultUserService)

    def test_invalid_service_type_raises_error(self, db_session) -> None:
        """Test that invalid service type raises ValueError."""
        with patch("src.config.USER_SERVICE_TYPE", "invalid_type"):
            with pytest.raises(ValueError) as exc_info:
                create_user_service(db_session)

            assert "invalid_type" in str(exc_info.value)

    def test_service_type_enum_value(self) -> None:
        """Test that UserServiceType enum has expected value."""
        assert UserServiceType.DEFAULT.value == "default"


class TestDocumentServiceFactory:
    """Test cases for document service factory."""

    def test_create_default_service_explicitly(self, db_session) -> None:
        """Test creating default document service with explicit type."""
        # Use real SQLite session and in-memory blob storage
        blob_storage = InMemoryBlobStorage()

        service = create_document_service(
            db_session,
            blob_storage=blob_storage,
            service_type=DocumentServiceType.DEFAULT,
        )

        assert isinstance(service, DefaultDocumentService)
        assert service.repository is not None
        assert service.blob_storage == blob_storage

    def test_create_service_from_config(self, db_session) -> None:
        """Test creating document service from config."""
        with patch("src.config.DOCUMENT_SERVICE_TYPE", "default"):
            with patch("src.config.BLOB_STORAGE_TYPE", "in_memory"):
                service = create_document_service(db_session)

                assert isinstance(service, DefaultDocumentService)
                # Should have created blob storage automatically
                assert service.blob_storage is not None

    def test_create_service_with_provided_blob_storage(self, db_session) -> None:
        """Test creating document service with provided blob storage."""
        blob_storage = InMemoryBlobStorage()

        with patch("src.config.DOCUMENT_SERVICE_TYPE", "default"):
            service = create_document_service(db_session, blob_storage=blob_storage)

            assert isinstance(service, DefaultDocumentService)
            assert service.blob_storage == blob_storage

    def test_service_type_enum_value(self) -> None:
        """Test that DocumentServiceType enum has expected value."""
        assert DocumentServiceType.DEFAULT.value == "default"


class TestChatServiceFactory:
    """Test cases for chat service factory."""

    def test_create_default_service_explicitly(self, db_session) -> None:
        """Test creating default chat service with explicit type."""
        # Use real SQLite session
        service = create_chat_service(db_session, ChatServiceType.DEFAULT)

        assert isinstance(service, DefaultChatService)
        assert service.session_repository is not None
        assert service.message_repository is not None

    def test_create_service_from_config(self, db_session) -> None:
        """Test creating chat service from config."""
        with patch("src.config.CHAT_SERVICE_TYPE", "default"):
            service = create_chat_service(db_session)

            assert isinstance(service, DefaultChatService)

    def test_service_type_enum_value(self) -> None:
        """Test that ChatServiceType enum has expected value."""
        assert ChatServiceType.DEFAULT.value == "default"
