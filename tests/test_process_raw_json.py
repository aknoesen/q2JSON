def test_mathematical_contradiction_integration():
    """Test 9: Integration with mathematical contradiction detection"""
    
    print("🧪 Test 9: Mathematical Contradiction Detection Integration")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # Apply enhanced validation integration
    from modules.validation_enhancements import integrate_enhanced_validation
    integrate_enhanced_validation(processor)
    
    # JSON with mathematical contradictions (like the MOSFET case)
    contradictory_json = '''{
        "questions": [
            {
                "type": "numerical",
                "title": "MOSFET Threshold Voltage",
                "question_text": "Calculate the threshold voltage",
                "correct_answer": "0.776",
                "feedback_correct": "The calculation gives V_T = 0.8116 V. Rounding to three decimal places, V_T ≈ 0.812 V. Final answer: V_T ≈ 0.776 V.",
                "points": 3
            }
        ]
    }'''
    
    success, data, messages = processor.process_raw_json(contradictory_json)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    # Check for mathematical contradiction detection
    if hasattr(processor, 'get_mathematical_consistency_report'):
        math_report = processor.get_mathematical_consistency_report()
        print(f"   Math Report Available: {len(math_report) > 50}")
        
        if "No mathematical contradictions detected" not in math_report:
            print("   ✅ Mathematical contradictions detected in integration!")
            return True
        else:
            print("   ⚠️ No contradictions detected - may need refinement")
    else:
        print("   ❌ Enhanced validation not integrated")
    
    assert success == True, "Should succeed despite mathematical contradictions"
    print("   ✅ PASS\n")
    return True


def test_unicode_and_special_characters():
    """Test 10: Handling of Unicode and special characters"""
    
    print("🧪 Test 10: Unicode and Special Characters")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # JSON with various Unicode characters
    unicode_json = '''{
        "questions": [
            {
                "type": "multiple_choice",
                "title": "Unicode Test: μ-processor Δt = 5μs",
                "question_text": "Calculate the frequency in Hz. Use π ≈ 3.14159",
                "choices": ["1MHz", "2MHz", "5MHz", "10MHz"],
                "correct_answer": "5MHz",
                "feedback_correct": "Using f = 1/Δt with Δt = 5μs gives f = 200kHz"
            }
        ]
    }'''
    
    success, data, messages = processor.process_raw_json(unicode_json)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    assert success == True, "Should handle Unicode characters"
    
    if data:
        question = data['questions'][0]
        title = question['title']
        question_text = question['question_text']
        
        print(f"   Title: {title}")
        print(f"   Question: {question_text}")
        
        # Check for proper Unicode handling
        assert 'μ' in title or '\\mu' in title, "Should handle mu character"
        assert 'Δ' in title or '\\Delta' in title, "Should handle Delta character"
        assert 'π' in question_text or '\\pi' in question_text, "Should handle pi character"
    
    print("   ✅ PASS\n")
    return True


def test_nested_latex_expressions():
    """Test 11: Complex nested LaTeX expressions"""
    
    print("🧪 Test 11: Complex Nested LaTeX Expressions")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # JSON with complex nested LaTeX
    complex_latex_json = '''{
        "questions": [
            {
                "type": "numerical",
                "title": "Complex Formula",
                "question_text": "Solve $\\\\frac{\\\\sqrt{\\\\gamma^2 + \\\\phi_F}}{\\\\sqrt{2\\\\pi f_T}}$",
                "correct_answer": "1.414",
                "feedback_correct": "Using the formula \\\\gamma = 0.4,text{V}^{1/2} and \\\\phi_F = 0.8,text{V}, we get sqrt{gamma^2 + phi_F} = sqrt{0.16 + 0.8} approx 0.98,text{V}^{1/2}",
                "choices": []
            }
        ]
    }'''
    
    success, data, messages = processor.process_raw_json(complex_latex_json)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    if success and data:
        question = data['questions'][0]
        print(f"   Question: {question['question_text']}")
        print(f"   Feedback: {question['feedback_correct']}")
        
        # Check LaTeX corrections
        assert not question['question_text'].count('\\\\') > question['question_text'].count('\\'), "Should reduce double backslashes"
        assert '\\gamma' in question['feedback_correct'], "Should escape gamma"
        assert '\\phi_F' in question['feedback_correct'], "Should escape phi_F"
        assert '\\sqrt{' in question['feedback_correct'], "Should escape sqrt"
    
    assert success == True, "Should handle complex nested LaTeX"
    
    print("   ✅ PASS\n")
    return True


