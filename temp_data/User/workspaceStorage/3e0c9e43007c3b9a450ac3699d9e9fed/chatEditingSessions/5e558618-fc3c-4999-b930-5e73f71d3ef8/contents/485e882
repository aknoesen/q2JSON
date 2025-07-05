import os
from modules.json_processor import JSONProcessor

# Helper to load a file

def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

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
    processor = JSONProcessor()
    # Test with valid file
    valid_path = os.path.join('test_data', 'MosfetQQDebug.json')
    if os.path.exists(valid_path):
        valid_json = load_file(valid_path)
        result = processor.process_raw_json(valid_json, llm_type="chatgpt")
        print_result("Valid JSON", result)
    else:
        print(f"File not found: {valid_path}")

    # Test with invalid JSON
    invalid_json = '{ "questions": [ { "type": "multiple_choice", "title": "Q1" '  # missing closing brackets
    result = processor.process_raw_json(invalid_json, llm_type="chatgpt")
    print_result("Invalid JSON (missing brackets)", result)

    # Test with missing 'questions' key
    missing_key_json = '{ "not_questions": [] }'
    result = processor.process_raw_json(missing_key_json, llm_type="chatgpt")
    print_result("Invalid JSON (missing 'questions' key)", result)
