# Test session state logic for validation

def test_session_state_behavior():
    def should_show_success(success, questions_data):
        # Mimic the Streamlit logic
        return bool(success and questions_data)

    # Test cases
    cases = [
        (True, {'questions': [{}]}),
        (True, None),
        (False, {'questions': [{}]}),
        (False, None),
        (True, {}),
        (True, {'not_questions': []}),
        (True, {'questions': []}),
    ]

    for i, (success, questions_data) in enumerate(cases):
        result = should_show_success(success, questions_data)
        print(f"Case {i+1}: success={success}, questions_data={questions_data} => show_success={result}")

if __name__ == "__main__":
    test_session_state_behavior()
