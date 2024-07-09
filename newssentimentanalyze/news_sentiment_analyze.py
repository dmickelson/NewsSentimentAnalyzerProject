import gradio as gr
import pandas as pd
import random
import time

# Placeholder function for web scraping and sentiment analysis


def analyze_news(sources, progress=gr.Progress()):
    headlines = [
        "Breaking news: Major event unfolds",
        "Economy shows signs of recovery",
        "New scientific discovery announced",
        "Sports team wins championship",
        "Political tensions rise in key region"
    ]
    stories = [
        "A significant event has occurred, impacting millions...",
        "Recent economic indicators suggest a positive trend...",
        "Scientists have made a groundbreaking discovery in the field of...",
        "In a thrilling match, the underdog team emerged victorious...",
        "Diplomatic relations are strained as leaders disagree on..."
    ]
    sentiments = ["Positive", "Negative", "Neutral"]

    results = []
    total_stories = len(sources) * 5  # 5 stories per source

    for i, source in enumerate(sources):
        progress(i / len(sources), f"Scraping {source}")
        for j in range(5):  # Simulate 5 stories per source
            time.sleep(0.5)  # Simulate processing time
            results.append({
                "Source": source,
                "Headline": random.choice(headlines),
                "Story": random.choice(stories),
                "Sentiment": random.choice(sentiments)
            })
            progress((i * 5 + j + 1) / total_stories,
                     f"Analyzing story {j+1} from {source}")
            yield pd.DataFrame(results)

    progress(1.0, "Analysis complete")
    yield pd.DataFrame(results)

# Gradio interface


def news_sentiment_analysis(cnn, abc, npr, progress=gr.Progress()):
    sources = []
    if cnn:
        sources.append("CNN")
    if abc:
        sources.append("ABC")
    if npr:
        sources.append("NPR")

    if not sources:
        yield "Please select at least one news source."
        return

    yield from analyze_news(sources, progress)


# Create the Gradio interface
iface = gr.Interface(
    fn=news_sentiment_analysis,
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

# Launch the interface
iface.launch()
