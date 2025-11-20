"""Database session management and connection utilities."""

import os
from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from shared.database.base import Base

# Global engine and session factory (created lazily)
_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_database_url() -> str:
    """Get database URL from environment variable."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return database_url


def get_engine() -> Engine:
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            get_database_url(),
            pool_pre_ping=True,  # Verify connections before using them
            pool_size=5,  # Connection pool size
            max_overflow=10,  # Max connections beyond pool_size
            echo=False,  # Set to True to log SQL queries (useful for debugging)
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def init_db() -> None:
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=get_engine())


def get_db() -> Generator[Session, None, None]:
    """
    Get database session for dependency injection.

    Yields:
        Session: SQLAlchemy session

    Example:
        @app.route('/users')
        def get_users():
            db = next(get_db())
            try:
                users = db.query(User).all()
                return jsonify(users)
            finally:
                db.close()
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
