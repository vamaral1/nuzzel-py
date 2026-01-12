"""
Template Renderer

This module handles rendering HTML templates using Jinja2 for the email digest.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from urllib.parse import urlparse

import markdown  # type: ignore[import-untyped]
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from nuzzel.models import Tweet
from nuzzel.utils.url_utils import construct_tweet_url

# Configure logging
logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Renders HTML templates for email digest"""

    def __init__(self, templates_dir: Optional[str | Path] = None):
        if templates_dir is None:
            # Default to templates directory relative to this file
            templates_dir = Path(__file__).parent.parent.parent / "templates"

        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom filters
        self.env.filters['format_datetime'] = self._format_datetime
        self.env.filters['truncate'] = self._truncate_text
        self.env.filters['url_domain'] = self._extract_domain
        self.env.filters['markdown'] = self._markdown_to_html

    def render_digest_email(self, digest_data: Dict[str, Any], time_window_days: int = 1) -> str:
        """
        Render the complete digest email template.

        Args:
            digest_data: Processed digest data
            time_window_days: Time window in days for the digest

        Returns:
            Rendered HTML email content
        """
        try:
            template = self.env.get_template('email.html')

            # Prepare template context
            context = self._prepare_email_context(digest_data, time_window_days)

            return template.render(**context)

        except Exception as e:
            logger.error("Error rendering email template: %s", e, exc_info=True)
            return self._render_error_email(str(e))

    def _prepare_email_context(self, digest_data: Dict[str, Any], time_window_days: int = 1) -> Dict[str, Any]:
        """
        Prepare the context data for email template rendering.

        Args:
            digest_data: Raw digest data
            time_window_days: Time window in days for the digest

        Returns:
            Processed context for template
        """
        # Get current date for subject
        current_date = datetime.now().strftime("%B %d, %Y")

        context = {
            'current_date': current_date,
            'time_window_days': time_window_days,
            'stats': digest_data.get('stats', {}),
            'themes_summary': digest_data.get('themes_summary', {}),
            'shared_links': digest_data.get('shared_links', {}),
            'top_liked_tweets': digest_data.get('top_liked_tweets', []),
            'top_retweeted_tweets': digest_data.get('top_retweeted_tweets', []),
            'list_engagement': digest_data.get('list_engagement', {}),
            'interest_tweets': digest_data.get('interest_tweets', {}),
            'context_categories': digest_data.get('context_categories', {}),
            'engagement_predictions': digest_data.get('engagement_predictions', {})
        }

        # Add helper functions
        context.update({
            'get_tweet_url': self._get_tweet_url,
            'format_engagement': self._format_engagement,
            'is_error': self._is_error_data
        })

        return context

    def _render_error_email(self, error_msg: str) -> str:
        """
        Render a simple error email when template rendering fails.

        Args:
            error_msg: Error message

        Returns:
            Simple HTML error email
        """
        return f"""
        <html>
        <body>
            <h1>Twitter Digest Error</h1>
            <p>There was an error generating your Twitter digest:</p>
            <p><strong>{error_msg}</strong></p>
            <p>Please check the logs for more details.</p>
        </body>
        </html>
        """

    def _format_datetime(self, datetime_str: str, format_str: str = "%B %d, %Y %H:%M UTC") -> str:
        """
        Format datetime string for display.

        Args:
            datetime_str: ISO datetime string
            format_str: Format string

        Returns:
            Formatted datetime string
        """
        try:
            if datetime_str.endswith('Z'):
                datetime_str = datetime_str[:-1] + '+00:00'
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt.strftime(format_str)
        except Exception:
            return datetime_str

    def _truncate_text(self, text: str, length: int = 100, suffix: str = "...") -> str:
        """
        Truncate text to specified length.

        Args:
            text: Text to truncate
            length: Maximum length
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        if not text or len(text) <= length:
            return text
        return text[:length].rstrip() + suffix

    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL for display.

        Args:
            url: URL string

        Returns:
            Domain name
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return url

    def _markdown_to_html(self, text: str) -> Markup:
        """
        Convert markdown text to HTML.

        Args:
            text: Markdown text to convert

        Returns:
            HTML as Markup (safe for Jinja2 templates)
        """
        if not text:
            return Markup('')
        try:
            html = markdown.markdown(text, extensions=['nl2br', 'fenced_code'])
            return Markup(html)
        except Exception:
            # If markdown conversion fails, return the original text escaped
            return Markup(text.replace('\n', '<br>'))

    def _get_tweet_url(self, tweet_id: str) -> str:
        """
        Generate Twitter URL for a tweet.

        Args:
            tweet_id: Tweet ID

        Returns:
            Twitter URL
        """
        return construct_tweet_url(tweet_id)

    def _format_engagement(self, tweet) -> str:
        """
        Format engagement metrics for display.

        Args:
            tweet: Tweet data (dict or Tweet object)

        Returns:
            Formatted engagement string
        """

        if isinstance(tweet, Tweet):
            like_count = tweet.like_count
            retweet_count = tweet.retweet_count
            reply_count = tweet.reply_count
        elif isinstance(tweet, dict):
            like_count = tweet.get('like_count', 0)
            retweet_count = tweet.get('retweet_count', 0)
            reply_count = tweet.get('reply_count', 0)
        else:
            return "No engagement"

        parts = [
            f"❤️ {like_count}",
            f"🔄 {retweet_count}",
            f"💬 {reply_count}"
        ]

        return " · ".join(parts) if parts else "No engagement"

    def _is_error_data(self, data: Any) -> bool:
        """
        Check if data represents an error.

        Args:
            data: Data to check

        Returns:
            True if data is an error
        """
        if isinstance(data, dict) and 'error' in data:
            return True
        if isinstance(data, list) and data and isinstance(data[0], dict) and 'error' in data[0]:
            return True
        return False


def render_digest_email(digest_data: Dict[str, Any], time_window_days: int = 1) -> str:
    """
    Convenience function to render digest email.

    Args:
        digest_data: Processed digest data
        time_window_days: Time window in days for the digest

    Returns:
        Rendered HTML email
    """
    renderer = TemplateRenderer()
    return renderer.render_digest_email(digest_data, time_window_days)
