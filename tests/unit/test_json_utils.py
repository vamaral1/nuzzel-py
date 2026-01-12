"""
Unit tests for JSON parsing utilities
"""
import pytest
import json
from nuzzel.utils.json_utils import parse_llm_json_response, extract_json_from_response, repair_json, fix_truncated_json


class TestExtractJsonFromResponse:
    """Test JSON extraction from LLM responses"""

    def test_extract_from_markdown_code_block(self):
        """Test extracting JSON from markdown code block formatting"""
        response = """Here's the categorization:
```json
{
  "tweet_1": {
    "technology": 0.8,
    "other": 0.2
  }
}
```
That's the result."""
        
        result = extract_json_from_response(response)
        parsed = json.loads(result)
        assert parsed == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            }
        }

    def test_extract_from_text_before_and_after(self):
        """Test extracting JSON with text before and after"""
        response = """Some explanatory text before the JSON.
{
  "tweet_1": {
    "technology": 0.9,
    "other": 0.1
  }
}
Some text after the JSON."""
        
        result = extract_json_from_response(response)
        parsed = json.loads(result)
        assert parsed == {
            "tweet_1": {
                "technology": 0.9,
                "other": 0.1
            }
        }

    def test_extract_pure_json(self):
        """Test extracting pure JSON"""
        response = """{
  "tweet_1": {
    "technology": 0.7,
    "other": 0.3
  }
}"""
        
        result = extract_json_from_response(response)
        parsed = json.loads(result)
        assert parsed == {
            "tweet_1": {
                "technology": 0.7,
                "other": 0.3
            }
        }

    def test_extract_multiple_code_blocks(self):
        """Test extracting when response has multiple code blocks"""
        response = """First code block:
```
some code
```
The actual JSON:
```json
{
  "tweet_1": {
    "technology": 0.85,
    "other": 0.15
  }
}
```
Done."""
        
        result = extract_json_from_response(response)
        parsed = json.loads(result)
        assert parsed == {
            "tweet_1": {
                "technology": 0.85,
                "other": 0.15
            }
        }

    def test_extract_with_json_like_text_before_code_block(self):
        """Test extracting when there's JSON-like text before the actual JSON in code block"""
        response = """Here's an example: { "fake": "json" }
Now the real response:
```json
{
  "tweet_1": {
    "technology": 0.9,
    "other": 0.1
  }
}
```"""
        
        result = extract_json_from_response(response)
        parsed = json.loads(result)
        # Should extract the JSON from the code block, not the fake JSON before it
        assert parsed == {
            "tweet_1": {
                "technology": 0.9,
                "other": 0.1
            }
        }

    def test_extract_no_json_raises_error(self):
        """Test that extracting from response with no JSON raises ValueError"""
        response = "No JSON here at all!"
        
        with pytest.raises(ValueError, match="No JSON found in response"):
            extract_json_from_response(response)


