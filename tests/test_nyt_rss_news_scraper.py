import pytest
from pathlib import Path
import yaml
import logging.config
from src.news_sentiment_analyzer import RSSNewsScraper, NYTRSSNewsScraperAdapter

# ? pytest -vs tests/test_nyt_rss_news_scraper.py

# Get the root directory of the project
ROOT_DIR = Path(__file__).parents[1]


# @pytest.fixture(scope="session", autouse=True)
# def setup_logging():
#     config_path = ROOT_DIR / "logging_config.yaml"
#     with open(config_path, "r") as f:
#         config = yaml.safe_load(f.read())
#     logging.config.dictConfig(config)


def test_rss_news_scraper_initialization():
    scraper = RSSNewsScraper(NYTRSSNewsScraperAdapter())
    assert scraper is not None
    print(scraper.scrape_rss_feed())
