"""
Digest Generator

This module generates the complete email digest content, including LLM-powered
themes and insights generation.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from nuzzel.llm_client import create_llm_client
from nuzzel.generators.template_renderer import render_digest_email
from nuzzel.generators.themes_and_insights import generate_themes_and_insights
from nuzzel.processors.link_extractor import extract_shared_links
from nuzzel.processors.categorizer import categorize_tweets_llm
from nuzzel.processors.engagement_predictor import predict_user_engagement
from nuzzel.processors.tweet_aggregator import (
    calculate_top_engagement,
    aggregate_context_annotations
)
from nuzzel.constants import INTERESTS
from nuzzel.models import ProcessedData

# Configure logging
logger = logging.getLogger(__name__)


class DigestGenerator:
    """Generates complete email digest content"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client or create_llm_client()

    def generate_digest(self,
                       processed_data: ProcessedData,
                       time_window_days: int = 1) -> Dict[str, Any]:
        """
        Generate complete digest with LLM-powered content.

        Args:
            processed_data: ProcessedData object from TweetProcessor
            time_window_days: Time window in days for the digest

        Returns:
            Complete digest data ready for email rendering
        """
        logger.info("Generating digest for %d tweets", len(processed_data.tweets))

        digest_data = {}

        # Section 1: Top Highlights (Themes and Insights)
        logger.info("Generating themes and insights...")
        try:
            themes_data = generate_themes_and_insights(
                processed_data.tweets,
                self.llm_client
            )
            if "error" in themes_data:
                digest_data["themes_summary"] = {
                    "error": themes_data["error"]
                }
            else:
                digest_data["themes_summary"] = themes_data
        except Exception as e:
            logger.error("Error generating themes: %s", e, exc_info=True)
            digest_data["themes_summary"] = {"error": "Error getting top themes"}

        # Section 2: Shared Links & Articles
        logger.info("Extracting shared links...")
        try:
            links_data = extract_shared_links(processed_data.tweets)
            digest_data["shared_links"] = links_data
        except Exception as e:
            logger.error("Error extracting links: %s", e, exc_info=True)
            error_msg = str(e)[:250]  # First 250 characters
            digest_data["shared_links"] = {
                "error": f"Error filtering links and articles: {error_msg}"
            }

        # Section 3: Top Engagement Tweets
        logger.info("Calculating top engagement tweets...")
        try:
            engagement_data = calculate_top_engagement(processed_data)
            digest_data.update(engagement_data)
        except Exception as e:
            logger.error("Error calculating engagement: %s", e, exc_info=True)
            digest_data["top_liked_tweets"] = []  # type: ignore
            digest_data["top_retweeted_tweets"] = []  # type: ignore
            digest_data["list_engagement"] = {}

        # Section 4: Tweets by Interest Category
        logger.info("Categorizing tweets by interests...")
        try:
            digest_data["interest_tweets"] = categorize_tweets_llm(
                processed_data.tweets,
                interest_categories=INTERESTS,
                threshold=0.5,
                max_tweets=5
            )
        except Exception as e:
            logger.error("Error categorizing tweets: %s", e, exc_info=True)
            digest_data["interest_tweets"] = {"error": "Error finding tweets for interests"}

        # Section 5: Top Discovered Categories (Context Annotations)
        logger.info("Aggregating context annotations...")
        try:
            context_categories = aggregate_context_annotations(processed_data.tweets)
            digest_data["context_categories"] = context_categories
        except Exception as e:
            logger.error("Error aggregating annotations: %s", e, exc_info=True)
            digest_data["context_categories"] = {"error": "Error aggregating annotations"}

        # Section 6: Most Likely to Like and Retweet
        logger.info("Predicting user engagement...")
        try:
            if processed_data.user_posted_content:
                digest_data["engagement_predictions"] = predict_user_engagement(
                    processed_data.tweets,
                    processed_data.user_liked_content,
                    processed_data.user_posted_content
                )
            else:
                digest_data["engagement_predictions"] = {
                    "skip": "No user tweet history available"
                }
        except Exception as e:
            logger.error("Error predicting engagement: %s", e, exc_info=True)
            digest_data["engagement_predictions"] = {
                "error": "Error predicting which tweet you will like or retweet"
            }

        # Stats
        digest_data["stats"] = {
            "total_tweets": processed_data.total_tweets,
            "unique_accounts": processed_data.unique_accounts,
            "total_links": processed_data.total_links
        }

        # Generate subject line
        subject = self._generate_subject_line(digest_data)

        # Render HTML
        html_content = render_digest_email(digest_data, time_window_days)

        return {
            "subject": subject,
            "html_content": html_content
        }

    def _generate_subject_line(self, digest_data: Dict[str, Any]) -> str:
        """
        Generate email subject line based on digest content.

        Args:
            digest_data: Complete digest data

        Returns:
            Subject line string
        """
        current_date = datetime.now().strftime("%B %d, %Y")

        # Try to extract a key theme from themes_summary
        key_theme = None
        themes_summary = digest_data.get("themes_summary", {})
        if "error" not in themes_summary and "themes" in themes_summary:
            themes = themes_summary.get("themes", [])
            if themes:
                # Handle both formats: list of strings or list of dicts
                first_theme = themes[0]
                if isinstance(first_theme, dict):
                    key_theme = first_theme.get("theme", "")
                elif isinstance(first_theme, str):
                    key_theme = first_theme

        if key_theme:
            return f"Your Twitter Digest: {current_date} - {key_theme}"
        else:
            return f"Your Twitter Digest: {current_date}"


def generate_email_digest(processed_data: ProcessedData,
                         time_window_days: int = 1) -> Dict[str, Any]:
    """
    Convenience function to generate complete email digest.

    Args:
        processed_data: ProcessedData from main processing pipeline
        time_window_days: Time window in days

    Returns:
        Complete digest with subject and HTML content
    """
    generator = DigestGenerator()
    return generator.generate_digest(processed_data, time_window_days)
