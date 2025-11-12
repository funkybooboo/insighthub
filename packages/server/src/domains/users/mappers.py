"""Mappers for converting between user models and DTOs."""

from .models import User


class UserMapper:
    """Handles conversions between user domain models and DTOs."""

    @staticmethod
    def user_to_dict(user: User) -> dict[str, str | int]:
        """
        Convert a User model to a dictionary for JSON serialization.

        Args:
            user: User model instance

        Returns:
            Dictionary representation of the user
        """
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name or "",
            "created_at": user.created_at.isoformat(),
        }

    @staticmethod
    def users_to_dicts(users: list[User]) -> list[dict[str, str | int]]:
        """
        Convert a list of User models to dictionaries.

        Args:
            users: List of User model instances

        Returns:
            List of dictionary representations
        """
        return [UserMapper.user_to_dict(user) for user in users]
