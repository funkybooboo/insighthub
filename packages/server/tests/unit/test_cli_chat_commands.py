"""Tests for CLI chat commands."""

import argparse
from typing import cast
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.domains.chat import commands


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock AppContext."""
    context = Mock()
    context.user_service = Mock()
    context.chat_service = Mock()
    context.document_service = Mock()
    return cast(MagicMock, context)


@pytest.fixture
def mock_user() -> Mock:
    """Create a mock user."""
    user = Mock()
    user.id = 1
    user.username = "testuser"
    return user


class TestSendChatMessage:
    """Tests for send_chat_message function."""

    def test_send_chat_message_success(self, mock_context: MagicMock, mock_user: Mock) -> None:
        """Test successful chat message."""
        mock_context.user_service.get_or_create_default_user.return_value = mock_user

        mock_chat_response = Mock()
        mock_chat_response.answer = "Test answer"
        mock_chat_response.session_id = 1
        mock_chat_response.context = [
            Mock(text="Context 1", score=0.9, metadata={"doc_id": "1"}),
            Mock(text="Context 2", score=0.8, metadata={"doc_id": "2"}),
        ]
        mock_context.chat_service.process_chat_message.return_value = mock_chat_response

        mock_context.document_service.list_user_documents.return_value = [Mock(), Mock()]

        result = commands.send_chat_message(mock_context, "test question")

        assert result["answer"] == "Test answer"
        assert result["session_id"] == 1
        assert result["documents_count"] == 2
        assert len(result["context"]) == 2
        mock_context.chat_service.process_chat_message.assert_called_once_with(
            user_id=1,
            message="test question",
            session_id=None,
            rag_type="vector",
        )

    def test_send_chat_message_with_session(self, mock_context: MagicMock, mock_user: Mock) -> None:
        """Test chat message with existing session."""
        mock_context.user_service.get_or_create_default_user.return_value = mock_user

        mock_chat_response = Mock()
        mock_chat_response.answer = "Test answer"
        mock_chat_response.session_id = 5
        mock_chat_response.context = []
        mock_context.chat_service.process_chat_message.return_value = mock_chat_response

        mock_context.document_service.list_user_documents.return_value = []

        result = commands.send_chat_message(mock_context, "test question", session_id=5)

        assert result["session_id"] == 5
        mock_context.chat_service.process_chat_message.assert_called_once_with(
            user_id=1,
            message="test question",
            session_id=5,
            rag_type="vector",
        )

    def test_send_chat_message_context_structure(self, mock_context: MagicMock, mock_user: Mock) -> None:
        """Test that context is properly formatted."""
        mock_context.user_service.get_or_create_default_user.return_value = mock_user

        mock_chat_response = Mock()
        mock_chat_response.answer = "Answer"
        mock_chat_response.session_id = 1
        mock_context_item = Mock()
        mock_context_item.text = "Test context"
        mock_context_item.score = 0.95
        mock_context_item.metadata = {"doc_id": "123"}
        mock_chat_response.context = [mock_context_item]
        mock_context.chat_service.process_chat_message.return_value = mock_chat_response

        mock_context.document_service.list_user_documents.return_value = []

        result = commands.send_chat_message(mock_context, "question")

        assert len(result["context"]) == 1
        assert result["context"][0]["text"] == "Test context"
        assert result["context"][0]["score"] == 0.95
        assert result["context"][0]["metadata"] == {"doc_id": "123"}


class TestListSessions:
    """Tests for list_sessions function."""

    def test_list_sessions_success(self, mock_context: MagicMock, mock_user: Mock) -> None:
        """Test successful session listing."""
        mock_context.user_service.get_or_create_default_user.return_value = mock_user

        mock_session1 = Mock()
        mock_session1.id = 1
        mock_session1.title = "Session 1"
        mock_session1.rag_type = "vector"
        mock_session1.created_at.isoformat.return_value = "2024-01-01T00:00:00"
        mock_session1.updated_at.isoformat.return_value = "2024-01-01T01:00:00"

        mock_session2 = Mock()
        mock_session2.id = 2
        mock_session2.title = None
        mock_session2.rag_type = "graph"
        mock_session2.created_at.isoformat.return_value = "2024-01-02T00:00:00"
        mock_session2.updated_at.isoformat.return_value = "2024-01-02T01:00:00"

        mock_context.chat_service.list_user_sessions.return_value = [mock_session1, mock_session2]

        result = commands.list_sessions(mock_context)

        assert result["count"] == 2
        assert len(result["sessions"]) == 2
        assert result["sessions"][0]["id"] == 1
        assert result["sessions"][0]["title"] == "Session 1"
        assert result["sessions"][1]["id"] == 2
        assert result["sessions"][1]["title"] == ""  # None converted to empty string

    def test_list_sessions_empty(self, mock_context: MagicMock, mock_user: Mock) -> None:
        """Test listing when no sessions exist."""
        mock_context.user_service.get_or_create_default_user.return_value = mock_user
        mock_context.chat_service.list_user_sessions.return_value = []

        result = commands.list_sessions(mock_context)

        assert result["count"] == 0
        assert result["sessions"] == []


class TestCmdChat:
    """Tests for cmd_chat CLI handler."""

    @patch("src.domains.chat.commands.send_chat_message")
    @patch("builtins.print")
    def test_cmd_chat_success(self, mock_print: MagicMock, mock_send_message: MagicMock, mock_context: MagicMock) -> None:
        """Test cmd_chat with successful message."""
        args = argparse.Namespace(message="test question", session_id=None, show_context=False)
        mock_send_message.return_value = {
            "answer": "Test answer",
            "context": [],
            "session_id": 1,
            "documents_count": 2,
        }

        commands.cmd_chat(mock_context, args)

        mock_send_message.assert_called_once_with(mock_context, "test question", None)
        assert mock_print.call_count >= 1
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Test answer" in str(call) for call in print_calls)

    @patch("src.domains.chat.commands.send_chat_message")
    @patch("builtins.print")
    def test_cmd_chat_with_context(self, mock_print: MagicMock, mock_send_message: MagicMock, mock_context: MagicMock) -> None:
        """Test cmd_chat with show_context flag."""
        args = argparse.Namespace(message="question", session_id=None, show_context=True)
        mock_send_message.return_value = {
            "answer": "Answer",
            "context": [
                {"text": "Context text here", "score": 0.95, "metadata": {}},
            ],
            "session_id": 1,
            "documents_count": 1,
        }

        commands.cmd_chat(mock_context, args)

        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Context" in str(call) for call in print_calls)
        assert any("0.95" in str(call) for call in print_calls)

    @patch("src.domains.chat.commands.send_chat_message")
    @patch("builtins.print")
    def test_cmd_chat_with_session_id(self, mock_print: MagicMock, mock_send_message: MagicMock, mock_context: MagicMock) -> None:
        """Test cmd_chat with session_id argument."""
        args = argparse.Namespace(message="question", session_id=5, show_context=False)
        mock_send_message.return_value = {
            "answer": "Answer",
            "context": [],
            "session_id": 5,
            "documents_count": 0,
        }

        commands.cmd_chat(mock_context, args)

        mock_send_message.assert_called_once_with(mock_context, "question", 5)

    @patch("src.domains.chat.commands.send_chat_message")
    @patch("builtins.print")
    def test_cmd_chat_error(self, mock_print: MagicMock, mock_send_message: MagicMock, mock_context: MagicMock) -> None:
        """Test cmd_chat with error."""
        args = argparse.Namespace(message="question", session_id=None, show_context=False)
        mock_send_message.side_effect = Exception("Test error")

        with pytest.raises(SystemExit) as exc_info:
            commands.cmd_chat(mock_context, args)

        assert exc_info.value.code == 1


class TestCmdSessions:
    """Tests for cmd_sessions CLI handler."""

    @patch("src.domains.chat.commands.list_sessions")
    @patch("builtins.print")
    def test_cmd_sessions_with_sessions(self, mock_print: MagicMock, mock_list_sessions: MagicMock, mock_context: MagicMock) -> None:
        """Test cmd_sessions with existing sessions."""
        args = argparse.Namespace()
        mock_list_sessions.return_value = {
            "sessions": [
                {
                    "id": 1,
                    "title": "Test Session",
                    "rag_type": "vector",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T01:00:00",
                }
            ],
            "count": 1,
        }

        commands.cmd_sessions(mock_context, args)

        mock_list_sessions.assert_called_once_with(mock_context)
        assert mock_print.call_count >= 1

    @patch("src.domains.chat.commands.list_sessions")
    @patch("builtins.print")
    def test_cmd_sessions_empty(self, mock_print: MagicMock, mock_list_sessions: MagicMock, mock_context: MagicMock) -> None:
        """Test cmd_sessions with no sessions."""
        args = argparse.Namespace()
        mock_list_sessions.return_value = {"sessions": [], "count": 0}

        commands.cmd_sessions(mock_context, args)

        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("No chat sessions" in str(call) for call in print_calls)


class TestCmdInteractive:
    """Tests for cmd_interactive CLI handler."""

    @patch("src.domains.chat.commands.send_chat_message")
    @patch("builtins.input", side_effect=["hello", "quit"])
    @patch("builtins.print")
    def test_cmd_interactive_basic(self, mock_print: MagicMock, mock_input: MagicMock, mock_send_message: MagicMock, mock_context: MagicMock) -> None:
        """Test basic interactive chat session."""
        args = argparse.Namespace()
        mock_send_message.return_value = {
            "answer": "Hi there!",
            "context": [],
            "session_id": 1,
            "documents_count": 0,
        }

        commands.cmd_interactive(mock_context, args)

        assert mock_send_message.call_count == 1
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Hi there!" in str(call) for call in print_calls)
        assert any("Goodbye" in str(call) for call in print_calls)

    @patch("src.domains.chat.commands.send_chat_message")
    @patch("builtins.input", side_effect=["exit"])
    @patch("builtins.print")
    def test_cmd_interactive_exit_command(self, mock_print: MagicMock, mock_input: MagicMock, mock_send_message: MagicMock, mock_context: MagicMock) -> None:
        """Test exiting with 'exit' command."""
        args = argparse.Namespace()

        commands.cmd_interactive(mock_context, args)

        assert mock_send_message.call_count == 0
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Goodbye" in str(call) for call in print_calls)

    @patch("src.domains.chat.commands.send_chat_message")
    @patch("builtins.input", side_effect=["", "   ", "test", "quit"])
    @patch("builtins.print")
    def test_cmd_interactive_empty_messages(self, mock_print: MagicMock, mock_input: MagicMock, mock_send_message: MagicMock, mock_context: MagicMock) -> None:
        """Test that empty messages are skipped."""
        args = argparse.Namespace()
        mock_send_message.return_value = {
            "answer": "Response",
            "context": [],
            "session_id": 1,
            "documents_count": 0,
        }

        commands.cmd_interactive(mock_context, args)

        # Should only send one message (the "test" message)
        assert mock_send_message.call_count == 1

    @patch("src.domains.chat.commands.send_chat_message")
    @patch("builtins.input", side_effect=["first", "second", "quit"])
    @patch("builtins.print")
    def test_cmd_interactive_session_persistence(self, mock_print: MagicMock, mock_input: MagicMock, mock_send_message: MagicMock, mock_context: MagicMock) -> None:
        """Test that session ID persists across messages."""
        args = argparse.Namespace()
        mock_send_message.side_effect = [
            {
                "answer": "First response",
                "context": [],
                "session_id": 5,
                "documents_count": 0,
            },
            {
                "answer": "Second response",
                "context": [],
                "session_id": 5,
                "documents_count": 0,
            },
        ]

        commands.cmd_interactive(mock_context, args)

        assert mock_send_message.call_count == 2
        # First call should have None session_id
        first_call = mock_send_message.call_args_list[0]
        assert first_call[0][2] is None
        # Second call should use session_id from first response
        second_call = mock_send_message.call_args_list[1]
        assert second_call[0][2] == 5

    @patch("src.domains.chat.commands.send_chat_message")
    @patch("builtins.input", side_effect=KeyboardInterrupt())
    @patch("builtins.print")
    def test_cmd_interactive_keyboard_interrupt(self, mock_print: MagicMock, mock_input: MagicMock, mock_send_message: MagicMock, mock_context: MagicMock) -> None:
        """Test handling keyboard interrupt (Ctrl+C)."""
        args = argparse.Namespace()

        commands.cmd_interactive(mock_context, args)

        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Goodbye" in str(call) for call in print_calls)

    @patch("src.domains.chat.commands.send_chat_message")
    @patch("builtins.input", side_effect=["test", "quit"])
    @patch("builtins.print")
    def test_cmd_interactive_error_handling(self, mock_print: MagicMock, mock_input: MagicMock, mock_send_message: MagicMock, mock_context: MagicMock) -> None:
        """Test error handling during interactive session."""
        args = argparse.Namespace()
        mock_send_message.side_effect = Exception("Test error")

        commands.cmd_interactive(mock_context, args)

        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Error" in str(call) for call in print_calls)
