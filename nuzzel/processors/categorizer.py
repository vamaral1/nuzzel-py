"""
Tweet Categorizer

This module provides LLM-based categorization of tweets into user-defined interest categories.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import random

from nuzzel.llm_client import create_llm_client, LLMError
from nuzzel.constants import INTERESTS
from nuzzel.models import Tweet
from nuzzel.utils.json_utils import parse_llm_json_response

# Configure logging
logger = logging.getLogger(__name__)


class TweetCategorizer:
    """Categorizes tweets into interest categories using LLM"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client or create_llm_client()
        self.interest_categories = INTERESTS + ["other"]  # Add 'other' as fallback

    def categorize_tweets(
        self, tweets: Dict[str, Tweet]
    ) -> Dict[str, Dict[str, float]]:
        """
        Categorize tweets into interest categories using LLM with confidence scores.

        Args:
            tweets: Dictionary of tweet_id -> Tweet objects

        Returns:
            Dictionary mapping tweet_id to category confidence scores
        """
        if not tweets:
            return {}

        try:
            # Load prompt template
            prompt_path = Path(__file__).parent.parent.parent / "prompts" / "interest_categorization.md"
            prompt_template = prompt_path.read_text()

            # Prepare tweet data for LLM (only text, urls, media, annotations)
            tweets_for_llm = []
            for tweet_id, tweet in tweets.items():
                # Convert set to list for JSON serialization
                tweet_data = {
                    "tweet_id": tweet_id,
                    "text": tweet.text,
                    "urls": tweet.urls,
                    "media": tweet.media,
                    "annotations": list(tweet.annotations)  # Convert set to list for JSON serialization
                }
                tweets_for_llm.append(tweet_data)

            # Format prompt
            prompt = prompt_template.format(
                interest_categories="\n".join(f"- {cat}" for cat in self.interest_categories),
                tweets_json=json.dumps(tweets_for_llm, indent=2)
            )

            # Call LLM
            response = self.llm_client.generate_text(prompt, system_message=None)

            # Parse response
            return self._parse_categorization_response(response)

        except LLMError as e:
            logger.error("LLM error categorizing tweets: %s", e, exc_info=True)
            return {}
        except Exception as e:
            logger.error("Error categorizing tweets: %s", e, exc_info=True)
            return {}

    def _parse_categorization_response(
        self, response: str
    ) -> Dict[str, Dict[str, float]]:
        """
        Parse the JSON response from LLM.

        Args:
            response: Raw LLM response

        Returns:
            Dictionary mapping tweet_id to category confidence scores
        """
        return parse_llm_json_response(response, default={})


def get_tweets_by_category(
    tweets: Dict[str, Tweet],
    categorizations: Dict[str, Dict[str, float]],
    category: str,
    threshold: float = 0.5,
    max_tweets: int = 5
) -> List[str]:
    """
    Get tweet IDs for a specific category, randomly selecting up to max_tweets.

    Args:
        tweets: Dictionary of tweet_id -> Tweet objects
        categorizations: Dictionary mapping tweet_id to category scores
        category: Category name to filter by
        threshold: Minimum confidence score (default 0.5)
        max_tweets: Maximum number of tweets to return

    Returns:
        List of tweet IDs
    """
    matching_tweets = []

    for tweet_id, scores in categorizations.items():
        if tweet_id in tweets:
            score = scores.get(category.lower(), 0.0)
            if score >= threshold:
                matching_tweets.append(tweet_id)

    # Randomly select up to max_tweets
    if len(matching_tweets) > max_tweets:
        return random.sample(matching_tweets, max_tweets)
    return matching_tweets


def categorize_tweets_llm(
    tweets: Dict[str, Tweet],
    interest_categories: Optional[List[str]] = None,
    threshold: float = 0.5,
    max_tweets: int = 5
) -> Dict[str, Any]:
    """
    Categorize tweets with confidence scores and optionally build interest tweets by category.

    Args:
        tweets: Dictionary of tweet_id -> Tweet objects
        interest_categories: Optional list of interest category names. If provided, returns
            interest_tweets dictionary. If None, returns only categorizations.
        threshold: Minimum confidence score (default 0.5)
        max_tweets: Maximum number of tweets per category (default 5)

    Returns:
        If interest_categories is provided: Dictionary mapping category name to list of Tweet objects
        If interest_categories is None: Dictionary mapping tweet_id to category confidence scores
    """
    categorizer = TweetCategorizer()
    categorizations = categorizer.categorize_tweets(tweets)

    if interest_categories is None:
        return categorizations

    # Build interest tweets by category
    interest_tweets = build_interest_tweets_by_category(
        tweets,
        categorizations,
        interest_categories,
        threshold=threshold,
        max_tweets=max_tweets
    )

    return interest_tweets


def build_interest_tweets_by_category(
    tweets: Dict[str, Tweet],
    categorizations: Dict[str, Dict[str, float]],
    interest_categories: List[str],
    threshold: float = 0.5,
    max_tweets: int = 5
) -> Dict[str, List[Tweet]]:
    """
    Build a dictionary of interest categories to lists of Tweet objects.

    Args:
        tweets: Dictionary of tweet_id -> Tweet objects
        categorizations: Dictionary mapping tweet_id to category confidence scores
        interest_categories: List of interest category names
        threshold: Minimum confidence score (default 0.5)
        max_tweets: Maximum number of tweets per category (default 5)

    Returns:
        Dictionary mapping category name to list of Tweet objects
    """
    interest_tweets = {}
    for category in interest_categories:
        tweet_ids = get_tweets_by_category(
            tweets,
            categorizations,
            category,
            threshold=threshold,
            max_tweets=max_tweets
        )
        interest_tweets[category] = [
            tweets[tid] for tid in tweet_ids if tid in tweets
        ]
    return interest_tweets
