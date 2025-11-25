class PostgresConnection:
    def __init__(self, db_url):
        self.db_url = db_url
        self.connection = None

    def connect(self):
        pass

    def get_cursor(self, as_dict=False):
        from contextlib import contextmanager
        @contextmanager
        def cursor_manager():
            class DummyCursor:
                def execute(self, query, params=None):
                    pass
                def fetchone(self):
                    return {"id": 1}
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc_val, exc_tb):
                    pass
            yield DummyCursor()
        return cursor_manager()