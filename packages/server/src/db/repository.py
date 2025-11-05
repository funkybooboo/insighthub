"""Repository layer for database operations."""

from typing import Optional

from sqlalchemy.orm import Session

from .models import User, Document, ChatSession, ChatMessage


class UserRepository:
    """Repository for User operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, username: str, email: str, full_name: Optional[str] = None) -> User:
        """Create a new user."""
        user = User(username=username, email=email, full_name=full_name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        return self.db.query(User).offset(skip).limit(limit).all()

    def update(self, user_id: int, **kwargs: str) -> Optional[User]:
        """Update user fields."""
        user = self.get_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False


class DocumentRepository:
    """Repository for Document operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        content_hash: str,
        chunk_count: Optional[int] = None,
        rag_collection: Optional[str] = None,
    ) -> Document:
        """Create a new document."""
        document = Document(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            content_hash=content_hash,
            chunk_count=chunk_count,
            rag_collection=rag_collection,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        return self.db.query(Document).filter(Document.id == document_id).first()

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
        """Get all documents for a user with pagination."""
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_content_hash(self, content_hash: str) -> Optional[Document]:
        """Get document by content hash."""
        return self.db.query(Document).filter(Document.content_hash == content_hash).first()

    def update(self, document_id: int, **kwargs: str | int) -> Optional[Document]:
        """Update document fields."""
        document = self.get_by_id(document_id)
        if document:
            for key, value in kwargs.items():
                if hasattr(document, key):
                    setattr(document, key, value)
            self.db.commit()
            self.db.refresh(document)
        return document

    def delete(self, document_id: int) -> bool:
        """Delete document by ID."""
        document = self.get_by_id(document_id)
        if document:
            self.db.delete(document)
            self.db.commit()
            return True
        return False


class ChatSessionRepository:
    """Repository for ChatSession operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self, user_id: int, title: Optional[str] = None, rag_type: str = "vector"
    ) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(user_id=user_id, title=title, rag_type=rag_type)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Get chat session by ID."""
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[ChatSession]:
        """Get all chat sessions for a user with pagination."""
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, session_id: int, **kwargs: str) -> Optional[ChatSession]:
        """Update chat session fields."""
        session = self.get_by_id(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            self.db.commit()
            self.db.refresh(session)
        return session

    def delete(self, session_id: int) -> bool:
        """Delete chat session by ID."""
        session = self.get_by_id(session_id)
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False


class ChatMessageRepository:
    """Repository for ChatMessage operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: Optional[str] = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        message = ChatMessage(session_id=session_id, role=role, content=content, extra_metadata=extra_metadata)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_id(self, message_id: int) -> Optional[ChatMessage]:
        """Get chat message by ID."""
        return self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()

    def get_by_session(
        self, session_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatMessage]:
        """Get all messages for a chat session with pagination."""
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete(self, message_id: int) -> bool:
        """Delete chat message by ID."""
        message = self.get_by_id(message_id)
        if message:
            self.db.delete(message)
            self.db.commit()
            return True
        return False
