"""
JSON Parsing Utilities for LLM Responses

This module provides robust JSON parsing functions for handling LLM responses
that may contain malformed or truncated JSON. It uses the json-repair package
to handle common JSON issues from LLM outputs.
"""

import json
import logging
import re
from typing import Dict, Any, Optional

import json_repair

# Configure logging
logger = logging.getLogger(__name__)


def parse_llm_json_response(response: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Parse JSON from an LLM response with robust error handling and repair.

    This function extracts JSON from the response (handling markdown code blocks),
    attempts to parse it, and if parsing fails, uses json-repair to fix
    common JSON issues before retrying.

    Args:
        response: Raw LLM response string
        default: Optional default value to return if parsing fails completely.
                 If None, raises ValueError.

    Returns:
        Parsed JSON as a dictionary

    Raises:
        ValueError: If JSON cannot be extracted or parsed even after repair attempts
    """
    try:
        # First, try to extract JSON from markdown code blocks
        json_str = extract_json_from_response(response)
        return json.loads(json_str)

    except json.JSONDecodeError as e:
        # Log the error location for debugging
        logger.warning("Initial JSON parse failed: %s. Attempting repair with json-repair...", e)

        # Try to repair and parse again using json-repair.loads() which is a drop-in replacement
        try:
            # json_repair.loads() automatically repairs and parses the JSON
            result = json_repair.loads(json_str)
            logger.info("JSON repair successful using json-repair")
            return result
        except (json.JSONDecodeError, ValueError, Exception) as repair_error:
            logger.error("Error parsing JSON response after json-repair: %s", repair_error, exc_info=True)
            # Log a snippet around the error position for debugging if available
            if hasattr(repair_error, 'pos') and hasattr(repair_error, 'doc'):
                pos = repair_error.pos
                doc = repair_error.doc
                start = max(0, pos - 50)
                end = min(len(doc), pos + 100)
                snippet = doc[start:end]
                # Mark the error position
                marker_pos = pos - start
                logger.error("JSON snippet around error (pos %d):\n%s\n%s^-- ERROR HERE",
                            pos, snippet, " " * marker_pos)
            elif hasattr(repair_error, 'pos'):
                pos = repair_error.pos
                start = max(0, pos - 50)
                end = min(len(json_str), pos + 100)
                snippet = json_str[start:end]
                marker_pos = pos - start
                logger.error("JSON snippet around error (pos %d):\n%s\n%s^-- ERROR HERE",
                            pos, snippet, " " * marker_pos)

            if default is not None:
                return default
            raise ValueError(f"Could not parse JSON even after repair: {repair_error}") from repair_error

    except ValueError as e:
        logger.error("Error extracting JSON from response: %s", e, exc_info=True)
        logger.debug("Raw response: %s", response)
        if default is not None:
            return default
        raise


def extract_json_from_response(response: str) -> str:
    """
    Extract JSON string from LLM response, handling markdown code blocks.

    Args:
        response: Raw LLM response

    Returns:
        JSON string extracted from the response

    Raises:
        ValueError: If no JSON found in response
    """
    # First, try to find JSON inside markdown code blocks (```json ... ``` or ``` ... ```)
    # Look for code blocks with optional json language identifier
    code_block_pattern = r'```(?:json)?\s*\n(.*?)```'
    matches = re.findall(code_block_pattern, response, re.DOTALL)

    if matches:
        # Try each code block match, starting from the last one (usually the actual response)
        for match in reversed(matches):
            match = match.strip()
            if match.startswith('{') and match.endswith('}'):
                try:
                    # Validate it's valid JSON
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue

    # Fall back to simple extraction: find first { and last }
    json_start = response.find("{")
    json_end = response.rfind("}") + 1

    if json_start == -1 or json_end == 0:
        raise ValueError("No JSON found in response")

    return response[json_start:json_end]
