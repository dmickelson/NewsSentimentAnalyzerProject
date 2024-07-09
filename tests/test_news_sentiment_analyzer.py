import pytest
from pathlib import Path
import yaml
import logging.config
from src.news_sentiment_analyzer import NewsSentimentAnalyzer

# Get the root directory of the project
ROOT_DIR = Path(__file__).parents[1]


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    config_path = ROOT_DIR / "logging_config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


def test_news_sentiment_analyzer_initialization():
    analyzer = NewsSentimentAnalyzer()
    assert analyzer is not None
    # Add more assertions as needed

# Add
