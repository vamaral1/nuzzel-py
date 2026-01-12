"""
URL Title Fetcher

This module provides functionality to fetch page titles when not provided by Twitter API.
"""

from typing import Dict, Optional
import logging
from urllib.parse import urlparse
import requests  # type: ignore[import-untyped]

from bs4 import BeautifulSoup
from bs4.element import AttributeValueList
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class TitleFetcher:
    """Fetches page titles from URLs with caching and rate limiting"""

    def __init__(self, timeout: int = 10, max_retries: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        # Simple in-memory cache for titles
        self._title_cache: Dict[str, str] = {}

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def fetch_title(self, url: str) -> Optional[str]:
        """
        Fetch page title from URL.

        Args:
            url: URL to fetch title from

        Returns:
            Page title or None if unable to fetch
        """
        if url in self._title_cache:
            return self._title_cache[url]

        try:
            # Only fetch from safe domains and schemes
            if not self._is_safe_url(url):
                return None

            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; TwitterDigest/1.0)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True,
                stream=True  # Don't download full content initially
            )
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('text/html'):
                return None

            # Parse HTML for title
            soup = BeautifulSoup(response.content, 'html.parser')

            # Try different title sources in order of preference
            title = self._extract_title_from_meta(soup)
            title_tag = soup.find('title')
            if not title:
                title = title_tag.get_text(strip=True) if title_tag else None

            if title:
                title = self._clean_title(str(title))
                self._title_cache[url] = title
                return title

        except requests.RequestException as e:
            logger.warning("Failed to fetch title from %s: %s", url, e)
        except Exception as e:
            logger.warning("Error parsing title from %s: %s", url, e)

        return None

    def _is_safe_url(self, url: str) -> bool:
        """Check if URL is safe to fetch from"""
        try:
            parsed = urlparse(url)
            # Only allow http/https
            if parsed.scheme not in ('http', 'https'):
                return False
            # Skip localhost/private IPs
            hostname = parsed.hostname
            if not hostname or hostname in ('localhost', '127.0.0.1', '::1'):
                return False
            # Skip private IP ranges (basic check)
            if hostname.startswith(('10.', '172.', '192.168.', '169.254.')):
                return False
            return True
        except Exception:
            return False

    def _extract_title_from_meta(self, soup: BeautifulSoup) -> Optional[str | AttributeValueList]:
        """Extract title from meta tags"""
        # Try Open Graph title first
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content']

        # Try Twitter card title
        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            return twitter_title['content']

        return None

    def _clean_title(self, title: str) -> str:
        """Clean and normalize title text"""
        if not title:
            return ""

        # Remove excessive whitespace
        title = ' '.join(title.split())

        # Limit length
        if len(title) > 200:
            title = title[:197] + "..."

        return title.strip()


# Global instance for reuse
_title_fetcher = None


def get_title_fetcher() -> TitleFetcher:
    """Get global title fetcher instance"""
    global _title_fetcher
    if _title_fetcher is None:
        _title_fetcher = TitleFetcher()
    return _title_fetcher


def fetch_url_title(url: str) -> Optional[str]:
    """Convenience function to fetch URL title"""
    return get_title_fetcher().fetch_title(url)
