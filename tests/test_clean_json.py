# tests/test_clean_json.py

import pytest
from howdoyoufindme.clean_json import clean_and_parse_json, extract_json_string

def test_extract_json_string_no_braces():
    """
    This tests the condition where no '{' or '}' is found,
    triggering the ValueError for missing braces.
    """
    with pytest.raises(ValueError) as exc_info:
        extract_json_string("No JSON here")
    assert "No JSON object braces found in response." in str(exc_info.value)


def test_clean_and_parse_json_no_braces():
    """
    This also tests the same missing braces condition but
    by going through clean_and_parse_json.
    """
    with pytest.raises(ValueError) as exc_info:
        clean_and_parse_json("No JSON here")
    assert "No JSON object braces found in response." in str(exc_info.value)


def test_clean_and_parse_json_decode_error():
    """
    This tests the JSON parsing error path, ensuring we hit
    the 'Failed to parse JSON' exception branch.
    """
    invalid_json_str = "{invalid: true,,}"
    with pytest.raises(ValueError) as exc_info:
        clean_and_parse_json(invalid_json_str)
    assert "Failed to parse JSON after cleaning" in str(exc_info.value)