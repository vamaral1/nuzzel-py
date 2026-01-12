"""
Tweet Aggregator

This module provides functions for aggregating and ranking tweets by various metrics,
including engagement scores, context annotations, and list-based filtering.
"""

import logging
from typing import Dict, Any
from collections import defaultdict

from nuzzel.models import ProcessedData, Tweet
from nuzzel.processors.list_processor import build_list_id_to_name_mapping, filter_tweets_by_list

# Configure logging
logger = logging.getLogger(__name__)


def calculate_top_engagement(processed_data: ProcessedData, top_k: int = 5) -> Dict[str, Any]:
    """
    Calculate top engagement tweets overall and by list.

    Args:
        processed_data: ProcessedData object with tweets
        top_k: Number of top tweets to return

    Returns:
        Dictionary with top_liked_tweets, top_retweeted_tweets, and list_engagement
    """
    # Top top_k liked (overall)
    top_liked = sorted(
        processed_data.tweets.values(),
        key=lambda t: t.normalized_like_count,
        reverse=True
    )[:top_k]

    # Top top_k retweeted (overall)
    top_retweeted = sorted(
        processed_data.tweets.values(),
        key=lambda t: t.normalized_retweet_count,
        reverse=True
    )[:top_k]

    result: Dict[str, Any] = {
        "top_liked_tweets": top_liked,
        "top_retweeted_tweets": top_retweeted,
        "list_engagement": {}
    }

    # Get list memberships
    try:
        lists = build_list_id_to_name_mapping()
        if lists:
            # Group tweets by list
            for list_id, list_name in lists.items():
                list_tweet_ids = filter_tweets_by_list(
                    processed_data.tweets,
                    list_id,
                )

                if list_tweet_ids:
                    tweet_objs_gen = (
                        processed_data.tweets[tid]
                        for tid in list_tweet_ids
                    )

                    top_liked_list = sorted(
                        tweet_objs_gen,
                        key=lambda t: t.normalized_like_count,
                        reverse=True
                    )[:top_k]

                    # Recreate generator for retweeted (generators are consumed)
                    tweet_objs_gen_retweet = (
                        processed_data.tweets[tid]
                        for tid in list_tweet_ids
                    )

                    top_retweeted_list = sorted(
                        tweet_objs_gen_retweet,
                        key=lambda t: t.normalized_retweet_count,
                        reverse=True
                    )[:top_k]

                    if list_name:
                        result["list_engagement"][list_name] = {
                            "top_liked": top_liked_list,
                            "top_retweeted": top_retweeted_list
                        }
    except Exception as e:
        logger.warning("Error processing list engagement: %s", e)

    return result


def aggregate_context_annotations(tweets: Dict[str, Tweet], top_k: int = 5) -> Dict[str, Any]:
    """
    Aggregate context annotations by counting occurrences.

    Args:
        tweets: Dictionary of tweet_id -> Tweet objects
        top_k: Number of top categories to return

    Returns:
        Dictionary with top_categories containing annotation statistics
    """
    annotation_counts: Dict[str, int] = defaultdict(int)

    for tweet in tweets.values():
        for ann in tweet.annotations:
            annotation_counts[ann] += 1

    # Sort annotations by count and take top_k
    sorted_annotations = sorted(
        annotation_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]

    top_categories = [
        {
            "name": name,
            "count": count
        }
        for name, count in sorted_annotations
    ]

    return {
        "top_categories": top_categories
    }
