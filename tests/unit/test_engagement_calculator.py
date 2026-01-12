"""
Unit tests for engagement calculation
"""

import pytest
import math
from nuzzel.processors.engagement_calculator import calculate_normalized_engagement


class TestCalculateNormalizedEngagement:
    """Test normalized engagement calculation"""

    def test_calculate_normalized_engagement_large_account(self):
        """Test engagement normalization for large accounts (logarithmic scaling)"""
        engagement_count = 1000
        followers = 1000000  # 1M followers

        result = calculate_normalized_engagement(engagement_count, followers)
        expected = engagement_count / math.log10(followers)

        assert result == pytest.approx(expected, rel=1e-6)

    def test_calculate_normalized_engagement_medium_account(self):
        """Test engagement normalization for medium-sized accounts"""
        engagement_count = 500
        followers = 10000  # 10K followers

        result = calculate_normalized_engagement(engagement_count, followers)
        expected = engagement_count / math.log10(followers)

        assert result == pytest.approx(expected, rel=1e-6)

    def test_calculate_normalized_engagement_small_account(self):
        """Test engagement normalization for small accounts"""
        engagement_count = 100
        followers = 1000  # 1K followers

        result = calculate_normalized_engagement(engagement_count, followers)
        expected = engagement_count / math.log10(followers)

        assert result == pytest.approx(expected, rel=1e-6)

    def test_calculate_normalized_engagement_zero_followers(self):
        """Test engagement calculation when followers is 0 (fallback to raw count)"""
        engagement_count = 50
        followers = 0

        result = calculate_normalized_engagement(engagement_count, followers)
        assert result == engagement_count + 0.0000

    def test_calculate_normalized_engagement_negative_followers(self):
        """Test engagement calculation when followers is negative (fallback to raw count)"""
        engagement_count = 25
        followers = -100

        result = calculate_normalized_engagement(engagement_count, followers)
        assert result == engagement_count + 0.0000

    def test_calculate_normalized_engagement_one_follower(self):
        """Test engagement calculation with minimum followers (fallback to raw count)"""
        engagement_count = 10
        followers = 1

        result = calculate_normalized_engagement(engagement_count, followers)
        # For followers <= 1, should return raw engagement count
        assert result == engagement_count + 0.0000

    def test_calculate_normalized_engagement_zero_engagement(self):
        """Test engagement calculation with zero engagement count"""
        engagement_count = 0
        followers = 50000

        result = calculate_normalized_engagement(engagement_count, followers)
        assert result == 0.0

    def test_calculate_normalized_engagement_high_engagement_ratio(self):
        """Test case where engagement significantly exceeds follower count"""
        engagement_count = 10000  # More than follower count
        followers = 5000

        result = calculate_normalized_engagement(engagement_count, followers)
        expected = engagement_count / math.log10(followers)
        assert result == pytest.approx(expected, rel=1e-6)
        assert result < engagement_count  # Should be reduced due to logarithmic normalization
