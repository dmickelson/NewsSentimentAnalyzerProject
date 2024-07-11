import gradio as gr
import pandas as pd
import random
import time
from typing import Union
import logging
import logging.config
import yaml
from tqdm import tqdm
from pathlib import Path
from rss_news_scraper import *
from sentiment_analyzer import *

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


class NewsSentimentAnalyzer:
    def __init__(self, config_path: Union[str, Path] = None):
        # if config_path is None:
        #    config_path = Path(__file__).parents[2] / "logging_config.yaml"
        # self.load_logging_config(config_path)
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initiating Class {__name__}")
        self.headlines = [
            "Breaking news: Major event unfolds",
            "Economy shows signs of recovery",
            "New scientific discovery announced",
            "Sports team wins championship",
            "Political tensions rise in key region"
        ]
        self.stories = [
            "A significant event has occurred, impacting millions...",
            "Recent economic indicators suggest a positive trend...",
            "Scientists have made a groundbreaking discovery in the field of...",
            "In a thrilling match, the underdog team emerged victorious...",
            "Diplomatic relations are strained as leaders disagree on..."
        ]
        self.sentiments = ["Positive", "Negative", "Neutral"]

    # def load_logging_config(self, config_path: Union[str, Path]):
    #     """
    #     Load the logging configuration from a YAML file.

    #     Args:
    #         config_path (Union[str, Path]): Path to the logging configuration file.

    #     Raises:
    #         FileNotFoundError: If the configuration file is not found.
    #         yaml.YAMLError: If there's an error parsing the YAML file.
    #     """
    #     config_path = Path(config_path)
    #     if not config_path.is_file():
    #         self.logger.error(f"Logging config file not found: {config_path}")
    #         raise FileNotFoundError(
    #             f"Logging config file not found: {config_path}")

    #     try:
    #         with open(config_path, 'r') as f:
    #             log_config = yaml.safe_load(f)
    #             logging.config.dictConfig(log_config)
    #     except yaml.YAMLError as ex:
    #         self.logger.exception(
    #             f"Error parsing logging config file: {str(ex)}")
    #         raise yaml.YAMLError(
    #             f"Error parsing logging config file: {str(ex)}")

    def analyze_news(self, sources: List[RSSNewsScraper], progress=gr.Progress()):
        """
        Analyze news from given sources and yield results progressively.

        Args:
            sources (List[RSSNewsScraper]): List of news sources to analyze.
            progress (gr.Progress, optional): Gradio progress bar.

        Yields:
            pd.DataFrame: DataFrame containing analysis results.
        """
        analyzer = SentimentAnalyzer()
        results = []
        total_stories = len(sources) * 10  # 10 stories per source
        for source in tqdm(iterable=sources, total=len(sources), desc="Processing sources", colour="blue"):
            # for source in sources:
            self.logger.info(f"Scraping {source}")
            progress(10 / len(sources), f"Scraping {source}")
            articles = source.scrape_rss_feed()
            for article in tqdm(articles, desc=f"Analyzing stories from {source}", leave=False):
                text = article["title"] + ' ' + article["description"]
                sentiment_results = analyzer.get_sentiment(text)
                results.append(sentiment_results)
                self.logger.debug(
                    f"Analyzed story from {source}: {article['title']}")
                progress((1 * 5 + 1 + 1) / total_stories,
                         f"Analyzing story {1} from {source}")
                yield pd.DataFrame(results)

        self.logger.info("Analysis complete")
        progress(1.0, "Analysis complete")
        yield pd.DataFrame(results)

    def gather_data(self, sources, progress=gr.Progress()):
        '''
        Gathers the data to be analyzed
        '''
        pass

    def news_sentiment_analysis(self, cnn: bool = False, abc: bool = False, npr: bool = False, nyt: bool = False, progress=gr.Progress()):
        ''' Get News Articles and Perform Sentiment Analysis'''
        sources = []
        if cnn:
            rss_url = 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
            base_adapter = BaseRSSNewsScraperAdapter(rss_url=rss_url)
            cnn_scraper = RSSNewsScraper(base_adapter)
            sources.append(cnn_scraper)
        if abc:
            sources.append("ABC")
        if npr:
            sources.append("NPR")
        if nyt:
            nyt_scraper = RSSNewsScraper(NYTRSSNewsScraperAdapter())
            sources.append(nyt_scraper)

        if not sources:
            self.logger.warning("No sources selected")
            yield "Please select at least one news source."
            return
        self.logger.debug(
            f'Starting analysis with {len(sources)} sources selected')
        yield from self.analyze_news(sources, progress)

    def create_interface(self):
        """
        Create and return the Gradio interface for the news sentiment analysis.

        Returns:
            gr.Interface: Gradio interface object.
        """
        return gr.Interface(
            fn=self.news_sentiment_analysis,

            inputs=[
                # gr.CheckboxGroup(["CNN", "ABC", "NPR", "NYT"], label="News Sources", info="Select News Sources", container=True),
                gr.Checkbox(label="CNN", value=True, info="CNN"),
                gr.Checkbox(label="ABC", info="ABC News"),
                gr.Checkbox(label="NPR", info="NPR News"),
                gr.Checkbox(label="NYT", value=True, info="New York Times")
            ],
            outputs=gr.Dataframe(
                label="Sentiment Results",
                headers=["Description", "Sentiment", "Confidence"],
                min_width=300,
                wrap=True,
                scale=3
            ),
            title="News Sentiment Analysis",
            description="Select news sources to analyze sentiment of headlines and stories.",
            show_progress=True,
            live=False
        )

    def run(self):
        self.logger.info("Starting Gradio interface")
        iface = self.create_interface()
        iface.launch()


if __name__ == "__main__":
    analyzer = NewsSentimentAnalyzer()
    analyzer.run()
