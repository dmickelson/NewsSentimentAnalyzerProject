from bs4 import BeautifulSoup
import requests
import logging
from pathlib import Path
from typing import Union, Dict, List
import yaml


class RSSNewsScraper:
    """
    A class for scraping news articles from RSS feeds.

    This class provides functionality to fetch and parse RSS feeds,
    extracting relevant information from news articles.

    Attributes:
        logger (logging.Logger): Logger instance for the class.
        __rss_url (str): The URL of the RSS feed to scrape.
    """

    def __init__(self, rss_url: str) -> None:
        config_path = Path(__file__).parents[2] / "logging_config.yaml"
        self.load_logging_config(config_path)
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initiating Class {__name__}")
        if not rss_url:
            self.logger.error(f'No RSS URL Provided')
            raise ValueError(f'No RSS URL Provided')
        self.logger.debug(f"Setting RSS URL: {rss_url}")
        self.__rss_url = rss_url

    def get_rss_url(self) -> str:
        """
        Get the RSS URL.

        Returns:
            str: The URL of the RSS feed.
        """
        return self.__rss_url

    def scrape_rss_feed(self) -> List[Dict[str, str]]:
        """
        Scrape the RSS feed and extract article information.

        This method fetches the RSS feed, parses its content, and extracts
        relevant information from each article.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, each containing
            information about a single article (title, link, description).

        Raises:
            requests.RequestException: If there's an error fetching the RSS feed.
        """
        articles = []
        try:
            self.logger.debug(f'Getting RSS feed from: {self.__rss_url}')
            response = requests.get(self.__rss_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as ex:
            self.logger.exception(f'Error getting RSS feed: {str(ex)}')
            raise

        soup = BeautifulSoup(response.content, 'xml')
        if not soup:
            self.logger.error(f'No XML content found at {self.__rss_url}')

        # * Find all the "item" elements (commonly used in RSS feeds)
        items = soup.find_all('item')
        if not items or len(items) == 0:
            self.logger.error(f'No items found at {self.__rss_url}')

        # * Iterate over each item to extract the data you need
        for item in items:
            title = item.find('title').text.strip()
            link = item.find('link').text.strip()
            description = item.find('description').text.strip()

            story = {
                'title': title,
                'link': link,
                'description': description
            }
            self.logger.debug(f'---')
            self.logger.debug(f'Story: {story}')
            # * Add it to the list of articles
            articles.append(story)

        self.logger.debug(f'Scraped {len(articles)} articles')
        return articles

    @staticmethod
    def load_logging_config(config_path: Union[str, Path]) -> None:
        '''
        Load the logging configuration from a YAML file.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            yaml.YAMLError: If there's an error parsing the YAML file.
        '''
        config_path = Path(config_path)
        if not config_path.is_file():
            raise FileNotFoundError(
                f"Logging config file not found: {config_path}")

        try:
            with open(config_path, 'r') as f:
                log_config = yaml.safe_load(f)
                logging.config.dictConfig(log_config)
        except yaml.YAMLError as ex:
            raise yaml.YAMLError(
                f"Error parsing logging config file: {str(ex)}")
