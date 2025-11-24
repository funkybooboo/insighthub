""Workspace endpoints access control scaffold tests"""

import json

import pytest
from io import BytesIO

from flask import Flask
from flask.testing import FlaskClient

from src.api import create_app


@pytest.fixture(scope="function")
def app() -> Flask:
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture(scope="function")
def client(app: Flask) -> FlaskClient:
    return app.test_client()


def test_workspace_upload_requires_auth(client: FlaskClient) -> None:
    data = {"file": (BytesIO(b"data"), "doc.txt", "text/plain")}
    resp = client.post("/api/workspaces/1/documents/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code in (401, 403)


def test_list_documents_requires_auth(client: FlaskClient) -> None:
    resp = client.get("/api/workspaces/1/documents")
    assert resp.status_code in (401, 403)


def test_wikipedia_fetch_requires_auth(client: FlaskClient) -> None:
    resp = client.post("/api/workspaces/1/rag/wikipedia", json={"query": "test"})
    assert resp.status_code in (401, 403)