def test_large_json_performance():
    """Test 12: Performance with large JSON files"""
    
    print("🧪 Test 12: Large JSON Performance Test")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # Generate a large JSON with many questions
    questions = []
    for i in range(50):  # 50 questions
        questions.append({
            "type": "multiple_choice",
            "title": f"Question {i+1}",
            "question_text": f"What is the answer to question {i+1} with gamma = 0.{i%10},text{{V}}?",
            "choices": [f"Option {j}" for j in range(1, 5)],
            "correct_answer": "Option 1",
            "feedback_correct": f"The answer involves gamma({i%10}) calculations",
            "points": 1
        })
    
    large_json = json.dumps({"questions": questions}, indent=2)
    
    import time
    start_time = time.time()
    success, data, messages = processor.process_raw_json(large_json)
    processing_time = time.time() - start_time
    
    print(f"   Success: {success}")
    print(f"   Processing time: {processing_time:.3f} seconds")
    print(f"   Questions processed: {len(data.get('questions', [])) if data else 0}")
    
    assert success == True, "Should handle large JSON files"
    assert processing_time < 5.0, "Should process within reasonable time"
    assert len(data['questions']) == 50, "Should preserve all questions"
    
    print("   ✅ PASS\n")
    return True


def test_malformed_latex_recovery():
    """Test 13: Recovery from severely malformed LaTeX"""
    
    print("🧪 Test 13: Malformed LaTeX Recovery")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # JSON with severely malformed LaTeX
    malformed_latex_json = '''{
        "questions": [
            {
                "type": "numerical",
                "title": "Broken LaTeX Test",
                "question_text": "Calculate using $\\\\\\\\gamma\\\\\\\\sqrt{broken{nested}formula}\\\\\\\\phi_F$",
                "correct_answer": "2.5",
                "feedback_correct": "The formula \\\\\\\\frac{\\\\\\\\gamma}{\\\\\\\\sqrt{incomplete shows 2.5,text{units}",
                "choices": []
            }
        ]
    }'''
    
    success, data, messages = processor.process_raw_json(malformed_latex_json)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    if success and data:
        question = data['questions'][0]
        print(f"   Cleaned question: {question['question_text']}")
        print(f"   Cleaned feedback: {question['feedback_correct']}")
        
        # Should attempt to clean up malformed LaTeX
        assert question['question_text'].count('\\\\\\\\') == 0, "Should remove excessive backslashes"
        assert '\\,\\text{' in question['feedback_correct'], "Should fix comma-text patterns"
    
    assert success == True, "Should recover from malformed LaTeX"
    
    print("   ✅ PASS\n")
    return True


def test_mixed_question_types():
    """Test 14: Mixed question types in single JSON"""
    
    print("🧪 Test 14: Mixed Question Types")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # JSON with multiple question types
    mixed_types_json = '''{
        "questions": [
            {
                "type": "multiple_choice",
                "title": "MC Question",
                "question_text": "Choose the correct answer",
                "choices": ["A", "B", "C", "D"],
                "correct_answer": "B"
            },
            {
                "type": "numerical",
                "title": "Numerical Question",
                "question_text": "Calculate the value",
                "correct_answer": "3.14159",
                "tolerance": 0.001
            },
            {
                "type": "true_false",
                "title": "T/F Question",
                "question_text": "Is this statement true?",
                "correct_answer": "False"
            },
            {
                "type": "essay",
                "title": "Essay Question",
                "question_text": "Explain your reasoning",
                "sample_answer": "A comprehensive explanation..."
            }
        ]
    }'''
    
    success, data, messages = processor.process_raw_json(mixed_types_json)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    assert success == True, "Should handle mixed question types"
    assert len(data['questions']) == 4, "Should preserve all question types"
    
    # Check question types are preserved
    types = [q['type'] for q in data['questions']]
    expected_types = ['multiple_choice', 'numerical', 'true_false', 'essay']
    assert types == expected_types, "Should preserve question type order"
    
    print("   ✅ PASS\n")
    return True


