import logging
from bs4 import BeautifulSoup
import requests
import logging
from pathlib import Path
from typing import Union, Dict, List
import yaml
import emoji

# NPR https://feeds.npr.org/1003/rss.xml
# NyTimes https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml
# yahoo news: https://news.yahoo.com/rss
# NBC news: http://feeds.nbcnews.com/feeds/topstories
# ABC news" http://abcnews.go.com/abcnews/topstories

config_path = Path(__file__).parents[2] / "logging_config.yaml"
config_path = Path(config_path)
if not config_path.is_file():
    raise FileNotFoundError(f"Logging config file not found: {config_path}")
try:
    with open(config_path, 'r') as f:
        log_config = yaml.safe_load(f)
        logging.config.dictConfig(log_config)
except yaml.YAMLError as ex:
    raise yaml.YAMLError(f"Error parsing logging config file: {str(ex)}")


class StringCleaner():
    @classmethod
    def clean_string(cls, input_string: str) -> str:
        """
        Clean up a string by removing unnecessary spaces, emojis, and other formatting.

        Args:
            input_string (str): The input string to be cleaned.

        Returns:
            str: The cleaned string.
        """
        emoji_free = emoji.replace_emoji(input_string, replace='')
        temp_string = emoji_free.replace(
            "\n", " ").replace("\r", " ").strip()
        clean_string = ' '.join(temp_string.split())
        clean_string = clean_string.encode(
            'ascii', 'ignore').decode('ascii').strip()
        return clean_string


class RSSNewsScraper():
    """
    A class for scraping news articles from RSS feeds using the Adapter pattern.

    This class provides functionality to fetch and parse RSS feeds,
    extracting relevant information from news articles using a specific RSS adapter.

    Attributes:
        logger (logging.Logger): Logger instance for the class.
        rss_adapter (object): The RSS adapter used to scrape the feed.
    """

    def __init__(self, rss_adapter: object) -> None:
        """
        Initialize the RSSNewsScraper with a specific RSS adapter.

        Args:
            rss_adapter (object): The RSS adapter to use for scraping.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initiating Class {__name__}")
        self.rss_adapter = rss_adapter

    def scrape_rss_feed(self) -> List[Dict[str, str]]:
        """
        Scrape the RSS feed using the provided adapter and extract article information.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, each containing
            information about a single article (title, link, description).
        """
        results = self.rss_adapter.scrape_rss_feed()
        if results:
            self.logger.debug(
                f'RSSNewsScraper.scrape_rss_feed Results Len: {len(results)}')
        return results


class BaseRSSNewsScraperAdapter():
    """
    Base class for RSS news scraper adapters.

    This class provides a common interface for different RSS feed adapters.

    Attributes:
        logger (logging.Logger): Logger instance for the class.
        __rss_url (str): The URL of the RSS feed to scrape.
    """

    def __init__(self, rss_url: str) -> None:
        """
        Initialize the BaseRSSNewsScraperAdapter with a specific RSS URL.

        Args:
            rss_url (str): The URL of the RSS feed to scrape.

        Raises:
            ValueError: If no RSS URL is provided.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initiating Class {__name__}")
        self.logger.debug(f"Setting RSS URL: {rss_url}")
        self.__rss_url = rss_url

    def scrape_rss_feed(self) -> List[Dict[str, str]]:
        """
        Scrape the RSS feed and extract article information.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, each containing
            information about a single article (title, link, description).

        Raises:
            requests.RequestException: If there's an error fetching the RSS feed.
        """
        articles = []
        try:
            self.logger.debug(f'Getting RSS feed from: {self.get_rss_url()}')
            response = requests.get(self.get_rss_url(), timeout=10)
            response.raise_for_status()
        except requests.RequestException as ex:
            self.logger.exception(f'Error getting RSS feed: {str(ex)}')
            raise

        soup = BeautifulSoup(response.content, 'xml')
        if not soup:
            self.logger.error(f'No XML content found at {self.get_rss_url()}')
            return None

        # * Find all the "item" elements (commonly used in RSS feeds)
        items = soup.find_all('item')
        if not items or len(items) == 0:
            self.logger.error(f'No items found at {self.get_rss_url()}')
            return None

        # * Iterate over each item to extract the data you need
        for item in items:
            title, link, description = "", "", ""
            if item.find('title'):
                title = StringCleaner.clean_string(item.find('title').text)
            if item.find('link'):
                link = StringCleaner.clean_string(item.find('link').text)
            if item.find('description'):
                description = StringCleaner.clean_string(item.find(
                    'description').text)

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

    def get_rss_url(self) -> str:
        """
        Get the RSS URL.

        Returns:
            str: The URL of the RSS feed.
        """
        self.logger.debug(f'RSS URL: {self.__rss_url}')
        return self.__rss_url

    def set_rss_url(self, rss_url: str) -> str:
        """
        Set the RSS URL.

        Args:
            rss_url (str): The new URL for the RSS feed.

        Returns:
            str: The updated URL of the RSS feed.
        """
        self.__rss_url = rss_url
        self.logger.debug(f'RSS URL: {self.__rss_url}')
        return self.__rss_url


