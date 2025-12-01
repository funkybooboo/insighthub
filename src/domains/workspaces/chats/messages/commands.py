"""Chat message CLI commands."""

import argparse


def cmd_list(ctx: object, args: argparse.Namespace) -> None:
    """List messages in the current chat session."""
    # Require a selected session
    if not hasattr(ctx, "current_session_id") or not ctx.current_session_id:
        print("Error: No chat session selected. Use 'chat select <id>' first.")
        return

    session = ctx.chat_session_service.get_session(ctx.current_session_id)
    if not session:
        print(f"Error: Chat session {ctx.current_session_id} not found.")
        return

    # List messages for the session
    messages, total = ctx.chat_message_service.get_session_messages(
        session_id=session.id, skip=0, limit=50
    )

    if not messages:
        print(f"No messages found in session '{session.title or f'Session {session.id'}'.")
        return

    print(f"\nMessages in session '{session.title or f'Session {session.id}'}' ({total} total):\n")
    for message in messages:
        role_label = message.role.upper()
        print(f"  [{message.id}] {role_label}:")
        print(f"      {message.content}")
        print(f"      Created: {message.created_at}")
        print()


def cmd_send(ctx: object, args: argparse.Namespace) -> None:
    """Send a message in the current chat session."""
    # Require a selected session
    if not hasattr(ctx, "current_session_id") or not ctx.current_session_id:
        print("Error: No chat session selected. Use 'chat select <id>' first.")
        return

    session = ctx.chat_session_service.get_session(ctx.current_session_id)
    if not session:
        print(f"Error: Chat session {ctx.current_session_id} not found.")
        return

    # Get the message content
    message_content = args.message

    # Create user message
    user_message = ctx.chat_message_service.create_message(
        session_id=session.id,
        role="user",
        content=message_content,
    )

    print(f"\nYou: {user_message.content}")

    # TODO: Generate assistant response using RAG query workflow
    # For now, just acknowledge the message
    print("\n(Assistant response generation not yet implemented)")


def cmd_delete(ctx: object, args: argparse.Namespace) -> None:
    """Delete a message."""
    message = ctx.chat_message_service.get_message(args.message_id)

    if not message:
        print(f"Error: Message {args.message_id} not found.")
        return

    # Confirm deletion
    confirm = input(f"Delete message {args.message_id}? (y/n): ").lower()
    if confirm != "y":
        print("Deletion cancelled.")
        return

    ctx.chat_message_service.delete_message(args.message_id)
    print(f"Message {args.message_id} deleted.")
