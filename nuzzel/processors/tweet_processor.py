"""
Main Tweet Processor

This module orchestrates the processing of tweets for the digest, including
data transformation from Twitter API format to our custom Tweet models,
handling referenced tweets, and calculating normalized engagement scores.
"""

import logging
from typing import Dict, Any, List, Optional, Set

from nuzzel.models import Tweet, ProcessedData
from nuzzel.processors.engagement_calculator import calculate_normalized_engagement
from nuzzel.utils.url_utils import normalize_url
from nuzzel.utils.title_fetcher import fetch_url_title
from nuzzel.utils.validation import clean_tweet_text

# Configure logging
logger = logging.getLogger(__name__)


def process_data_for_digest(
    timeline_data: Dict[str, Any],
    liked_tweets_data: Dict[str, Any],
    posted_tweets_data: Dict[str, Any]
) -> ProcessedData:
    """
    Transform Twitter API data into ProcessedData with Tweet models.

    Args:
        timeline_data: Timeline data from Twitter API (with referenced tweets)
        liked_tweets_data: User's liked tweets data
        posted_tweets_data: User's posted tweets data

    Returns:
        ProcessedData object with transformed tweets
    """
    processed = ProcessedData()

    # Process timeline tweets
    timeline_tweets = _build_tweet_id_to_tweet_dict(
        timeline_data.get('data', []),
        timeline_data.get('users', {}),
        timeline_data.get('media', {}),
        timeline_data.get('referenced_tweets', {})
    )
    processed.tweets = timeline_tweets

    # Process liked tweets
    liked_tweets = _build_tweet_id_to_tweet_dict(
        liked_tweets_data.get('data', []),
        liked_tweets_data.get('users', {}),
        liked_tweets_data.get('media', {}),
        liked_tweets_data.get('referenced_tweets', {})
    )
    processed.user_liked_content = liked_tweets

    # Process posted tweets
    posted_tweets = _build_tweet_id_to_tweet_dict(
        posted_tweets_data.get('data', []),
        posted_tweets_data.get('users', {}),
        posted_tweets_data.get('media', {}),
        posted_tweets_data.get('referenced_tweets', {})
    )
    processed.user_posted_content = posted_tweets

    # Calculate statistics
    processed.total_tweets = len(processed.tweets)
    processed.unique_accounts = len(timeline_data.get('users', {}).keys())
    processed.total_links = sum(
        len(tweet.urls) for tweet in processed.tweets.values()
    )

    logger.info(
        "Processed %d tweets from %d unique accounts with %d total links",
        processed.total_tweets,
        processed.unique_accounts,
        processed.total_links
    )

    return processed


def _build_tweet_id_to_tweet_dict(
    tweets: List[Any],
    users: Dict[str, Any],
    media: Dict[str, Any],
    referenced_tweets: Dict[str, Any]
) -> Dict[str, Tweet]:
    """
    Transform Twitter API tweet data into Tweet models.

    Args:
        tweets: List of tweet dictionaries from Twitter API (already converted by twitter_client)
        users: Dictionary mapping user_id -> user data from Twitter API
        media: Dictionary mapping media_key -> media data from Twitter API
        referenced_tweets: Dictionary mapping tweet_id -> referenced tweet data from includes.tweets

    Returns:
        Dictionary mapping tweet_id -> Tweet object
    """
    result = {}

    for tweet in tweets:
        tweet_id = tweet.get('id')
        if not tweet_id:
            continue

        # Check if this is a referenced tweet (reply, quote, retweet)
        referenced_tweet_refs = tweet.get('referenced_tweets', [])
        is_referenced = len(referenced_tweet_refs) > 0

        if is_referenced:
            tweet_obj = _merge_with_referenced_tweet(
                tweet, referenced_tweets, users, media
            )
        else:
            # Handle original tweets
            tweet_obj = _transform_dict_to_tweet_obj(
                tweet, users, media
            )

        if tweet_obj:
            result[tweet_id] = tweet_obj

    return result


def _transform_dict_to_tweet_obj(
    tweet: Dict[str, Any],
    users: Dict[str, Dict[str, Any]],
    media: Dict[str, Dict[str, Any]]
) -> Optional[Tweet]:
    """
    Transform a tweet with no referenced tweets returned by the API into a Tweet model.

    Args:
        tweet: Tweet dictionary from Twitter API
        users: Map of user_id -> user data
        media: Map of media_key -> media data

    Returns:
        Tweet object or None if transformation fails
    """
    try:
        # Extract basic info
        author_id = tweet.get('author_id', '')
        author_username = _get_username(author_id, users)
        author_followers = _get_followers(author_id, users)

        # Extract engagement metrics
        public_metrics = tweet.get('public_metrics', {})
        like_count = public_metrics.get('like_count', 0)
        retweet_count = public_metrics.get('retweet_count', 0)
        quote_count = public_metrics.get('quote_count', 0)
        reply_count = public_metrics.get('reply_count', 0)

        # Extract text and clean t.co links
        text = clean_tweet_text(tweet.get('text', ''))

        # Extract URLs
        urls = _extract_urls(tweet)

        # Extract media
        media_list = _extract_media(tweet, media)

        # Extract annotations
        annotations = _extract_annotations(tweet)

        # Calculate normalized engagement scores
        normalized_like_count = calculate_normalized_engagement(
            like_count, author_followers
        )
        normalized_retweet_count = calculate_normalized_engagement(
            retweet_count, author_followers
        )
        normalized_reply_count = calculate_normalized_engagement(
            reply_count, author_followers
        )

        # Create Tweet object
        tweet_obj = Tweet(
            id=tweet.get('id', ''),
            author_id=author_id,
            author_username=author_username,
            like_count=like_count,
            retweet_count=retweet_count + quote_count,
            reply_count=reply_count,
            normalized_like_count=normalized_like_count,
            normalized_retweet_count=normalized_retweet_count,
            normalized_reply_count=normalized_reply_count,
            text=text,
            urls=urls,
            media=media_list,
            annotations=annotations
        )

        return tweet_obj

    except Exception as e:
        logger.warning("Failed to transform tweet %s: %s", tweet.get('id'), e, exc_info=True)
        return None


