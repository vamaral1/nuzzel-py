"""
Themes and Insights Generator

This module generates high-level themes and insights from tweets using LLM.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from nuzzel.llm_client import create_llm_client, LLMError
from nuzzel.models import Tweet
from nuzzel.utils.json_utils import parse_llm_json_response

# Configure logging
logger = logging.getLogger(__name__)


def generate_themes_and_insights(
    tweets: Dict[str, Tweet],
    llm_client=None
) -> Dict[str, Any]:
    """
    Generate themes and insights from tweets using LLM.

    Args:
        tweets: Dictionary of tweet_id -> Tweet objects
        time_window_days: Time window in days
        llm_client: Optional LLM client (creates one if not provided)

    Returns:
        Dictionary with summary and themes, or error message
    """
    if not tweets:
        return {"error": "No tweets to analyze"}

    try:
        llm = llm_client or create_llm_client()

        # Load prompt template
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "themes_and_insights.md"
        prompt_template = prompt_path.read_text()

        # Prepare tweet data for LLM (only text, urls, media, annotations)
        tweets_for_llm = []
        for tweet_id, tweet in tweets.items():
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
            tweets_json=json.dumps(tweets_for_llm, indent=2)
        )

        # Call LLM
        response = llm.generate_text(prompt, system_message=None)

        # Parse response
        result = _parse_themes_response(response)
        return result

    except LLMError as e:
        logger.error("LLM error generating themes: %s", e, exc_info=True)
        return {"error": "Error getting top themes"}
    except Exception as e:
        logger.error("Error generating themes: %s", e, exc_info=True)
        return {"error": "Error getting top themes"}


def _parse_themes_response(response: str) -> Dict[str, Any]:
    """Parse LLM response into themes structure"""
    default_result = {
        "summary": "Error parsing themes response",
        "themes": []
    }

    try:
        result = parse_llm_json_response(response, default=default_result)

        # LLM may return JSON that parses to a list (e.g. array of themes); require a dict
        if not isinstance(result, dict):
            return default_result

        # Validate structure
        if "summary" not in result:
            result["summary"] = "Unable to generate summary"
        if "themes" not in result:
            result["themes"] = []

        return result

    except ValueError as e:
        logger.error("Error parsing themes response: %s", e, exc_info=True)
        logger.debug("Raw response: %s", response)
        return default_result
