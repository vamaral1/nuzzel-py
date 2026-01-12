"""
Unit tests for URL normalization utilities
"""

import pytest
from nuzzel.utils.url_utils import normalize_url, extract_domain, construct_tweet_url


class TestNormalizeUrl:
    """Test URL normalization functionality"""

    def test_normalize_url_basic_https(self):
        """Test basic HTTPS URL normalization"""
        url = "https://example.com/path"
        result = normalize_url(url)
        assert result == "https://example.com/path"

    def test_normalize_url_http_to_https(self):
        """Test HTTP URL converted to HTTPS"""
        url = "http://example.com/path"
        result = normalize_url(url)
        assert result == "https://example.com/path"

    def test_normalize_url_remove_utm_params(self):
        """Test removal of UTM tracking parameters"""
        url = "https://example.com/article?utm_source=twitter&utm_medium=social&utm_campaign=share"
        result = normalize_url(url)
        assert result == "https://example.com/article"

    def test_normalize_url_remove_mixed_tracking_params(self):
        """Test removal of various tracking parameters"""
        url = "https://example.com/page?ref=newsletter&fbclid=123&session_id=abc&utm_source=email"
        result = normalize_url(url)
        assert result == "https://example.com/page"

    def test_normalize_url_preserve_legitimate_params(self):
        """Test preservation of legitimate query parameters"""
        url = "https://example.com/search?q=python&page=1"
        result = normalize_url(url)
        assert result == "https://example.com/search?q=python&page=1"

    def test_normalize_url_remove_trailing_slash(self):
        """Test removal of trailing slashes from path"""
        url = "https://example.com/path/"
        result = normalize_url(url)
        assert result == "https://example.com/path"

    def test_normalize_url_domain_lowercase(self):
        """Test domain normalization to lowercase"""
        url = "https://EXAMPLE.COM/path"
        result = normalize_url(url)
        assert result == "https://example.com/path"

    def test_normalize_url_remove_fragment(self):
        """Test removal of URL fragments"""
        url = "https://example.com/page#section"
        result = normalize_url(url)
        assert result == "https://example.com/page"

    def test_normalize_url_invalid_scheme(self):
        """Test invalid URL schemes return None"""
        url = "ftp://example.com/file"
        result = normalize_url(url)
        assert result is None

    def test_normalize_url_no_scheme(self):
        """Test URLs without scheme return None"""
        url = "example.com/path"
        result = normalize_url(url)
        assert result is None

    def test_normalize_url_empty_string(self):
        """Test empty string returns None"""
        result = normalize_url("")
        assert result is None

    def test_normalize_url_none_input(self):
        """Test None input returns None"""
        result = normalize_url(None)
        assert result is None

    def test_normalize_url_non_string_input(self):
        """Test non-string input returns None"""
        result = normalize_url(123)
        assert result is None


class TestExtractDomain:
    """Test domain extraction functionality"""

    def test_extract_domain_basic(self):
        """Test basic domain extraction"""
        url = "https://example.com/path"
        result = extract_domain(url)
        assert result == "example.com"

    def test_extract_domain_with_www(self):
        """Test domain extraction removes www prefix"""
        url = "https://www.example.com/path"
        result = extract_domain(url)
        assert result == "example.com"

    def test_extract_domain_subdomain(self):
        """Test subdomain preservation"""
        url = "https://blog.example.com/article"
        result = extract_domain(url)
        assert result == "blog.example.com"

    def test_extract_domain_uppercase(self):
        """Test domain normalization to lowercase"""
        url = "https://EXAMPLE.COM/path"
        result = extract_domain(url)
        assert result == "example.com"

    def test_extract_domain_no_scheme(self):
        """Test URLs without scheme"""
        url = "example.com"
        result = extract_domain(url)
        assert result is None

    def test_extract_domain_invalid_url(self):
        """Test invalid URLs return None"""
        url = "not-a-url"
        result = extract_domain(url)
        assert result is None

    def test_extract_domain_empty_string(self):
        """Test empty string returns None"""
        result = extract_domain("")
        assert result is None


class TestConstructTweetUrl:
    """Test tweet URL construction"""

    def test_construct_tweet_url_valid_id(self):
        """Test valid tweet ID construction"""
        tweet_id = "1234567890123456789"
        result = construct_tweet_url(tweet_id)
        assert result == "https://twitter.com/i/status/1234567890123456789"

    def test_construct_tweet_url_empty_string(self):
        """Test empty string returns empty string"""
        result = construct_tweet_url("")
        assert result == ""

    def test_construct_tweet_url_none_input(self):
        """Test None input returns empty string"""
        result = construct_tweet_url(None)
        assert result == ""

    def test_construct_tweet_url_non_string_input(self):
        """Test non-string input returns empty string"""
        result = construct_tweet_url(123)
        assert result == ""
