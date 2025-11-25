from unittest.mock import MagicMock, patch

from src.main import WikipediaFetcher, WikipediaWorker


def test_wikipedia_worker_processes_request():
    """Test that the worker processes a Wikipedia fetch request correctly."""
    # Mock the external dependencies
    with patch("src.main.PostgresConnection") as mock_db, patch(
        "src.main.S3BlobStorage"
    ) as mock_storage, patch("src.main.WikipediaFetcher") as mock_fetcher:

        # Setup mocks
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.connect.return_value = None

        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_fetcher_instance = MagicMock()
        mock_fetcher.return_value = mock_fetcher_instance
        mock_fetcher_instance.search_and_fetch.return_value = [
            {
                "title": "Python (programming language)",
                "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
                "content": "Python is a programming language.",
                "summary": "Python is a high-level programming language.",
                "page_id": 23862,
            }
        ]

        # Create worker
        worker = WikipediaWorker()

        # Mock the publish_event method on the worker instance
        worker.publish_event = MagicMock()

        # Mock the database cursor and upload result
        mock_cursor = MagicMock()
        mock_db_instance.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"id": 123}

        mock_upload_result = MagicMock()
        mock_upload_result.is_err.return_value = False
        mock_storage_instance.upload_file.return_value = mock_upload_result

        # Test event processing
        event_data = {
            "workspace_id": "ws1",
            "query": "Python programming",
            "user_id": "user1",
        }

        worker.process_event(event_data)

        # Verify fetcher was called
        mock_fetcher_instance.search_and_fetch.assert_called_once_with(
            "Python programming"
        )

        # Verify database operations
        mock_cursor.execute.assert_called()
        mock_db_instance.connection.commit.assert_called()

        # Verify storage upload
        mock_storage_instance.upload_file.assert_called_once()

        # Verify event publishing (at least status and document events)
        assert worker.publish_event.call_count >= 2


def test_wikipedia_fetcher_with_mock():
    """Test the WikipediaFetcher with mocked Wikipedia API."""
    with patch("wikipediaapi.Wikipedia") as mock_wiki_class:
        mock_wiki_instance = MagicMock()
        mock_wiki_class.return_value = mock_wiki_instance

        mock_page = MagicMock()
        mock_page.exists.return_value = True
        mock_page.title = "Test Page"
        mock_page.fullurl = "https://en.wikipedia.org/wiki/Test_Page"
        mock_page.text = "This is test content."
        mock_page.summary = "Test summary."
        mock_page.pageid = 12345

        mock_wiki_instance.page.return_value = mock_page
        mock_wiki_instance.search.return_value = ["Test Page"]

        fetcher = WikipediaFetcher()
        results = fetcher.search_and_fetch("test query")

        assert len(results) == 1
        assert results[0]["title"] == "Test Page"
        assert results[0]["content"] == "This is test content."
        assert results[0]["page_id"] == 12345


def test_wikipedia_worker_handles_no_results():
    """Test that the worker handles cases where no Wikipedia pages are found."""
    with patch("src.main.PostgresConnection") as mock_db, patch(
        "src.main.S3BlobStorage"
    ) as mock_storage, patch("src.main.WikipediaFetcher") as mock_fetcher:

        # Setup mocks
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance

        mock_storage_instance = MagicMock()
        mock_storage.return_value = mock_storage_instance

        mock_fetcher_instance = MagicMock()
        mock_fetcher.return_value = mock_fetcher_instance
        mock_fetcher_instance.search_and_fetch.return_value = []  # No results

        # Create worker
        worker = WikipediaWorker()
        worker.publish_event = MagicMock()

        # Test event processing
        event_data = {
            "workspace_id": "ws1",
            "query": "nonexistent topic",
            "user_id": "user1",
        }

        worker.process_event(event_data)

        # Verify fetcher was called
        mock_fetcher_instance.search_and_fetch.assert_called_once_with(
            "nonexistent topic"
        )

        # Verify failure status was published
        worker.publish_event.assert_called_with(
            "wikipedia.fetch_status",
            {
                "workspace_id": "ws1",
                "query": "nonexistent topic",
                "status": "failed",
                "document_ids": [],
                "message": "No Wikipedia pages found",
            },
        )
