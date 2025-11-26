"""User model."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

import bcrypt


@dataclass
class User:
    """User model for storing users metadata."""

    username: str
    email: str
    password_hash: str
    full_name: str | None = None
    id: int = 0
    theme_preference: str = "dark"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def set_password(self, password: str) -> None:
        """Hash and set the users's password."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password and return the hash string."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
