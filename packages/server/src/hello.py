"""
Hello world module for testing CI/CD setup.
"""


def greet(name: str) -> str:
    """
    Return a greeting message.

    Args:
        name: The name to greet

    Returns:
        A greeting message string
    """
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}!"


def main() -> None:
    """Main entry point for the hello world program."""
    message = greet("World")
    print(message)


if __name__ == "__main__":
    main()
