"""Factory for creating UserService instances."""

from enum import Enum

from sqlalchemy.orm import Session

from src import config
from src.repositories import create_user_repository

from .default_user_service import DefaultUserService
from .user_service import UserService


class UserServiceType(Enum):
    """Enum for user service implementation types."""

    DEFAULT = "default"


def create_user_service(
    db: Session, service_type: UserServiceType | None = None
) -> UserService:
    """
    Create a UserService instance with dependencies.

    Args:
        db: Database session
        service_type: Type of user service implementation to use.
                     If None, reads from config.USER_SERVICE_TYPE.

    Returns:
        UserService: Service instance with injected dependencies

    Raises:
        ValueError: If service_type is not supported
    """
    if service_type is None:
        service_type = UserServiceType(config.USER_SERVICE_TYPE)

    repository = create_user_repository(db)

    if service_type == UserServiceType.DEFAULT:
        return DefaultUserService(repository=repository)
    else:
        raise ValueError(f"Unsupported user service type: {service_type}")
