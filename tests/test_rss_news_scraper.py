import pytest
from pathlib import Path
import yaml
import logging
import logging.config
from unittest.mock import patch, Mock
from src.news_sentiment_analyzer import RSSNewsScraper

# ? pytest -vs tests/test_rss_news_scraper.py

# Get the root directory of the project
ROOT_DIR = Path(__file__).parents[1]


def setup_logging():
    config_path = ROOT_DIR / "logging_config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f.read())

    # Ensure the logs directory exists
    log_dir = ROOT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)

    # Update the log file path in the config
    config['handlers']['file']['filename'] = str(
        log_dir / "test_news_sentiment_analysis.log")

    logging.config.dictConfig(config)


@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    setup_logging()
    yield
    # Clean up logging handlers after tests
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        handler.close()


@pytest.fixture(autouse=True)
def reset_logger():
    yield
    # Reset the logger after each test
    setup_logging()


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


def test_rss_news_scraper_initialization():
    logger = logging.getLogger(__name__)
    logger.info("Starting initialization test")
    scraper = RSSNewsScraper("http://example.com/rss")
    assert scraper is not None
    assert scraper.get_rss_url() == "http://example.com/rss"
    logger.info("Finished initialization test")


def test_scrape_rss_feed(mock_requests_get):
    logger = logging.getLogger(__name__)
    logger.info("Starting scrape test")
    scraper = RSSNewsScraper("http://example.com/rss")
    articles = scraper.scrape_rss_feed()

    assert len(articles) == 2
    assert articles[0]['title'] == "Test Article 1"
    assert articles[0]['link'] == "http://example.com/article1"
    assert articles[0]['description'] == "This is the first test article"
    assert articles[1]['title'] == "Test Article 2"
    assert articles[1]['link'] == "http://example.com/article2"
    assert articles[1]['description'] == "This is the second test article"

    logger.info("Finished scrape test")


def test_scrape_rss_feed_error(mock_requests_get):
    logger = logging.getLogger(__name__)
    logger.info("Starting error test")
    mock_requests_get.side_effect = Exception("Network error")
    scraper = RSSNewsScraper("http://example.com/rss")

    with pytest.raises(Exception):
        scraper.scrape_rss_feed()

    logger.info("Finished error test")


def test_log_file_writing():
    logger = logging.getLogger(__name__)
    test_message = "Test log message for file writing"
    logger.info(test_message)

    log_file = ROOT_DIR / "logs" / "test_news_sentiment_analysis.log"
    assert log_file.exists(), f"Log file does not exist: {log_file}"

    with open(log_file, 'r') as f:
        log_content = f.read()
    assert test_message in log_content, f"Test message not found in log file. Log content: {log_content}"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