class TestRepairJson:
    """Test JSON repair functionality"""

    def test_repair_missing_comma_inside_object(self):
        """Test repairing missing comma inside object"""
        # Missing comma inside an object after a number
        malformed = """{
  "tweet_1": {
    "technology": 0.8
    "other": 0.2
  }
}"""
        
        repaired = repair_json(malformed)
        result = json.loads(repaired)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            }
        }

    def test_repair_missing_comma_between_objects(self):
        """Test repairing missing comma between objects"""
        malformed = """{
  "tweet_1": {
    "technology": 0.8,
    "other": 0.2
  }
  "tweet_2": {
    "technology": 0.5,
    "other": 0.5
  }
}"""
        
        repaired = repair_json(malformed)
        result = json.loads(repaired)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            },
            "tweet_2": {
                "technology": 0.5,
                "other": 0.5
            }
        }

    def test_repair_missing_comma_multiline(self):
        """Test repairing missing comma between objects across multiple lines"""
        malformed = """{
  "tweet_1": {
    "technology": 0.9,
    "other": 0.1
  }

  "tweet_2": {
    "technology": 0.3,
    "other": 0.7
  }
}"""
        
        repaired = repair_json(malformed)
        result = json.loads(repaired)
        assert result == {
            "tweet_1": {
                "technology": 0.9,
                "other": 0.1
            },
            "tweet_2": {
                "technology": 0.3,
                "other": 0.7
            }
        }

    def test_repair_trailing_comma(self):
        """Test repairing trailing comma"""
        malformed = """{
  "tweet_1": {
    "technology": 0.8,
    "other": 0.2,
  },
}"""
        
        repaired = repair_json(malformed)
        result = json.loads(repaired)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            }
        }

    def test_repair_missing_comma_no_whitespace(self):
        """Test repairing missing comma with no whitespace between objects"""
        # Edge case: } immediately followed by " with no space
        malformed = """{
  "tweet_1": {
    "technology": 0.8,
    "other": 0.2
  }"tweet_2": {
    "technology": 0.5,
    "other": 0.5
  }
}"""
        
        repaired = repair_json(malformed)
        result = json.loads(repaired)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            },
            "tweet_2": {
                "technology": 0.5,
                "other": 0.5
            }
        }

    def test_repair_missing_comma_after_number(self):
        """Test repairing missing comma after number before quote"""
        malformed = """{
  "tweet_1": {
    "technology": 0.8
    "other": 0.2
  }
}"""
        
        repaired = repair_json(malformed)
        result = json.loads(repaired)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            }
        }

    def test_repair_missing_comma_after_bracket(self):
        """Test repairing missing comma after closing bracket"""
        malformed = """{
  "items": [1, 2, 3]
  "other": "value"
}"""
        
        repaired = repair_json(malformed)
        result = json.loads(repaired)
        assert result == {
            "items": [1, 2, 3],
            "other": "value"
        }

    def test_repair_double_commas(self):
        """Test repairing double commas that might be introduced"""
        malformed = """{
  "tweet_1": {
    "technology": 0.8,,
    "other": 0.2
  }
}"""
        
        repaired = repair_json(malformed)
        result = json.loads(repaired)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            }
        }


class TestFixTruncatedJson:
    """Test truncated JSON fixing functionality"""

    def test_fix_truncated_missing_closing_brace(self):
        """Test fixing truncated JSON missing closing brace"""
        truncated = """{
  "tweet_1": {
    "technology": 0.8,
    "other": 0.2
  }"""
        # Missing the final }
        
        fixed = fix_truncated_json(truncated)
        result = json.loads(fixed)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            }
        }

    def test_fix_truncated_missing_multiple_braces(self):
        """Test fixing truncated JSON missing multiple closing braces"""
        truncated = """{
  "outer": {
    "inner": {
      "value": 1"""
        # Missing 3 closing braces
        
        fixed = fix_truncated_json(truncated)
        result = json.loads(fixed)
        assert result == {
            "outer": {
                "inner": {
                    "value": 1
                }
            }
        }

    def test_fix_truncated_missing_brackets(self):
        """Test fixing truncated JSON missing closing brackets"""
        truncated = """{
  "items": [1, 2, 3"""
        # Missing closing bracket and brace
        
        fixed = fix_truncated_json(truncated)
        result = json.loads(fixed)
        assert result == {
            "items": [1, 2, 3]
        }

    def test_fix_truncated_no_repair_needed(self):
        """Test that valid JSON is not modified"""
        valid = """{
  "tweet_1": {
    "technology": 0.8,
    "other": 0.2
  }
}"""
        
        fixed = fix_truncated_json(valid)
        assert fixed == valid
        result = json.loads(fixed)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            }
        }


