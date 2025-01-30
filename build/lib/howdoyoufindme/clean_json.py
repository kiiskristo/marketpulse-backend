import json
import re


def extract_json_string(response: str) -> str:
    """
    Attempts to extract just the JSON part from a string.
    Finds the first '{' and the last '}' and returns the substring.
    """
    start_idx = response.find("{")
    end_idx = response.rfind("}")
    if start_idx == -1 or end_idx == -1:
        raise ValueError("No JSON object braces found in response.")
    return response[start_idx : end_idx + 1]


def clean_and_parse_json(response: str) -> dict:
    """
    Clean and parse JSON from a string response
    """
    json_string = extract_json_string(response)
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {str(e)}")
