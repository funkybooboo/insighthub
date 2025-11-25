"""Dummy database modules for testing."""


class DummyConnection:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connection = None

    def connect(self) -> None:
        pass

    def get_cursor(self, as_dict: bool = False) -> "DummyCursor":
        return DummyCursor()

    def commit(self) -> None:
        pass


class DummyCursor:
    def __init__(self) -> None:
        self.results: list[dict] = []
        # Mock data for testing
        self.mock_data = {
            "SELECT rag_collection FROM workspaces WHERE id = %s": [
                {"rag_collection": "delete_test_collection"}
            ],
            "SELECT file_path FROM documents WHERE workspace_id = %s": [
                {"file_path": "delete_test.txt"}
            ],
            "SELECT id FROM document_chunks WHERE document_id = %s": [
                {"id": "chunk_1"},
                {"id": "chunk_2"},
            ],
        }

    def __enter__(self) -> "DummyCursor":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        self.close()

    def execute(self, query: str, params: list | None = None) -> None:
        # Store the query for fetch methods
        self.last_query = query
        self.last_params = params

    def fetchone(self) -> dict | None:
        if hasattr(self, "last_query") and self.last_query in self.mock_data:
            return self.mock_data[self.last_query][0] if self.mock_data[self.last_query] else None
        return None

    def fetchall(self) -> list[dict]:
        if hasattr(self, "last_query") and self.last_query in self.mock_data:
            return self.mock_data[self.last_query]
        return []

    def close(self) -> None:
        pass


class PostgresConnection:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connection = DummyConnection(db_url)

    def connect(self) -> None:
        pass

    def get_cursor(self, as_dict: bool = False) -> "DummyCursor":
        return self.connection.get_cursor(as_dict)

    def commit(self) -> None:
        pass
