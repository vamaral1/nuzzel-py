"""
Unit tests for categorizer

Note: JSON parsing tests have been moved to tests/unit/test_json_utils.py
"""
from nuzzel.processors.categorizer import TweetCategorizer


class TestCategorizerIntegration:
    """Test categorizer integration with JSON parsing utility"""

    def test_parse_categorization_response_uses_utility(self):
        """Test that categorizer correctly uses the JSON parsing utility"""
        categorizer = TweetCategorizer()
        
        # Test with valid JSON response
        response = """{
  "tweet_1": {
    "technology": 0.8,
    "other": 0.2
  }
}"""
        
        result = categorizer._parse_categorization_response(response)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            }
        }

    def test_parse_categorization_response_handles_malformed_json(self):
        """Test that categorizer handles malformed JSON via utility"""
        categorizer = TweetCategorizer()
        
        # Test with malformed JSON (missing comma) - should be repaired by utility
        response = """{
  "tweet_1": {
    "technology": 0.8
    "other": 0.2
  }
}"""
        
        result = categorizer._parse_categorization_response(response)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            }
        }

    def test_parse_categorization_response_returns_empty_dict_on_error(self):
        """Test that categorizer returns empty dict when JSON parsing fails"""
        categorizer = TweetCategorizer()
        
        response = "No JSON here at all!"
        result = categorizer._parse_categorization_response(response)
        assert result == {}
