""Contract tests: validate signatures for all repository interfaces."""

from .contract_utils import assert_abstract, assert_signature_matches

# Import interface classes and models to drive tests
from shared.repositories.document import DocumentRepository
from shared.repositories.user import UserRepository
from shared.repositories.chat import (
    ChatSessionRepository,
    ChatMessageRepository,
)
from shared.repositories.status import StatusRepository

from shared.models.document import Document
from shared.models.user import User
from shared.models.chat import ChatSession, ChatMessage
from shared.models.workspace import Workspace


def test_document_repository_contracts():
    assert_abstract(DocumentRepository, [
        "create","get_by_id","get_by_user","get_by_content_hash","update","delete"
    ])

    assert_signature_matches(DocumentRepository, "create",
        ["user_id","filename","file_path","file_size","mime_type","content_hash","chunk_count","rag_collection"],
        expected_return_contains="Document")
    assert_signature_matches(DocumentRepository, "get_by_id",
        ["document_id"], expected_return_contains="Document")
    assert_signature_matches(DocumentRepository, "get_by_user",
        ["user_id","skip","limit"], expected_return_contains="Document")
    assert_signature_matches(DocumentRepository, "get_by_content_hash",
        ["content_hash"], expected_return_contains="Document")
    assert_signature_matches(DocumentRepository, "update",
        ["document_id","kwargs"], expected_return_contains="Document")
    assert_signature_matches(DocumentRepository, "delete",
        ["document_id"], expected_return_contains="bool")


def test_user_repository_contracts():
    assert_abstract(UserRepository, ["create","get_by_id","get_by_username","get_by_email","get_all","update","delete"])
    assert_signature_matches(UserRepository, "create",
        ["username","email","password","full_name"], expected_return_contains="User")
    assert_signature_matches(UserRepository, "get_by_id", ["user_id"], expected_return_contains="User")
    assert_signature_matches(UserRepository, "get_by_username", ["username"], expected_return_contains="User")
    assert_signature_matches(UserRepository, "get_by_email", ["email"], expected_return_contains="User")
    assert_signature_matches(UserRepository, "get_all", ["skip","limit"], expected_return_contains="list[User]")
    assert_signature_matches(UserRepository, "update", ["user_id","kwargs"], expected_return_contains="User")
    assert_signature_matches(UserRepository, "delete", ["user_id"], expected_return_contains="bool")


def test_chat_session_and_message_contracts():
    assert_abstract(ChatSessionRepository, ["create","get_by_id","get_by_user","update","delete"])
    assert_signature_matches(ChatSessionRepository, "create", ["user_id","title","rag_type"], expected_return_contains="ChatSession")
    assert_signature_matches(ChatSessionRepository, "get_by_id", ["session_id"], expected_return_contains="ChatSession")
    assert_signature_matches(ChatSessionRepository, "get_by_user", ["user_id","skip","limit"], expected_return_contains="list[ChatSession]")
    assert_signature_matches(ChatSessionRepository, "update", ["session_id","kwargs"], expected_return_contains="ChatSession")
    assert_signature_matches(ChatSessionRepository, "delete", ["session_id"], expected_return_contains="bool")

    assert_abstract(ChatMessageRepository, ["create","get_by_id","get_by_session","delete"])
    assert_signature_matches(ChatMessageRepository, "create", ["session_id","role","content","extra_metadata"], expected_return_contains="ChatMessage")
    assert_signature_matches(ChatMessageRepository, "get_by_id", ["message_id"], expected_return_contains="ChatMessage")
    assert_signature_matches(ChatMessageRepository, "get_by_session", ["session_id","skip","limit"], expected_return_contains="list[ChatMessage]")
    assert_signature_matches(ChatMessageRepository, "delete", ["message_id"], expected_return_contains="bool")


def test_status_repository_contracts():
    assert_abstract(StatusRepository, ["update_document_status","update_workspace_status"])
    assert_signature_matches(StatusRepository, "update_document_status",
        ["document_id","status","error","chunk_count"], expected_return_contains="Option")
    assert_signature_matches(StatusRepository, "update_workspace_status",
        ["workspace_id","status","message"], expected_return_contains="Option")
