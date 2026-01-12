"""
JSON Parsing Utilities for LLM Responses

This module provides robust JSON parsing functions for handling LLM responses
that may contain malformed or truncated JSON. It includes repair mechanisms
for common JSON issues like missing commas, trailing commas, and truncated responses.
"""

import json
import logging
import re
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)


def parse_llm_json_response(response: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Parse JSON from an LLM response with robust error handling and repair.

    This function extracts JSON from the response (handling markdown code blocks),
    attempts to parse it, and if parsing fails, applies repair mechanisms to fix
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
        logger.warning("Initial JSON parse failed: %s. Attempting repair...", e)

        # Try to repair and parse again
        try:
            repaired_json = repair_json(json_str)

            # Log what changed for debugging
            if repaired_json != json_str:
                logger.debug("JSON was modified by repair")

            result = json.loads(repaired_json)
            logger.info("JSON repair successful")
            return result
        except (json.JSONDecodeError, ValueError) as repair_error:
            logger.error("Error parsing JSON response after repair: %s", repair_error, exc_info=True)
            # Log a snippet around the error position for debugging
            if hasattr(repair_error, 'pos'):
                pos = repair_error.pos
                start = max(0, pos - 50)
                end = min(len(repaired_json), pos + 100)
                snippet = repaired_json[start:end]
                # Mark the error position
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


def repair_json(json_str: str) -> str:
    """
    Attempt to repair common JSON issues from LLM responses.

    Args:
        json_str: Potentially malformed JSON string

    Returns:
        Repaired JSON string
    """
    repaired = json_str

    # Fix 1: Missing commas after closing brace before opening quote
    # Handles: }\n  "key" or }  "key" or }"key"
    # Uses \s* to match zero or more whitespace (including none)
    repaired = re.sub(r'\}(\s*)"([^}])', r'},\1"\2', repaired)

    # Fix 2: Missing commas after numbers before opening quote (next key)
    # Handles: 0.5\n  "key" - number followed by whitespace and quote
    # Be careful to only match at end of values, not inside strings
    repaired = re.sub(r'(\d)(\s*\n\s*)"', r'\1,\2"', repaired)

    # Fix 3: Missing commas after closing bracket before opening quote
    # Handles: ]\n  "key" or ]  "key"
    repaired = re.sub(r'\](\s*)"', r'],\1"', repaired)

    # Fix 4: Trailing commas before closing braces/brackets (invalid JSON)
    repaired = re.sub(r',(\s*)\}', r'\1}', repaired)
    repaired = re.sub(r',(\s*)\]', r'\1]', repaired)

    # Fix 5: Double commas that might have been introduced
    repaired = re.sub(r',(\s*),', r',\1', repaired)

    # Fix 6: Handle truncated JSON - try to close it properly
    repaired = fix_truncated_json(repaired)

    return repaired


def fix_truncated_json(json_str: str) -> str:
    """
    Attempt to fix truncated JSON by closing unclosed braces/brackets.

    Args:
        json_str: Potentially truncated JSON string

    Returns:
        JSON string with balanced braces
    """
    # Count opening and closing braces/brackets
    open_braces = json_str.count('{')
    close_braces = json_str.count('}')
    open_brackets = json_str.count('[')
    close_brackets = json_str.count(']')

    # Check if truncated (more opens than closes)
    if open_braces > close_braces or open_brackets > close_brackets:
        logger.warning("Detected truncated JSON response (braces: %d open, %d close; brackets: %d open, %d close). Attempting to salvage...",
                     open_braces, close_braces, open_brackets, close_brackets)

        # Add missing closing braces/brackets
        missing_brackets = open_brackets - close_brackets
        missing_braces = open_braces - close_braces

        # Add closing brackets first, then braces (reverse of typical nesting)
        json_str = json_str.rstrip()
        if missing_brackets > 0:
            json_str += ']' * missing_brackets
        if missing_braces > 0:
            json_str += '\n}' * missing_braces

        logger.info("Salvaged truncated JSON by adding %d closing braces and %d closing brackets",
                   missing_braces, missing_brackets)

    return json_str
