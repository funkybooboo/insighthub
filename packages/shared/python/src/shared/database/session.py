"""Database session management and connection utilities."""

import os
from collections.abc import Generator
from typing import Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from .base import Base

# Global engine and session factory (created lazily)
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker[Session]] = None


def get_database_url() -> str:
    """
    Get database URL from environment variable.
    
    Returns:
        Database connection URL
        
    Raises:
        ValueError: If DATABASE_URL is not set
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return database_url


def get_engine(echo: bool = False) -> Engine:
    """
    Get or create the database engine.
    
    Args:
        echo: Whether to log SQL queries (useful for debugging)
        
    Returns:
        SQLAlchemy engine instance
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            get_database_url(),
            pool_pre_ping=True,  # Verify connections before using them
            pool_size=5,  # Connection pool size
            max_overflow=10,  # Max connections beyond pool_size
            echo=echo,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """
    Get or create the session factory.
    
    Returns:
        SQLAlchemy session factory
    """
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    Note: This should be called from the server, not workers.
    Workers should assume tables already exist.
    """
    Base.metadata.create_all(bind=get_engine())


def get_db() -> Generator[Session, None, None]:
    """
    Get database session for dependency injection or context managers.
    
    Yields:
        SQLAlchemy session
        
    Example:
        # In a worker
        with next(get_db()) as db:
            chunks = db.query(Chunk).filter_by(document_id=doc_id).all()
            
        # Or simpler
        db = next(get_db())
        try:
            chunks = db.query(Chunk).all()
        finally:
            db.close()
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
