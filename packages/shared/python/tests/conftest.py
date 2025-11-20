"""Pytest configuration for shared library tests."""

import pytest


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
    }


@pytest.fixture
def sample_document_data():
    """Sample document data for testing."""
    return {
        "id": 1,
        "workspace_id": 1,
        "user_id": 1,
        "filename": "test.pdf",
        "original_filename": "test.pdf",
        "file_size": 1024,
        "mime_type": "application/pdf",
        "storage_path": "documents/test.pdf",
    }


@pytest.fixture
def sample_workspace_data():
    """Sample workspace data for testing."""
    return {
        "id": 1,
        "user_id": 1,
        "name": "Test Workspace",
        "description": "A test workspace",
        "is_active": True,
        "status": "ready",
    }
