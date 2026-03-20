"""
Themes and Insights Generator

This module generates high-level themes and insights from tweets using LLM.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from nuzzel.llm_client import create_llm_client, LLMError
from nuzzel.models import Tweet
from nuzzel.utils.json_utils import parse_llm_json_response

# Configure logging
logger = logging.getLogger(__name__)

_DEFAULT_CHUNK_SIZE = 100
_PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def _themes_chunk_size() -> int:
    raw = os.environ.get("NUZZEL_THEMES_CHUNK_SIZE", str(_DEFAULT_CHUNK_SIZE))
    try:
        n = int(raw)
    except ValueError:
        return _DEFAULT_CHUNK_SIZE
    if n < 1:
        return _DEFAULT_CHUNK_SIZE
    return n


def _tweet_sort_key(tweet_id: str) -> int:
    try:
        return int(tweet_id)
    except ValueError:
        return 0


def _tweets_for_llm_payload(tweets: Dict[str, Tweet]) -> List[Dict[str, Any]]:
    ordered_ids = sorted(tweets.keys(), key=_tweet_sort_key)
    out: List[Dict[str, Any]] = []
    for tweet_id in ordered_ids:
        tweet = tweets[tweet_id]
        out.append(
            {
                "tweet_id": tweet_id,
                "text": tweet.text,
                "urls": tweet.urls,
                "media": tweet.media,
                "annotations": list(tweet.annotations),
            }
        )
    return out


def _json_compact(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def _parse_chunk_response(response: str) -> Dict[str, Any]:
    default: Dict[str, Any] = {"notes": "", "themes": []}
    try:
        result = parse_llm_json_response(response, default=default)
    except ValueError:
        return default
    if not isinstance(result, dict):
        return default
    themes = result.get("themes", [])
    if not isinstance(themes, list):
        themes = []
    return {"notes": result.get("notes", "") or "", "themes": themes}


def _run_chunked_themes(
    llm: Any,
    tweets_payload: List[Dict[str, Any]],
    chunk_size: int,
) -> Dict[str, Any]:
    chunk_template = (_PROMPTS_DIR / "themes_chunk.md").read_text()
    merge_template = (_PROMPTS_DIR / "themes_merge.md").read_text()

    n = len(tweets_payload)
    chunk_count = (n + chunk_size - 1) // chunk_size
    merge_inputs: List[Dict[str, Any]] = []

    for i in range(chunk_count):
        start = i * chunk_size
        chunk = tweets_payload[start : start + chunk_size]
        prompt = chunk_template.format(
            chunk_index=i + 1,
            chunk_count=chunk_count,
            tweets_json=_json_compact(chunk),
        )
        raw = llm.generate_text(prompt, system_message=None)
        parsed = _parse_chunk_response(raw)
        merge_inputs.append(
            {
                "chunk_index": i + 1,
                "notes": parsed["notes"],
                "themes": parsed["themes"],
            }
        )

    merge_prompt = merge_template.format(chunks_json=_json_compact(merge_inputs))
    merged_raw = llm.generate_text(merge_prompt, system_message=None)
    return _parse_themes_response(merged_raw)


def _run_single_pass_themes(llm: Any, tweets_payload: List[Dict[str, Any]]) -> Dict[str, Any]:
    prompt_template = (_PROMPTS_DIR / "themes_and_insights.md").read_text()
    prompt = prompt_template.format(tweets_json=_json_compact(tweets_payload))
    response = llm.generate_text(prompt, system_message=None)
    return _parse_themes_response(response)


def generate_themes_and_insights(
    tweets: Dict[str, Tweet],
    llm_client=None,
) -> Dict[str, Any]:
    """
    Generate themes and insights from tweets using LLM.

    Args:
        tweets: Dictionary of tweet_id -> Tweet objects
        llm_client: Optional LLM client (creates one if not provided)

    Returns:
        Dictionary with ``highlights`` (bullet strings), optional legacy ``summary``,
        and ``themes``, or an error message

    When the tweet count exceeds ``NUZZEL_THEMES_CHUNK_SIZE`` (default 45), themes
    are produced with one LLM call per chunk plus a final merge call so backup
    providers with smaller HTTP payload limits (e.g. Groq) can succeed.
    """
    if not tweets:
        return {"error": "No tweets to analyze"}

    try:
        llm = llm_client or create_llm_client()
        tweets_payload = _tweets_for_llm_payload(tweets)
        chunk_size = _themes_chunk_size()

        if len(tweets_payload) > chunk_size:
            logger.info(
                "Themes: using chunked LLM flow (%d tweets, chunk_size=%d)",
                len(tweets_payload),
                chunk_size,
            )
            result = _run_chunked_themes(llm, tweets_payload, chunk_size)
        else:
            result = _run_single_pass_themes(llm, tweets_payload)

        return result

    except LLMError as e:
        logger.error("LLM error generating themes: %s", e, exc_info=True)
        return {"error": "Error getting top themes"}
    except Exception as e:
        logger.error("Error generating themes: %s", e, exc_info=True)
        return {"error": "Error getting top themes"}


def _normalize_highlights(value: Any) -> List[str]:
    """Keep 3–7-style bullet strings from the model; cap length for email layout."""
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for item in value:
        if isinstance(item, str):
            s = item.strip()
            if s:
                out.append(s)
        elif item is not None:
            s = str(item).strip()
            if s:
                out.append(s)
    return out[:7]


def _parse_themes_response(response: str) -> Dict[str, Any]:
    """Parse LLM response into themes structure"""
    default_result = {
        "summary": "Error parsing themes response",
        "highlights": [],
        "themes": [],
    }

    try:
        result = parse_llm_json_response(response, default=default_result)

        # LLM may return JSON that parses to a list (e.g. array of themes); require a dict
        if not isinstance(result, dict):
            return default_result

        # Validate structure
        if "summary" not in result:
            result["summary"] = ""
        if "highlights" not in result:
            result["highlights"] = []
        else:
            result["highlights"] = _normalize_highlights(result["highlights"])
        if "themes" not in result:
            result["themes"] = []

        return result

    except ValueError as e:
        logger.error("Error parsing themes response: %s", e, exc_info=True)
        logger.debug("Raw response: %s", response)
        return default_result
