"""Integration tests for the DocumentService component."""

import tempfile
from collections.abc import Generator
from typing import Any, Optional

import pytest
from returns.result import Failure, Success  # Import Failure
from testcontainers.minio import MinioContainer
from testcontainers.redis import RedisContainer

from src.domains.default_rag_config.data_access import DefaultRagConfigDataAccess
from src.domains.default_rag_config.repositories import DefaultRagConfigRepository
from src.domains.default_rag_config.service import DefaultRagConfigService
from src.domains.workspace.data_access import WorkspaceDataAccess
from src.domains.workspace.document.data_access import DocumentDataAccess
from src.domains.workspace.document.repositories import DocumentRepository
from src.domains.workspace.document.service import DocumentService
from src.domains.workspace.repositories import WorkspaceRepository
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.llm.llm_provider import LlmProvider
from src.infrastructure.rag.rag_config_provider import (
    GraphRagConfigProvider,
    RagConfigProviderFactory,
    VectorRagConfigProvider,
)
from src.infrastructure.rag.store_manager import RAGStoreManager
from src.infrastructure.sql_database import SqlDatabase
from src.infrastructure.storage.file_system_storage import FileSystemBlobStorage
from src.infrastructure.storage.s3_storage import S3BlobStorage


@pytest.mark.integration
class TestDocumentServiceIntegration:
    """Integration tests for the DocumentService component."""

    @pytest.fixture(scope="function")
    def workspace_repository(self, db_session: SqlDatabase) -> WorkspaceRepository:
        """Fixture to create a WorkspaceRepository."""
        return WorkspaceRepository(db_session)

    @pytest.fixture(scope="function")
    def workspace_data_access(
        self, workspace_repository: WorkspaceRepository, cache_instance: RedisCache
    ) -> WorkspaceDataAccess:
        """Fixture for WorkspaceDataAccess with a Redis cache."""
        return WorkspaceDataAccess(repository=workspace_repository, cache=cache_instance)

    @pytest.fixture(scope="function")
    def document_repository(self, db_session: SqlDatabase) -> DocumentRepository:
        """Fixture to create a DocumentRepository."""
        return DocumentRepository(db_session)

    @pytest.fixture(scope="function")
    def cache_instance(self, redis_container: RedisContainer) -> Generator[RedisCache, None, None]:
        """Fixture to create a RedisCache instance connected to the test container."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)
        cache = RedisCache(host=host, port=int(port))
        cache.clear()
        yield cache

    @pytest.fixture(scope="function")
    def document_data_access(
        self, document_repository: DocumentRepository, cache_instance: RedisCache
    ) -> DocumentDataAccess:
        """Fixture for DocumentDataAccess with a Redis cache."""
        return DocumentDataAccess(repository=document_repository, cache=cache_instance)

    @pytest.fixture(scope="function")
    def default_rag_config_repository(self, db_session: SqlDatabase) -> DefaultRagConfigRepository:
        """Fixture to create a DefaultRagConfigRepository."""
        return DefaultRagConfigRepository(db_session)

    @pytest.fixture(scope="function")
    def default_rag_config_data_access(
        self, default_rag_config_repository: DefaultRagConfigRepository, cache_instance: RedisCache
    ) -> DefaultRagConfigDataAccess:
        """Fixture to create a DefaultRagConfigDataAccess."""
        return DefaultRagConfigDataAccess(
            repository=default_rag_config_repository, cache=cache_instance
        )

    @pytest.fixture(scope="function")
    def default_rag_config_service(
        self, default_rag_config_data_access: DefaultRagConfigDataAccess
    ) -> DefaultRagConfigService:
        """Fixture to create a DefaultRagConfigService."""
        return DefaultRagConfigService(data_access=default_rag_config_data_access)

    @pytest.fixture(scope="function")
    def vector_rag_config_provider(
        self, workspace_data_access: WorkspaceDataAccess
    ) -> VectorRagConfigProvider:
        """Fixture to create a VectorRagConfigProvider."""
        return VectorRagConfigProvider(workspace_data_access=workspace_data_access)

    @pytest.fixture(scope="function")
    def graph_rag_config_provider(
        self, workspace_data_access: WorkspaceDataAccess
    ) -> GraphRagConfigProvider:
        """Fixture to create a GraphRagConfigProvider."""
        return GraphRagConfigProvider(workspace_data_access=workspace_data_access)

    @pytest.fixture(scope="function")
    def rag_config_provider_factory(
        self,
        vector_rag_config_provider: VectorRagConfigProvider,
        graph_rag_config_provider: GraphRagConfigProvider,
    ) -> RagConfigProviderFactory:
        """Fixture to create a RagConfigProviderFactory."""
        return RagConfigProviderFactory(
            vector_provider=vector_rag_config_provider,
            graph_provider=graph_rag_config_provider,
        )

    @pytest.fixture(scope="function")
    def llm_provider(self) -> LlmProvider:
        """Fixture to create a dummy LlmProvider."""

        class DummyLlmProvider(LlmProvider):
            def generate_response(self, prompt: str) -> str:
                return "dummy response"

            def chat(self, message: str, conversation_history: Optional[list[dict]] = None) -> str:
                return "dummy response"

            def chat_stream(
                self, message: str, conversation_history: Optional[list[dict]] = None
            ) -> Generator[str, None, None]:
                yield "dummy response"

            def health_check(self) -> dict[str, Any]:
                return {"status": "ok"}

            def get_model_name(self) -> str:
                return "dummy-model"

        return DummyLlmProvider()

    @pytest.fixture(scope="function")
    def rag_store_manager(self) -> RAGStoreManager:
        """Fixture to create a RAGStoreManager."""
        return RAGStoreManager()

    @pytest.fixture(scope="function")
    def file_system_blob_storage(self):
        """Fixture for FileSystemBlobStorage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield FileSystemBlobStorage(base_path=tmpdir)

    @pytest.fixture(scope="function")
    def s3_blob_storage(self, minio_container: MinioContainer):
        """Fixture for S3BlobStorage connected to Minio."""
        endpoint = minio_container.get_config()["endpoint"]
        endpoint = endpoint.replace("https://", "").replace("http://", "")
        access_key = minio_container.get_config()["access_key"]
        secret_key = minio_container.get_config()["secret_key"]
        bucket_name = "test-s3-bucket"

        storage = S3BlobStorage(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            bucket_name=bucket_name,
            secure=False,
        )
        # Ensure bucket is created
        _ = storage.client
        yield storage
        # Clean up bucket after test
        for obj in storage.client.list_objects(bucket_name, recursive=True):
            storage.client.remove_object(bucket_name, obj.object_name)

    @pytest.fixture(scope="function")
    def document_service_fs(
        self,
        document_data_access: DocumentDataAccess,
        workspace_repository: WorkspaceRepository,
        file_system_blob_storage: FileSystemBlobStorage,
        rag_config_provider_factory: RagConfigProviderFactory,
        rag_store_manager: RAGStoreManager,
    ) -> DocumentService:
        """Fixture for DocumentService with FileSystemBlobStorage."""
        return DocumentService(
            data_access=document_data_access,
            workspace_repository=workspace_repository,
            blob_storage=file_system_blob_storage,
            config_provider_factory=rag_config_provider_factory,
            rag_store_manager=rag_store_manager,
        )

    def test_upload_and_process_document_fs_success(
        self, document_service_fs: DocumentService, setup_workspace
    ):
        """Test successful upload and processing of a document with FileSystemBlobStorage."""
        # Arrange
        workspace_id = setup_workspace.id
        filename = "test_doc.txt"
        file_content = b"This is a test document for processing."

        # Act
        result = document_service_fs.upload_and_process_document(
            workspace_id=workspace_id,
            filename=filename,
            file_content=file_content,
        )

        # Assert
        assert isinstance(result, Success)
        document = result.unwrap()
        assert document.filename == filename
        assert document.workspace_id == workspace_id
        assert document.status == "ready"
        assert document.chunk_count > 0

        # Verify file exists in storage
        assert document_service_fs.blob_storage.exists(document.file_path) is True

    def test_upload_and_process_document_fs_workspace_not_found(
        self, document_service_fs: DocumentService
    ):
        """Test upload and process failure when workspace is not found."""
        # Act
        result = document_service_fs.upload_and_process_document(
            workspace_id=999,  # Non-existent workspace
            filename="nonexistent.txt",
            file_content=b"content",
        )

        # Assert
        assert isinstance(result, Failure)  # Corrected assertion
        assert result.failure().resource == "workspace"

    def test_remove_document_fs_success(
        self, document_service_fs: DocumentService, setup_workspace
    ):
        """Test successful removal of a document from FileSystemBlobStorage."""
        # Arrange
        workspace_id = setup_workspace.id
        filename = "delete_me.txt"
        file_content = b"Content to be deleted."

        upload_result = document_service_fs.upload_and_process_document(
            workspace_id=workspace_id,
            filename=filename,
            file_content=file_content,
        )
        assert isinstance(upload_result, Success)
        document = upload_result.unwrap()

        # Act
        deleted = document_service_fs.remove_document(document.id)

        # Assert
        assert deleted is True
        assert document_service_fs.get_document_by_id(document.id) is None
        assert document_service_fs.blob_storage.exists(document.file_path) is False

    def test_list_documents_by_workspace(
        self, document_service_fs: DocumentService, setup_workspace
    ):
        """Test listing documents for a specific workspace."""
        # Arrange
        workspace_id = setup_workspace.id
        doc1_content = b"Doc 1 content"
        doc2_content = b"Doc 2 content"
        document_service_fs.upload_and_process_document(workspace_id, "doc1.txt", doc1_content)
        document_service_fs.upload_and_process_document(workspace_id, "doc2.txt", doc2_content)

        # Act
        documents = document_service_fs.list_documents_by_workspace(workspace_id)

        # Assert
        assert len(documents) == 2
        assert any(d.filename == "doc1.txt" for d in documents)
        assert any(d.filename == "doc2.txt" for d in documents)

    def test_get_document_by_id(self, document_service_fs: DocumentService, setup_workspace):
        """Test retrieving a document by its ID."""
        # Arrange
        workspace_id = setup_workspace.id
        filename = "single_doc.txt"
        file_content = b"Single document content."

        upload_result = document_service_fs.upload_and_process_document(
            workspace_id=workspace_id, filename=filename, file_content=file_content
        )
        assert isinstance(upload_result, Success)
        uploaded_document = upload_result.unwrap()

        # Act
        retrieved_document = document_service_fs.get_document_by_id(uploaded_document.id)

        # Assert
        assert retrieved_document is not None
        assert retrieved_document.id == uploaded_document.id
        assert retrieved_document.filename == filename
