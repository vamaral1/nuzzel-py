"""
Unit tests for validation utilities
"""

import pytest
from nuzzel.utils.validation import clean_tweet_text, sanitize_text, validate_tweet_data, ValidationError


class TestCleanTweetText:
    """Test tweet text cleaning functionality"""

    def test_clean_tweet_text_removes_https_t_co_link(self):
        """Test removal of https://t.co/ links"""
        text = "Check out this article https://t.co/wvKTJweAjp"
        result = clean_tweet_text(text)
        assert result == "Check out this article"

    def test_clean_tweet_text_removes_http_t_co_link(self):
        """Test removal of http://t.co/ links"""
        text = "Check out this article http://t.co/abc123"
        result = clean_tweet_text(text)
        assert result == "Check out this article"

    def test_clean_tweet_text_removes_multiple_t_co_links(self):
        """Test removal of multiple t.co links"""
        text = "First link https://t.co/abc123 and second http://t.co/xyz789"
        result = clean_tweet_text(text)
        assert result == "First link and second"

    def test_clean_tweet_text_removes_t_co_link_at_end(self):
        """Test removal of t.co link at end of text"""
        text = "It's not art, it's pictures. It's not writing, it's typing. It's not music, it's sound. It's useful to have alternative names for these new media. How do we secure the arena of human creativity to prevent AI from entering the competition and risk devaluing human generated work? https://t.co/wvKTJweAjp"
        result = clean_tweet_text(text)
        assert result == "It's not art, it's pictures. It's not writing, it's typing. It's not music, it's sound. It's useful to have alternative names for these new media. How do we secure the arena of human creativity to prevent AI from entering the competition and risk devaluing human generated work?"

    def test_clean_tweet_text_removes_t_co_link_in_middle(self):
        """Test removal of t.co link in middle of text"""
        text = "Check out https://t.co/abc123 this article"
        result = clean_tweet_text(text)
        assert result == "Check out this article"

    def test_clean_tweet_text_removes_t_co_link_at_start(self):
        """Test removal of t.co link at start of text"""
        text = "https://t.co/abc123 Check out this article"
        result = clean_tweet_text(text)
        assert result == "Check out this article"

    def test_clean_tweet_text_preserves_other_urls(self):
        """Test that non-t.co URLs are preserved"""
        text = "Check out https://example.com/article and https://t.co/abc123"
        result = clean_tweet_text(text)
        assert result == "Check out https://example.com/article and"

    def test_clean_tweet_text_handles_text_without_links(self):
        """Test text without any links remains unchanged"""
        text = "This is a regular tweet without any links"
        result = clean_tweet_text(text)
        assert result == "This is a regular tweet without any links"

    def test_clean_tweet_text_handles_empty_string(self):
        """Test empty string returns empty string"""
        result = clean_tweet_text("")
        assert result == ""

    def test_clean_tweet_text_handles_only_t_co_link(self):
        """Test text containing only t.co link"""
        text = "https://t.co/abc123"
        result = clean_tweet_text(text)
        assert result == ""

    def test_clean_tweet_text_cleans_extra_whitespace(self):
        """Test that extra whitespace is cleaned up"""
        text = "Text   with    multiple   spaces   https://t.co/abc123"
        result = clean_tweet_text(text)
        assert result == "Text with multiple spaces"

    def test_clean_tweet_text_handles_whitespace_around_link(self):
        """Test whitespace around t.co link is cleaned"""
        text = "Text   https://t.co/abc123   more text"
        result = clean_tweet_text(text)
        assert result == "Text more text"

    def test_clean_tweet_text_preserves_special_chars(self):
        """Test that special characters like hashtags and mentions are preserved"""
        text = "Line 1 Line 2 https://t.co/abc123 #hashtag @mention"
        result = clean_tweet_text(text)
        assert result == "Line 1 Line 2 #hashtag @mention"

    def test_clean_tweet_text_handles_unicode_characters(self):
        """Test handling of unicode characters"""
        text = "Check this out 🚀 https://t.co/abc123"
        result = clean_tweet_text(text)
        assert result == "Check this out 🚀"


class TestSanitizeText:
    """Test text sanitization functionality"""

    def test_sanitize_text_basic(self):
        """Test basic text sanitization"""
        text = "Hello world"
        result = sanitize_text(text)
        assert result == "Hello world"

    def test_sanitize_text_strips_whitespace(self):
        """Test whitespace stripping"""
        text = "  Hello world  "
        result = sanitize_text(text)
        assert result == "Hello world"

    def test_sanitize_text_handles_none(self):
        """Test None input returns empty string"""
        result = sanitize_text(None)
        assert result == ""

    def test_sanitize_text_handles_non_string(self):
        """Test non-string input is converted to string"""
        result = sanitize_text(123)
        assert result == "123"

    def test_sanitize_text_removes_control_characters(self):
        """Test removal of control characters"""
        text = "Hello\x00world\x01test"
        result = sanitize_text(text)
        assert result == "Helloworldtest"

    def test_sanitize_text_truncates_long_text(self):
        """Test truncation of very long text"""
        text = "a" * 10001
        result = sanitize_text(text)
        assert len(result) == 10000
        assert result.endswith("...")


class TestValidateTweetData:
    """Test tweet data validation"""

    def test_validate_tweet_data_valid(self):
        """Test validation of valid tweet data"""
        tweet = {
            'id': '1234567890123456789',
            'text': 'Hello world'
        }
        result = validate_tweet_data(tweet)
        assert result['id'] == '1234567890123456789'
        assert result['text'] == 'Hello world'

    def test_validate_tweet_data_missing_id(self):
        """Test validation fails when id is missing"""
        tweet = {'text': 'Hello world'}
        with pytest.raises(ValidationError):
            validate_tweet_data(tweet)

    def test_validate_tweet_data_invalid_id(self):
        """Test validation fails with invalid id"""
        tweet = {'id': 'not-a-number'}
        with pytest.raises(ValidationError):
            validate_tweet_data(tweet)

    def test_validate_tweet_data_sanitizes_text(self):
        """Test that text is sanitized during validation"""
        tweet = {
            'id': '1234567890123456789',
            'text': '  Hello world  '
        }
        result = validate_tweet_data(tweet)
        assert result['text'] == 'Hello world'

