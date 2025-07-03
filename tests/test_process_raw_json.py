"""
Comprehensive test suite for JSONProcessor.process_raw_json method
Tests all scenarios: valid JSON, preprocessing, repairs, LaTeX corrections, failures
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from modules.json_processor import JSONProcessor


def test_valid_json_direct_parsing():
    """Test 1: Valid JSON should parse directly without repair"""
    
    print("🧪 Test 1: Valid JSON Direct Parsing")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # Perfect valid JSON
    valid_json = '''{
        "questions": [
            {
                "type": "multiple_choice",
                "title": "Test Question",
                "question_text": "What is 2+2?",
                "choices": ["3", "4", "5", "6"],
                "correct_answer": "4",
                "points": 1,
                "feedback_correct": "Correct!",
                "feedback_incorrect": "Try again."
            }
        ]
    }'''
    
    success, data, messages = processor.process_raw_json(valid_json)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    print(f"   Questions found: {len(data.get('questions', [])) if data else 0}")
    
    expected_messages = ["✅ Direct JSON parsing successful"]
    assert success == True, "Valid JSON should succeed"
    assert data is not None, "Should return parsed data"
    assert any("Direct JSON parsing successful" in msg for msg in messages), "Should indicate direct parsing"
    
    print("   ✅ PASS\n")
    return True


def test_json_with_latex_corrections():
    """Test 2: JSON with LaTeX errors should be corrected"""
    
    print("🧪 Test 2: JSON with LaTeX Corrections Needed")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # JSON with LaTeX errors that need correction
    latex_error_json = '''{
        "questions": [
            {
                "type": "numerical",
                "title": "MOSFET Question",
                "question_text": "Calculate the voltage $0.5,text{V}$ and current with gamma factor.",
                "correct_answer": "0.776",
                "feedback_correct": "Using gamma(sqrt{2phi_F}) we get 5,text{mS}",
                "choices": []
            }
        ]
    }'''
    
    success, data, messages = processor.process_raw_json(latex_error_json)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    if success and data:
        question = data['questions'][0]
        print(f"   Question text: {question['question_text']}")
        print(f"   Feedback: {question['feedback_correct']}")
    
    assert success == True, "Should succeed with LaTeX corrections"
    assert any("LaTeX corrections" in msg for msg in messages), "Should report LaTeX corrections"
    
    if data:
        # Check that corrections were applied
        question_text = data['questions'][0]['question_text']
        feedback = data['questions'][0]['feedback_correct']
        
        assert "\\,\\text{V}" in question_text, "Should fix comma-text spacing"
        assert "\\gamma" in feedback, "Should escape gamma"
        assert "\\sqrt{" in feedback, "Should escape sqrt"
        assert "\\phi_F" in feedback, "Should escape phi_F"
    
    print("   ✅ PASS\n")
    return True


def test_markdown_wrapped_json():
    """Test 3: JSON wrapped in markdown code blocks should be extracted"""
    
    print("🧪 Test 3: Markdown-Wrapped JSON Extraction")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # JSON wrapped in markdown (common LLM response format)
    markdown_json = '''Here are the questions you requested:

```json
{
    "questions": [
        {
            "type": "true_false",
            "title": "Basic Question",
            "question_text": "Is this a test?",
            "correct_answer": "True",
            "choices": []
        }
    ]
}
```

Let me know if you need any modifications!'''
    
    success, data, messages = processor.process_raw_json(markdown_json)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    assert success == True, "Should extract JSON from markdown"
    assert any("Preprocessing applied" in msg for msg in messages), "Should report preprocessing"
    assert data is not None, "Should return extracted data"
    
    print("   ✅ PASS\n")
    return True


def test_json_with_comments_and_smart_quotes():
    """Test 4: JSON with comments and smart quotes should be cleaned"""
    
    print("🧪 Test 4: JSON with Comments and Smart Quotes")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # JSON with preprocessing issues
    problematic_json = '''{
    # This is a comment that breaks JSON
    "questions": [
        {
            "type": "multiple_choice",
            "title": "Question with "smart quotes"",
            "question_text": "What's the answer?",
            "choices": ["Option 1", "Option 2"],
            "correct_answer": "Option 1"
        }
    ]
}'''
    
    success, data, messages = processor.process_raw_json(problematic_json)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    assert success == True, "Should handle preprocessing issues"
    assert any("Preprocessing applied" in msg for msg in messages), "Should report preprocessing"
    
    if data:
        title = data['questions'][0]['title']
        print(f"   Cleaned title: {title}")
        assert '"' in title or '"' in title, "Should fix smart quotes"
    
    print("   ✅ PASS\n")
    return True


def test_json_needing_repair():
    """Test 5: Malformed JSON should trigger auto-repair"""
    
    print("🧪 Test 5: JSON Needing Auto-Repair")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # Malformed JSON (missing closing brace)
    broken_json = '''{
    "questions": [
        {
            "type": "numerical",
            "title": "Broken Question",
            "question_text": "What is broken?",
            "correct_answer": "42"
        }
    ]
    # Missing closing brace'''
    
    success, data, messages = processor.process_raw_json(broken_json, llm_type="chatgpt")
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    # This might succeed (if repair works) or fail (if repair doesn't work)
    if success:
        assert any("automatically repaired" in msg for msg in messages), "Should report auto-repair"
        print("   ✅ PASS - Repair successful")
    else:
        assert any("Auto-repair failed" in msg or "parsing error" in msg for msg in messages), "Should report repair failure"
        print("   ✅ PASS - Repair failed as expected")
    
    print()
    return True


def test_invalid_structure():
    """Test 6: Valid JSON but missing questions array should fail"""
    
    print("🧪 Test 6: Valid JSON with Invalid Structure")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # Valid JSON but wrong structure
    wrong_structure = '''{
    "data": [
        {"title": "Not a question"}
    ],
    "metadata": {
        "count": 1
    }
}'''
    
    success, data, messages = processor.process_raw_json(wrong_structure)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    assert success == False, "Should fail with missing questions array"
    assert any("missing 'questions' array" in msg for msg in messages), "Should report missing questions"
    assert data is None, "Should return None for invalid structure"
    
    print("   ✅ PASS\n")
    return True


def test_empty_questions_array():
    """Test 7: Valid JSON with empty questions array should fail"""
    
    print("🧪 Test 7: Valid JSON with Empty Questions Array")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # Valid JSON with empty questions
    empty_questions = '''{
    "questions": []
}'''
    
    success, data, messages = processor.process_raw_json(empty_questions)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    assert success == False, "Should fail with empty questions array"
    print("   ✅ PASS\n")
    return True


def test_complex_real_world_scenario():
    """Test 8: Complex real-world scenario with multiple issues"""
    
    print("🧪 Test 8: Complex Real-World Scenario")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # Complex scenario: markdown + comments + LaTeX errors + smart quotes
    complex_json = '''Here's the JSON for your MOSFET questions:

```json
{
    # Educational questions about MOSFETs
    "questions": [
        {
            "type": "numerical",
            "title": "Body Effect Calculation",
            "question_text": "Calculate threshold voltage with gamma = 0.4,text{V}^{1/2}",
            "correct_answer": "0.812",
            "feedback_correct": "Using gamma(sqrt{2phi_F + V_SB}) we get approx 0.812,text{V}",
            "feedback_incorrect": "Check your calculation",
            "points": 2
        }
    ]
}
```

This should work correctly now!'''
    
    success, data, messages = processor.process_raw_json(complex_json)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    if success and data:
        question = data['questions'][0]
        print(f"   Question text: {question['question_text']}")
        print(f"   Feedback: {question['feedback_correct']}")
        
        # Check that all corrections were applied
        assert "\\,\\text{V}" in question['question_text'], "Should fix comma-text in question"
        assert "\\gamma" in question['feedback_correct'], "Should escape gamma in feedback"
        assert "\\sqrt{" in question['feedback_correct'], "Should escape sqrt in feedback"
        assert "\\phi_F" in question['feedback_correct'], "Should escape phi_F in feedback"
    
    assert success == True, "Should handle complex real-world scenario"
    assert any("Preprocessing applied" in msg for msg in messages), "Should report preprocessing"
    assert any("LaTeX corrections" in msg for msg in messages), "Should report LaTeX corrections"
    
    print("   ✅ PASS\n")
    return True


def run_all_tests():
    """Run all process_raw_json tests"""
    
    print("=" * 60)
    print("JSONProcessor.process_raw_json() Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_valid_json_direct_parsing,
        test_json_with_latex_corrections,
        test_markdown_wrapped_json,
        test_json_with_comments_and_smart_quotes,
        test_json_needing_repair,
        test_invalid_structure,
        test_empty_questions_array,
        test_complex_real_world_scenario
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
    
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! JSONProcessor.process_raw_json() is working correctly!")
    else:
        print(f"\n🔧 {failed} tests failed. Review implementation.")
    
    return failed == 0


if __name__ == "__main__":
    run_all_tests()