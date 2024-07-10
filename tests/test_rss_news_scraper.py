import pytest
from pathlib import Path
import yaml
import logging
from unittest.mock import patch, Mock
from src.news_sentiment_analyzer import RSSNewsScraper

# ? pytest -vs tests/test_rss_news_scraper.py --capture=no
# Get the root directory of the project
ROOT_DIR = Path(__file__).parents[1]


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    config_path = ROOT_DIR / "logging_config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    # Set the logging level to DEBUG for testing
    logging.getLogger().setLevel(logging.DEBUG)


@pytest.fixture
def mock_rss_content():
    return """
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Sample RSS Feed</title>
            <description>A sample RSS feed for testing</description>
            <item>
                <title>Test Article 1</title>
                <link>http://example.com/article1</link>
                <description>This is the first test article</description>
            </item>
            <item>
                <title>Test Article 2</title>
                <link>http://example.com/article2</link>
                <description>This is the second test article</description>
            </item>
        </channel>
    </rss>
    """


@pytest.fixture
def mock_requests_get(mock_rss_content):
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.content = mock_rss_content.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        yield mock_get


def test_rss_news_scraper_initialization(caplog):
    with caplog.at_level(logging.INFO):
        scraper = RSSNewsScraper("http://example.com/rss")
        assert scraper is not None
        assert scraper.get_rss_url() == "http://example.com/rss"
        assert "Initializing RSSNewsScraper" in caplog.text
        assert "RSS URL set to: http://example.com/rss" in caplog.text


def test_rss_news_scraper_initialization_error(caplog):
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            RSSNewsScraper("")
        assert "No RSS URL Provided" in caplog.text


def test_scrape_rss_feed(mock_requests_get, caplog):
    with caplog.at_level(logging.DEBUG):
        scraper = RSSNewsScraper("http://example.com/rss")
        articles = scraper.scrape_rss_feed()

        assert len(articles) == 2
        assert articles[0]['title'] == "Test Article 1"
        assert articles[0]['link'] == "http://example.com/article1"
        assert articles[0]['description'] == "This is the first test article"
        assert articles[1]['title'] == "Test Article 2"
        assert articles[1]['link'] == "http://example.com/article2"
        assert articles[1]['description'] == "This is the second test article"

        assert "Getting RSS feed from: http://example.com/rss" in caplog.text
        assert "Scraped story:" in caplog.text
        assert "Scraped 2 articles" in caplog.text


def test_scrape_rss_feed_error(mock_requests_get, caplog):
    with caplog.at_level(logging.ERROR):
        mock_requests_get.side_effect = Exception("Network error")
        scraper = RSSNewsScraper("http://example.com/rss")

        with pytest.raises(Exception):
            scraper.scrape_rss_feed()

        assert "Error getting RSS feed: Network error" in caplog.text


if __name__ == "__main__":
    pytest.main(["-vs", __file__])
