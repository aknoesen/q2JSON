"""
Debug LaTeX correction implementation for real-world patterns
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.json_processor import JSONProcessor


def test_problematic_patterns():
    """Test the specific patterns that are being missed"""
    processor = JSONProcessor()
    
    # Test individual patterns
    test_patterns = [
        # Comma-text patterns
        ("0.5,text{V}", r"0.5,\\text{V}"),
        ("3.2,text{A}", r"3.2,\\text{A}"),
        ("value,text{units}", r"value,\\text{units}"),
        
        # Unescaped Greek letters
        ("gamma", r"\\gamma"),
        ("phi_F", r"\\phi_F"),
        ("alpha", r"\\alpha"),
        ("beta", r"\\beta"),
        ("theta", r"\\theta"),
        ("lambda", r"\\lambda"),
        ("sigma", r"\\sigma"),
        ("delta", r"\\delta"),
        ("epsilon", r"\\epsilon"),
        ("omega", r"\\omega"),
        
        # Mixed patterns
        ("The gamma coefficient is 0.5,text{V}", "complex pattern"),
        ("phi_F threshold with gamma dependency", "multiple Greek letters"),
    ]
    
    print("=== Testing Individual Pattern Corrections ===")
    for input_text, expected_contains in test_patterns:
        print(f"\nTesting: '{input_text}'")
        corrected, corrections = processor._latex_auto_correct(input_text)
        print(f"Corrected: '{corrected}'")
        print(f"Corrections made: {corrections}")
        
        if corrected == input_text:
            print(f"❌ NO CORRECTION APPLIED!")
        else:
            print(f"✅ Correction applied")


def test_full_json_processing():
    """Test with actual JSON data"""
    processor = JSONProcessor()
    
    with open('test_data/debug_latex_patterns.json', 'r', encoding='utf-8') as f:
        json_content = f.read()
    
    print("\n\n=== Testing Full JSON Processing ===")
    print("Original JSON content:")
    print(json_content)
    
    success, data, messages = processor.process_raw_json(json_content)
    
    print(f"\nProcessing success: {success}")
    print(f"Messages: {messages}")
    
    if success and data:
        print("\nProcessed data:")
        import json
        print(json.dumps(data, indent=2))
        
        # Check if corrections were actually applied
        question_text = data['questions'][0]['question_text']
        choices = data['questions'][0]['choices']
        
        print(f"\nQuestion text: {question_text}")
        print(f"Choices: {choices}")
        
        # Check for specific patterns
        patterns_to_check = [
            (",text{", "comma-text pattern"),
            ("gamma", "unescaped gamma"),
            ("phi_F", "unescaped phi_F"),
        ]
        
        all_text = question_text + " " + " ".join(str(c) for c in choices)
        
        for pattern, description in patterns_to_check:
            if pattern in all_text:
                print(f"❌ {description} still present: '{pattern}'")
            else:
                print(f"✅ {description} was corrected")


def debug_pattern_matching():
    """Debug the specific regex patterns"""
    import re
    
    print("\n\n=== Debugging Regex Patterns ===")
    
    test_strings = [
        "0.5,text{V}",
        "gamma",
        "phi_F",
        "The gamma coefficient",
        "value,text{units}",
    ]
    
    # Test current patterns from the implementation
    current_patterns = [
        # mutext patterns
        (r'(\d+)\s*mutext\{', r'\1\\,\\mu\\text{'),
        (r'\bmutext\{', r'\\mu\\text{'),
        (r'\\mutext\{', r'\\mu\\text{'),
        
        # unit patterns  
        (r'(\d+)\s*ohmtext\{', r'\1\\,\\Omega\\text{'),
        (r'(\d+)\s*degreetext\{', r'\1^\\circ\\text{'),
        (r'\bohmtext\{', r'\\Omega\\text{'),
        (r'\\ohmtext\{', r'\\Omega\\text{'),
        (r'\bdegreetext\{', r'^\\circ\\text{'),
        (r'\\degreetext\{', r'^\\circ\\text{'),
        
        # double backslash patterns
        (r'\\\\mu\b', r'\\mu'),
        (r'\\\\gamma\b', r'\\gamma'),
        (r'\\\\text\{', r'\\text{'),
    ]
    
    for test_string in test_strings:
        print(f"\nTesting string: '{test_string}'")
        
        for pattern, replacement in current_patterns:
            if re.search(pattern, test_string, re.IGNORECASE):
                print(f"  ✅ Matches pattern: {pattern}")
                result = re.sub(pattern, replacement, test_string, flags=re.IGNORECASE)
                print(f"     Result: '{result}'")
            else:
                print(f"  ❌ No match for: {pattern}")


if __name__ == '__main__':
    print("🔍 Debugging LaTeX Correction Implementation")
    print("=" * 50)
    
    test_problematic_patterns()
    debug_pattern_matching()
    test_full_json_processing()
    
    print("\n" + "=" * 50)
    print("🎯 Debug Analysis Complete")
