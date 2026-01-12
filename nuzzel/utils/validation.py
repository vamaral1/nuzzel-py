"""
Input Validation Utilities

This module provides comprehensive input validation functions.
"""

import re
from typing import Any, Dict, Union
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when input validation fails"""


def validate_tweet_data(tweet: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize tweet data"""

    # Required fields
    if 'id' not in tweet:
        raise ValidationError("Tweet missing required 'id' field")

    tweet_id = str(tweet['id']).strip()
    if not tweet_id or not tweet_id.isdigit():
        raise ValidationError(f"Invalid tweet ID: {tweet_id}")

    # Sanitize text
    if 'text' in tweet:
        tweet['text'] = sanitize_text(tweet['text'])

    return tweet


def sanitize_text(text: Any) -> str:
    """Sanitize text input"""
    if text is None:
        return ""

    text = str(text)

    # Remove null bytes and control characters
    text = ''.join(char for char in text if ord(char) >= 32)

    # Limit length
    if len(text) > 10000:  # Reasonable limit for tweet text
        text = text[:9997] + "..."

    return text.strip()


def clean_tweet_text(text: str) -> str:
    """
    Clean tweet text by removing t.co shortened links.

    Args:
        text: The tweet text to clean

    Returns:
        Text with t.co links removed
    """
    if not text:
        return text

    # Pattern to match t.co links (both http and https)
    # Matches: https://t.co/xxxxx or http://t.co/xxxxx
    t_co_pattern = re.compile(r'https?://t\.co/\w+')

    # Remove t.co links and clean up any extra spaces
    cleaned_text = t_co_pattern.sub('', text)

    # Remove any trailing/leading whitespace and clean up multiple spaces
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    return cleaned_text


def validate_time_window(days: Union[int, str]) -> int:
    """Validate time window days"""
    try:
        days_int = int(days)
        if days_int < 1:
            raise ValidationError("Time window must be at least 1 day")
        if days_int > 30:
            raise ValidationError("Time window cannot exceed 30 days (1 month)")
        return days_int
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid time window: {days}") from e


def validate_email_address(email: str) -> str:
    """Validate email address format"""

    email = email.strip()

    # Basic email pattern
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    if not email_pattern.match(email):
        raise ValidationError(f"Invalid email format: {email}")

    return email
