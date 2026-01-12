"""
Unit tests for tweet aggregation functionality
"""

import pytest
from unittest.mock import MagicMock, patch
from nuzzel.processors.tweet_aggregator import aggregate_context_annotations, calculate_top_engagement
from nuzzel.processors.tweet_processor import _extract_annotations
from nuzzel.models import Tweet, ProcessedData


class TestExtractAnnotations:
    """Test context annotation extraction and filtering"""

    def test_extract_annotations_uses_entity_as_topic_for_unified_twitter_taxonomy(self):
        """Test that Unified Twitter Taxonomy annotations use entity name as topic instead of domain"""
        tweet_data = {
            'context_annotations': [
                {
                    'domain': {
                        'id': '131',
                        'name': 'Unified Twitter Taxonomy'
                    },
                    'entity': {
                        'id': '123',
                        'name': 'Some Entity'
                    }
                },
                {
                    'domain': {
                        'id': '29',
                        'name': 'Technology'
                    },
                    'entity': {
                        'id': '456',
                        'name': 'Artificial Intelligence'
                    }
                },
                {
                    'domain': {
                        'id': '131',
                        'name': 'Unified Twitter Taxonomy'
                    },
                    'entity': {
                        'id': '789',
                        'name': 'Another Entity'
                    }
                }
            ]
        }

        annotations = _extract_annotations(tweet_data)

        # Should have 4 annotations (entity names, domain names excluding Unified Twitter Taxonomy)
        assert len(annotations) == 4

        # Verify entities are included
        assert 'Some Entity' in annotations
        assert 'Another Entity' in annotations
        assert 'Artificial Intelligence' in annotations

        # Verify Technology domain is included
        assert 'Technology' in annotations

        # Verify Unified Twitter Taxonomy domain is NOT included
        assert 'Unified Twitter Taxonomy' not in annotations

    def test_extract_annotations_handles_empty_context_annotations(self):
        """Test extraction with no context annotations"""
        tweet_data = {}
        annotations = _extract_annotations(tweet_data)
        assert annotations == set()

    def test_extract_annotations_handles_only_unified_twitter_taxonomy(self):
        """Test that if only Unified Twitter Taxonomy annotations exist, entities are still included"""
        tweet_data = {
            'context_annotations': [
                {
                    'domain': {
                        'id': '131',
                        'name': 'Unified Twitter Taxonomy'
                    },
                    'entity': {
                        'id': '123',
                        'name': 'Some Entity'
                    }
                }
            ]
        }

        annotations = _extract_annotations(tweet_data)
        # Should have 1 annotation (entity name, Unified Twitter Taxonomy domain excluded)
        assert len(annotations) == 1
        assert 'Some Entity' in annotations

    def test_extract_annotations_from_entities_annotations(self):
        """Test extraction of normalized_text from entities.annotations when probability > 0.5"""
        tweet_data = {
            'entities': {
                'annotations': [
                    {
                        'probability': 0.6979,
                        'type': 'Organization',
                        'normalized_text': 'AI'
                    },
                    {
                        'probability': 0.3,
                        'type': 'Person',
                        'normalized_text': 'John Doe'
                    },
                    {
                        'probability': 0.85,
                        'type': 'Place',
                        'normalized_text': 'San Francisco'
                    }
                ]
            },
            'context_annotations': []
        }

        annotations = _extract_annotations(tweet_data)

        # Should have 2 annotations (AI and San Francisco, but not John Doe due to low probability)
        assert len(annotations) == 2
        assert 'AI' in annotations
        assert 'San Francisco' in annotations
        assert 'John Doe' not in annotations

    def test_extract_annotations_combines_context_and_entity_annotations(self):
        """Test that context_annotations and entities.annotations are both extracted"""
        tweet_data = {
            'context_annotations': [
                {
                    'domain': {
                        'id': '29',
                        'name': 'Technology'
                    },
                    'entity': {
                        'id': '456',
                        'name': 'Machine Learning'
                    }
                }
            ],
            'entities': {
                'annotations': [
                    {
                        'probability': 0.7,
                        'type': 'Organization',
                        'normalized_text': 'OpenAI'
                    }
                ]
            }
        }

        annotations = _extract_annotations(tweet_data)

        # Should have 3 annotations: Technology (domain), Machine Learning (entity), OpenAI (entity annotation)
        assert len(annotations) == 3
        assert 'Technology' in annotations
        assert 'Machine Learning' in annotations
        assert 'OpenAI' in annotations