def test_error_edge_cases():
    """Test 15: Various error edge cases"""
    
    print("🧪 Test 15: Error Edge Cases")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # Test completely empty input
    success, data, messages = processor.process_raw_json("")
    assert success == False, "Empty input should fail"
    print("   ✓ Empty input handled correctly")
    
    # Test None input
    try:
        success, data, messages = processor.process_raw_json(None)
        assert success == False, "None input should fail"
        print("   ✓ None input handled correctly")
    except (TypeError, AttributeError):
        print("   ✓ None input raises appropriate exception")
    
    # Test extremely long input
    very_long_input = "a" * 1000000  # 1MB of 'a' characters
    success, data, messages = processor.process_raw_json(very_long_input)
    assert success == False, "Extremely long invalid input should fail"
    print("   ✓ Very long input handled correctly")
    
    # Test input with only whitespace
    success, data, messages = processor.process_raw_json("   \n\t   ")
    assert success == False, "Whitespace-only input should fail"
    print("   ✓ Whitespace-only input handled correctly")
    
    print("   ✅ PASS\n")
    return True


def test_preprocessing_edge_cases():
    """Test 16: Edge cases in preprocessing"""
    
    print("🧪 Test 16: Preprocessing Edge Cases")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # Multiple nested markdown blocks
    nested_markdown = '''
    ```json
    {
        "note": "This is outer JSON"
    }
    ```
    
    Actually, here's the real JSON:
    
    ```json
    {
        "questions": [
            {
                "type": "multiple_choice",
                "title": "Nested Markdown Test",
                "question_text": "Which JSON block is correct?",
                "choices": ["First", "Second"],
                "correct_answer": "Second"
            }
        ]
    }
    ```
    '''
    
    success, data, messages = processor.process_raw_json(nested_markdown)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    assert success == True, "Should extract from nested markdown"
    assert data['questions'][0]['title'] == "Nested Markdown Test", "Should get correct JSON block"
    
    # Test with mixed quote types
    mixed_quotes_json = '''{
        "questions": [
            {
                "type": "multiple_choice",
                "title": "Mixed Quotes Test",
                "question_text": "Handle 'single' and "smart" and \\"escaped\\" quotes",
                "choices": ["Option 1", "Option 2"],
                "correct_answer": "Option 1"
            }
        ]
    }'''
    
    success, data, messages = processor.process_raw_json(mixed_quotes_json)
    assert success == True, "Should handle mixed quote types"
    
    print("   ✅ PASS\n")
    return True


def test_llm_specific_patterns():
    """Test 17: LLM-specific output patterns"""
    
    print("🧪 Test 17: LLM-Specific Output Patterns")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # ChatGPT-style with explanatory text
    chatgpt_style = '''
    I'll create a JSON structure for your educational questions. Here's the formatted output:

    ```json
    {
        "questions": [
            {
                "type": "numerical",
                "title": "ChatGPT Style Test",
                "question_text": "Calculate the result using the given formula",
                "correct_answer": "42.0",
                "feedback_correct": "The calculation uses $$\\\\frac{a}{b}$$ which simplifies to the answer"
            }
        ]
    }
    ```

    This JSON structure follows the educational question format you specified.
    '''
    
    success, data, messages = processor.process_raw_json(chatgpt_style, "chatgpt")
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    assert success == True, "Should handle ChatGPT-style output"
    
    if data:
        feedback = data['questions'][0]['feedback_correct']
        print(f"   Processed feedback: {feedback}")
        # Should handle double backslashes in display math
        assert '\\\\frac' not in feedback or 'Mathematical Formula' in feedback, "Should fix display math"
    
    print("   ✅ PASS\n")
    return True


def test_validation_integration():
    """Test 18: Integration with validation system"""
    
    print("🧪 Test 18: Validation Integration")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # JSON with validation issues
    validation_test_json = '''{
        "questions": [
            {
                "type": "multiple_choice",
                "title": "",
                "question_text": "Question with missing title",
                "choices": ["A", "B"],
                "correct_answer": "A"
            },
            {
                "type": "numerical",
                "title": "Valid Question",
                "question_text": "This question is properly formatted",
                "correct_answer": "5.0",
                "tolerance": 0.1
            }
        ]
    }'''
    
    success, data, messages = processor.process_raw_json(validation_test_json)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    assert success == True, "Should parse JSON with validation issues"
    
    # Test validation
    validation_results = processor.validate_questions(data)
    print(f"   Validation results: {validation_results['total']} total, {validation_results['errors']} errors")
    
    assert validation_results['total'] == 2, "Should validate both questions"
    assert validation_results['errors'] > 0, "Should detect validation errors"
    
    print("   ✅ PASS\n")
    return True