class NYTRSSNewsScraperAdapter(BaseRSSNewsScraperAdapter):
    """
    Adapter class for scraping New York Times RSS feed.

    This class provides specific functionality to scrape the NYT RSS feed,
    including handling of additional fields like 'media:description'.

    Attributes:
        logger (logging.Logger): Logger instance for the class.
        rss_url (str): The URL of the NYT News RSS feed.
    """

    def __init__(self):
        """
        Initialize the NYTRSSNewsScraperAdapter.
        """
        rss_url = 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initiating Class {__name__}")
        super().__init__(rss_url)

    def scrape_rss_feed(self) -> List[Dict[str, str]]:
        """
        Scrape the NYT RSS feed and extract article information.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, each containing
            information about a single article (title, link, description).

        Raises:
            requests.RequestException: If there's an error fetching the RSS feed.
        """
        articles = []
        try:
            self.logger.debug(f'Getting RSS feed from: {self.get_rss_url()}')
            response = requests.get(self.get_rss_url(), timeout=10)
            response.raise_for_status()
        except requests.RequestException as ex:
            self.logger.exception(f'Error getting RSS feed: {str(ex)}')
            raise

        soup = BeautifulSoup(response.content, 'xml')
        if not soup:
            self.logger.error(f'No XML content found at {self.get_rss_url()}')
            return None

        # * Find all the "item" elements (commonly used in RSS feeds)
        items = soup.find_all('item')
        if not items or len(items) == 0:
            self.logger.error(f'No items found at {self.get_rss_url()}')
            return None

        # * Iterate over each item to extract the data you need
        for item in items:
            title, link, description = "", "", ""
            if item.find('title'):
                title = StringCleaner.clean_string(item.find('title').text)
            if item.find('link'):
                link = StringCleaner.clean_string(item.find('link').text)
            if item.find('description'):
                description = StringCleaner.clean_string(item.find(
                    'description').text)
            if item.find('media:description'):
                description += " " + \
                    StringCleaner.clean_string(item.find(
                        'media:description').text)

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


class ABCRSSNewsScraperAdapter(BaseRSSNewsScraperAdapter):
    """
    Adapter class for scraping ABC News RSS feed.

    This class provides specific functionality to scrape the ABC News RSS feed and
    extract article information.

    Attributes:
        logger (Logger): Logger instance for the class.
        rss_url (str): The URL of the ABC News RSS feed.
    """

    def __init__(self):
        """
        Initialize the ABCRSSNewsScraperAdapter.

        Args:
            rss_url (str): The URL of the ABC News RSS feed to scrape.
        """
        rss_url = "https://abcnews.go.com/abcnews/topstories"
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initiating Class {__name__}")
        super().__init__(rss_url)

    def scrape_rss_feed(self) -> list[dict[str, str]]:
        """
        Scrape the ABC News RSS feed and extract article information.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, each containing
            information about a single article (title, link, description).

        Raises:
            requests.RequestException: If there's an error fetching the RSS feed.
        """
        articles = []
        try:
            self.logger.debug(f'Getting RSS feed from: {self.get_rss_url()}')
            response = requests.get(self.get_rss_url(), timeout=10)
            response.raise_for_status()
        except requests.RequestException as ex:
            self.logger.exception(f'Error getting RSS feed: {str(ex)}')
            raise

        soup = BeautifulSoup(response.content, 'xml')
        if not soup:
            self.logger.error(f'No XML content found at {self.get_rss_url()}')
            return []

        # Find all the "item" elements (commonly used in RSS feeds)
        items = soup.find_all('item')
        if not items:
            self.logger.error(f'No items found at {self.get_rss_url()}')
            return []

        # Iterate over each item to extract the data you need
        for item in items:
            title = StringCleaner.clean_string(item.find('title').text)
            link = StringCleaner.clean_string(item.find('link').text)
            description = StringCleaner.clean_string(
                item.find('description').text)

            # Handle CDATA sections
            title = self._extract_cdata(title)
            link = self._extract_cdata(link)
            description = self._extract_cdata(description)

            story = {
                'title': title,
                'link': link,
                'description': description
            }
            self.logger.debug(f'---')
            self.logger.debug(f'Story: {story}')
            # Add it to the list of articles
            articles.append(story)

        self.logger.debug(f'Scraped {len(articles)} articles')
        return articles

    def _extract_cdata(self, text: str) -> str:
        """
        Extract text from CDATA sections.

        Args:
            text (str): The text potentially containing CDATA sections.

        Returns:
            str: The extracted text without the CDATA tags.
        """
        if text.startswith('<![CDATA[') and text.endswith(']]>'):
            text = text[9:-3]
        return text