class TestAggregateContextAnnotations:
    """Test context annotations aggregation"""

    def test_aggregate_context_annotations_empty_tweets(self):
        """Test with empty tweets dictionary"""
        result = aggregate_context_annotations({})
        assert result == {"top_categories": []}

    def test_aggregate_context_annotations_single_annotation(self):
        """Test aggregation of single context annotation"""
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
            text="Test tweet",
            urls=[],
            media=[],
            annotations={"Technology", "Artificial Intelligence"}
        )

        tweets = {"123": tweet}
        result = aggregate_context_annotations(tweets)

        assert len(result["top_categories"]) == 2
        names = {cat["name"] for cat in result["top_categories"]}
        assert "Technology" in names
        assert "Artificial Intelligence" in names
        # Both should have count 1
        for cat in result["top_categories"]:
            assert cat["count"] == 1

    def test_aggregate_context_annotations_multiple_entities_same_domain(self):
        """Test multiple entities within same domain"""
        tweet1 = Tweet(
            id="123",
            text="AI tweet",
            urls=[],
            media=[],
            annotations={"Technology", "Artificial Intelligence"},
            author_id="user123",
            author_username="testuser",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0
        )

        tweet2 = Tweet(
            id="124",
            text="ML tweet",
            urls=[],
            media=[],
            annotations={"Technology", "Machine Learning"},
            author_id="user123",
            author_username="testuser",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0
        )

        tweets = {"123": tweet1, "124": tweet2}
        result = aggregate_context_annotations(tweets)

        # Technology appears in both tweets (count 2), entities appear once each
        assert len(result["top_categories"]) == 3
        counts = {cat["name"]: cat["count"] for cat in result["top_categories"]}
        assert counts["Technology"] == 2
        assert counts["Artificial Intelligence"] == 1
        assert counts["Machine Learning"] == 1

    def test_aggregate_context_annotations_same_entity_multiple_times(self):
        """Test same entity appearing multiple times"""
        tweet1 = Tweet(
            id="123",
            text="First AI tweet",
            urls=[],
            media=[],
            annotations={"Technology", "Artificial Intelligence"},
            author_id="user123",
            author_username="testuser",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0
        )

        tweet2 = Tweet(
            id="124",
            text="Second AI tweet",
            urls=[],
            media=[],
            annotations={"Technology", "Artificial Intelligence"},
            author_id="user123",
            author_username="testuser",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0
        )

        tweets = {"123": tweet1, "124": tweet2}
        result = aggregate_context_annotations(tweets)

        assert len(result["top_categories"]) == 2
        counts = {cat["name"]: cat["count"] for cat in result["top_categories"]}
        assert counts["Technology"] == 2
        assert counts["Artificial Intelligence"] == 2

    def test_aggregate_context_annotations_multiple_domains(self):
        """Test annotations across multiple domains"""
        tweet1 = Tweet(
            id="123",
            text="Tech tweet",
            urls=[],
            media=[],
            annotations={"Technology", "Python"},
            author_id="user123",
            author_username="testuser",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0
        )

        tweet2 = Tweet(
            id="124",
            text="Sports tweet",
            urls=[],
            media=[],
            annotations={"Sports", "Football"},
            author_id="user123",
            author_username="testuser",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0
        )

        tweet3 = Tweet(
            id="125",
            text="Another tech tweet",
            urls=[],
            media=[],
            annotations={"Technology", "JavaScript"},
            author_id="user123",
            author_username="testuser",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0
        )

        tweets = {"123": tweet1, "124": tweet2, "125": tweet3}
        result = aggregate_context_annotations(tweets)

        # Technology appears 2 times, Sports appears once
        counts = {cat["name"]: cat["count"] for cat in result["top_categories"]}
        assert counts["Technology"] == 2
        assert counts["Sports"] == 1
        assert counts["Python"] == 1
        assert counts["Football"] == 1
        assert counts["JavaScript"] == 1

        # Technology should appear first (higher count)
        assert result["top_categories"][0]["name"] == "Technology"
        assert result["top_categories"][0]["count"] == 2

    def test_aggregate_context_annotations_missing_fields(self):
        """Test handling of annotations with missing fields"""
        tweet = Tweet(
            id="123",
            text="Test tweet",
            urls=[],
            media=[],
            annotations={"Technology", "AI"},
            author_id="user123",
            author_username="testuser",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0
        )

        tweets = {"123": tweet}
        result = aggregate_context_annotations(tweets)

        assert len(result["top_categories"]) == 2
        names = {cat["name"] for cat in result["top_categories"]}
        assert "Technology" in names
        assert "AI" in names

    def test_aggregate_context_annotations_no_annotations(self):
        """Test tweet with no annotations"""
        tweet = Tweet(
            id="123",
            text="Plain tweet",
            urls=[],
            media=[],
            annotations=set(),
            author_id="user123",
            author_username="testuser",
            like_count=10,
            retweet_count=5,
            reply_count=2,
            normalized_like_count=10.0,
            normalized_retweet_count=5.0,
            normalized_reply_count=2.0
        )

        tweets = {"123": tweet}
        result = aggregate_context_annotations(tweets, top_k=5)

        assert result == {"top_categories": []}

    def test_aggregate_context_annotations_limit_results(self):
        """Test limiting number of top categories"""
        tweets = {}

        # Create tweets with many different domains
        for i in range(10):
            tweet = Tweet(
                id=str(i),
                text=f"Tweet {i}",
                urls=[],
                media=[],
                annotations={f"Domain{i}", f"Entity{i}"},
                author_id="user123",
                author_username="testuser",
                like_count=10,
                retweet_count=5,
                reply_count=2,
                normalized_like_count=10.0,
                normalized_retweet_count=5.0,
            normalized_reply_count=2.0
            )
            tweets[str(i)] = tweet

        result = aggregate_context_annotations(tweets, top_k=3)
        assert len(result["top_categories"]) == 3


