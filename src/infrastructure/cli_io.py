"""Generic CLI I/O wrappers for infrastructure layer.

Provides simple wrappers around input() and print() that can be used
across all domain command files. Does not contain domain-specific logic.
"""

import sys
from typing import Optional


class IO:
    """Generic I/O wrappers for CLI (infrastructure, not domain-specific)."""

    @staticmethod
    def print(message: str) -> None:
        """Print message to stdout.

        Args:
            message: Message to print
        """
        print(message)

    @staticmethod
    def print_error(message: str) -> None:
        """Print error message to stderr.

        Args:
            message: Error message to print
        """
        print(message, file=sys.stderr)

    @staticmethod
    def input(prompt: str) -> str:
        """Get input from user.

        Args:
            prompt: Prompt to display

        Returns:
            User input string
        """
        return input(prompt)

    @staticmethod
    def confirm(prompt: str) -> bool:
        """Get yes/no confirmation from user.

        Args:
            prompt: Confirmation prompt

        Returns:
            True if user confirmed (yes/y), False otherwise
        """
        response = input(prompt).strip().lower()
        return response in ["yes", "y"]