class TestParseLlmJsonResponse:
    """Test the main parse_llm_json_response function"""

    def test_parse_with_markdown_code_block(self):
        """Test parsing response that includes markdown code block formatting"""
        response = """Here's the categorization:
```json
{
  "tweet_1": {
    "technology": 0.8,
    "other": 0.2
  }
}
```
That's the result."""
        
        result = parse_llm_json_response(response)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            }
        }

    def test_parse_with_text_before_and_after(self):
        """Test parsing response with text before and after JSON"""
        response = """Some explanatory text before the JSON.
{
  "tweet_1": {
    "technology": 0.9,
    "other": 0.1
  }
}
Some text after the JSON."""
        
        result = parse_llm_json_response(response)
        assert result == {
            "tweet_1": {
                "technology": 0.9,
                "other": 0.1
            }
        }

    def test_parse_pure_json(self):
        """Test parsing response that is pure JSON"""
        response = """{
  "tweet_1": {
    "technology": 0.7,
    "other": 0.3
  }
}"""
        
        result = parse_llm_json_response(response)
        assert result == {
            "tweet_1": {
                "technology": 0.7,
                "other": 0.3
            }
        }

    def test_parse_malformed_json_missing_comma_inside_object(self):
        """Test parsing response with malformed JSON (missing comma inside object) - should repair"""
        # Missing comma inside an object after a number - repair can fix this
        response = """{
  "tweet_1": {
    "technology": 0.8
    "other": 0.2
  }
}"""
        
        # Should repair the missing comma and parse successfully
        result = parse_llm_json_response(response)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            }
        }

    def test_parse_missing_comma_between_objects(self):
        """Test parsing response with missing comma between objects - should repair"""
        # This is the actual error scenario: missing comma between tweet entries
        response = """{
  "tweet_1": {
    "technology": 0.8,
    "other": 0.2
  }
  "tweet_2": {
    "technology": 0.5,
    "other": 0.5
  }
}"""
        
        # Should repair the missing comma and parse successfully
        result = parse_llm_json_response(response)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            },
            "tweet_2": {
                "technology": 0.5,
                "other": 0.5
            }
        }

    def test_parse_missing_comma_multiline(self):
        """Test parsing response with missing comma between objects across multiple lines"""
        # Missing comma with newline between objects
        response = """{
  "tweet_1": {
    "technology": 0.9,
    "other": 0.1
  }

  "tweet_2": {
    "technology": 0.3,
    "other": 0.7
  }
}"""
        
        result = parse_llm_json_response(response)
        assert result == {
            "tweet_1": {
                "technology": 0.9,
                "other": 0.1
            },
            "tweet_2": {
                "technology": 0.3,
                "other": 0.7
            }
        }

    def test_parse_trailing_comma(self):
        """Test parsing response with trailing comma - should repair"""
        response = """{
  "tweet_1": {
    "technology": 0.8,
    "other": 0.2,
  },
}"""
        
        # Should repair trailing commas and parse successfully
        result = parse_llm_json_response(response)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            }
        }

    def test_parse_empty_dict_on_error(self):
        """Test that parsing errors return default value"""
        response = "No JSON here at all!"
        result = parse_llm_json_response(response, default={})
        assert result == {}

    def test_parse_raises_error_without_default(self):
        """Test that parsing errors raise ValueError when no default provided"""
        response = "No JSON here at all!"
        
        with pytest.raises(ValueError, match="No JSON found in response"):
            parse_llm_json_response(response)

    def test_parse_large_json_with_many_tweets(self):
        """Test parsing large JSON response with missing comma - should repair"""
        # Create a larger JSON structure that might have parsing issues
        large_data = {}
        for i in range(200):
            large_data[f"tweet_{i}"] = {
                "technology": 0.5,
                "other": 0.5
            }
        
        # Simulate a response that might have been corrupted
        response = json.dumps(large_data, indent=2)
        # Intentionally break it by removing a comma (simulating the actual error)
        # Find a comma and remove it to create malformed JSON
        lines = response.split('\n')
        # Find a line with a comma in the middle of the structure
        for i, line in enumerate(lines):
            if '},' in line and i < len(lines) - 10:  # Not the last one
                lines[i] = line.replace('},', '}')
                break
        
        malformed_response = '\n'.join(lines)
        
        # Should repair the missing comma and parse successfully
        result = parse_llm_json_response(malformed_response)
        assert isinstance(result, dict)
        assert len(result) == 200  # All tweets should be parsed
        assert "tweet_0" in result
        assert "tweet_199" in result

    def test_parse_missing_comma_no_whitespace(self):
        """Test parsing response with missing comma and no whitespace between objects"""
        # Edge case: } immediately followed by " with no space
        response = """{
  "tweet_1": {
    "technology": 0.8,
    "other": 0.2
  }"tweet_2": {
    "technology": 0.5,
    "other": 0.5
  }
}"""
        
        result = parse_llm_json_response(response)
        assert result == {
            "tweet_1": {
                "technology": 0.8,
                "other": 0.2
            },
            "tweet_2": {
                "technology": 0.5,
                "other": 0.5
            }
        }

    def test_parse_realistic_llm_output(self):
        """Test parsing realistic LLM output with categories similar to actual usage"""
        # Simulate realistic output matching the error scenario
        response = """{
  "1880651918221545510": {
    "technology": 0.9,
    "programming": 0.8,
    "ai": 0.7,
    "science": 0.0,
    "cultural trends": 0.0,
    "relationships": 0.0,
    "art": 0.0,
    "other": 0.1
  }
  "1880651918221545511": {
    "technology": 0.0,
    "programming": 0.0,
    "ai": 0.0,
    "science": 0.0,
    "cultural trends": 0.4,
    "relationships": 0.0,
    "art": 0.5,
    "other": 0.1
  }
}"""
        
        result = parse_llm_json_response(response)
        assert len(result) == 2
        assert "1880651918221545510" in result
        assert "1880651918221545511" in result
        assert result["1880651918221545510"]["technology"] == 0.9
        assert result["1880651918221545511"]["art"] == 0.5

    def test_parse_truncated_json(self):
        """Test parsing truncated JSON response - should salvage what's complete"""
        # Simulate truncated response - LLM hit token limit mid-response
        # This has 2 complete entries with proper commas, then starts a 3rd that's cut off
        response = """{
  "1880651918221545510": {
    "technology": 0.9,
    "programming": 0.8,
    "ai": 0.7,
    "science": 0.0,
    "cultural trends": 0.0,
    "relationships": 0.0,
    "art": 0.0,
    "other": 0.1
  },
  "1880651918221545511": {
    "technology": 0.0,
    "programming": 0.0,
    "ai": 0.0,
    "science": 0.0,
    "cultural trends": 0.4,
    "relationships": 0.0,
    "art": 0.5,
    "other": 0.3
  },
  "1880651918221545512": {
    "technology": 0.5,
    "programming": 0.2"""
        # JSON is truncated here - missing the rest
        
        result = parse_llm_json_response(response, default={})
        # Should salvage at least the first 2 complete entries
        assert len(result) >= 2
        assert "1880651918221545510" in result
        assert "1880651918221545511" in result
        assert result["1880651918221545510"]["technology"] == 0.9
        assert result["1880651918221545511"]["other"] == 0.3

    def test_parse_truncated_at_entry_boundary(self):
        """Test truncated JSON at entry boundary (missing final })"""
        # Truncated right after a complete entry but missing outer closing brace
        response = """{
  "tweet_1": {
    "technology": 0.8,
    "other": 0.2
  }"""
        # Missing the final }
        
        result = parse_llm_json_response(response, default={})
        assert len(result) == 1
        assert "tweet_1" in result
        assert result["tweet_1"]["technology"] == 0.8

    def test_parse_custom_default(self):
        """Test parsing with custom default value"""
        response = "No JSON here!"
        default = {"error": "parsing failed"}
        result = parse_llm_json_response(response, default=default)
        assert result == default
