"""
Rate Limit Utilities

This module provides utilities for handling rate limits with jitter to avoid
thundering herd problems.
"""

import random
import time
import logging

logger = logging.getLogger(__name__)


def sleep_with_jitter(base_seconds: float, min_jitter: float = 10.0, max_jitter: float = 60.0) -> None:
    """
    Sleep for the specified base time plus a random jitter.

    This prevents thundering herd problems by spreading out retries across
    multiple clients that hit rate limits at the same time.

    Args:
        base_seconds: Base sleep time in seconds
        min_jitter: Minimum additional jitter in seconds (default: 10.0)
        max_jitter: Maximum additional jitter in seconds (default: 60.0)
    """
    jitter = random.uniform(min_jitter, max_jitter)
    total_sleep = base_seconds + jitter

    logger.info(
        "Sleeping for %.1f seconds (%.1f base + %.1f jitter)",
        total_sleep, base_seconds, jitter
    )

    time.sleep(total_sleep)
