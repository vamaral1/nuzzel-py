"""
List Membership Processor

This module handles loading and processing of cached Twitter list memberships.
"""

import csv
import logging
from pathlib import Path
from typing import Dict, Set, List, Optional, Any
from nuzzel.models import Tweet

logger = logging.getLogger(__name__)

# Global cache for list memberships data
_list_memberships_cache: Optional[Dict[str, Dict[str, Any]]] = None


def _load_list_memberships() -> Dict[str, Dict[str, Any]]:
    """
    Load list memberships from cached CSV file and return structured data.

    Returns:
        Dictionary with 'list_names' (list_id -> list_name) and 'user_ids' (list_id -> set of user_ids)
    """
    global _list_memberships_cache

    if _list_memberships_cache is not None:
        return _list_memberships_cache

    csv_path = Path(__file__).parent.parent.parent / "data" / "list_memberships.csv"

    if not csv_path.exists():
        logger.warning("List memberships CSV not found: %s", csv_path)
        _list_memberships_cache = {'list_names': {}, 'user_ids': {}}
        return _list_memberships_cache

    list_names: Dict[str, str] = {}
    user_ids: Dict[str, Set[str]] = {}

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                list_id = row.get('list_id', '').strip()
                list_name = row.get('list_name', '').strip()
                user_id = row.get('user_id', '').strip()

                if list_id:
                    # Build list name mapping
                    if list_name and list_id not in list_names:
                        list_names[list_id] = list_name

                    # Build user IDs mapping
                    if user_id:
                        if list_id not in user_ids:
                            user_ids[list_id] = set()
                        user_ids[list_id].add(user_id)

        _list_memberships_cache = {'list_names': list_names, 'user_ids': user_ids}
        total_memberships = sum(len(user_set) for user_set in user_ids.values())
        logger.info("Loaded %d list memberships with %d lists", total_memberships, len(list_names))
        return _list_memberships_cache

    except Exception as e:
        logger.error("Error loading list memberships: %s", e, exc_info=True)
        _list_memberships_cache = {'list_names': {}, 'user_ids': {}}
        return _list_memberships_cache


def build_list_id_to_name_mapping() -> Dict[str, str]:
    """
    Load list memberships from cached CSV file.

    Returns:
        Dictionary mapping list_id -> list_name, or empty dict if file doesn't exist
    """
    memberships = _load_list_memberships()
    return memberships['list_names']


def get_list_user_ids(list_id: str) -> Set[str]:
    """
    Get set of user IDs for a specific list.

    Args:
        list_id: List ID

    Returns:
        Set of user IDs in the list
    """
    memberships = _load_list_memberships()
    return memberships['user_ids'].get(list_id, set())



def filter_tweets_by_list(
    tweets: Dict[str, Tweet],
    list_id: str,
) -> List[str]:
    """
    Filter tweets to only include those from users in a specific list.

    Args:
        tweets: Dictionary of tweet_id -> Tweet objects
        list_id: List ID to filter by

    Returns:
        List of tweet IDs that match the list
    """
    # Get user IDs for this list
    list_user_ids = get_list_user_ids(list_id)

    if not list_user_ids:
        logger.warning("No users found for list %s", list_id)
        return []

    # Filter tweets
    matching_tweet_ids = []
    for tweet_id, tweet in tweets.items():
        if tweet.author_id in list_user_ids:
            matching_tweet_ids.append(tweet_id)

    logger.info("Filtered %d tweets for list %s", len(matching_tweet_ids), list_id)
    return matching_tweet_ids
