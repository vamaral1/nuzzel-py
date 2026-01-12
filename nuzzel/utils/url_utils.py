"""
URL Normalization Utilities

This module provides functions for cleaning and normalizing URLs found in tweets,
including removing tracking parameters and extracting canonical URLs.
"""

import urllib.parse
from typing import Optional


def normalize_url(url: str) -> Optional[str]:
    """
    Normalize a URL by removing tracking parameters and standardizing format.

    Args:
        url: The URL to normalize

    Returns:
        Normalized URL or None if invalid
    """
    if not url or not isinstance(url, str):
        return None
    # Parse the URL
    parsed = urllib.parse.urlparse(url)

    # Skip invalid URLs
    if not parsed.scheme or not parsed.netloc:
        return None

    # Standardize scheme to https (unless it's already http and valid)
    scheme = parsed.scheme.lower()
    if scheme not in ['http', 'https']:
        return None

    # Remove tracking parameters
    cleaned_query = _remove_tracking_params(parsed.query)

    # Reconstruct URL with cleaned query
    cleaned_url = urllib.parse.urlunparse((
        'https',
        parsed.netloc.lower(),  # Normalize domain to lowercase
        parsed.path.rstrip('/'),  # Remove trailing slashes from path
        parsed.params,
        cleaned_query,
        ''  # Remove fragment
    ))

    return cleaned_url if cleaned_url else None


def _remove_tracking_params(query_string: str) -> str:
    """
    Remove common tracking parameters from query string.

    Args:
        query_string: URL query string

    Returns:
        Cleaned query string
    """
    if not query_string:
        return ''

    params = urllib.parse.parse_qs(query_string, keep_blank_values=False)

    # Common tracking parameters to remove
    tracking_params = {
        # UTM parameters
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        # Referral parameters
        'ref', 'referrer', 'source',
        # Social media tracking
        'fbclid', 'gclid', 'msclkid', 'twclid',
        # Generic tracking
        'campaign_id', 'ad_group_id', 'ad_id', 'creative_id',
        # Email tracking
        'mc_cid', 'mc_eid',
        # Other common parameters
        'igshid', 'share_id', 'session_id'
    }

    # Remove tracking parameters
    cleaned_params = {
        key: value for key, value in params.items()
        if key.lower() not in tracking_params
    }

    # Reconstruct query string
    if cleaned_params:
        return urllib.parse.urlencode(cleaned_params, doseq=True)
    else:
        return ''



def extract_domain(url: str) -> Optional[str]:
    """
    Extract the domain from a URL.

    Args:
        url: The URL to extract domain from

    Returns:
        Domain name or None if invalid URL
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc:
        # Remove www. prefix if present
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    return None


def construct_tweet_url(tweet_id: str) -> str:
    """
    Construct a tweet URL from tweet ID.

    Uses the universal Twitter URL format that works without username.

    Args:
        tweet_id: The tweet ID

    Returns:
        Full tweet URL
    """
    if not tweet_id or not isinstance(tweet_id, str):
        return ""
    return f"https://twitter.com/i/status/{tweet_id}"
