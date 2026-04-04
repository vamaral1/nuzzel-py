"""
Unified Tweet Feed Builder

Build a single list of tweet cards for the email by merging the curated
sections (themes, top engagement, lists, interests, shared links, predictions)
into a unique set of tweet IDs with one-or-more tags per tweet.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple, cast

from nuzzel.models import ProcessedData, Tweet

logger = logging.getLogger(__name__)


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_tweet_id(value: Any) -> Optional[str]:
    """Normalize tweet id from JSON (str or int); empty/invalid -> None."""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _tweet_id_from_any(value: Any) -> Optional[str]:
    if isinstance(value, Tweet):
        return value.id
    if isinstance(value, dict):
        tweet_id = value.get("id") or value.get("tweet_id")
        return _normalize_tweet_id(tweet_id)
    return None


def _tweet_id_from_tweet_url(tweet_url: str) -> Optional[str]:
    """
    Extract numeric tweet id from common X/Twitter status URLs.

    Prefers the segment after /status/ or /statuses/ so paths like
    .../status/123/photo/1 resolve to 123, not 1.
    """
    if not tweet_url or not isinstance(tweet_url, str):
        return None
    try:
        cleaned = tweet_url.split("?", 1)[0].rstrip("/")
        parts = cleaned.split("/")
        for i, part in enumerate(parts):
            if part in ("status", "statuses") and i + 1 < len(parts):
                candidate = parts[i + 1]
                if candidate.isdigit():
                    return candidate
        last = parts[-1]
        if last.isdigit():
            return last
    except Exception:
        return None
    return None


def _pick_representative_tweet_id_for_shared_link(
    tweet_refs: List[Any],
    tweets: Dict[str, Tweet],
) -> Optional[str]:
    """
    For one aggregated shared URL, choose a single tweet to surface in the feed.

    Multiple tweets can share the same URL; tagging all of them duplicates cards.
    We pick the tweet with the strongest engagement among refs that exist in `tweets`.
    """
    candidate_ids: List[str] = []
    for tweet_ref in tweet_refs:
        if not isinstance(tweet_ref, dict):
            continue
        tweet_url = _safe_str(tweet_ref.get("tweet_url"))
        raw_tid = tweet_ref.get("tweet_id") if "tweet_id" in tweet_ref else None
        resolved_tweet_id = _normalize_tweet_id(raw_tid)
        if not resolved_tweet_id:
            resolved_tweet_id = _tweet_id_from_tweet_url(tweet_url)
        if not resolved_tweet_id or resolved_tweet_id not in tweets:
            continue
        if resolved_tweet_id not in candidate_ids:
            candidate_ids.append(resolved_tweet_id)

    if not candidate_ids:
        return None

    def _rep_score(tid: str) -> Tuple[float, int]:
        t = tweets[tid]
        return (
            float(t.normalized_like_count) + float(t.normalized_retweet_count),
            int(t.like_count) + int(t.retweet_count),
        )

    return max(candidate_ids, key=_rep_score)


def _tag_count_sort_key(item: Dict[str, Any]) -> Tuple[int, float, float, str]:
    # Feed is primarily sorted by tag count (descending), then by engagement
    # proxies (descending), then by id for deterministic ordering.
    tag_count = len(item.get("tags") or [])
    like_metric = float(item.get("normalized_like_count") or 0.0)
    retweet_metric = float(item.get("normalized_retweet_count") or 0.0)
    tweet_id = cast(str, item.get("id") or item.get("tweet_id") or "")
    return (-tag_count, -like_metric, -retweet_metric, tweet_id)


def build_merged_tweet_feed(processed_data: ProcessedData, digest_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Merge digest sources into a single, tagged tweet feed.

    Returns a list of dicts suitable for Jinja2 rendering. Each dict contains:
    `id`, `text`, `like_count`, `retweet_count`, `reply_count`, `tags`.
    """

    tweet_tags: Dict[str, Set[str]] = defaultdict(set)

    def add_tag(tweet_id: str, tag: str) -> None:
        if not tweet_id:
            return
        tag = _safe_str(tag)
        if not tag:
            return
        tweet_tags[tweet_id].add(tag)

    # 1) Themes -> tags (use tweet_ids; theme headings are not rendered anymore)
    themes_summary = digest_data.get("themes_summary") or {}
    themes = themes_summary.get("themes") if isinstance(themes_summary, dict) else None
    if isinstance(themes, list):
        for theme_obj in themes:
            if not isinstance(theme_obj, dict):
                continue
            theme_name = _safe_str(theme_obj.get("theme"))
            tweet_ids = theme_obj.get("tweet_ids") or []
            if not isinstance(tweet_ids, list):
                continue
            for raw_tid in tweet_ids:
                tid = _normalize_tweet_id(raw_tid)
                if not tid:
                    continue
                # Implementation detail: prefix is part of the product voice.
                add_tag(tid, f"Theme: {theme_name}" if theme_name else "Theme")

    # 2) Overall engagement picks
    for tweet_obj in digest_data.get("top_liked_tweets") or []:
        tid = _tweet_id_from_any(tweet_obj)
        if tid:
            add_tag(tid, "Top Liked")
    for tweet_obj in digest_data.get("top_retweeted_tweets") or []:
        tid = _tweet_id_from_any(tweet_obj)
        if tid:
            add_tag(tid, "Top Retweeted")

    # 3) Lists -> tags
    list_engagement = digest_data.get("list_engagement") or {}
    if isinstance(list_engagement, dict):
        for list_name, list_data in list_engagement.items():
            if not isinstance(list_data, dict):
                continue
            list_name_str = _safe_str(list_name)
            for tweet_obj in list_data.get("top_liked") or []:
                tid = _tweet_id_from_any(tweet_obj)
                if tid and list_name_str:
                    add_tag(tid, list_name_str)
                    add_tag(tid, "Top Liked")
            for tweet_obj in list_data.get("top_retweeted") or []:
                tid = _tweet_id_from_any(tweet_obj)
                if tid and list_name_str:
                    add_tag(tid, list_name_str)
                    add_tag(tid, "Top Retweeted")

    # 4) Interests -> tags
    interest_tweets = digest_data.get("interest_tweets") or {}
    if isinstance(interest_tweets, dict) and "error" not in interest_tweets:
        for category, tweets in interest_tweets.items():
            category_str = _safe_str(category)
            if not category_str:
                continue
            if not isinstance(tweets, list):
                continue
            for tweet_obj in tweets:
                tid = _tweet_id_from_any(tweet_obj)
                if tid:
                    add_tag(tid, f"Interest: {category_str}")

    # 5) Shared links -> tags
    shared_links = digest_data.get("shared_links") or {}
    links_by_domain = shared_links.get("links_by_domain") if isinstance(shared_links, dict) else None
    if isinstance(links_by_domain, dict):
        for domain, domain_data in links_by_domain.items():
            if not isinstance(domain_data, dict):
                continue
            domain_str = _safe_str(domain)
            for link_obj in domain_data.get("links") or []:
                if not isinstance(link_obj, dict):
                    continue
                tweet_refs = link_obj.get("tweets") or []
                if not isinstance(tweet_refs, list):
                    tweet_refs = []

                rep_id = _pick_representative_tweet_id_for_shared_link(
                    tweet_refs, processed_data.tweets
                )
                if rep_id:
                    add_tag(rep_id, "Shared link")
                    if domain_str:
                        add_tag(rep_id, f"Links: {domain_str}")
                    continue

                for tweet_ref in tweet_refs:
                    if not isinstance(tweet_ref, dict):
                        continue
                    tweet_url = _safe_str(tweet_ref.get("tweet_url"))
                    raw_tid = tweet_ref.get("tweet_id") if "tweet_id" in tweet_ref else None
                    resolved_tweet_id = _normalize_tweet_id(raw_tid)
                    if not resolved_tweet_id:
                        resolved_tweet_id = _tweet_id_from_tweet_url(tweet_url)
                    if not resolved_tweet_id:
                        if tweet_url:
                            logger.warning(
                                "Shared link: could not resolve tweet id from tweet_url=%r",
                                tweet_url,
                            )
                        elif raw_tid is not None:
                            logger.warning(
                                "Shared link: invalid tweet_id=%r (expected string or int)",
                                raw_tid,
                            )
                        continue

    # 6) Predictions -> tags
    engagement_predictions = digest_data.get("engagement_predictions") or {}
    if isinstance(engagement_predictions, dict):
        like_pred = engagement_predictions.get("most_likely_to_like") or {}
        retweet_pred = engagement_predictions.get("most_likely_to_retweet") or {}
        if isinstance(like_pred, dict):
            tid = _normalize_tweet_id(like_pred.get("tweet_id"))
            if tid:
                add_tag(tid, "Most Likely to Like")
        if isinstance(retweet_pred, dict):
            tid = _normalize_tweet_id(retweet_pred.get("tweet_id"))
            if tid:
                add_tag(tid, "Most Likely to Retweet")

    # Hydrate tweet cards from processed_data.
    feed: List[Dict[str, Any]] = []
    for tweet_id, tags in tweet_tags.items():
        tweet = processed_data.tweets.get(tweet_id)
        if not tweet:
            logger.warning("Tweet id %s present in digest sources but missing from processed_data", tweet_id)
            continue

        feed.append(
            {
                "id": tweet.id,
                "text": tweet.text,
                "like_count": tweet.like_count,
                "retweet_count": tweet.retweet_count,
                "reply_count": tweet.reply_count,
                "normalized_like_count": tweet.normalized_like_count,
                "normalized_retweet_count": tweet.normalized_retweet_count,
                "tags": sorted(tags),
            }
        )

    feed.sort(key=_tag_count_sort_key)
    return feed