def _merge_with_referenced_tweet(
    tweet: Dict[str, Any],
    referenced_tweets: Dict[str, Dict[str, Any]],
    users: Dict[str, Dict[str, Any]],
    media: Dict[str, Dict[str, Any]]
) -> Optional[Tweet]:
    """
    Merge original tweet with referenced tweet.

    Args:
        tweet: Original tweet dictionary (the reply/quote/retweet) containing
            referenced_tweets field
        referenced_tweets: Dictionary mapping tweet_id -> referenced tweet data from includes.tweets
        users: Map of user_id -> user data
        media: Map of media_key -> media data

    Returns:
        Tweet object with merged content or None if transformation fails
    """
    try:
        # Extract referenced tweet references from the original tweet itself
        referenced_tweet_refs = tweet.get('referenced_tweets', [])

        if not referenced_tweet_refs:
            # Fallback to original tweet processing
            return _transform_dict_to_tweet_obj(tweet, users, media)

        # Extract original tweet info (the reply/quote/retweet itself)
        original_author_id = tweet.get('author_id', '')
        original_author_username = _get_username(original_author_id, users)
        original_author_followers = _get_followers(original_author_id, users)

        # Extract original tweet info
        original_text = clean_tweet_text(tweet.get('text', ''))
        original_urls = _extract_urls(tweet)
        original_media = _extract_media(tweet, media)
        original_annotations = _extract_annotations(tweet)

        # Collect all referenced tweets and merge their content
        all_referenced_texts = []
        all_referenced_urls = []
        all_referenced_media = []
        all_referenced_annotations = set()
        primary_ref_type = None

        for ref in referenced_tweet_refs:
            referenced_id = ref.get('id')
            ref_type = ref.get('type', '')  # 'replied_to', 'quoted', 'retweeted'

            # Track the primary reference type (first one, typically the most important)
            if primary_ref_type is None:
                primary_ref_type = ref_type

            # Find referenced tweet in the referenced_tweets dictionary
            referenced_tweet = referenced_tweets.get(referenced_id) if referenced_id else None

            if not referenced_tweet:
                logger.debug(
                    "Referenced tweet %s not found in referenced_tweets for original tweet %s",
                    referenced_id, tweet.get('id'))
                continue

            # Extract referenced tweet info
            referenced_text = clean_tweet_text(referenced_tweet.get('text', ''))
            referenced_urls = _extract_urls(referenced_tweet)
            referenced_media = _extract_media(referenced_tweet, media)
            referenced_annotations = _extract_annotations(referenced_tweet)

            # Collect text with type marker
            if referenced_text:
                all_referenced_texts.append(f"[{ref_type}] {referenced_text}")

            # Collect URLs, media, and annotations
            all_referenced_urls.extend(referenced_urls)
            all_referenced_media.extend(referenced_media)
            all_referenced_annotations.update(referenced_annotations)

        # Build merged text: all referenced tweets, then original
        if all_referenced_texts:
            referenced_text_combined = " ".join(all_referenced_texts)
            if primary_ref_type == 'retweeted':
                # For retweets, original text is usually empty or just the retweet indicator
                merged_text = f"{referenced_text_combined} [Retweeted]"
            elif primary_ref_type == 'replied_to':
                merged_text = f"{referenced_text_combined} [Reply] {original_text}"
            elif primary_ref_type == 'quoted':
                merged_text = f"{referenced_text_combined} [Quote] {original_text}"
            else:
                # For unknown types, concatenate all referenced then original
                merged_text = f"{referenced_text_combined} [Original] {original_text}"
        else:
            # No referenced tweets found, fallback to original
            merged_text = original_text

        # Merge URLs (deduplicate by URL)
        merged_urls = _merge_urls(all_referenced_urls, original_urls)

        # Merge media (deduplicate by URL or type+description)
        merged_media = _merge_media(all_referenced_media, original_media)

        # Merge annotations (deduplicate by topic+entity)
        merged_annotations = _merge_annotations(all_referenced_annotations, original_annotations)

        # Use original tweet's engagement metrics (the reply/quote/retweet itself)
        public_metrics = tweet.get('public_metrics', {})
        like_count = public_metrics.get('like_count', 0)
        retweet_count = public_metrics.get('retweet_count', 0)
        quote_count = public_metrics.get('quote_count', 0)
        reply_count = public_metrics.get('reply_count', 0)

        # Calculate normalized engagement scores using original author's follower count
        normalized_like_count = calculate_normalized_engagement(
            like_count, original_author_followers
        )
        normalized_retweet_count = calculate_normalized_engagement(
            retweet_count, original_author_followers
        )
        normalized_reply_count = calculate_normalized_engagement(
            reply_count, original_author_followers
        )

        # Create Tweet object using original tweet's ID and author
        tweet_obj = Tweet(
            id=tweet.get('id', ''),
            author_id=original_author_id,
            author_username=original_author_username,
            like_count=like_count,
            retweet_count=retweet_count + quote_count,
            reply_count=reply_count,
            normalized_like_count=normalized_like_count,
            normalized_retweet_count=normalized_retweet_count,
            normalized_reply_count=normalized_reply_count,
            text=merged_text,
            urls=merged_urls,
            media=merged_media,
            annotations=merged_annotations
        )

        return tweet_obj

    except Exception as e:
        logger.warning(
            "Failed to transform referenced tweet %s: %s", tweet.get('id'), e,
            exc_info=True)
        return None


