from unittest.mock import MagicMock

import pytest

from src.main import ParserWorker


@pytest.fixture
def worker_mocks(mocker):
    mocker.patch("src.main.PostgresConnection")
    mocker.patch("src.main.S3BlobStorage")
    mocker.patch("src.main.parser_factory")
    mocker.patch("src.main.create_logger")


@pytest.fixture
def parser_worker(worker_mocks):
    return ParserWorker()


def test_process_event_success(parser_worker, mocker):
    # Arrange
    event_data = {
        "document_id": "doc123",
        "workspace_id": "ws456",
        "content_type": "application/pdf",
        "file_path": "path/to/doc.pdf",
        "metadata": {"source": "upload"},
    }
    mock_document_text = "This is the parsed text."

    mock_parser = MagicMock()
    mock_parser.parse_document.return_value = mock_document_text
    parser_worker.parser = mock_parser

    mock_db = MagicMock()
    parser_worker.db_connection = mock_db

    parser_worker.publish_event = MagicMock()
    parser_worker._update_document_status = MagicMock()
    parser_worker._store_parsed_text = MagicMock()

    # Act
    parser_worker.process_event(event_data)

    # Assert
    parser_worker._update_document_status.assert_any_call("doc123", "parsing")
    mock_parser.parse_document.assert_called_once_with(
        "doc123", "application/pdf", "path/to/doc.pdf"
    )
    parser_worker._store_parsed_text.assert_called_once_with(
        "doc123", mock_document_text
    )
    parser_worker._update_document_status.assert_any_call(
        "doc123", "parsed", {"text_length": len(mock_document_text)}
    )

    parser_worker.publish_event.assert_called_once()
    call_args = parser_worker.publish_event.call_args
    assert call_args.kwargs["routing_key"] == "document.parsed"


def test_process_event_parsing_failure(parser_worker, mocker):
    # Arrange
    event_data = {
        "document_id": "doc123",
        "workspace_id": "ws456",
        "content_type": "application/pdf",
        "file_path": "path/to/doc.pdf",
        "metadata": {"source": "upload"},
    }

    mock_parser = MagicMock()
    mock_parser.parse_document.side_effect = Exception("Parsing failed")
    parser_worker.parser = mock_parser

    parser_worker.publish_event = MagicMock()
    parser_worker._update_document_status = MagicMock()

    # Act & Assert
    with pytest.raises(Exception, match="Parsing failed"):
        parser_worker.process_event(event_data)

    parser_worker._update_document_status.assert_any_call("doc123", "parsing")
    parser_worker._update_document_status.assert_any_call(
        "doc123", "failed", {"error": "Parsing failed"}
    )
    parser_worker.publish_event.assert_not_called()
