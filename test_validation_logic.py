import sys
import types
from modules.json_processor import JSONProcessor

# Mock Streamlit session state
global_session_state = {}

def mock_process_and_validate_json(raw_json):
    processor = JSONProcessor()
    success, questions_data, messages = processor.process_raw_json(raw_json, "chatgpt")
    # Simulate the defensive logic from stage_2_validation.py
    if success and questions_data and isinstance(questions_data, dict) and 'questions' in questions_data:
        global_session_state['questions_data'] = questions_data
        print("DEBUG: questions_data stored in session_state")
    else:
        print("DEBUG: Not storing questions_data in session_state (invalid or failed)")
    return success, questions_data, messages

def print_result(label, result):
    success, questions_data, messages = result
    print(f"\n--- {label} ---")
    print(f"Success: {success}")
    print(f"questions_data: {questions_data}")
    print(f"Type: {type(questions_data)}")
    print(f"Messages: {messages}")
    if questions_data and isinstance(questions_data, dict):
        print(f"Questions count: {len(questions_data.get('questions', []))}")

if __name__ == "__main__":
    # Valid JSON
    valid_json = '{ "questions": [ { "type": "multiple_choice", "title": "Q1", "question_text": "What is 2+2?", "choices": ["2", "3", "4", "5"] } ] }'
    result = mock_process_and_validate_json(valid_json)
    print_result("Valid JSON", result)

    # Invalid JSON (syntax error)
    invalid_json = '{ "questions": [ { "type": "multiple_choice", "title": "Q1" '
    result = mock_process_and_validate_json(invalid_json)
    print_result("Invalid JSON (syntax error)", result)

    # Missing 'questions' key
    missing_key_json = '{ "not_questions": [] }'
    result = mock_process_and_validate_json(missing_key_json)
    print_result("Invalid JSON (missing 'questions' key)", result)
