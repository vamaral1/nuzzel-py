"""
Data Models

This module defines the data models used throughout the Twitter digest system.
These models provide type safety, validation, and consistent interfaces for
tweet data from the Twitter API through to LLM analysis.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class Tweet:
    """Tweet object"""
    # Tweet ID
    id: str
    # Tweet author id
    author_id: str
    # Tweet author username
    author_username: str
    # Total number of likes
    like_count: int
    # Total number of retweets or quotes
    retweet_count: int
    # Total number of replies
    reply_count: int
    # Normalized like count
    normalized_like_count: float
    # Normalized retweets or quotes count
    normalized_retweet_count: float
    # Normalized reply count
    normalized_reply_count: float
    # Tweet text
    text: str
    # List of {url: str, title: str, description: str}
    urls: List[Dict[str, str]]
    # List of {type: str, description: str}
    media: List[Dict[str, str]]
    # Set of annotation strings (topics and entities)
    annotations: Set[str] = field(default_factory=set)


@dataclass
class ProcessedData:
    """
    Processed tweet data in a simplified format.

    Contains a list of tweets and computed statistics.
    """
    # List of all processed tweets
    tweets: Dict[str, Tweet] = field(default_factory=dict)

    # User history converted to our models
    user_liked_content: Dict[str, Tweet] = field(default_factory=dict)
    user_posted_content: Dict[str, Tweet] = field(default_factory=dict)

    # Basic stats
    total_tweets: int = 0
    unique_accounts: int = 0
    total_links: int = 0
