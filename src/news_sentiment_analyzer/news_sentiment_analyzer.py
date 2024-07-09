import gradio as gr
import pandas as pd
import random
import time
import logging
import logging.config
import yaml
from tqdm import tqdm
from pathlib import Path


class NewsSentimentAnalyzer:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parents[2] / "logging_config.yaml"
        self.load_logging_config(config_path)
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

    def load_logging_config(self, config_path):
        config_path = Path(config_path)
        if not config_path.is_file():
            raise FileNotFoundError(
                f"Logging config file not found: {config_path}")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)

    def analyze_news(self, sources, progress=gr.Progress()):
        self.logger.info(f"Starting analysis for sources: {sources}")
        results = []
        total_stories = len(sources) * 5  # 5 stories per source

        for i, source in tqdm(enumerate(sources), total=len(sources), desc="Processing sources"):
            self.logger.info(f"Scraping {source}")
            progress(i / len(sources), f"Scraping {source}")
            for j in tqdm(range(5), desc=f"Analyzing stories from {source}", leave=False):
                time.sleep(0.5)  # Simulate processing time
                story = {
                    "Source": source,
                    "Headline": random.choice(self.headlines),
                    "Story": random.choice(self.stories),
                    "Sentiment": random.choice(self.sentiments)
                }
                results.append(story)
                self.logger.debug(
                    f"Analyzed story from {source}: {story['Headline']}")
                progress((i * 5 + j + 1) / total_stories,
                         f"Analyzing story {j+1} from {source}")
                yield pd.DataFrame(results)

        self.logger.info("Analysis complete")
        progress(1.0, "Analysis complete")
        yield pd.DataFrame(results)

    def news_sentiment_analysis(self, cnn, abc, npr, progress=gr.Progress()):
        sources = []
        if cnn:
            sources.append("CNN")
        if abc:
            sources.append("ABC")
        if npr:
            sources.append("NPR")

        if not sources:
            self.logger.warning("No sources selected")
            yield "Please select at least one news source."
            return

        self.logger.info(f"Starting analysis with sources: {sources}")
        yield from self.analyze_news(sources, progress)

    def create_interface(self):
        return gr.Interface(
            fn=self.news_sentiment_analysis,
            inputs=[
                gr.Checkbox(label="CNN"),
                gr.Checkbox(label="ABC"),
                gr.Checkbox(label="NPR")
            ],
            outputs=gr.Dataframe(),
            title="News Sentiment Analysis",
            description="Select news sources to analyze sentiment of headlines and stories.",
            theme="huggingface",
            live=False
        )

    def run(self):
        self.logger.info("Starting Gradio interface")
        iface = self.create_interface()
        iface.launch()


if __name__ == "__main__":
    analyzer = NewsSentimentAnalyzer()
    analyzer.run()
