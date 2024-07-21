import pytest
from pathlib import Path
import yaml
import logging.config
from src.news_sentiment_analyzer import RSSNewsScraper, BaseRSSNewsScraperAdapter

# ? pytest -vs tests/test_rss_news_scraper_simple.py

# Get the root directory of the project
ROOT_DIR = Path(__file__).parents[1]


@pytest.fixture(scope="session", autouse=True)
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


def test_rss_news_scraper_initialization():
    logger = logging.getLogger(__name__)
    logger.info("Starting test_rss_news_scraper_initialization")
    rss_url = 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
    base_adapter = BaseRSSNewsScraperAdapter(rss_url=rss_url)
    assert base_adapter.get_rss_url() == rss_url
    scraper = RSSNewsScraper(base_adapter)
    assert scraper is not None
    print(scraper.scrape_rss_feed())
