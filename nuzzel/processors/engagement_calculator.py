"""
Engagement Calculator

This module provides functions for calculating normalized engagement scores
to ensure fair comparison across accounts of different sizes.
"""

import math


def calculate_normalized_engagement(
    engagement_count: int, author_followers: int
) -> float:
    """
    Calculate normalized engagement score for a tweet.

    Formula: normalized_score = engagement_count / log(max(follower_count, 1))
    This prevents large accounts from dominating while still giving credit to quality content.

    Args:
        engagement_count: The non-normalized engagement count (likes, retweets, or replies)
        author_followers: Number of followers for the tweet author

    Returns:
        Normalized engagement score
    """

    # Apply logarithmic normalization to prevent large accounts from dominating
    # Using log(max(followers, 2)) to handle accounts with 0-1 followers
    # This ensures we never divide by zero or very small numbers
    if author_followers <= 1:
        normalized_score = engagement_count + 0.0000
    else:
        # Use log base 10 for normalization
        normalized_score = engagement_count / math.log10(author_followers)

    return normalized_score
