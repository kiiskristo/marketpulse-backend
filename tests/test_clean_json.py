# tests/test_clean_json.py

import pytest
import json
from marketpulse.clean_json import clean_and_parse_json, extract_json_string

def test_direct_json_parse_success():
    """Test the case where direct JSON parsing succeeds"""
    json_str = '{"key1": "value1", "key2": 42}'
    result = clean_and_parse_json(json_str)
    assert result["key1"] == "value1"
    assert result["key2"] == 42

def test_nested_quotes_handling():
    """Test handling of nested quotes in JSON"""
    json_str = '{"text": "He said \\"hello\\" to me"}'
    result = clean_and_parse_json(json_str)
    assert result["text"] == 'He said "hello" to me'

def test_trailing_comma_cleaning():
    """Test cleaning of trailing commas in objects and arrays"""
    json_with_commas = '{"items": ["a", "b",], "more": {"x": 1,}}'
    
    cleaned_str = extract_json_string(json_with_commas)
    
    result = json.loads(cleaned_str)
    
    assert result["items"] == ["a", "b"]
    assert result["more"]["x"] == 1

def test_object_extraction():
    """Test extraction of JSON from text with surrounding content"""
    text_with_json = 'Some prefix text {"data": "important stuff"} and suffix text'
    result = clean_and_parse_json(text_with_json)
    assert result["data"] == "important stuff"

def test_error_on_no_json():
    """Test error handling when no JSON is present"""
    text_without_json = "This is just plain text with no JSON"
    with pytest.raises(ValueError) as excinfo:
        clean_and_parse_json(text_without_json)
    assert "No JSON object braces found" in str(excinfo.value)

def test_error_context():
    """Test error context is included in error messages"""
    invalid_json = '{"test": invalid_value}'
    with pytest.raises(ValueError) as excinfo:
        clean_and_parse_json(invalid_json)
    assert "Failed to parse JSON after cleaning" in str(excinfo.value)