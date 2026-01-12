"""
Engagement Predictor

This module predicts which tweets a user is most likely to engage with
based on their past liking and posting behavior.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from nuzzel.llm_client import create_llm_client, LLMError
from nuzzel.models import Tweet
from nuzzel.utils.json_utils import parse_llm_json_response

# Configure logging
logger = logging.getLogger(__name__)


class EngagementPredictor:
    """Predicts user engagement with tweets using LLM analysis of past behavior"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client or create_llm_client()

    def predict_engagement(self,
                          timeline_tweets: Dict[str, Tweet],
                          liked_tweets: Dict[str, Tweet],
                          written_tweets: Dict[str, Tweet]) -> Dict[str, Any]:
        """
        Predict which tweets the user is most likely to like or retweet.

        Args:
            timeline_tweets: Dictionary of tweet_id -> Tweet objects from current timeline
            liked_tweets: Dictionary of tweet_id -> Tweet objects (user's recently liked tweets)
            written_tweets: Dictionary of tweet_id -> Tweet objects (user's recent tweets)

        Returns:
            Dictionary with predictions and explanations, or error message
        """
        if not timeline_tweets:
            return {"error": "No timeline tweets to analyze"}

        if not liked_tweets and not written_tweets:
            return {"error": "No user history available"}

        # Filter out user's own tweets from timeline tweets
        # User's tweets should not be considered for "Most Likely to Retweet"
        user_tweet_ids = set(written_tweets.keys())
        user_author_id = None
        if written_tweets:
            # Get the user's author_id from their posted tweets (all should have the same author_id)
            first_user_tweet = next(iter(written_tweets.values()))
            user_author_id = first_user_tweet.author_id

        # Filter timeline to exclude user's own tweets
        filtered_timeline_tweets = {}
        excluded_count = 0
        for tweet_id, tweet in timeline_tweets.items():
            # Exclude if tweet_id matches a user tweet, or if author_id matches user's author_id
            if tweet_id in user_tweet_ids or tweet.author_id == user_author_id:
                excluded_count += 1
            else:
                filtered_timeline_tweets[tweet_id] = tweet

        if excluded_count > 0:
            logger.debug("Filtered out %d user's own tweets from timeline for engagement prediction", excluded_count)

        if not filtered_timeline_tweets:
            return {"error": "No timeline tweets to analyze (all are user's own tweets)"}

        try:
            # Load prompt template
            prompt_path = Path(__file__).parent.parent.parent / "prompts" / "engagement_prediction.md"
            prompt_template = prompt_path.read_text()

            # Prepare tweet data for LLM (only text, urls, media, annotations)
            def prepare_tweets_for_llm(tweets_dict: Dict[str, Tweet]) -> List[Dict[str, Any]]:
                result = []
                for tweet_id, tweet in tweets_dict.items():
                    # Convert set to list for JSON serialization
                    result.append({
                        "tweet_id": tweet_id,
                        "text": tweet.text,
                        "urls": tweet.urls,
                        "media": tweet.media,
                        "annotations": list(tweet.annotations)  # Convert set to list for JSON serialization
                    })
                return result

            liked_tweets_data = prepare_tweets_for_llm(liked_tweets)
            posted_tweets_data = prepare_tweets_for_llm(written_tweets)
            current_tweets_data = prepare_tweets_for_llm(filtered_timeline_tweets)

            # Format prompt
            prompt = prompt_template.format(
                liked_count=len(liked_tweets),
                posted_count=len(written_tweets),
                liked_tweets=json.dumps(liked_tweets_data, indent=2),
                posted_tweets=json.dumps(posted_tweets_data, indent=2),
                current_tweets=json.dumps(current_tweets_data, indent=2)
            )

            # Call LLM
            response = self.llm_client.generate_text(prompt, system_message=None)

            # Parse response
            return self._parse_prediction_response(response)

        except LLMError as e:
            logger.error("LLM error predicting engagement: %s", e, exc_info=True)
            return {"error": "Error predicting which tweet you will like or retweet"}
        except Exception as e:
            logger.error("Error predicting engagement: %s", e, exc_info=True)
            return {"error": "Error predicting which tweet you will like or retweet"}

    def _parse_prediction_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into prediction structure"""
        default_result = {
            "error": "Error parsing prediction response",
            "most_likely_to_like": {"tweet_id": "", "explanation": ""},
            "most_likely_to_retweet": {"tweet_id": "", "explanation": ""}
        }
        
        try:
            result = parse_llm_json_response(response, default=default_result)

            # Validate structure
            if "most_likely_to_like" not in result:
                result["most_likely_to_like"] = {"tweet_id": "", "explanation": ""}
            if "most_likely_to_retweet" not in result:
                result["most_likely_to_retweet"] = {"tweet_id": "", "explanation": ""}

            return result

        except ValueError as e:
            logger.error("Error parsing prediction response: %s", e, exc_info=True)
            logger.debug("Raw response: %s", response)
            return default_result


def predict_user_engagement(
    timeline_tweets: Dict[str, Tweet],
    liked_tweets: Dict[str, Tweet],
    posted_tweets: Dict[str, Tweet]
) -> Dict[str, Any]:
    """
    Predict user engagement and enrich predictions with full tweet objects.

    Args:
        timeline_tweets: Dictionary of tweet_id -> Tweet objects from current timeline
        liked_tweets: Dictionary of tweet_id -> Tweet objects (user's liked tweets)
        posted_tweets: Dictionary of tweet_id -> Tweet objects (user's posted tweets)

    Returns:
        Enriched prediction results with full tweet objects
    """
    predictor = EngagementPredictor()
    predictions = predictor.predict_engagement(timeline_tweets, liked_tweets, posted_tweets)

    # Enrich predictions with full tweet objects
    return enrich_engagement_predictions(predictions, timeline_tweets)


def enrich_engagement_predictions(
    predictions: Dict[str, Any],
    tweets: Dict[str, Tweet]
) -> Dict[str, Any]:
    """
    Enrich engagement predictions with full tweet objects.

    Args:
        predictions: Raw predictions with tweet IDs
        tweets: Dictionary of tweet_id -> Tweet objects

    Returns:
        Enriched predictions with full tweet objects
    """
    enriched = {}

    # Enrich most_likely_to_like
    if "most_likely_to_like" in predictions:
        like_pred = predictions["most_likely_to_like"]
        tweet_id = like_pred.get("tweet_id", "")
        if tweet_id and tweet_id in tweets:
            enriched["most_likely_to_like"] = {
                "tweet_id": tweet_id,
                "tweet": tweets[tweet_id],
                "explanation": like_pred.get("explanation", "")
            }
        else:
            # Keep original if tweet not found
            enriched["most_likely_to_like"] = like_pred

    # Enrich most_likely_to_retweet
    if "most_likely_to_retweet" in predictions:
        retweet_pred = predictions["most_likely_to_retweet"]
        tweet_id = retweet_pred.get("tweet_id", "")
        if tweet_id and tweet_id in tweets:
            enriched["most_likely_to_retweet"] = {
                "tweet_id": tweet_id,
                "tweet": tweets[tweet_id],
                "explanation": retweet_pred.get("explanation", "")
            }
        else:
            # Keep original if tweet not found
            enriched["most_likely_to_retweet"] = retweet_pred

    # Preserve any other fields (like "error")
    for key, value in predictions.items():
        if key not in ["most_likely_to_like", "most_likely_to_retweet"]:
            enriched[key] = value

    return enriched
