"""Data extraction helpers for Twitter GraphQL responses"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def extract_tweets_from_graphql_response(response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract tweets from Twitter GraphQL response.

    Twitter's internal API uses GraphQL with nested structures. This function
    extracts tweet data from various possible response formats.

    Args:
        response_data: Raw GraphQL response dictionary

    Returns:
        List of tweet dictionaries in standard format
    """
    tweets = []

    # Try to find tweets in various possible locations
    # User timeline path
    instructions = response_data.get("data", {}).get("user", {}).get("result", {})\
        .get("timeline_v2", {}).get("timeline", {}).get("instructions", [])

    if not instructions:
        # Home timeline path
        instructions = response_data.get("data", {}).get("home", {})\
            .get("home_timeline_urt", {}).get("instructions", [])

    if not instructions:
        # User timeline fallback (no v2)
        instructions = response_data.get("data", {}).get("user", {}).get("result", {})\
            .get("timeline", {}).get("timeline", {}).get("instructions", [])

    if not instructions:
        # List timeline path
        instructions = response_data.get("data", {}).get("list", {}).get("tweets_timeline", {})\
            .get("timeline", {}).get("instructions", [])

    # Extract entries from instructions
    entries = []
    for instruction in instructions:
        if instruction.get("type") == "TimelineAddEntries":
            entries.extend(instruction.get("entries", []))
        elif instruction.get("type") == "TimelineReplaceEntry":
            entries.append(instruction.get("entry", {}))
        elif instruction.get("type") == "TimelineAddToModule":
            # Some tweets are inside modules
            module_items = instruction.get("moduleItems", [])
            for item in module_items:
                entries.append(item.get("item", {}))

    # Process entries to extract tweets
    for entry in entries:
        content = entry.get("content", {})

        # Determine the item content location
        item_content = None
        if content.get("entryType") == "TimelineTimelineItem":
            item_content = content.get("itemContent", {})
        elif content.get("itemContent"): # For TimelineAddToModule items
            item_content = content.get("itemContent", {})

        if item_content:
            tweet_result = item_content.get("tweet_results", {}).get("result", {})
            if tweet_result:
                tweet = _map_tweet_to_standard_format(tweet_result)
                if tweet:
                    tweets.append(tweet)

        # Check for legacy tweet format
        elif content.get("entryType") == "TimelineTweet":
            tweet_result = content.get("tweet", {})
            if tweet_result:
                tweet = _map_tweet_to_standard_format(tweet_result)
                if tweet:
                    tweets.append(tweet)

    return tweets


def extract_users_from_graphql_response(response_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Extract user information from GraphQL response.

    Args:
        response_data: Raw GraphQL response dictionary

    Returns:
        Dictionary mapping user IDs to user data
    """
    users = {}

    # Extract from various possible locations
    instructions = response_data.get("data", {}).get("user", {}).get("result", {})\
        .get("timeline_v2", {}).get("timeline", {}).get("instructions", [])

    if not instructions:
        instructions = response_data.get("data", {}).get("home", {})\
            .get("home_timeline_urt", {}).get("instructions", [])

    if not instructions:
        instructions = response_data.get("data", {}).get("list", {}).get("tweets_timeline", {})\
            .get("timeline", {}).get("instructions", [])

    entries = []
    for instruction in instructions:
        if instruction.get("type") == "TimelineAddEntries":
            entries.extend(instruction.get("entries", []))
        elif instruction.get("type") == "TimelineAddToModule":
            module_items = instruction.get("moduleItems", [])
            for item in module_items:
                entries.append(item.get("item", {}))

    # Extract users from entries
    for entry in entries:
        content = entry.get("content", {})
        item_content = content.get("itemContent", {}) or content.get("item", {}).get("itemContent", {})

        tweet_result = item_content.get("tweet_results", {}).get("result", {}) if item_content else None

        if tweet_result:
            # Handle TweetWithVisibilityResults wrapping
            if tweet_result.get("__typename") == "TweetWithVisibilityResults":
                tweet_result = tweet_result.get("tweet") or {}

            core = tweet_result.get("core", {})
            user_result = core.get("user_results", {}).get("result", {})

            if user_result:
                user = map_user_to_standard_format(user_result)
                if user and user.get("id"):
                    users[user["id"]] = user

    return users


def _map_tweet_to_standard_format(tweet_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Convert Twitter GraphQL tweet to standard format matching API response.

    Args:
        tweet_result: Raw tweet from GraphQL response

    Returns:
        Tweet in standard format or None if invalid
    """
    try:
        # Handle TweetWithVisibilityResults wrapping
        if tweet_result.get("__typename") == "TweetWithVisibilityResults":
            tweet_result = tweet_result.get("tweet") or {}

        legacy = tweet_result.get("legacy", {})
        if not legacy:
            return None

        # Get user info
        core = tweet_result.get("core", {})
        user_result = core.get("user_results", {}).get("result", {})

        # Extract referenced tweets (retweets, quotes)
        referenced_tweets = []
        if legacy.get("retweeted_status_result"):
            ref_tweet = legacy["retweeted_status_result"].get("result", {})
            if ref_tweet:
                referenced_tweets.append({
                    "type": "retweeted",
                    "id": ref_tweet.get("rest_id"),
                })

        # Extract entities (URLs, mentions, hashtags)
        entities = legacy.get("entities", {})

        # Map to standard format
        tweet = {
            "id": tweet_result.get("rest_id") or legacy.get("id_str"),
            "text": legacy.get("full_text") or legacy.get("text", ""),
            "created_at": _parse_twitter_date(legacy.get("created_at")),
            "author_id": user_result.get("rest_id") if user_result else None,
            "public_metrics": {
                "like_count": legacy.get("favorite_count", 0),
                "retweet_count": legacy.get("retweet_count", 0),
                "reply_count": legacy.get("reply_count", 0),
                "quote_count": legacy.get("quote_count", 0),
            },
            "entities": entities,
        }

        # Add referenced tweets if present
        if referenced_tweets:
            tweet["referenced_tweets"] = referenced_tweets

        # Extract media attachments
        media_entities = entities.get("media", [])
        if media_entities:
            tweet["attachments"] = {
                "media_keys": [
                    media.get("id_str") or media.get("media_url_https", "").split("/")[-1]
                    for media in media_entities
                ]
            }

        return tweet
    except Exception as e:
        logger.warning("Failed to map tweet: %s", e)
        return None


def map_user_to_standard_format(user_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Convert Twitter GraphQL user to standard format.

    Args:
        user_result: Raw user from GraphQL response

    Returns:
        User in standard format or None if invalid
    """
    try:
        legacy = user_result.get("legacy", {})
        if not legacy:
            return None

        return {
            "id": user_result.get("rest_id"),
            "username": legacy.get("screen_name"),
            "name": legacy.get("name"),
            "public_metrics": {
                "followers_count": legacy.get("followers_count", 0),
                "following_count": legacy.get("friends_count", 0),
                "tweet_count": legacy.get("statuses_count", 0),
            },
        }
    except Exception as e:
        logger.warning("Failed to map user: %s", e)
        return None


def _parse_twitter_date(date_str: Optional[str]) -> Optional[str]:
    """
    Parse Twitter date string to ISO 8601 format.

    Twitter uses format: "Wed Oct 10 20:19:24 +0000 2018"
    Convert to: "2018-10-10T20:19:24Z"
    """
    if not date_str:
        return None

    try:
        # Try parsing Twitter's date format
        dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        # If already in ISO format, return as-is
        return date_str
