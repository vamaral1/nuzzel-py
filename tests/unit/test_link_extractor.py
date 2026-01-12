"""
Unit tests for link extraction and aggregation
"""

import pytest
from unittest.mock import MagicMock
from nuzzel.processors.link_extractor import extract_shared_links
from nuzzel.models import Tweet


class TestExtractSharedLinks:
    """Test link extraction and aggregation functionality"""

    def test_extract_shared_links_empty_tweets(self):
        """Test with empty tweets dictionary"""
        result = extract_shared_links({})
        assert result == {'links_by_domain': {}}

    def test_extract_shared_links_single_link(self):
        """Test that links shared only once are filtered out"""
        tweet = Tweet(
            id="123",
            author_id="user123",
            author_username="testuser",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0,
            text="Check this out!",
            urls=[{"url": "https://example.com/article", "title": "Example Article"}],
            media=[],
            annotations=set()
        )

        tweets = {"123": tweet}
        result = extract_shared_links(tweets)

        # Links shared only once should be filtered out
        assert result == {'links_by_domain': {}}

    def test_extract_shared_links_multiple_links_same_domain(self):
        """Test multiple links from the same domain - only links shared more than once are included"""
        tweet1 = Tweet(
            id="123",
            author_id="user123",
            author_username="testuser1",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0,
            text="First article",
            urls=[{"url": "https://example.com/article1", "title": "Article 1"}],
            media=[],
            annotations=set()
        )

        tweet2 = Tweet(
            id="124",
            author_id="user124",
            author_username="testuser2",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0,
            text="Second article",
            urls=[{"url": "https://example.com/article2", "title": "Article 2"}],
            media=[],
            annotations=set()
        )

        tweets = {"123": tweet1, "124": tweet2}
        result = extract_shared_links(tweets)

        # Both links are shared only once, so they should be filtered out
        assert result == {'links_by_domain': {}}

    def test_extract_shared_links_same_link_multiple_tweets(self):
        """Test same link shared by multiple tweets - should be included since share_count > 1"""
        tweet1 = Tweet(
            id="123",
            author_id="user123",
            author_username="testuser1",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0,
            text="Great article!",
            urls=[{"url": "https://example.com/article", "title": "Example Article"}],
            media=[],
            annotations=set()
        )

        tweet2 = Tweet(
            id="124",
            author_id="user124",
            author_username="testuser2",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0,
            text="Must read!",
            urls=[{"url": "https://example.com/article", "title": "Example Article"}],
            media=[],
            annotations=set()
        )

        tweets = {"123": tweet1, "124": tweet2}
        result = extract_shared_links(tweets)

        assert "example.com" in result['links_by_domain']
        domain_data = result['links_by_domain']['example.com']
        assert domain_data['total_shares'] == 2
        assert len(domain_data['links']) == 1  # Same link should be aggregated

        link = domain_data['links'][0]
        assert link['link'] == 'https://example.com/article'
        assert link['share_count'] == 2
        assert len(link['tweets']) == 2

        # Check that both tweet URLs are included
        tweet_urls = [t['tweet_url'] for t in link['tweets']]
        assert 'https://twitter.com/i/status/123' in tweet_urls
        assert 'https://twitter.com/i/status/124' in tweet_urls

    def test_extract_shared_links_filters_single_shares(self):
        """Test that links shared only once are filtered out, but links shared multiple times are included"""
        # Link shared once - should be filtered out
        tweet1 = Tweet(
            id="123",
            author_id="user123",
            author_username="testuser1",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0,
            text="Single share",
            urls=[{"url": "https://example.com/single", "title": "Single Share"}],
            media=[],
            annotations=set()
        )

        # Link shared twice - should be included
        tweet2 = Tweet(
            id="124",
            author_id="user124",
            author_username="testuser2",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0,
            text="First share",
            urls=[{"url": "https://example.com/popular", "title": "Popular Article"}],
            media=[],
            annotations=set()
        )

        tweet3 = Tweet(
            id="125",
            author_id="user125",
            author_username="testuser3",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0,
            text="Second share",
            urls=[{"url": "https://example.com/popular", "title": "Popular Article"}],
            media=[],
            annotations=set()
        )

        tweets = {"123": tweet1, "124": tweet2, "125": tweet3}
        result = extract_shared_links(tweets)

        # Only the link shared twice should be included
        assert "example.com" in result['links_by_domain']
        domain_data = result['links_by_domain']['example.com']
        assert domain_data['total_shares'] == 2
        assert len(domain_data['links']) == 1

        link = domain_data['links'][0]
        assert link['link'] == 'https://example.com/popular'
        assert link['share_count'] == 2

    def test_extract_shared_links_multiple_domains(self):
        """Test links from multiple domains - only links shared more than once are included"""
        tweet1 = Tweet(
            id="123",
            author_id="user123",
            author_username="testuser1",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0,
            text="Tech article",
            urls=[{"url": "https://techcrunch.com/article", "title": "Tech Article"}],
            media=[],
            annotations=set()
        )

        tweet2 = Tweet(
            id="124",
            author_id="user124",
            author_username="testuser2",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0,
            text="News article",
            urls=[{"url": "https://nytimes.com/story", "title": "News Story"}],
            media=[],
            annotations=set()
        )

        tweets = {"123": tweet1, "124": tweet2}
        result = extract_shared_links(tweets)

        # Both links are shared only once, so they should be filtered out
        assert result == {'links_by_domain': {}}

    def test_extract_shared_links_invalid_domain(self):
        """Test handling of invalid domains"""
        tweet = Tweet(
            id="123",
            author_id="user123",
            author_username="testuser",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0,
            text="Invalid link",
            urls=[{"url": "not-a-valid-url", "title": "Invalid"}],
            media=[],
            annotations=set()
        )

        tweets = {"123": tweet}
        result = extract_shared_links(tweets)

        # Invalid URLs should be skipped
        assert result == {'links_by_domain': {}}

    def test_extract_shared_links_mixed_valid_invalid(self):
        """Test mix of valid and invalid URLs - only links shared more than once are included"""
        tweet = Tweet(
            id="123",
            author_id="user123",
            author_username="testuser",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0,
            text="Mixed links",
            urls=[
                {"url": "https://example.com/good", "title": "Good Link"},
                {"url": "invalid-url", "title": "Bad Link"}
            ],
            media=[],
            annotations=set()
        )

        tweets = {"123": tweet}
        result = extract_shared_links(tweets)

        # Link is shared only once, so it should be filtered out
        assert result == {'links_by_domain': {}}
