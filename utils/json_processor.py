"""
JSON processing utilities for q2JSON
"""
import json
import re

def clean_ai_response(response_text, auto_extract=True, clean_markdown=True, fix_quotes=True):
    """
    Clean AI response text and extract JSON
    """
    processed = response_text
    
    # Auto-extract JSON
    if auto_extract:
        json_match = re.search(r'\{.*\}', processed, re.DOTALL)
        if json_match:
            processed = json_match.group(0)
    
    # Clean markdown
    if clean_markdown:
        processed = processed.replace('`json', '').replace('`', '')
        processed = processed.replace('json\n', '')
    
    # Fix quotes
    if fix_quotes:
        processed = processed.replace('"', '"').replace('"', '"')
        processed = processed.replace(''', "'").replace(''', "'")
    
    return processed.strip()

def validate_json_structure(json_data):
    """
    Validate that JSON has the expected structure
    """
    if not isinstance(json_data, dict):
        return False, "JSON must be an object"
    
    if 'questions' not in json_data:
        return False, "Missing 'questions' array"
    
    if not isinstance(json_data['questions'], list):
        return False, "'questions' must be an array"
    
    if len(json_data['questions']) == 0:
        return False, "Questions array is empty"
    
    return True, "Valid structure"
