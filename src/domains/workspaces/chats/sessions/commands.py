"""Chat session CLI commands."""

import argparse


def cmd_list(ctx: object, args: argparse.Namespace) -> None:
    """List chat sessions in the current workspace."""
    # Require a selected workspace
    if not ctx.current_workspace_id:
        print("Error: No workspace selected. Use 'workspace select <id>' first.")
        return

    workspace = ctx.workspace_repo.get_by_id(ctx.current_workspace_id)
    if not workspace:
        print(f"Error: Workspace {ctx.current_workspace_id} not found.")
        return

    # List sessions for the workspace
    sessions, total = ctx.chat_session_service.list_workspace_sessions(
        workspace_id=workspace.id, skip=0, limit=50
    )

    if not sessions:
        print(f"No chat sessions found in workspace '{workspace.name}'.")
        return

    print(f"\nChat sessions in workspace '{workspace.name}' ({total} total):\n")
    for session in sessions:
        title = session.title or "(No title)"
        print(f"  [{session.id}] {title}")
        print(f"      Created: {session.created_at}")
        print()


def cmd_new(ctx: object, args: argparse.Namespace) -> None:
    """Create a new chat session (interactive)."""
    # Require a selected workspace
    if not ctx.current_workspace_id:
        print("Error: No workspace selected. Use 'workspace select <id>' first.")
        return

    workspace = ctx.workspace_repo.get_by_id(ctx.current_workspace_id)
    if not workspace:
        print(f"Error: Workspace {ctx.current_workspace_id} not found.")
        return

    # Interactive prompts
    title = input("Session title (optional): ").strip() or None

    # Create session
    session = ctx.chat_session_service.create_session(
        title=title,
        workspace_id=workspace.id,
        rag_type=workspace.rag_type,
    )

    print(f"\nChat session created with ID: {session.id}")
    print(f"  Title: {session.title or '(No title)'}")
    print(f"  Workspace: {workspace.name}")
    print(f"  RAG type: {session.rag_type if hasattr(session, 'rag_type') else workspace.rag_type}")


def cmd_select(ctx: object, args: argparse.Namespace) -> None:
    """Select a chat session as the current session."""
    session = ctx.chat_session_service.get_session(args.session_id)

    if not session:
        print(f"Error: Chat session {args.session_id} not found.")
        return

    ctx.current_session_id = session.id
    print(f"Selected chat session: {session.title or f'Session {session.id}'}")


def cmd_delete(ctx: object, args: argparse.Namespace) -> None:
    """Delete a chat session."""
    session = ctx.chat_session_service.get_session(args.session_id)

    if not session:
        print(f"Error: Chat session {args.session_id} not found.")
        return

    # Confirm deletion
    confirm = input(f"Delete session '{session.title or f'Session {session.id}'}? (y/n): ").lower()
    if confirm != "y":
        print("Deletion cancelled.")
        return

    ctx.chat_session_service.delete_session(args.session_id)
    print(f"Chat session {args.session_id} deleted.")