class TestCalculateTopEngagement:
    """Test top engagement calculation"""

    def test_calculate_top_engagement_empty_data(self):
        """Test with empty processed data"""
        processed_data = ProcessedData(tweets={}, user_liked_content={}, user_posted_content={})
        result = calculate_top_engagement(processed_data)

        assert result["top_liked_tweets"] == []
        assert result["top_retweeted_tweets"] == []
        assert result["list_engagement"] == {}

    def test_calculate_top_engagement_basic_tweets(self):
        """Test basic top engagement calculation"""
        tweets = {}

        # Create tweets with different engagement scores
        for i in range(5):
            tweet = Tweet(
                id=str(i),
                text=f"Tweet {i}",
                urls=[],
                media=[],
                annotations=set(),
                author_id="user123",
                author_username="testuser",
                like_count=i * 10,  # 0, 10, 20, 30, 40
                retweet_count=i * 5,  # 0, 5, 10, 15, 20
                reply_count=0,
                normalized_like_count=float(i * 10),
                normalized_retweet_count=float(i * 5),
            normalized_reply_count=0.0
            )
            tweets[str(i)] = tweet

        processed_data = ProcessedData(tweets=tweets, user_liked_content={}, user_posted_content={})
        result = calculate_top_engagement(processed_data, top_k=3)

        # Top liked should be sorted by normalized_like_count descending
        assert len(result["top_liked_tweets"]) == 3
        assert result["top_liked_tweets"][0].normalized_like_count == 40.0  # Highest score (i=4)
        assert result["top_liked_tweets"][1].normalized_like_count == 30.0  # i=3
        assert result["top_liked_tweets"][2].normalized_like_count == 20.0  # i=2

        # Top retweeted should be sorted by normalized_retweet_count descending
        assert len(result["top_retweeted_tweets"]) == 3
        assert result["top_retweeted_tweets"][0].normalized_retweet_count == 20.0  # i=4
        assert result["top_retweeted_tweets"][1].normalized_retweet_count == 15.0  # i=3
        assert result["top_retweeted_tweets"][2].normalized_retweet_count == 10.0  # i=2

    @patch('nuzzel.processors.tweet_aggregator.build_list_id_to_name_mapping')
    def test_calculate_top_engagement_with_lists(self, mock_build_mapping):
        """Test list-based engagement calculation"""
        # Mock the list mapping
        mock_build_mapping.return_value = {"list1": "Tech List", "list2": "News List"}

        tweets = {}

        # Create tweets - some in lists, some not
        for i in range(4):
            tweet = Tweet(
                id=str(i),
                text=f"Tweet {i}",
                urls=[],
                media=[],
                annotations=set(),
                author_id="user123",
                author_username="testuser",
                like_count=i * 10,
                retweet_count=i * 5,
                reply_count=0,
                normalized_like_count=float(i * 10),
                normalized_retweet_count=float(i * 5),
            normalized_reply_count=0.0
            )
            tweets[str(i)] = tweet

        processed_data = ProcessedData(tweets=tweets, user_liked_content={}, user_posted_content={})

        with patch('nuzzel.processors.tweet_aggregator.filter_tweets_by_list') as mock_filter:
            # Mock filter to return different tweet IDs for each list
            mock_filter.side_effect = [
                ["0", "1"],  # Tech list gets tweets 0 and 1
                ["2", "3"]   # News list gets tweets 2 and 3
            ]

            result = calculate_top_engagement(processed_data, top_k=2)

            assert "Tech List" in result["list_engagement"]
            assert "News List" in result["list_engagement"]

            tech_engagement = result["list_engagement"]["Tech List"]
            assert len(tech_engagement["top_liked"]) == 2
            assert len(tech_engagement["top_retweeted"]) == 2

    @patch('nuzzel.processors.tweet_aggregator.build_list_id_to_name_mapping')
    def test_calculate_top_engagement_list_error_handling(self, mock_build_mapping):
        """Test error handling when list processing fails"""
        mock_build_mapping.side_effect = Exception("List error")

        tweets = {
            "123": Tweet(
                id="123",
                text="Test tweet",
                urls=[],
                media=[],
                annotations=set(),
                author_id="user123",
            author_username="testuser",
                like_count=10,
                retweet_count=5,
                reply_count=0,
                normalized_like_count=10.0,
                normalized_retweet_count=5.0,
            normalized_reply_count=2.0
            )
        }

        processed_data = ProcessedData(tweets=tweets, user_liked_content={}, user_posted_content={})

        # Should not raise exception, just log warning
        result = calculate_top_engagement(processed_data)

        assert result["top_liked_tweets"]  # Overall engagement should still work
        assert result["list_engagement"] == {}  # List engagement should be empty on error
