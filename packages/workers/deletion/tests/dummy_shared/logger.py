"""Dummy logger module for testing."""

import logging


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
