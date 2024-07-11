import pytest
from pathlib import Path
import yaml
import logging.config
from src.news_sentiment_analyzer import RSSNewsScraper, BaseRSSNewsScraperAdapter

# ? pytest -vs tests/test_rss_news_scraper_simple.py

# Get the root directory of the project
ROOT_DIR = Path(__file__).parents[1]


# @pytest.fixture(scope="session", autouse=True)
# def setup_logging():
#     config_path = ROOT_DIR / "logging_config.yaml"
#     with open(config_path, "r") as f:
#         config = yaml.safe_load(f.read())
#     logging.config.dictConfig(config)


# ! Logging is fine with one method
def test_rss_news_scraper_initialization():
    rss_url = 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
    base_adapter = BaseRSSNewsScraperAdapter(rss_url=rss_url)
    assert base_adapter.get_rss_url() == rss_url
    scraper = RSSNewsScraper(base_adapter)
    assert scraper is not None
    print(scraper.scrape_rss_feed())


# # ! Why does the logging stop working when I add a second function???
# def test_scrape_rss_empty_feed_error():
#     empty_rss_url = "http://google.com"
#     scraper = RSSNewsScraper(empty_rss_url)
#     assert scraper is not None
#     assert scraper.get_rss_url() == empty_rss_url
#     print(scraper.scrape_rss_feed())
