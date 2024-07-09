import yaml
import logging
from typing import Union, List, Dict
from pathlib import Path
from transformers import pipeline
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification


class SentimentAnalyzer:
    '''
    A class for performing sentiment analysis on text using a pre-trained DistilBERT model.

    This class uses the DistilBERT model fine-tuned for sentiment analysis on the SST-2 dataset.
    It can analyze single texts or batches of texts for sentiment.

    Attributes:
        logger (logging.Logger): Logger for the class.
        tokenizer (DistilBertTokenizer): Tokenizer for the DistilBERT model.
        model (DistilBertForSequenceClassification): Pre-trained DistilBERT model.
        nlp (pipeline): Sentiment analysis pipeline.
    '''

    def __init__(self, config_path: Union[str, Path] = None):
        """
        Initialize the SentimentAnalyzer with logging configuration and pre-trained model.

        Args:
            config_path (Union[str, Path], optional): Path to the logging configuration file.
                If None, it looks for 'logging_config.yaml' in the project root.

        Raises:
            FileNotFoundError: If the logging configuration file is not found.
        """
        if config_path is None:
            config_path = Path(__file__).parents[2] / "logging_config.yaml"
        self.load_logging_config(config_path)
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initiating Class {__name__}")

        model_name = "distilbert-base-uncased-finetuned-sst-2-english"

        try:
            # Load the pre-trained tokenizer and model from HuggingFace
            self.tokenizer = DistilBertTokenizer.from_pretrained(model_name)
            self.model = DistilBertForSequenceClassification.from_pretrained(
                model_name)

            # Create the sentiment analysis pipeline
            self.nlp = pipeline('sentiment-analysis',
                                model=self.model, tokenizer=self.tokenizer)
        except Exception as e:
            self.logger.error(
                f"Error loading model or creating pipeline: {str(e)}")
            raise

    def load_logging_config(self, config_path: Union[str, Path]):
        """
        Load the logging configuration from a YAML file.

        Args:
            config_path (Union[str, Path]): Path to the logging configuration file.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            yaml.YAMLError: If there's an error parsing the YAML file.
        """
        config_path = Path(config_path)
        if not config_path.is_file():
            self.logger.error(f"Logging config file not found: {config_path}")
            raise FileNotFoundError(
                f"Logging config file not found: {config_path}")

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logging.config.dictConfig(config)
        except yaml.YAMLError as e:
            self.logger.exception(
                f"Error parsing logging config file: {str(e)}")
            raise yaml.YAMLError(
                f"Error parsing logging config file: {str(e)}")

    def get_sentiment(self, text: Union[str, List[str]]) -> Union[Dict, List[Dict]]:
        """
        Generate sentiment analysis for the given text or list of texts.

        This method performs sentiment analysis on the input text(s) using the pre-trained model.

        Args:
            text (Union[str, List[str]]): A single text string or a list of text strings to analyze.

        Returns:
            Union[Dict, List[Dict]]: A dictionary (for single input) or list of dictionaries (for multiple inputs)
                containing the sentiment analysis results. Each dictionary includes 'label' and 'score' keys.

        Raises:
            ValueError: If the input text is empty or None.
        """

        if not text:
            self.logger.exception("Input text cannot be empty or None")
            raise ValueError("Input text cannot be empty or None")

        try:
            if isinstance(text, str):
                return self._process_single_text(text)
            elif isinstance(text, list):
                return [self._process_single_text(t) for t in text]
            else:
                raise ValueError("Input must be a string or a list of strings")
        except Exception as e:
            self.logger.exception(f"Error during sentiment analysis: {str(e)}")
            raise

    def _process_single_text(self, text: str) -> Dict:
        """
        Process a single text for sentiment analysis.

        Args:
            text (str): The text to analyze.

        Returns:
            Dict: A dictionary containing the sentiment analysis result.

        Raises:
            ValueError: If the input text is too long for the model.
        """
        # Check if the text is too long for the model
        if len(self.tokenizer.encode(text)) > self.model.config.max_position_embeddings:
            self.logger.exception(
                f"Input text is too long. Maximum length is {self.model.config.max_position_embeddings} tokens.")
            raise ValueError(
                f"Input text is too long. Maximum length is {self.model.config.max_position_embeddings} tokens.")
        result = self.nlp(text)[0]
        json_result = {
            'text': text,
            'sentiment': result['label'],
            'confidence': result['score']
        }
        self.logger.debug(f'result: {json_result}')
        return json_result