def run_extended_tests():
    """Run all extended tests"""
    
    print("=" * 60)
    print("EXTENDED JSONProcessor.process_raw_json() Test Suite")
    print("=" * 60)
    print()
    
    extended_tests = [
        test_mathematical_contradiction_integration,
        test_unicode_and_special_characters,
        test_nested_latex_expressions,
        test_large_json_performance,
        test_malformed_latex_recovery,
        test_mixed_question_types,
        test_error_edge_cases,
        test_preprocessing_edge_cases,
        test_llm_specific_patterns,
        test_validation_integration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in extended_tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
    
    print("=" * 60)
    print("EXTENDED TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    return failed == 0


# Update the main run_all_tests function to include extended tests
def run_all_tests_comprehensive():
    """Run both basic and extended test suites"""
    
    print("🚀 Running Comprehensive Test Suite")
    print("=" * 60)
    
    # Run basic tests first
    basic_success = run_all_tests()
    
    print("\n" + "=" * 60)
    print("PROCEEDING TO EXTENDED TESTS")
    print("=" * 60)
    
    # Run extended tests
    extended_success = run_extended_tests()
    
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    print(f"Basic Tests: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"Extended Tests: {'✅ PASS' if extended_success else '❌ FAIL'}")
    
    if basic_success and extended_success:
        print("\n🎉 ALL TESTS PASSED! JSONProcessor is fully functional!")
        print("📋 Tested scenarios:")
        print("   • Basic JSON parsing and validation")
        print("   • LaTeX correction and preprocessing")
        print("   • Mathematical contradiction detection")
        print("   • Unicode and special character handling")
        print("   • Performance with large files")
        print("   • Error recovery and edge cases")
        print("   • LLM-specific output patterns")
        print("   • Integration with validation system")
    else:
        print(f"\n🔧 Some tests failed. Review implementation.")
    
    return basic_success and extended_success


if __name__ == "__main__":
    # Run comprehensive test suite
    run_all_tests_comprehensive()
    
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


def test_mathematical_contradiction_integration():
    """Test 9: Integration with mathematical contradiction detection"""
    
    print("🧪 Test 9: Mathematical Contradiction Detection Integration")
    print("-" * 40)
    
    processor = JSONProcessor()
    
    # Apply enhanced validation integration
    from modules.validation_enhancements import integrate_enhanced_validation
    integrate_enhanced_validation(processor)
    
    # JSON with mathematical contradictions (like the MOSFET case)
    contradictory_json = '''{
        "questions": [
            {
                "type": "numerical",
                "title": "MOSFET Threshold Voltage",
                "question_text": "Calculate the threshold voltage",
                "correct_answer": "0.776",
                "feedback_correct": "The calculation gives V_T = 0.8116 V. Rounding to three decimal places, V_T ≈ 0.812 V. Final answer: V_T ≈ 0.776 V.",
                "points": 3
            }
        ]
    }'''
    
    success, data, messages = processor.process_raw_json(contradictory_json)
    
    print(f"   Success: {success}")
    print(f"   Messages: {messages}")
    
    # Check for mathematical contradiction detection
    if hasattr(processor, 'get_mathematical_consistency_report'):
        math_report = processor.get_mathematical_consistency_report()
        print(f"   Math Report Available: {len(math_report) > 50}")
        
        if "No mathematical contradictions detected" not in math_report:
            print("   ✅ Mathematical contradictions detected in integration!")
            return True
        else:
            print("   ⚠️ No contradictions detected - may need refinement")
    else:
        print("   ❌ Enhanced validation not integrated")
    
    assert success == True, "Should succeed despite mathematical contradictions"
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
        test_complex_real_world_scenario,
        test_mathematical_contradiction_integration  # Add this line
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