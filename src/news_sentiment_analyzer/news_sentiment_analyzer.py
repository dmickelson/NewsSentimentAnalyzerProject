import logging
from typing import List
import gradio as gr
import pandas as pd
from typing import Union
import logging
import logging.config
import yaml
from tqdm import tqdm
from pathlib import Path
from .rss_news_scraper import RSSNewsScraper, BaseRSSNewsScraperAdapter, ABCRSSNewsScraperAdapter, NYTRSSNewsScraperAdapter
from .sentiment_analyzer import SentimentAnalyzer

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
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initiating Class {__name__}")

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
        progress(0, desc="Starting...")
        total_stories = len(sources) * 10  # 10 stories per source
        for source in progress.tqdm(iterable=sources, total=len(sources), desc=f"Processing News Sources"):
            self.logger.info(f"Scraping {source.rss_adapter.get_rss_url()}")
            articles = source.scrape_rss_feed()
            for article in tqdm(articles, desc=f"Analyzing {len(articles)} stories", leave=False):
                text = article["title"] + ' ' + article["description"]
                sentiment_results = analyzer.get_sentiment(text)
                results.append(sentiment_results)
                self.logger.debug(
                    f"Analyzed story from {source}: {article['title']}")
                yield pd.DataFrame(results)

        self.logger.info("Analysis complete")
        progress(1.0, "Analysis complete")
        return pd.DataFrame(results)

    def gather_data(self, data: pd.DataFrame, progress=gr.Progress()):
        '''
        Gathers the data to be analyzed
        '''
        self.logger.debug("Starting Gathering Data")
        return

    def news_sentiment_analysis(self, cnn: bool = False, abc: bool = False, nyt: bool = False, progress=gr.Progress()):
        ''' Get News Articles and Perform Sentiment Analysis'''
        sources = []
        if cnn:
            rss_url = 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
            base_adapter = BaseRSSNewsScraperAdapter(rss_url=rss_url)
            cnn_scraper = RSSNewsScraper(base_adapter)
            sources.append(cnn_scraper)
        if abc:
            abc_scraper = RSSNewsScraper(ABCRSSNewsScraperAdapter())
            sources.append(abc_scraper)
        if nyt:
            nyt_scraper = RSSNewsScraper(NYTRSSNewsScraperAdapter())
            sources.append(nyt_scraper)

        if not sources:
            self.logger.warning("No sources selected")
            # "Please select at least one news source."
            raise gr.Error(
                "Please select at least one news source.", duration=5)
            return
        self.logger.debug(
            f'Starting analysis with {len(sources)} sources selected')
        pdf_results = yield from self.analyze_news(sources, progress)
        self.logger.debug(f'Total number of News Stores {pdf_results.size}')
        self.gather_data(pdf_results)
        return pdf_results, 0.5

    def create_blocks(self) -> gr.Blocks:
        with gr.Blocks(title="News Sentiment Analysis", fill_height=True) as demo:
            gr.Markdown(
                "Select at least one News Sources below to analyze sentiment of headlines and stories and then click **Run** to see the output.")
            with gr.Row():
                inp = [
                    gr.Checkbox(label="CNN", value=True, info="CNN"),
                    gr.Checkbox(label="ABC", value=True, info="ABC News"),
                    gr.Checkbox(label="NYT", value=True, info="New York Times")
                ]
                btn = gr.Button("Run")
            with gr.Row():
                out = [
                    gr.Dataframe(
                        label="Sentiment Results",
                        headers=["Description", "Sentiment", "Confidence"],
                        min_width=300,
                        wrap=True,
                        scale=3
                    )
                ]
            btn.click(fn=self.news_sentiment_analysis, inputs=inp, outputs=out)
        return demo

    def run(self):
        self.logger.info("Starting Gradio interface")
        iface = self.create_blocks()
        iface.launch()
