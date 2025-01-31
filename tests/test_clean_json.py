# tests/test_clean_json.py

import pytest
from howdoyoufindme.clean_json import clean_and_parse_json, extract_json_string

def test_direct_json_parse_success():
    """Test the case where direct JSON parsing succeeds"""
    valid_json = '{"test": "value"}'
    result = extract_json_string(valid_json)
    assert result == valid_json

def test_nested_quotes_handling():
    """Test handling of nested quotes in JSON"""
    json_with_quotes = '{\"message\": \"This has \\"nested\\" quotes\"}'
    result = clean_and_parse_json(json_with_quotes)
    assert result["message"] == 'This has "nested" quotes'

def test_trailing_comma_cleaning():
    """Test cleaning of trailing commas in objects and arrays"""
    json_with_commas = '{"items": ["a", "b",], "more": {"x": 1,}}'
    result = clean_and_parse_json(json_with_commas)
    assert result == {"items": ["a", "b"], "more": {"x": 1}}

def test_full_error_context():
    """Test error context is included in ValueError"""
    invalid_json = '{"test": invalid_value' * 10  # Make it longer than 100 chars
    with pytest.raises(ValueError) as exc_info:
        clean_and_parse_json(invalid_json)
    assert "Content:" in str(exc_info.value)
    assert "..." in str(exc_info.value)  # Should truncate long content