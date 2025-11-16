"""Tests for CLI module."""

import argparse
from typing import cast
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.cli import CLIClient, cmd_chat, cmd_delete, cmd_interactive, cmd_list, cmd_sessions, cmd_upload, main


@pytest.fixture
def mock_cli_client() -> MagicMock:
    """Create a mock CLI client."""
    client = Mock(spec=CLIClient)
    client.context = Mock()
    client.db = Mock()
    client.close = Mock()
    return cast(MagicMock, client)


@pytest.fixture
def mock_args() -> argparse.Namespace:
    """Create mock command line arguments."""
    return argparse.Namespace()


class TestCLIClient:
    """Tests for CLIClient initialization and cleanup."""

    @patch("src.cli.init_db")
    @patch("src.cli.get_db")
    @patch("src.cli.AppContext")
    def test_init_creates_context(
        self, mock_app_context: MagicMock, mock_get_db: MagicMock, mock_init_db: MagicMock
    ) -> None:
        """Test that CLIClient initializes database and context."""
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])

        client = CLIClient()

        mock_init_db.assert_called_once()
        mock_get_db.assert_called_once()
        mock_app_context.assert_called_once_with(mock_db)
        assert client.db == mock_db

    @patch("src.cli.init_db")
    @patch("src.cli.get_db")
    @patch("src.cli.AppContext")
    def test_close_closes_db(
        self, mock_app_context: MagicMock, mock_get_db: MagicMock, mock_init_db: MagicMock
    ) -> None:
        """Test that close() closes the database session."""
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])

        client = CLIClient()
        client.close()

        mock_db.close.assert_called_once()


class TestCommandHandlers:
    """Tests for command handler delegation."""

    @patch("src.cli.doc_commands.cmd_upload")
    def test_cmd_upload_delegates(self, mock_doc_upload: MagicMock, mock_cli_client: MagicMock, mock_args: argparse.Namespace) -> None:
        """Test that cmd_upload delegates to document commands."""
        mock_args.file = "test.pdf"

        cmd_upload(mock_cli_client, mock_args)

        mock_doc_upload.assert_called_once_with(mock_cli_client.context, mock_args)

    @patch("src.cli.doc_commands.cmd_list")
    def test_cmd_list_delegates(self, mock_doc_list: MagicMock, mock_cli_client: MagicMock, mock_args: argparse.Namespace) -> None:
        """Test that cmd_list delegates to document commands."""
        cmd_list(mock_cli_client, mock_args)

        mock_doc_list.assert_called_once_with(mock_cli_client.context, mock_args)

    @patch("src.cli.doc_commands.cmd_delete")
    def test_cmd_delete_delegates(self, mock_doc_delete: MagicMock, mock_cli_client: MagicMock, mock_args: argparse.Namespace) -> None:
        """Test that cmd_delete delegates to document commands."""
        mock_args.doc_id = 1

        cmd_delete(mock_cli_client, mock_args)

        mock_doc_delete.assert_called_once_with(mock_cli_client.context, mock_args)

    @patch("src.cli.chat_commands.cmd_chat")
    def test_cmd_chat_delegates(self, mock_chat_chat: MagicMock, mock_cli_client: MagicMock, mock_args: argparse.Namespace) -> None:
        """Test that cmd_chat delegates to chat commands."""
        mock_args.message = "test question"

        cmd_chat(mock_cli_client, mock_args)

        mock_chat_chat.assert_called_once_with(mock_cli_client.context, mock_args)

    @patch("src.cli.chat_commands.cmd_sessions")
    def test_cmd_sessions_delegates(self, mock_chat_sessions: MagicMock, mock_cli_client: MagicMock, mock_args: argparse.Namespace) -> None:
        """Test that cmd_sessions delegates to chat commands."""
        cmd_sessions(mock_cli_client, mock_args)

        mock_chat_sessions.assert_called_once_with(mock_cli_client.context, mock_args)

    @patch("src.cli.chat_commands.cmd_interactive")
    def test_cmd_interactive_delegates(self, mock_chat_interactive: MagicMock, mock_cli_client: MagicMock, mock_args: argparse.Namespace) -> None:
        """Test that cmd_interactive delegates to chat commands."""
        cmd_interactive(mock_cli_client, mock_args)

        mock_chat_interactive.assert_called_once_with(mock_cli_client.context, mock_args)


