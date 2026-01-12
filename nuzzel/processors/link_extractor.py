"""
Link Extractor and Normalizer

This module provides functionality to extract, clean, and normalize URLs from tweets,
removing tracking parameters and grouping by domain.
"""

from typing import Dict, Any
from collections import defaultdict

from nuzzel.utils.url_utils import extract_domain, construct_tweet_url
from nuzzel.models import Tweet


def extract_shared_links(tweets: Dict[str, Tweet], max_links_per_domain: int = 5) -> Dict[str, Any]:
    """
    Extract and aggregate shared links from tweets, grouped by domain.

    Args:
        tweets: Dictionary of tweet ID to Tweet objects

    Returns:
        Dictionary containing links_by_domain with aggregated link data
    """
    # Structure: domain -> {link -> link_info}
    links_by_domain: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)

    for tweet_id, tweet in tweets.items():
        for url_data in tweet.urls:
            # Extract domain
            url = url_data["url"]
            domain = extract_domain(url)
            if not domain:
                continue

            # Initialize link data if not exists
            if url not in links_by_domain[domain]:
                links_by_domain[domain][url] = {
                    'link': url,
                    'title': url_data["title"],
                    'share_count': 0,
                    'tweets': []
                }

            # Increment share count and add tweet info
            link_data = links_by_domain[domain][url]
            link_data['share_count'] += 1
            # Construct tweet URL
            link_data['tweets'].append({
                'tweet_url': construct_tweet_url(tweet_id)
            })

    # Convert to final output format
    result: Dict[str, Any] = {'links_by_domain': {}}

    for domain, domain_links in links_by_domain.items():
        # Filter out links shared only once (share_count <= 1)
        filtered_links = [
            link for link in domain_links.values()
            if link['share_count'] > 1
        ]

        # Skip domains with no links after filtering
        if not filtered_links:
            continue

        # Sort links by share count (descending)
        sorted_links = sorted(
            filtered_links,
            key=lambda x: x['share_count'],
            reverse=True
        )

        # Calculate total shares for domain
        total_shares = sum(link['share_count'] for link in sorted_links)

        result['links_by_domain'][domain] = {
            'total_shares': total_shares,
            'links': sorted_links[:max_links_per_domain]
        }

    # Sort domains by total shares (descending)
    sorted_domains = sorted(
        result['links_by_domain'].items(),
        key=lambda x: x[1]['total_shares'],
        reverse=True
    )
    result['links_by_domain'] = dict(sorted_domains)

    return result