def _get_username(author_id: str, users: Dict[str, Dict[str, Any]]) -> str:
    """Get username for author_id"""
    user = users.get(author_id, {})
    return user.get('username', '') if isinstance(user, dict) else ''


def _get_followers(author_id: str, users: Dict[str, Dict[str, Any]]) -> int:
    """Get follower count for author_id"""
    user = users.get(author_id, {})
    public_metrics = user.get('public_metrics', {})
    if not public_metrics:
        logger.warning("No public metrics found for user %s", author_id)
        return 0
    return public_metrics.get('followers_count', 0)

def _extract_urls(tweet: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract URLs from tweet entities and normalize them"""
    urls: List[Dict[str, str]] = []
    entities = tweet.get('entities', {})
    if not isinstance(entities, dict):
        return urls

    url_list = entities.get('urls', [])
    for url_obj in url_list:
        # URL objects are already dictionaries from twitter_client
        expanded_url = url_obj.get('expanded_url', '')
        title = url_obj.get('title', '').strip()

        if expanded_url:
            # Normalize URL to remove tracking parameters and standardize format
            normalized_url = normalize_url(expanded_url)
            if normalized_url:
                # Fetch title if not provided by Twitter API
                if not title:
                    title = fetch_url_title(normalized_url) or ''
                urls.append({
                    'url': normalized_url,
                    'title': title
                })
    return urls


def _extract_media(tweet: Dict[str, Any], media: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
    """Extract media from tweet attachments"""
    media_list: List[Dict[str, str]] = []
    attachments = tweet.get('attachments', {})
    if not isinstance(attachments, dict):
        return media_list

    media_keys = attachments.get('media_keys', [])
    for media_key in media_keys:
        media_data = media.get(media_key)
        if media_data:
            media_type = media_data.get('type', '')
            alt_text = media_data.get('alt_text', '')

            media_list.append({
                'type': media_type,
                'description': alt_text or ''
            })
    return media_list


def _extract_annotations(tweet: Dict[str, Any]) -> Set[str]:
    """Extract context annotations from tweet"""
    annotations = set()
    context_annotations = tweet.get('context_annotations', [])
    for ann in context_annotations:
        # Annotations are already dictionaries from twitter_client
        domain = ann.get('domain', {})
        entity = ann.get('entity', {})

        domain_name = domain.get('name', '') if isinstance(domain, dict) else ''
        entity_name = entity.get('name', '') if isinstance(entity, dict) else ''

        if domain_name and domain_name != 'Unified Twitter Taxonomy':
            annotations.add(domain_name)
        if entity_name:
            annotations.add(entity_name)

    entity_annotations = tweet.get('entities', {}).get('annotations', [])
    for ann in entity_annotations:
        probability = ann.get('probability', 0.0)
        normalized_text = ann.get('normalized_text', '')
        if probability > 0.5 and normalized_text:
            annotations.add(normalized_text)

    return annotations


def _merge_urls(
    referenced_urls: List[Dict[str, str]],
    original_urls: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """Merge URL lists, deduplicating by URL"""
    seen_urls = set()
    merged = []

    for url_dict in referenced_urls + original_urls:
        url = url_dict.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            merged.append(url_dict)

    return merged


def _merge_media(
    referenced_media: List[Dict[str, str]],
    original_media: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """Merge media lists, deduplicating by type+description"""
    seen_media = set()
    merged = []

    for media_dict in referenced_media + original_media:
        media_key = (media_dict.get('type', ''), media_dict.get('description', ''))
        if media_key not in seen_media:
            seen_media.add(media_key)
            merged.append(media_dict)

    return merged


def _merge_annotations(referenced_anns: Set[str], original_anns: Set[str]) -> Set[str]:
    """Merge annotation sets, deduplicating"""
    return referenced_anns | original_anns