class TestMain:
    """Tests for main CLI entry point."""

    @patch("src.cli.CLIClient")
    @patch("src.cli.sys.argv", ["cli.py"])
    def test_main_no_command_shows_help(self, mock_cli_client_class: MagicMock) -> None:
        """Test that main() shows help when no command is provided."""
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        # Client should not be created when no command is provided
        mock_cli_client_class.assert_not_called()

    @patch("src.cli.cmd_upload")
    @patch("src.cli.CLIClient")
    @patch("src.cli.sys.argv", ["cli.py", "upload", "test.pdf"])
    def test_main_upload_command(self, mock_cli_client_class: MagicMock, mock_cmd_upload: MagicMock) -> None:
        """Test that main() executes upload command."""
        mock_client = Mock()
        mock_cli_client_class.return_value = mock_client

        main()

        mock_cmd_upload.assert_called_once()
        args = mock_cmd_upload.call_args[0][1]
        assert args.file == "test.pdf"
        mock_client.close.assert_called_once()

    @patch("src.cli.cmd_list")
    @patch("src.cli.CLIClient")
    @patch("src.cli.sys.argv", ["cli.py", "list"])
    def test_main_list_command(self, mock_cli_client_class: MagicMock, mock_cmd_list: MagicMock) -> None:
        """Test that main() executes list command."""
        mock_client = Mock()
        mock_cli_client_class.return_value = mock_client

        main()

        mock_cmd_list.assert_called_once()
        mock_client.close.assert_called_once()

    @patch("src.cli.cmd_delete")
    @patch("src.cli.CLIClient")
    @patch("src.cli.sys.argv", ["cli.py", "delete", "1"])
    def test_main_delete_command(self, mock_cli_client_class: MagicMock, mock_cmd_delete: MagicMock) -> None:
        """Test that main() executes delete command."""
        mock_client = Mock()
        mock_cli_client_class.return_value = mock_client

        main()

        mock_cmd_delete.assert_called_once()
        args = mock_cmd_delete.call_args[0][1]
        assert args.doc_id == 1
        mock_client.close.assert_called_once()

    @patch("src.cli.cmd_chat")
    @patch("src.cli.CLIClient")
    @patch("src.cli.sys.argv", ["cli.py", "chat", "test question"])
    def test_main_chat_command(self, mock_cli_client_class: MagicMock, mock_cmd_chat: MagicMock) -> None:
        """Test that main() executes chat command."""
        mock_client = Mock()
        mock_cli_client_class.return_value = mock_client

        main()

        mock_cmd_chat.assert_called_once()
        args = mock_cmd_chat.call_args[0][1]
        assert args.message == "test question"
        mock_client.close.assert_called_once()

    @patch("src.cli.cmd_chat")
    @patch("src.cli.CLIClient")
    @patch("src.cli.sys.argv", ["cli.py", "chat", "test", "--session-id", "5", "--show-context"])
    def test_main_chat_with_options(self, mock_cli_client_class: MagicMock, mock_cmd_chat: MagicMock) -> None:
        """Test that main() handles chat command with options."""
        mock_client = Mock()
        mock_cli_client_class.return_value = mock_client

        main()

        mock_cmd_chat.assert_called_once()
        args = mock_cmd_chat.call_args[0][1]
        assert args.message == "test"
        assert args.session_id == 5
        assert args.show_context is True
        mock_client.close.assert_called_once()

    @patch("src.cli.cmd_sessions")
    @patch("src.cli.CLIClient")
    @patch("src.cli.sys.argv", ["cli.py", "sessions"])
    def test_main_sessions_command(self, mock_cli_client_class: MagicMock, mock_cmd_sessions: MagicMock) -> None:
        """Test that main() executes sessions command."""
        mock_client = Mock()
        mock_cli_client_class.return_value = mock_client

        main()

        mock_cmd_sessions.assert_called_once()
        mock_client.close.assert_called_once()

    @patch("src.cli.cmd_interactive")
    @patch("src.cli.CLIClient")
    @patch("src.cli.sys.argv", ["cli.py", "interactive"])
    def test_main_interactive_command(self, mock_cli_client_class: MagicMock, mock_cmd_interactive: MagicMock) -> None:
        """Test that main() executes interactive command."""
        mock_client = Mock()
        mock_cli_client_class.return_value = mock_client

        main()

        mock_cmd_interactive.assert_called_once()
        mock_client.close.assert_called_once()

    @patch("src.cli.cmd_upload")
    @patch("src.cli.CLIClient")
    @patch("src.cli.sys.argv", ["cli.py", "upload", "test.pdf"])
    def test_main_closes_client_on_exception(
        self, mock_cli_client_class: MagicMock, mock_cmd_upload: MagicMock
    ) -> None:
        """Test that main() closes client even when command raises exception."""
        mock_client = Mock()
        mock_cli_client_class.return_value = mock_client
        mock_cmd_upload.side_effect = RuntimeError("Test error")

        with pytest.raises(RuntimeError, match="Test error"):
            main()

        mock_client.close.assert_called_once()
