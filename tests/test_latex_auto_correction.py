"""
Test cases for LaTeX auto-correction functionality in JSON processor
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from modules.json_processor import JSONProcessor


class TestLaTeXAutoCorrection:
    """Test LaTeX auto-correction functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.processor = JSONProcessor()
    
    def test_mutext_corrections(self):
        """Test mutext pattern corrections (primary focus)"""
        test_cases = [
            # Basic mutext corrections
            ('mutext{kg}', r'\mu\text{kg}'),
            (r'\mutext{A}', r'\mu\text{A}'),
            ('5 mutext{F}', r'5\,\mu\text{F}'),
            ('10mutext{H}', r'10\,\mu\text{H}'),
            
            # Case insensitive
            ('MUTEXT{V}', r'\mu\text{V}'),
            ('MuText{W}', r'\mu\text{W}'),
        ]
        
        for input_text, expected in test_cases:
            corrected, corrections = self.processor._latex_auto_correct(input_text)
            assert expected in corrected, f"Failed to correct '{input_text}' to contain '{expected}', got '{corrected}'"
            assert len(corrections) > 0, f"No corrections reported for '{input_text}'"
    
    def test_unit_pattern_corrections(self):
        """Test other unit pattern corrections"""
        test_cases = [
            # Ohm corrections
            ('ohmtext{m}', r'\Omega\text{m}'),
            (r'\ohmtext{cm}', r'\Omega\text{cm}'),
            ('5 ohmtext{m}', r'5\,\Omega\text{m}'),
            
            # Degree corrections
            ('degreetext{C}', r'^\circ\text{C}'),
            (r'\degreetext{F}', r'^\circ\text{F}'),
            ('25 degreetext{C}', r'25^\circ\text{C}'),
        ]
        
        for input_text, expected in test_cases:
            corrected, corrections = self.processor._latex_auto_correct(input_text)
            assert expected in corrected, f"Failed to correct '{input_text}' to contain '{expected}', got '{corrected}'"
            assert len(corrections) > 0, f"No corrections reported for '{input_text}'"
    
    def test_double_backslash_corrections(self):
        """Test double backslash corrections"""
        test_cases = [
            (r'\\mu', r'\mu'),
            (r'\\Omega', r'\Omega'),
            (r'\\text{kg}', r'\text{kg}'),
            (r'\\frac{1}{2}', r'\frac{1}{2}'),
            (r'\\sqrt{2}', r'\sqrt{2}'),
            (r'\\times', r'\times'),
            (r'\\circ', r'\circ'),
            (r'\\pi', r'\pi'),
            (r'\\alpha', r'\alpha'),
            (r'\\beta', r'\beta'),
            (r'\\gamma', r'\gamma'),
            (r'\\theta', r'\theta'),
            (r'\\lambda', r'\lambda'),
            (r'\\sigma', r'\sigma'),
        ]
        
        for input_text, expected in test_cases:
            corrected, corrections = self.processor._latex_auto_correct(input_text)
            assert corrected == expected, f"Failed to correct '{input_text}' to '{expected}', got '{corrected}'"
            assert len(corrections) > 0, f"No corrections reported for '{input_text}'"
    
    def test_unicode_math_delimiters(self):
        """Test adding math delimiters for Unicode characters"""
        test_cases = [
            ('5°', r'$5^\circ$'),
            ('10Ω', r'$10\,\Omega$'),
            ('3μ', r'$3\,\mu$'),
            ('2π', r'$2\pi$'),
            ('±', r'$\pm$'),
            ('≤', r'$\leq$'),
            ('≥', r'$\geq$'),
            ('∞', r'$\infty$'),
        ]
        
        for input_text, expected in test_cases:
            corrected, corrections = self.processor._latex_auto_correct(input_text)
            assert corrected == expected, f"Failed to correct '{input_text}' to '{expected}', got '{corrected}'"
            assert len(corrections) > 0, f"No corrections reported for '{input_text}'"
    
    def test_no_false_corrections(self):
        """Test that already correct LaTeX is not modified"""
        correct_cases = [
            r'$\mu\text{F}$',  # Already properly formatted
            r'$5\,\Omega$',    # Already has proper spacing
            r'\frac{1}{2}',    # Single backslash is correct
            r'$25^\circ$',     # Already in math mode
            r'\text{resistance}',  # Normal text command
        ]
        
        for correct_text in correct_cases:
            corrected, corrections = self.processor._latex_auto_correct(correct_text)
            assert corrected == correct_text, f"Incorrectly modified '{correct_text}' to '{corrected}'"
            assert len(corrections) == 0, f"Unnecessary corrections reported for '{correct_text}': {corrections}"
    
    def test_complex_text_with_multiple_corrections(self):
        """Test complex text with multiple LaTeX errors"""
        complex_text = """
        The circuit has a 5 mutext{F} capacitor and a 10 ohmtext{m} resistor.
        The temperature is 25 degreetext{C} with \\\\mu coefficient.
        The angle is 30° and resistance is 100Ω.
        """
        
        corrected, corrections = self.processor._latex_auto_correct(complex_text)
        
        # Check that multiple corrections were made
        assert len(corrections) > 3, f"Expected multiple corrections, got {len(corrections)}: {corrections}"
        
        # Check specific patterns are corrected
        assert r'\mu\text{F}' in corrected, "mutext{F} not corrected"
        assert r'\Omega\text{m}' in corrected, "ohmtext{m} not corrected"
        assert r'^\circ\text{C}' in corrected, "degreetext{C} not corrected"
        assert r'\mu' in corrected and r'\\mu' not in corrected, "Double backslash not corrected"
        assert r'$30^\circ$' in corrected, "Unicode degree not corrected"
        assert r'$100\,\Omega$' in corrected, "Unicode ohm not corrected"
    
    def test_json_context_integration(self):
        """Test LaTeX correction in JSON context"""
        json_with_latex_errors = '''
        {
            "questions": [
                {
                    "type": "multiple_choice",
                    "title": "Capacitor Question",
                    "question_text": "What is the capacitance of a 5 mutext{F} capacitor?",
                    "choices": [
                        "5 \\\\mu F",
                        "5 × 10⁻⁶ F",
                        "5 μF",
                        "0.005 F"
                    ],
                    "correct_answer": "5 μF"
                }
            ]
        }
        '''
        
        # Process through the full pipeline
        success, data, messages = self.processor.process_raw_json(json_with_latex_errors)
        
        # Check that processing succeeded
        assert success, f"Processing failed. Messages: {messages}"
        
        # Debug: Print what we got
        print(f"Success: {success}")
        print(f"Messages: {messages}")
        print(f"Data keys: {list(data.keys()) if data else 'None'}")
        if data and 'questions' in data:
            question = data['questions'][0]
            print(f"Question text: {question.get('question_text', 'Not found')}")
            print(f"Choices: {question.get('choices', 'Not found')}")
        
        # Check that LaTeX corrections were applied
        processed_content = str(data)
        print(f"Processed content: {processed_content}")
        
        # Check for the corrected patterns (accounting for Python string escaping)
        assert r'\\mu\\text{F}' in processed_content or r'\mu\text{F}' in processed_content, "mutext correction not applied in JSON processing"
        
        # Also check the actual question content directly
        question_text = data['questions'][0]['question_text']
        assert r'\mu\text{F}' in question_text, f"mutext correction not in question text: {question_text}"


if __name__ == '__main__':
    # Run the tests
    test_instance = TestLaTeXAutoCorrection()
    test_instance.setup_method()
    
    print("Testing mutext corrections...")
    test_instance.test_mutext_corrections()
    print("✅ mutext corrections test passed")
    
    print("Testing unit pattern corrections...")
    test_instance.test_unit_pattern_corrections()
    print("✅ Unit pattern corrections test passed")
    
    print("Testing double backslash corrections...")
    test_instance.test_double_backslash_corrections()
    print("✅ Double backslash corrections test passed")
    
    print("Testing Unicode math delimiters...")
    test_instance.test_unicode_math_delimiters()
    print("✅ Unicode math delimiters test passed")
    
    print("Testing no false corrections...")
    test_instance.test_no_false_corrections()
    print("✅ No false corrections test passed")
    
    print("Testing complex text with multiple corrections...")
    test_instance.test_complex_text_with_multiple_corrections()
    print("✅ Complex text corrections test passed")
    
    print("Testing JSON context integration...")
    test_instance.test_json_context_integration()
    print("✅ JSON context integration test passed")
    
    print("\n🎉 All LaTeX auto-correction tests passed!")
