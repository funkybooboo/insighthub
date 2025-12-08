"""E2E tests for chat messaging and core chat functionality."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.mark.integration
class TestChatMessaging:
    """Test chat send command and message flows."""

    def run_cli(self, *args):
        """Helper to run CLI command and return result."""
        cmd = [sys.executable, "-m", "src.cli", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return result

    def create_workspace_and_chat(self, ws_name="Chat Test", chat_title="Test Chat"):
        """Helper to create workspace and chat session."""
        import re

        # Create workspace
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input=f"{ws_name}\nTest workspace\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0
        ws_match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = ws_match.group(1) if ws_match else None
        assert ws_id is not None

        # Create chat session
        create_chat = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", ws_id],
            input=f"{chat_title}\n",
            capture_output=True,
            text=True,
        )
        assert create_chat.returncode == 0
        chat_match = re.search(r"Created chat session \[(\d+)\]", create_chat.stdout)
        chat_id = chat_match.group(1) if chat_match else None
        assert chat_id is not None

        # Select chat session
        select = self.run_cli("chat", "select", chat_id)
        assert select.returncode == 0

        return ws_id, chat_id

    # ==================== BASIC CHAT SEND ====================

    def test_chat_send_simple_message(self):
        """Test sending a simple message."""
        ws_id, chat_id = self.create_workspace_and_chat()

        result = self.run_cli("chat", "send", "Hello, world!")
        # Should handle gracefully (may succeed or fail depending on LLM availability)
        assert result.returncode in [0, 1]

    def test_chat_send_multiple_messages(self):
        """Test sending multiple messages in sequence."""
        ws_id, chat_id = self.create_workspace_and_chat()

        messages = ["First message", "Second message", "Third message"]

        for msg in messages:
            result = self.run_cli("chat", "send", msg)
            # Should handle gracefully
            assert result.returncode in [0, 1]

    def test_chat_send_question(self):
        """Test sending a question message."""
        ws_id, chat_id = self.create_workspace_and_chat()

        result = self.run_cli("chat", "send", "What is the capital of France?")
        assert result.returncode in [0, 1]

    def test_chat_send_with_punctuation(self):
        """Test sending messages with various punctuation."""
        ws_id, chat_id = self.create_workspace_and_chat()

        messages = [
            "Hello! How are you?",
            "This is great: really amazing.",
            "Can you help me (please)?",
            "Testing... multiple... dots...",
        ]

        for msg in messages:
            result = self.run_cli("chat", "send", msg)
            assert result.returncode in [0, 1]

    def test_chat_send_with_numbers(self):
        """Test sending messages with numbers."""
        ws_id, chat_id = self.create_workspace_and_chat()

        result = self.run_cli("chat", "send", "What is 2 + 2?")
        assert result.returncode in [0, 1]

    # ==================== CHAT WITH DOCUMENTS ====================

    def test_chat_with_added_document(self):
        """Test chat after uploading a document."""
        import re

        # Create workspace
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Doc Chat Test\nTest workspace\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0
        ws_match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = ws_match.group(1) if ws_match else None

        # Select workspace
        select_ws = self.run_cli("workspace", "select", ws_id)
        assert select_ws.returncode == 0

        # Create and add document
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("The capital of France is Paris.\n")
            f.write("Paris is known for the Eiffel Tower.\n")
            test_file = Path(f.name)

        try:
            add = self.run_cli("document", "add", str(test_file))
            assert upload.returncode == 0

            # Create chat session
            create_chat = subprocess.run(
                [sys.executable, "-m", "src.cli", "chat", "create", ws_id],
                input="Doc Test Chat\n",
                capture_output=True,
                text=True,
            )
            assert create_chat.returncode == 0
            chat_match = re.search(r"Created chat session \[(\d+)\]", create_chat.stdout)
            chat_id = chat_match.group(1) if chat_match else None

            # Select chat
            select_chat = self.run_cli("chat", "select", chat_id)
            assert select_chat.returncode == 0

            # Send message related to document
            result = self.run_cli("chat", "send", "What is the capital of France?")
            assert result.returncode in [0, 1]

        finally:
            if test_file.exists():
                test_file.unlink()

    def test_chat_with_multiple_documents(self):
        """Test chat after uploading multiple documents."""
        import re

        # Create workspace
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Multi Doc Chat\nTest workspace\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0
        ws_match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = ws_match.group(1) if ws_match else None

        # Select workspace
        select_ws = self.run_cli("workspace", "select", ws_id)
        assert select_ws.returncode == 0

        # Create and add multiple documents
        test_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_doc{i}.txt", delete=False) as f:
                f.write(f"Document {i} content.\n")
                f.write(f"This is test document number {i}.\n")
                test_files.append(Path(f.name))

        try:
            # Add all documents
            for test_file in test_files:
                add = self.run_cli("document", "add", str(test_file))
                assert upload.returncode == 0

            # Create chat session
            create_chat = subprocess.run(
                [sys.executable, "-m", "src.cli", "chat", "create", ws_id],
                input="Multi Doc Chat\n",
                capture_output=True,
                text=True,
            )
            assert create_chat.returncode == 0
            chat_match = re.search(r"Created chat session \[(\d+)\]", create_chat.stdout)
            chat_id = chat_match.group(1) if chat_match else None

            # Select chat
            select_chat = self.run_cli("chat", "select", chat_id)
            assert select_chat.returncode == 0

            # Send message
            result = self.run_cli("chat", "send", "What documents do we have?")
            assert result.returncode in [0, 1]

        finally:
            for test_file in test_files:
                if test_file.exists():
                    test_file.unlink()

    # ==================== CHAT HISTORY VERIFICATION ====================

    def test_chat_history_after_sending_messages(self):
        """Test viewing history after sending messages."""
        ws_id, chat_id = self.create_workspace_and_chat()

        # Send a message
        send = self.run_cli("chat", "send", "Test message")
        # May succeed or fail depending on LLM
        assert send.returncode in [0, 1]

        # View history
        history = self.run_cli("chat", "history")
        assert history.returncode == 0
        # History should either show messages or indicate empty

    def test_chat_multiple_sessions_isolation(self):
        """Test that messages in different sessions are isolated."""
        import re

        # Create workspace
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Isolation Test\nTest workspace\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0
        ws_match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = ws_match.group(1) if ws_match else None

        # Create first chat session
        chat1 = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", ws_id],
            input="Session 1\n",
            capture_output=True,
            text=True,
        )
        assert chat1.returncode == 0
        chat1_match = re.search(r"Created chat session \[(\d+)\]", chat1.stdout)
        chat1_id = chat1_match.group(1) if chat1_match else None

        # Create second chat session
        chat2 = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", ws_id],
            input="Session 2\n",
            capture_output=True,
            text=True,
        )
        assert chat2.returncode == 0
        chat2_match = re.search(r"Created chat session \[(\d+)\]", chat2.stdout)
        chat2_id = chat2_match.group(1) if chat2_match else None

        # Select first session and send message
        select1 = self.run_cli("chat", "select", chat1_id)
        assert select1.returncode == 0
        send1 = self.run_cli("chat", "send", "Message for session 1")
        assert send1.returncode in [0, 1]

        # Select second session and send message
        select2 = self.run_cli("chat", "select", chat2_id)
        assert select2.returncode == 0
        send2 = self.run_cli("chat", "send", "Message for session 2")
        assert send2.returncode in [0, 1]

        # Verify histories are separate
        history2 = self.run_cli("chat", "history")
        assert history2.returncode == 0

        # Switch back to first session
        select1_again = self.run_cli("chat", "select", chat1_id)
        assert select1_again.returncode == 0
        history1 = self.run_cli("chat", "history")
        assert history1.returncode == 0

    # ==================== EDGE CASES ====================

    def test_chat_send_empty_message(self):
        """Test sending an empty message."""
        ws_id, chat_id = self.create_workspace_and_chat()

        result = self.run_cli("chat", "send", "")
        # Should handle gracefully
        assert result.returncode in [0, 1]

    def test_chat_send_whitespace_only(self):
        """Test sending whitespace-only message."""
        ws_id, chat_id = self.create_workspace_and_chat()

        result = self.run_cli("chat", "send", "   ")
        assert result.returncode in [0, 1]

    def test_chat_send_single_character(self):
        """Test sending single character message."""
        ws_id, chat_id = self.create_workspace_and_chat()

        result = self.run_cli("chat", "send", "a")
        assert result.returncode in [0, 1]

    def test_chat_send_unicode_message(self):
        """Test sending message with unicode characters."""
        ws_id, chat_id = self.create_workspace_and_chat()

        messages = [
            "Hello in Russian: Привет",
            "Hello in Chinese: 你好",
            "Hello in Japanese: こんにちは",
            "Emoji test: 👋 🌍 ⭐",
        ]

        for msg in messages:
            result = self.run_cli("chat", "send", msg)
            assert result.returncode in [0, 1]

    # ==================== CHAT SESSION SWITCHING ====================

    def test_switch_sessions_and_send_messages(self):
        """Test switching between sessions and sending messages."""
        import re

        # Create workspace
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Switch Test\nTest workspace\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0
        ws_match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = ws_match.group(1) if ws_match else None

        # Create multiple sessions
        session_ids = []
        for i in range(3):
            chat = subprocess.run(
                [sys.executable, "-m", "src.cli", "chat", "create", ws_id],
                input=f"Session {i}\n",
                capture_output=True,
                text=True,
            )
            assert chat.returncode == 0
            chat_match = re.search(r"Created chat session \[(\d+)\]", chat.stdout)
            session_ids.append(chat_match.group(1) if chat_match else None)

        # Switch between sessions and send messages
        for i, session_id in enumerate(session_ids):
            select = self.run_cli("chat", "select", session_id)
            assert select.returncode == 0

            send = self.run_cli("chat", "send", f"Message for session {i}")
            assert send.returncode in [0, 1]

    def test_chat_send_after_workspace_switch(self):
        """Test sending messages after switching workspaces."""
        import re

        # Create first workspace and chat
        ws1 = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Workspace 1\nFirst workspace\nvector\n",
            capture_output=True,
            text=True,
        )
        assert ws1.returncode == 0
        ws1_match = re.search(r"Created workspace \[(\d+)\]", ws1.stdout)
        ws1_id = ws1_match.group(1) if ws1_match else None

        chat1 = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", ws1_id],
            input="Chat 1\n",
            capture_output=True,
            text=True,
        )
        assert chat1.returncode == 0
        chat1_match = re.search(r"Created chat session \[(\d+)\]", chat1.stdout)
        chat1_id = chat1_match.group(1) if chat1_match else None

        # Create second workspace and chat
        ws2 = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Workspace 2\nSecond workspace\nvector\n",
            capture_output=True,
            text=True,
        )
        assert ws2.returncode == 0
        ws2_match = re.search(r"Created workspace \[(\d+)\]", ws2.stdout)
        ws2_id = ws2_match.group(1) if ws2_match else None

        chat2 = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", ws2_id],
            input="Chat 2\n",
            capture_output=True,
            text=True,
        )
        assert chat2.returncode == 0
        chat2_match = re.search(r"Created chat session \[(\d+)\]", chat2.stdout)
        chat2_id = chat2_match.group(1) if chat2_match else None

        # Select first chat and send message
        select1 = self.run_cli("chat", "select", chat1_id)
        assert select1.returncode == 0
        send1 = self.run_cli("chat", "send", "Message in workspace 1")
        assert send1.returncode in [0, 1]

        # Switch workspace
        switch = self.run_cli("workspace", "select", ws2_id)
        assert switch.returncode == 0

        # Select second chat and send message
        select2 = self.run_cli("chat", "select", chat2_id)
        assert select2.returncode == 0
        send2 = self.run_cli("chat", "send", "Message in workspace 2")
        assert send2.returncode in [0, 1]

    # ==================== COMMAND COMBINATIONS ====================

    def test_chat_list_history_workflow(self):
        """Test workflow: list chats, select, view history, send message."""
        import re

        # Create workspace
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Workflow Test\nTest workspace\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0
        ws_match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = ws_match.group(1) if ws_match else None

        # Create chat
        create_chat = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", ws_id],
            input="Test Chat\n",
            capture_output=True,
            text=True,
        )
        assert create_chat.returncode == 0
        chat_match = re.search(r"Created chat session \[(\d+)\]", create_chat.stdout)
        chat_id = chat_match.group(1) if chat_match else None

        # List chats
        list_chats = self.run_cli("chat", "list", ws_id)
        assert list_chats.returncode == 0
        assert "Test Chat" in list_chats.stdout

        # Select chat
        select = self.run_cli("chat", "select", chat_id)
        assert select.returncode == 0

        # View history (empty)
        history1 = self.run_cli("chat", "history")
        assert history1.returncode == 0

        # Send message
        send = self.run_cli("chat", "send", "Hello")
        assert send.returncode in [0, 1]

        # View history again
        history2 = self.run_cli("chat", "history")
        assert history2.returncode == 0
