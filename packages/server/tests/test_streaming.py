#!/usr/bin/env python3
"""Test script for Socket.IO streaming functionality."""

import time

from socketio import Client  # type: ignore[import-untyped]

# Create a Socket.IO client
sio: Client = Client()

# Track received chunks
chunks_received: list[object] = []
full_response: str = ""


@sio.on("connected")
def on_connected(data: dict[str, object]) -> None:
    print(f"Connected to server: {data}")


@sio.on("chat_chunk")
def on_chat_chunk(data: dict[str, object]) -> None:
    chunk = data.get("chunk", "")
    chunks_received.append(chunk)
    print(f"Received chunk ({len(chunks_received)}): {chunk!r}")


@sio.on("chat_complete")
def on_chat_complete(data: dict[str, object]) -> None:
    global full_response
    full_response = str(data.get("full_response", ""))
    print(f"\nChat complete! Session ID: {data.get('session_id')}")
    print(f"Total chunks received: {len(chunks_received)}")
    print(f"Full response length: {len(full_response)}")
    print(f"\nFull response:\n{full_response}")


@sio.on("error")
def on_error(data: dict[str, object]) -> None:
    print(f"Error: {data.get('error')}")


def test_streaming() -> None:
    """Test the streaming chat functionality."""
    print("Connecting to server at http://localhost:5000...")

    try:
        # Connect to the server
        sio.connect("http://localhost:5000")

        # Wait for connection
        time.sleep(1)

        # Send a test message
        test_message = "What is Python?"
        print(f"\nSending message: {test_message}")

        sio.emit("chat_message", {"message": test_message})

        # Wait for response (adjust timeout as needed)
        print("\nWaiting for response...\n")
        time.sleep(15)  # Wait for LLM to respond

        # Disconnect
        sio.disconnect()

        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print(f"Received {len(chunks_received)} chunks")
        print("=" * 60)

    except Exception as e:
        print(f"Error during test: {e}")
        sio.disconnect()


if __name__ == "__main__":
    test_streaming()
