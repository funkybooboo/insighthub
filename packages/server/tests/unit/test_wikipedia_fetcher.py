"""Unit tests for Wikipedia fetcher."""

import pytest
from unittest.mock import Mock, patch

from src.infrastructure.wikipedia import WikipediaFetcher, wikipedia_fetcher


class TestWikipediaFetcher:
    """Tests for Wikipedia fetcher functionality."""

    def test_fetcher_initialization(self):
        """Test Wikipedia fetcher initialization."""
        fetcher = WikipediaFetcher(timeout=10, max_retries=2)
        assert fetcher.timeout == 10
        assert fetcher.max_retries == 2

    @patch('src.infrastructure.wikipedia.fetch.requests.Session')
    def test_search_articles_success(self, mock_session):
        """Test successful article search."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = [
            ["Machine learning"],  # titles
            ["Machine learning is..."],  # descriptions
            ["https://en.wikipedia.org/wiki/Machine_learning"]  # urls
        ]
        mock_response.raise_for_status.return_value = None

        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        fetcher = WikipediaFetcher()
        result = fetcher.search_articles("machine learning", limit=1)

        assert result.is_ok()
        articles = result.unwrap()
        assert len(articles) == 1
        assert articles[0]["title"] == "Machine learning"
        assert "wikipedia.org" in articles[0]["url"]

    @patch('src.infrastructure.wikipedia.fetch.requests.Session')
    def test_search_articles_network_error(self, mock_session):
        """Test search with network error."""
        mock_session_instance = Mock()
        mock_session_instance.get.side_effect = Exception("Network error")
        mock_session.return_value = mock_session_instance

        fetcher = WikipediaFetcher()
        result = fetcher.search_articles("test query")

        assert result.is_err()
        assert "Search request failed" in result.err()

    @patch('src.infrastructure.wikipedia.fetch.requests.Session')
    def test_fetch_article_direct_success(self, mock_session):
        """Test direct article fetch success."""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "title": "Python (programming language)",
            "extract": "Python is a programming language...",
            "content_urls": {
                "desktop": {
                    "page": "https://en.wikipedia.org/wiki/Python_(programming_language)"
                }
            },
            "categories": [{"title": "Category:Programming languages"}]
        }
        mock_response.raise_for_status.return_value = None

        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        fetcher = WikipediaFetcher()
        result = fetcher.fetch_article("Python (programming language)")

        assert result.is_ok()
        article = result.unwrap()
        assert article.title == "Python (programming language)"
        assert "Python is a programming language" in article.content
        assert article.language == "en"

    @patch('src.infrastructure.wikipedia.fetch.requests.Session')
    def test_fetch_article_not_found(self, mock_session):
        """Test article fetch when article doesn't exist."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("404 Client Error")
        mock_response.status_code = 404

        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        fetcher = WikipediaFetcher()
        result = fetcher.fetch_article("NonExistentArticle12345")

        assert result.is_err()
        assert "not found" in result.err()

    def test_article_to_markdown(self):
        """Test article to markdown conversion."""
        article = wikipedia_fetcher.WikipediaArticle(
            title="Test Article",
            content="This is the content.\n\nWith multiple paragraphs.",
            url="https://en.wikipedia.org/wiki/Test_Article",
            language="en",
            summary="A test summary",
            categories=["Category:Test articles"]
        )

        markdown = article.to_markdown()
        assert "# Test Article" in markdown
        assert "A test summary" in markdown
        assert "https://en.wikipedia.org/wiki/Test_Article" in markdown
        assert "Category:Test articles" in markdown
        assert "This is the content." in markdown