"""
Command-line interface for the InsightHub RAG system.

This CLI provides a direct interface to the RAG system without going through HTTP/REST.
"""

import argparse
import sys
from pathlib import Path
from typing import Any

from pypdf import PdfReader


class RagClient:
    """Direct client for interacting with the RAG system."""

    def __init__(self) -> None:
        """Initialize the RAG client."""
        # TODO: Initialize RAG system here when implemented
        # self.rag = create_rag(...)
        self.documents: list[dict[str, Any]] = []
        self.next_doc_id = 1

    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text content from a PDF file."""
        reader = PdfReader(str(file_path))
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n".join(text_parts)

    def extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text content from a TXT file."""
        with open(file_path, encoding="utf-8") as f:
            return f.read()

    def upload_document(self, file_path: Path) -> dict[str, Any]:
        """Process and add a document to the RAG system."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = file_path.suffix.lower().lstrip(".")

        if extension == "pdf":
            text = self.extract_text_from_pdf(file_path)
        elif extension == "txt":
            text = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

        # TODO: Add document to RAG system
        # self.rag.add_documents([{"text": text, "metadata": {"filename": file_path.name}}])

        doc = {
            "id": self.next_doc_id,
            "filename": file_path.name,
            "text_length": len(text),
            "type": extension,
            "text": text,
        }
        self.documents.append(doc)
        self.next_doc_id += 1

        return doc

    def send_chat_message(self, message: str, conversation_id: str | None = None) -> dict[str, Any]:
        """Query the RAG system with a message."""
        # TODO: Query RAG system
        # results = self.rag.query(message, top_k=5)
        # return {
        #     "answer": results["answer"],
        #     "context": results["context"],
        #     "conversation_id": conversation_id or "default",
        #     "documents_count": len(self.documents),
        # }

        # Mock response for now
        return {
            "answer": f"Mock response to: {message}",
            "context": [
                {
                    "text": "Sample context chunk 1",
                    "score": 0.85,
                    "metadata": {"source": "document_1"},
                },
            ],
            "conversation_id": conversation_id or "default",
            "documents_count": len(self.documents),
        }

    def list_documents(self) -> dict[str, Any]:
        """List all documents in the RAG system."""
        return {
            "documents": [
                {
                    "id": doc["id"],
                    "filename": doc["filename"],
                    "text_length": doc["text_length"],
                    "type": doc["type"],
                }
                for doc in self.documents
            ],
            "count": len(self.documents),
        }

    def delete_document(self, doc_id: int) -> dict[str, str]:
        """Delete a document from the RAG system."""
        doc = next((d for d in self.documents if d["id"] == doc_id), None)

        if not doc:
            raise ValueError(f"Document with ID {doc_id} not found")

        # TODO: Remove from RAG system
        # self.rag.remove_document(doc_id)

        self.documents = [d for d in self.documents if d["id"] != doc_id]

        return {"message": f"Document {doc_id} deleted successfully"}


def cmd_upload(client: RagClient, args: argparse.Namespace) -> None:
    """Upload a document."""
    try:
        file_path = Path(args.file)
        result = client.upload_document(file_path)
        print("Document added successfully!")
        print(f"Document ID: {result['id']}")
        print(f"Filename: {result['filename']}")
        print(f"Type: {result['type']}")
        print(f"Text Length: {result['text_length']} characters")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_chat(client: RagClient, args: argparse.Namespace) -> None:
    """Send a chat message."""
    try:
        result = client.send_chat_message(args.message, args.conversation_id)
        print("\nAnswer:")
        print("-" * 80)
        print(result["answer"])
        print("-" * 80)

        if args.show_context and "context" in result:
            print("\nContext:")
            for i, ctx in enumerate(result["context"], 1):
                print(f"\n{i}. Score: {ctx['score']:.2f}")
                print(f"   {ctx['text'][:200]}...")

        print(f"\nDocuments in system: {result.get('documents_count', 0)}")
        print(f"Conversation ID: {result.get('conversation_id', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(client: RagClient, args: argparse.Namespace) -> None:
    """List all documents."""
    try:
        result = client.list_documents()
        documents = result.get("documents", [])

        if not documents:
            print("No documents found.")
            return

        print(f"Total documents: {result.get('count', 0)}\n")
        for doc in documents:
            print(f"ID: {doc['id']}")
            print(f"  Filename: {doc['filename']}")
            print(f"  Type: {doc['type']}")
            print(f"  Text Length: {doc['text_length']} characters")
            print()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_delete(client: RagClient, args: argparse.Namespace) -> None:
    """Delete a document."""
    try:
        result = client.delete_document(args.doc_id)
        print(result["message"])
    except (ValueError, Exception) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_interactive(client: RagClient, args: argparse.Namespace) -> None:
    """Start an interactive chat session."""
    print("Interactive Chat Session")
    print("Type 'quit' or 'exit' to end the session")
    print("-" * 80)

    conversation_id = "cli-session"

    while True:
        try:
            message = input("\nYou: ").strip()

            if message.lower() in ["quit", "exit"]:
                print("Goodbye!")
                break

            if not message:
                continue

            result = client.send_chat_message(message, conversation_id)
            print(f"\nBot: {result['answer']}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="InsightHub RAG CLI")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Add a document to the RAG system")
    upload_parser.add_argument("file", help="Path to the file to upload (PDF or TXT)")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Query the RAG system")
    chat_parser.add_argument("message", help="The question or message to send")
    chat_parser.add_argument("--conversation-id", help="Optional conversation ID for context")
    chat_parser.add_argument(
        "--show-context", action="store_true", help="Show retrieved context chunks"
    )

    # List command
    subparsers.add_parser("list", help="List all documents in the system")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a document")
    delete_parser.add_argument("doc_id", type=int, help="Document ID to delete")

    # Interactive command
    subparsers.add_parser("interactive", help="Start an interactive chat session")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    client = RagClient()

    commands = {
        "upload": cmd_upload,
        "chat": cmd_chat,
        "list": cmd_list,
        "delete": cmd_delete,
        "interactive": cmd_interactive,
    }

    command_func = commands.get(args.command)
    if command_func:
        command_func(client, args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
