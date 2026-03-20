"""
Unit tests for unified tweet feed merging and tagging.
"""

import logging

from nuzzel.generators.tweet_feed import build_merged_tweet_feed
from nuzzel.models import ProcessedData, Tweet


def _tweet(
    tweet_id: str,
    *,
    like_count: int,
    retweet_count: int,
    reply_count: int = 0,
    normalized_like_count: float,
    normalized_retweet_count: float,
) -> Tweet:
    return Tweet(
        id=tweet_id,
        author_id="author",
        author_username="@user",
        like_count=like_count,
        retweet_count=retweet_count,
        reply_count=reply_count,
        normalized_like_count=normalized_like_count,
        normalized_retweet_count=normalized_retweet_count,
        normalized_reply_count=0.0,
        text=f"text {tweet_id}",
        urls=[],
        media=[],
        annotations=set(),
    )


def test_build_merged_tweet_feed_merges_tags_and_sorts_by_tag_count():
    t1 = _tweet(
        "1",
        like_count=10,
        retweet_count=1,
        normalized_like_count=0.9,
        normalized_retweet_count=0.1,
    )
    t2 = _tweet(
        "2",
        like_count=5,
        retweet_count=20,
        normalized_like_count=0.2,
        normalized_retweet_count=0.8,
    )
    t3 = _tweet(
        "3",
        like_count=30,
        retweet_count=2,
        normalized_like_count=0.7,
        normalized_retweet_count=0.05,
    )

    processed = ProcessedData(tweets={"1": t1, "2": t2, "3": t3})

    digest_data = {
        "themes_summary": {
            "themes": [
                {"theme": "AI", "tweet_ids": ["1", "2"]},
            ]
        },
        "top_liked_tweets": [t1],
        "top_retweeted_tweets": [t2],
        "list_engagement": {
            "ListA": {
                "top_liked": [t1],
                "top_retweeted": [t2],
            }
        },
        "interest_tweets": {
            "Tech": [t2],
            "Other": [t3],
        },
        "shared_links": {
            "links_by_domain": {
                "example.com": {
                    "total_shares": 2,
                    "links": [
                        {
                            "link": "https://example.com/whatever",
                            "title": "Whatever",
                            "share_count": 2,
                            "tweets": [
                                {"tweet_url": "https://twitter.com/i/status/3"},
                            ],
                        }
                    ],
                }
            }
        },
        "engagement_predictions": {
            "most_likely_to_like": {"tweet_id": "2", "explanation": "", "tweet": t2},
            "most_likely_to_retweet": {"tweet_id": "1", "explanation": "", "tweet": t1},
        },
    }

    feed = build_merged_tweet_feed(processed, digest_data)

    # Tag-count order: t2 has the most tags, then t1, then t3.
    assert [item["id"] for item in feed] == ["2", "1", "3"]

    t2_tags = set(feed[0]["tags"])
    assert "Theme: AI" in t2_tags
    assert "Top Retweeted" in t2_tags
    assert "ListA" in t2_tags
    assert "Interest: Tech" in t2_tags
    assert "Most Likely to Like" in t2_tags

    t1_tags = set(next(item for item in feed if item["id"] == "1")["tags"])
    assert "Top Liked" in t1_tags
    assert "ListA" in t1_tags

    t3_tags = set(feed[2]["tags"])
    assert "Interest: Other" in t3_tags
    assert "Shared link" in t3_tags
    assert "Links: example.com" in t3_tags


def test_theme_tweet_ids_numeric_json_coerced_to_str():
    t1 = _tweet(
        "1",
        like_count=1,
        retweet_count=0,
        normalized_like_count=0.1,
        normalized_retweet_count=0.0,
    )
    processed = ProcessedData(tweets={"1": t1})
    digest_data = {
        "themes_summary": {
            "themes": [
                {"theme": "AI", "tweet_ids": [1]},
            ]
        },
    }
    feed = build_merged_tweet_feed(processed, digest_data)
    assert len(feed) == 1
    assert feed[0]["id"] == "1"
    assert "Theme: AI" in feed[0]["tags"]


def test_shared_link_status_url_with_photo_segment():
    tid = "1234567890123456789"
    tw = _tweet(
        tid,
        like_count=1,
        retweet_count=0,
        normalized_like_count=0.1,
        normalized_retweet_count=0.0,
    )
    processed = ProcessedData(tweets={tid: tw})
    digest_data = {
        "shared_links": {
            "links_by_domain": {
                "example.com": {
                    "links": [
                        {
                            "tweets": [
                                {
                                    "tweet_url": (
                                        f"https://x.com/user/status/{tid}/photo/1"
                                    ),
                                },
                            ],
                        },
                    ],
                },
            },
        },
    }
    feed = build_merged_tweet_feed(processed, digest_data)
    assert len(feed) == 1
    tags = set(feed[0]["tags"])
    assert "Shared link" in tags
    assert "Links: example.com" in tags


def test_shared_link_tweet_id_int_coerced():
    tid = "42"
    tw = _tweet(
        tid,
        like_count=1,
        retweet_count=0,
        normalized_like_count=0.1,
        normalized_retweet_count=0.0,
    )
    processed = ProcessedData(tweets={tid: tw})
    digest_data = {
        "shared_links": {
            "links_by_domain": {
                "ex.com": {
                    "links": [
                        {"tweets": [{"tweet_id": 42}]},
                    ],
                },
            },
        },
    }
    feed = build_merged_tweet_feed(processed, digest_data)
    assert len(feed) == 1
    assert "Shared link" in feed[0]["tags"]


def test_shared_link_unparseable_tweet_url_logs_warning(caplog):
    caplog.set_level(logging.WARNING)
    tw = _tweet(
        "1",
        like_count=1,
        retweet_count=0,
        normalized_like_count=0.1,
        normalized_retweet_count=0.0,
    )
    processed = ProcessedData(tweets={"1": tw})
    digest_data = {
        "shared_links": {
            "links_by_domain": {
                "example.com": {
                    "links": [
                        {
                            "tweets": [
                                {"tweet_url": "https://example.com/not-a-status"},
                            ],
                        },
                    ],
                },
            },
        },
    }
    feed = build_merged_tweet_feed(processed, digest_data)
    assert feed == []
    assert "could not resolve tweet id" in caplog.text

