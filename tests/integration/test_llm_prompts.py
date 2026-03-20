"""
Integration tests for LLM prompt quality assessment.

These tests call real LLM APIs with mock Twitter data and save the raw responses
to files for manual quality inspection. Requires valid LLM API keys in environment.
"""

import json
import os
import logging
from pathlib import Path
from datetime import datetime

import pytest
import pytest_asyncio

from nuzzel.twitter_client import create_twitter_client
from nuzzel.processors.tweet_processor import process_data_for_digest
from nuzzel.generators.themes_and_insights import generate_themes_and_insights
from nuzzel.processors.categorizer import categorize_tweets_llm, TweetCategorizer
from nuzzel.processors.engagement_predictor import EngagementPredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestLLMPrompts:
    """Test LLM prompts with mock data and save responses for quality inspection"""

    @pytest_asyncio.fixture(scope="class", loop_scope="class")
    async def mock_twitter_data(self):
        """Load mock Twitter data and process it into Tweet objects"""
        # Force mock client
        original_env = os.environ.get('USE_MOCK')
        os.environ['USE_MOCK'] = 'true'

        try:
            # Get mock client
            twitter_client = create_twitter_client()

            # Fetch mock data - await async methods
            timeline_data = await twitter_client.get_user_timeline(
                start_time=datetime(2024, 1, 1),
                max_pages=1
            )
            liked_tweets = await twitter_client.get_user_liked_tweets(max_results=10)
            posted_tweets = await twitter_client.get_user_tweets(max_results=10)

            # Process into Tweet objects
            processed_data = process_data_for_digest(
                timeline_data, liked_tweets, posted_tweets
            )

            return processed_data

        finally:
            # Restore original environment
            if original_env is not None:
                os.environ['USE_MOCK'] = original_env
            else:
                os.environ.pop('USE_MOCK', None)

    def save_response_to_file(self, response: dict, filename: str):
        """Save LLM response (already a dict) to JSON file for inspection"""
        output_dir = Path(__file__).parent.parent / "output" / "llm"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)

        logger.info("Saved LLM response to %s", output_file)

    @pytest.mark.integration
    def test_themes_and_insights_prompt(self, mock_twitter_data):
        """Test themes and insights generation prompt"""
        logger.info("Testing themes and insights generation...")

        try:
            response = generate_themes_and_insights(mock_twitter_data.tweets)
            self.save_response_to_file(response, "themes_and_insights_response.json")

            # Basic structure validation
            assert isinstance(response, dict)
            if 'error' not in response:
                assert 'highlights' in response
                assert 'themes' in response
                assert isinstance(response['highlights'], list)
                assert isinstance(response['themes'], list)

            logger.info("Themes and insights test completed successfully")

        except Exception as e:
            logger.error("Themes and insights test failed: %s", e, exc_info=True)
            self.save_response_to_file({'error': str(e)}, "themes_and_insights_error.json")
            raise

    @pytest.mark.integration
    def test_interest_categorization_prompt(self, mock_twitter_data):
        """Test interest categorization prompt - saves raw LLM response (confidence scores only)"""
        logger.info("Testing interest categorization...")

        try:
            # Raw LLM response is just confidence scores (already a dict)
            categorizer = TweetCategorizer()
            response = categorizer.categorize_tweets(mock_twitter_data.tweets)
            self.save_response_to_file(response, "interest_categorization_response.json")

            # Basic structure validation
            assert isinstance(response, dict)
            for tweet_id, scores in response.items():
                assert isinstance(scores, dict)
                assert tweet_id in mock_twitter_data.tweets

            logger.info("Interest categorization test completed successfully")

        except Exception as e:
            logger.error("Interest categorization test failed: %s", e, exc_info=True)
            self.save_response_to_file({'error': str(e)}, "interest_categorization_error.json")
            raise

    @pytest.mark.integration
    def test_engagement_prediction_prompt(self, mock_twitter_data):
        """Test engagement prediction prompt"""
        logger.info("Testing engagement prediction...")

        try:
            # Raw LLM response is just tweet_id and explanation (already a dict)
            predictor = EngagementPredictor()
            response = predictor.predict_engagement(
                timeline_tweets=mock_twitter_data.tweets,
                liked_tweets=mock_twitter_data.user_liked_content,
                written_tweets=mock_twitter_data.user_posted_content
            )
            self.save_response_to_file(response, "engagement_prediction_response.json")

            # Basic structure validation
            assert isinstance(response, dict)
            if 'error' not in response:
                assert 'most_likely_to_like' in response
                assert 'most_likely_to_retweet' in response

            logger.info("Engagement prediction test completed successfully")

        except Exception as e:
            logger.error("Engagement prediction test failed: %s", e, exc_info=True)
            self.save_response_to_file({'error': str(e)}, "engagement_prediction_error.json")
            raise

    @pytest.mark.integration
    def test_categorization_confidence_scores(self, mock_twitter_data):
        """Test categorization confidence scores (without interest filtering)"""
        logger.info("Testing categorization confidence scores...")

        try:
            response = categorize_tweets_llm(
                tweets=mock_twitter_data.tweets,
                interest_categories=None  # Get raw confidence scores
            )
            self.save_response_to_file(response, "categorization_confidence_response.json")

            # Basic structure validation
            assert isinstance(response, dict)
            # Should map tweet_id to category confidence scores
            for tweet_id, scores in response.items():
                assert isinstance(scores, dict)
                assert tweet_id in mock_twitter_data.tweets

            logger.info("Categorization confidence test completed successfully")

        except Exception as e:
            logger.error("Categorization confidence test failed: %s", e, exc_info=True)
            self.save_response_to_file({'error': str(e)}, "categorization_confidence_error.json")
            raise


if __name__ == "__main__":
    # Allow running individual tests for manual inspection
    import sys

    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        print(f"Running LLM integration test: {test_name}")

        # Set up mock environment
        os.environ['USE_MOCK'] = 'true'

        test_instance = TestLLMPrompts()

        # Load mock data
        mock_data = test_instance.mock_twitter_data()

        # Run specific test
        if test_name == "themes":
            test_instance.test_themes_and_insights_prompt(mock_data)
        elif test_name == "categorization":
            test_instance.test_interest_categorization_prompt(mock_data)
        elif test_name == "engagement":
            test_instance.test_engagement_prediction_prompt(mock_data)
        elif test_name == "confidence":
            test_instance.test_categorization_confidence_scores(mock_data)
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: themes, categorization, engagement, confidence")
    else:
        print("Usage: python test_llm_prompts.py <test_name>")
        print("Available tests: themes, categorization, engagement, confidence")
        print("Example: python test_llm_prompts.py themes")
