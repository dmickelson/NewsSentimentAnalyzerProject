

import pytest
from pathlib import Path
import yaml
import logging.config
from src.news_sentiment_analyzer import SentimentAnalyzer

# ? pytest -vs tests/test_sentiment_analyzer.py

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


def test_sentiment_analyzer_initialization():
    logger = logging.getLogger(__name__)
    logger.info("Starting test_sentiment_analyzer_initialization")
    analyzer = SentimentAnalyzer()
    assert analyzer is not None

    # Analyze a single text
    result = analyzer.get_sentiment("I love this movie!")
    print(result)

    # Analyze multiple texts
    texts = ["This is great!", "I'm feeling sad", "The weather is okay"]
    results = analyzer.get_sentiment(texts)
    for result in results:
        print(result)
        # Add more assertions as needed
