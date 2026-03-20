"""
Unit tests for themes and insights generator.
"""
import pytest
from unittest.mock import patch

from nuzzel.generators.themes_and_insights import _parse_themes_response
from nuzzel.generators.themes_and_insights import generate_themes_and_insights
from nuzzel.models import Tweet


def _tweet(tweet_id: str, text: str) -> Tweet:
    return Tweet(
        id=tweet_id,
        author_id="1",
        author_username="user",
        like_count=0,
        retweet_count=0,
        reply_count=0,
        normalized_like_count=0.0,
        normalized_retweet_count=0.0,
        normalized_reply_count=0.0,
        text=text,
        urls=[],
        media=[],
        annotations=set(),
    )


class TestParseThemesResponse:
    """Test _parse_themes_response."""

    def test_parses_highlights_and_caps_at_seven(self):
        raw = """{
  "highlights": ["  a  ", "b", "", 42, "c", "d", "e", "f", "g", "h"],
  "themes": []
}"""
        result = _parse_themes_response(raw)
        assert result["highlights"] == ["a", "b", "42", "c", "d", "e", "f"]
        assert result["summary"] == ""

    def test_returns_dict_when_llm_returns_list(self):
        """When the LLM returns JSON that parses to a list, we must return a dict, not crash."""
        # Replicates production: parse_llm_json_response can return a list when the LLM
        # returns a JSON array (e.g. [{"name": "Theme 1"}]); then result["summary"] = ...
        # raised TypeError: list indices must be integers or slices, not str
        with patch("nuzzel.generators.themes_and_insights.parse_llm_json_response") as mock_parse:
            mock_parse.return_value = [{"name": "Theme A"}, {"name": "Theme B"}]

            result = _parse_themes_response("ignored")

            assert isinstance(result, dict)
            assert "summary" in result
            assert "highlights" in result
            assert "themes" in result
            assert result["summary"] == "Error parsing themes response"
            assert result["highlights"] == []
            assert result["themes"] == []


def test_chunked_flow_with_mock_llm(monkeypatch):
    """Large tweet sets use per-chunk + merge prompts; mock must return valid JSON for each."""
    monkeypatch.setenv("USE_MOCK", "true")
    monkeypatch.setenv("NUZZEL_THEMES_CHUNK_SIZE", "2")
    tweets = {str(i): _tweet(str(i), f"post {i}") for i in range(1, 6)}
    out = generate_themes_and_insights(tweets)
    assert "error" not in out
    assert "highlights" in out
    assert isinstance(out["highlights"], list)
    assert "summary" in out
    assert isinstance(out["themes"], list)
