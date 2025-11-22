"""Factory for creating user repository instances.

Note: Concrete implementations (SQLAlchemy, etc.) should be registered here
when available. The shared library defines interfaces; implementations
typically live in the server package.
"""

from shared.types.option import Nothing, Option

from .user_repository import UserRepository


def create_user_repository(
    repo_type: str,
    **kwargs: str,
) -> Option[UserRepository]:
    """
    Create a user repository instance based on configuration.

    Args:
        repo_type: Type of repository (e.g., "sqlalchemy")
        **kwargs: Repository-specific configuration

    Returns:
        Some(UserRepository) if creation succeeds, Nothing() if type unknown

    Note:
        Register concrete implementations here when available.
        Example:
            if repo_type == "sqlalchemy":
                session = kwargs.get("session")
                return Some(SQLAlchemyUserRepository(session))
    """
    # No implementations registered in shared library
    # Concrete implementations should be added when available
    return Nothing()
