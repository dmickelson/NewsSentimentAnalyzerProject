# main.py

from src.news_sentiment_analyzer.news_sentiment_analyzer import NewsSentimentAnalyzer


def main():
    print("Starting News Sentiment Analyzer")
    analyzer = NewsSentimentAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()
